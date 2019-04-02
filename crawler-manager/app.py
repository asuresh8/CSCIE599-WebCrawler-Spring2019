import boto3
import flask
from google.cloud import storage
import json
import logging
import os
import requests
import signal
import sys
import threading
import time

import crawler_manager_context
import helpers
import redis_connect
import work_processor

app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_manager_context.Context(app.logger)

INIT_TIME = time.time()
JOB_ID = os.environ.get('JOB_ID', '')
IMAGE_TAG = os.environ.get('IMAGE_TAG', '0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
RELEASE_DATE = os.environ.get('RELEASE_DATE', '0')
HOSTNAME = os.environ.get('JOB_IP', '0.0.0.0')
NUM_CRAWLERS = os.environ.get('NUM_CRAWLERS', 1)
INITIAL_URLS = os.environ.get('STARTING_URLS', 'http://recurship.com').split(';')
DOMAIN_RESTRICTIONS = os.environ.get('DOMAIN_RESTRICTIONS', 'http://www.garbage.com').split(';')
MAIN_APPLICATION_ENDPOINT = os.environ.get('MAIN_APPLICATION_ENDPOINT', 'http://0.0.0.0:8001')
PORT = 8002 if HOSTNAME == '0.0.0.0' else 80
ENDPOINT = 'http://{}:{}'.format(HOSTNAME, PORT)

CRAWLER_MANAGER_ENDPOINT = 'http://0.0.0.0:8002';
if ENVIRONMENT == 'prod':
    CRAWLER_MANAGER_ENDPOINT = f"http://crawler-manager-service-{RELEASE_DATE}.default/"

def after_this_request(func):
    if not hasattr(flask.g, 'call_after_request'):
        flask.g.call_after_request = []
    flask.g.call_after_request.append(func)
    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(flask.g, 'call_after_request', ()):
        response = func(response)
    return response


@app.route('/', methods=['GET'])
def main():
    context.logger.info('Received request at home')
    return 'Crawler Manager'


@app.route('/kill', methods=['POST'])
def kill():
    @after_this_request
    def maybe_kill(response):
        if ENVIRONMENT == 'local':
            context.logger.info("Not killing crawler manager because running locally")
        else:
            context.logger.info("Kill confirmed")
            sys.exit()

        return response

    context.logger.info('Kill called for')
    return ""


#Register endpoint
#An endpoint that the crawler will call to register itself once instantiated, ip/dns added to available crawler list.
@app.route('/register_crawler', methods=['POST'])
def register():
    crawler_endpoint = flask.request.json('endpoint')
    context.logger.info('registering crawler with endpoint %s', crawler_endpoint)
    context.crawlers.add(crawler_endpoint)
    return ""


#Result endpoint
#An endpoint that the  crawler calls to respond with the url assigned, it's corresponding S3 Link and the list of child url's
#example JSON
# {
# "main_url":"http://recurship.com/",
# "S3":"https://bucket.s3-aws-region.amazonaws.com/key",
# "child_urls":[ "a", "b", "c" ]
# }
@app.route('/links', methods=['POST'])
def links():
    context.logger.info('Received response from crawler: %s', flask.request.data)
    main_url = flask.request.json['main_url']
    s3_uri = flask.request.json['s3_uri']
    child_urls = flask.request.json['child_urls']
    for url in child_urls:
        if helpers.is_absolute_url(url):
            absolute_url = helpers.expand_url(helpers.get_domain_name(main_url), url)
        else:
            absolute_url = url

        if not context.queued_urls.contains(absolute_url) and \
           not context.in_process_urls.contains(absolute_url) and \
           not redis_connect.exists(absolute_url):
            context.logger.info('Adding %s to queue', absolute_url)
            context.queued_urls.add(absolute_url)

    redis_connect.put(main_url, s3_uri)
    context.processed_urls.increment()
    context.in_process_urls.remove(main_url)
    return ""


#Returns statistics on the current crawl
@app.route('/status', methods=['GET'])
def status():
    context.logger.info('Received status request')
    processedCount = context.processed_urls.get()
    processingCount = context.in_process_urls.size()
    queuedCount = context.queued_urls.size()
    return flask.jsonify({
        'processedCount' : processedCount,
        'processingCount': processingCount,
        'queuedCount' : queuedCount}
    )


def deploy_crawlers():
    for _ in range(NUM_CRAWLERS):
        helm_command = get_helm_command()
        context.logger.info('Running helm command: %s', helm_command)
        os.system(helm_command)


def get_helm_command():
    return f"""helm init --service-account tiller && \\
        helm upgrade --install \\
        --set-string image.tag='{IMAGE_TAG}' \\
        --set-string params.endpoint='{ENDPOINT}' \\
        --set-string params.crawlerManagerEndpoint='{CRAWLER_MANAGER_ENDPOINT}' \\
        \"crawler-{RELEASE_DATE}\" ./cluster-templates/chart-crawler"""


#Testing Connections
def test_connections():
    redis_connect.test_redis_connection()


def run_flask():
    app.run(debug=False, host=HOSTNAME, port=PORT, use_reloader=False)


def run_work_processor():
    processor = work_processor.Processor(context)
    processor.run()
    # tell workers to go kill themselves
    if ENVIRONMENT != 'local':
        crawlers = context.crawlers.get()
        for crawler in crawlers:
            kill_api = os.path.join(crawler, "kill")
            try:
                requests.post(kill_api, data=json.dumps({}))
            except Exception as e:
                context.logger.error('Unable to kill crawler: %s', str(e))

    # load manifest from local redis
    manifest = redis_connect.write_data_to_file()
    manifest_filename = 'manifest-{}.csv'.format(manifest)
    # Write to S3
    # s3 = boto3.resource('s3')
    # s3.meta.client.upload_file(manifest, 'mybucket', manifest_filename)
    # Write to GCS
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    blob = bucket.blob(manifest_filename)
    blob.upload_from_filename(manifest)
    blob.make_public()
    os.remove(manifest)
    crawl_complete_api = os.path.join(MAIN_APPLICATION_ENDPOINT, 'api/crawl_complete')
    try:
        requests.post(crawl_complete_api, data=json.dumps({'manifest': blob.public_url}))
    except Exception as e:
        context.logger.error('Unable to send crawl_complete to main applications: %s', str(e))


def setup():
    try:
        requests.post(os.path.join(MAIN_APPLICATION_ENDPOINT, 'api/register_crawler_manager'),
                      data=json.dumps({'job_id': JOB_ID, 'endpoint': ENDPOINT}))
    except Exception as e:
        context.logger.error('Unable to register with main application: %s', str(e))

    processor_thread = threading.Thread(target=run_work_processor)
    processor_thread.start()


if __name__ == "__main__":
    test_connections()
    # if running locally, then run normally. If running on Kubernetes cluster, then do weird shit
    if ENVIRONMENT == 'local':
        setup()
        run_flask()
    else:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()
        print('Will kill server after 20s -- jobId', JOB_ID,file=sys.stderr)
        deploy_crawlers()
        time.sleep(60)
        sys.exit(0)
