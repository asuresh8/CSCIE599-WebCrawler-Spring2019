import boto3
import flask
import json
import logging
import os
import redis
import reppy
import requests
import signal
import sys
import threading
import time
import urllib
import uuid

import crawler_manager_context
import helpers
import redis_connect
import work_processor



app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_manager_context.Context(app.logger)

INIT_TIME = time.time()
NAMESPACE = os.environ.get('NAMESPACE', 'default')
JOB_ID = os.environ.get('JOB_ID', '0')
IMAGE_TAG = os.environ.get('IMAGE_TAG', '0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
DEBUG_MODE = ENVIRONMENT == 'local'
RELEASE_DATE = os.environ.get('RELEASE_DATE', '0')
HOSTNAME = os.environ.get('JOB_IP', 'crawler-manager')
MAIN_APPLICATION_ENDPOINT = os.environ.get('MAIN_APPLICATION_ENDPOINT', 'http://main:8001')
PORT = 8002
ENDPOINT = 'http://{}:{}'.format(HOSTNAME, PORT)
TOKEN = os.environ.get('TOKEN', '')
TOKEN_PREFIX = 'Bearer '

CRAWLER_MANAGER_ENDPOINT = 'http://crawler-manager:8002'
if (ENVIRONMENT == 'prod' and RELEASE_DATE != '0'):
  CRAWLER_MANAGER_ENDPOINT = f"http://crawler-manager-service-{RELEASE_DATE}.{NAMESPACE}/"


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


@app.route('/crawl', methods=['POST'])
def crawl():
    global JOB_ID
    global TOKEN
    JOB_ID = flask.request.json['job_id']
    TOKEN = flask.request.json['token']
    crawl_thread = threading.Thread(target=do_crawl)
    crawl_thread.start()
    return ''


@app.route('/ping', methods=['GET'])
def ping():
    context.logger.info('Received request at PING')
    return 'PONG'


@app.route('/kill', methods=['POST'])
def kill():
    @after_this_request
    def maybe_kill(response):
        if ENVIRONMENT == 'local':
            context.logger.info("Not killing crawler manager because running locally")
        else:
            context.logger.info("Kill confirmed")
            sys.exit(0)

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
            absolute_url = url
        else:
            absolute_url = helpers.expand_url(helpers.get_root_url(main_url), url)

        if any(map(lambda x: helpers.strip_protocol_from_url(absolute_url)\
                             .startswith(helpers.strip_protocol_from_url(x)),
                   context.parameters['domain'])) and \
          not context.queued_urls.contains(absolute_url) and \
          not context.in_process_urls.contains(absolute_url) and \
          not context.cache.exists(absolute_url):
            context.logger.info('Adding %s to queue', absolute_url)
            context.queued_urls.add(absolute_url)

    context.processed_urls.increment()
    context.in_process_urls.remove(main_url)
    context.logger.info('added to cache')
    context.cache.put(main_url, s3_uri)
    return ""


# Returns statistics on the current crawl
@app.route('/status', methods=['GET'])
def status():
    context.logger.info('Received status request')
    return flask.jsonify({
        'processed_count' : context.processed_urls.get(),
        'processing_count': context.in_process_urls.size(),
        'queued_count' : context.queued_urls.size()
    })


def run_flask():
    app.run(debug=DEBUG_MODE, host=HOSTNAME, port=PORT, use_reloader=False)


def do_crawl():
    setup()
    processor = work_processor.Processor(context)
    processor.run()
    teardown()


def setup():
    global context
    context.cache = redis_connect.RedisClient(redis.Redis(host='0.0.0.0', port=6379, db=0))
    try:
        context.logger.info('Attempting to register with main application')
        header = {'Authorization': TOKEN_PREFIX + TOKEN}
        response = requests.post(os.path.join(MAIN_APPLICATION_ENDPOINT, 'main_app/api/register_crawler_manager'),
                                 json={'job_id': JOB_ID, 'endpoint': ENDPOINT},
                                 headers=header)
        context.parameters = json.loads(response.text)
        context.logger.info('Registered with main application!')
    except Exception as e:
        context.logger.error('Unable to register with main application: %s', str(e))
        sys.exit(1)

    for url in context.parameters['urls']:
        context.queued_urls.add(url)

    if ENVIRONMENT != 'local':
        context.logger.info('deploying crawlers')
        for _ in range(context.parameters['num_crawlers']):
            helm_command = f"""
                helm init --service-account tiller && helm upgrade --install \\
                --set-string image.tag='{IMAGE_TAG}' \\
                --set-string params.crawlerManagerEndpoint='{CRAWLER_MANAGER_ENDPOINT}' \\
                --set-string application.namespace='{NAMESPACE}' \\
                --set-string params.jobId='{JOB_ID}' \\
                \"crawler-{RELEASE_DATE}\" ./cluster-templates/chart-crawler
            """
            context.logger.info('Running helm command: %s', helm_command)
            os.system(helm_command)


def teardown():
    context.logger.info("Killing crawlers")
    crawlers = context.crawlers.get()
    for crawler in crawlers:
        kill_api = os.path.join(crawler, "kill")
        try:
            context.logger.info("Sending kill request to crawler: %s", crawler)
            response = requests.post(kill_api, json={})
            #response.raise_for_status()
            context.logger.info("Successfully killed crawler: %s", crawler)
        except Exception as e:
            context.logger.error('Unable to kill crawler: %s', str(e))

    context.logger.info("creating manifest")
    manifest = context.cache.write_manifest()
    manifest_key = 'manifest-{}.csv'.format(str(uuid.uuid4()))
    context.logger.info("Uploading manifest to GCS")
    public_manifest = helpers.upload_public_file(manifest, os.environ['GCS_BUCKET'], manifest_key)
    context.logger.info("Manifest and CSV uploaded! Deleting local files")
    os.remove(manifest)

    crawl_complete_api = os.path.join(MAIN_APPLICATION_ENDPOINT, 'main_app/api/crawl_complete')
    try:
        context.logger.info("Calling crawl_complete api %s", crawl_complete_api)
        json_data = {
            'job_id': JOB_ID,
            'manifest': public_manifest,
            'resources_count': context.processed_urls.get()
        }
        header = {'Authorization': TOKEN_PREFIX + TOKEN}
        response = requests.post(crawl_complete_api, json=json_data, headers=header)
        response.raise_for_status()
        context.logger.info("crawl_complete call successful")
    except Exception as e:
        context.logger.error('Unable to send crawl_complete to main applications: %s', str(e))


if __name__ == "__main__":
    context.logger.info('ENVIRONMENT -- %s ', ENVIRONMENT)
    context.logger.info('starting flask app in separate thread')
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    if ENVIRONMENT != 'local':
        setup()
        processor = work_processor.Processor(context)
        processor.run()
        teardown()
