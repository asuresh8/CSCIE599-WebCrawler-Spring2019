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

import _thread

app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_manager_context.Context(app.logger)

INIT_TIME = time.time()
JOB_ID = os.environ.get('JOB_ID', '')
IMAGE_TAG = os.environ.get('IMAGE_TAG', '0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
DEBUG_MODE = ENVIRONMENT == 'local'
RELEASE_DATE = os.environ.get('RELEASE_DATE', '0')
HOSTNAME = os.environ.get('JOB_IP', 'crawler-manager')
NUM_CRAWLERS = os.environ.get('NUM_CRAWLERS', 1)
INITIAL_URLS = os.environ.get('STARTING_URLS', 'http://recurship.com').split(';')
DOMAIN_RESTRICTIONS = os.environ.get('DOMAIN_RESTRICTIONS', 'http://www.garbage.com').split(';')
MAIN_APPLICATION_ENDPOINT = os.environ.get('MAIN_APPLICATION_ENDPOINT', 'http://main:8001')
PORT = 8002 if HOSTNAME == 'crawler-manager' else 80
ENDPOINT = 'http://{}:{}'.format(HOSTNAME, PORT)

CRAWLER_MANAGER_ENDPOINT = 'http://crawler-manager:8002'
if (ENVIRONMENT == 'prod' and RELEASE_DATE != '0'):
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

@app.route('/ping', methods=['GET'])
def ping():
    context.logger.info('Received request at PING')
    return 'Crawler Manager PING'

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
    crawler_endpoint = flask.request.json['endpoint']
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
        

        if any(map(lambda x: url.startswith(x), DOMAIN_RESTRICTIONS)) and \
          not context.queued_urls.contains(absolute_url) and \
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
    app.run(debug=DEBUG_MODE, host=HOSTNAME, port=PORT, use_reloader=False)


def run_work_processor():
    processor = work_processor.Processor(context)
    processor.run()
    # tell workers to go kill themselves
    crawlers = context.crawlers.get()
    for crawler in crawlers:
        kill_api = os.path.join(crawler, "kill")
        try:
            context.logger.info("Sending kill request to crawler: %s", crawler)
            requests.post(kill_api, json={})
            context.logger.info("Successfully killed crawler: %s", crawler)
        except Exception as e:
            context.logger.error('Unable to kill crawler: %s', str(e))

    # load manifest from local redis
    context.logger.info("creating manifest from redis")
    manifest = redis_connect.write_data_to_file()
    key = 'manifest-{}.csv'.format(JOB_ID)
    # Write to S3
    # s3 = boto3.resource('s3')
    # s3.meta.client.upload_file(manifest, 'mybucket', manifest_filename)
    # Write to GCS
    context.logger.info("Uploading manifest to GCS")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    blob = bucket.blob(key)
    blob.upload_from_filename(manifest)
    blob.make_public()
    context.logger.info("Manifest uploaded! Deleting local file")
    os.remove(manifest)
    crawl_complete_api = os.path.join(MAIN_APPLICATION_ENDPOINT, 'api/crawl_complete')
    try:
        context.logger.info("Calling crawl_complete api")
        requests.post(crawl_complete_api, json={'manifest': blob.public_url})
        context.logger.info("crawl_complete call successful")
    except Exception as e:
        context.logger.error('Unable to send crawl_complete to main applications: %s', str(e))


def setup():
    try:
        context.logger.info('Attempting to register with main application')
        requests.post(os.path.join(MAIN_APPLICATION_ENDPOINT, 'api/register_crawler_manager'),
                      json={'job_id': JOB_ID, 'endpoint': ENDPOINT})
        context.logger.info('Registered with main application!')
    except Exception as e:
        context.logger.error('Unable to register with main application: %s', str(e))

    for url in INITIAL_URLS:
        context.queued_urls.add(url)
    
    processor_thread = threading.Thread(target=run_work_processor)
    processor_thread.start()

def ping_main():
    try:
        main_url = os.path.join(MAIN_APPLICATION_ENDPOINT, f'main_app/api/ping?releaseDate={RELEASE_DATE}')
        context.logger.info('main_url %s', main_url)
        r = requests.get(main_url)
        return r.text
    except requests.RequestException as rex:
        return "request exception"
    except requests.HTTPException as htex:
        return "http exception"
    except Exception as ex:
        return "general exception"

if __name__ == "__main__":
    ping = ping_main()
    context.logger.info('ping main app -- %s', ping)
    context.logger.info('MAIN_APPLICATION_ENDPOINT -- %s', MAIN_APPLICATION_ENDPOINT)

    context.logger.info('will connect to redis')
    test_connections()
    # if running locally, then run normally. If running on Kubernetes cluster, then do weird shit
    context.logger.info('ENVIRONMENT -- %s ', ENVIRONMENT)
    if ENVIRONMENT == 'local':
        setup()
        run_flask()
    else:
        #flask_thread = threading.Thread(target=run_flask)
        #flask_thread.start()
        _thread.start_new_thread(run_flask,())
        time.sleep(5)
        ping = ping_main()
        context.logger.info('second ping to main app %s ', ping)
        context.logger.info('SECOND PING TO MAIN_APPLICATION_ENDPOINT %s ', MAIN_APPLICATION_ENDPOINT)
        context.logger.info('Will kill server after 60s -- jobId %s ', JOB_ID)

        deploy_crawlers()
        time.sleep(60)

        context.logger.info('should kill it now')
        sys.exit(0)
