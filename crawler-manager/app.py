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
import uuid

import crawler_manager_context
import helpers
import redis_connect
import work_processor
from urllib import parse
from urllib import robotparser
from reppy.robots import Robots

import _thread

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
INITIAL_URLS = os.environ.get('INITIAL_URLS', '/').split(';')
NUM_CRAWLERS_TOTAL = len(INITIAL_URLS)
NUM_CRAWLERS_FINISHED = 0
DOMAIN_RESTRICTIONS = os.environ.get('DOMAIN', 'http://www.garbage.com').split(';')
MAIN_APPLICATION_ENDPOINT = os.environ.get('MAIN_APPLICATION_ENDPOINT', 'http://main:8001')
PORT = 8002
ENDPOINT = 'http://{}:{}'.format(HOSTNAME, PORT)

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
    setup()
    return ''

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
    global NUM_CRAWLERS_FINISHED, NUM_CRAWLERS_FINISHED

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

    NUM_CRAWLERS_FINISHED += 1
    context.processed_urls.increment()
    context.in_process_urls.remove(main_url)

    if NUM_CRAWLERS_FINISHED == NUM_CRAWLERS_TOTAL and ENVIRONMENT != 'local':
        context.logger.info('Kill - Crawlers done')
        mark_job_completed(main_url)
        _thread.start_new_thread(kill_after,(3,))

    return ""


def kill_after(secs):
  context.logger.info('system will be killed in %s seconds', secs)
  time.sleep(secs)
  os._exit(0)


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
    for url in INITIAL_URLS:
        context.logger.info('deploying crawlers %s', url)
        helm_command = get_helm_command(url)
        context.logger.info('Running helm command: %s', helm_command)
        os.system(helm_command)


def get_helm_command(url):
    return f"""helm init --service-account tiller && \\
        helm upgrade --install \\
        --set-string image.tag='{IMAGE_TAG}' \\
        --set-string params.url='{url}' \\
        --set-string params.crawlerManagerEndpoint='{CRAWLER_MANAGER_ENDPOINT}' \\
        --set-string application.namespace='{NAMESPACE}'
        \"crawler-{RELEASE_DATE}\" ./cluster-templates/chart-crawler"""


#Testing Connections
def test_connections():
    redis_connect.test_redis_connection()


def run_flask():
    app.run(debug=DEBUG_MODE, host=HOSTNAME, port=PORT, use_reloader=False)


def run_work_processor():
    global INITIAL_URLS
    robotparsers = {}

    # Save all parsing rules for the * user-agent in dictionary for all seed urls
    for url in INITIAL_URLS:
        robots = Robots.fetch(url + "/robots.txt")
        robotparsers["{0}_RobotAgent".format(url)] = robots.agent('*')

    processor = work_processor.Processor(context, robotparsers)
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

    mark_job_completed(INITIAL_URLS[0])

def upload_file(file_path, key):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    blob = bucket.blob(key)
    blob.upload_from_filename(file_path)
    blob.make_public()

    return blob.public_url

def mark_job_completed(redis_key=None):
    context.logger.info("1. creating manifest from redis %s", redis_key)

    url_data = redis_connect.get_json(redis_key)
    url_count = 0
    if url_data != None:
        url_count = len(url_data['child_urls'])

    manifest = redis_connect.write_crawler_manifest(redis_key)
    manifest_key = 'manifest-{}.csv'.format(str(uuid.uuid4()))

    csv = redis_connect.write_crawler_csv(redis_key)
    csv_key = 'data-{}.csv'.format(str(uuid.uuid4()))

    # Write to GCS
    context.logger.info("Uploading manifest to GCS")
    public_manifest = upload_file(manifest, manifest_key)

    context.logger.info("Uploading csv to GCS")
    public_csv = upload_file(csv, csv_key)

    context.logger.info("Manifest and CSV uploaded! Deleting local files")
    os.remove(manifest)
    os.remove(csv)

    crawl_complete_api = os.path.join(MAIN_APPLICATION_ENDPOINT, 'main_app/api/crawl_complete')
    try:
        context.logger.info("Calling crawl_complete api %s", url_count)

        json_data = {
            'job_id': JOB_ID,
            'manifest': public_manifest,
            'csv': public_csv,
            'resources_count': url_count
        }

        requests.post(crawl_complete_api, json=json_data)
        context.logger.info("crawl_complete call successful")
    except Exception as e:
        context.logger.error('Unable to send crawl_complete to main applications: %s', str(e))

def setup():
    global JOB_ID
    global INITIAL_URLS
    try:
        context.logger.info('Attempting to register with main application')
        response = requests.post(os.path.join(MAIN_APPLICATION_ENDPOINT, 'main_app/api/register_crawler_manager'),
                                 json={'job_id': JOB_ID, 'endpoint': ENDPOINT})
        if ENVIRONMENT == 'local':
            payload = json.loads(response.text)
            JOB_ID = payload["JOB_ID"]
            if payload['URLS'] != "":
                INITIAL_URLS = payload['URLS'].split(';')
            context.logger.info('[223] JOBID: %s, URLS: %s', JOB_ID, INITIAL_URLS)
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
    # ping = ping_main()
    context.logger.info('will connect to redis')
    test_connections()
    context.logger.info('ENVIRONMENT -- %s ', ENVIRONMENT)

    if ENVIRONMENT == 'local':
        run_flask()
    else:
        _thread.start_new_thread(run_flask,())
        deploy_crawlers()
        time.sleep(400)
