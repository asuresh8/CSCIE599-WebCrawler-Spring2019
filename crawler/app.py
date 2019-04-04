import concurrent
import flask
import json
import logging
import os
import requests
import signal
import sys
import threading
import time
import uuid

import crawler_context
import helpers
import redis_connect

import _thread

app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_context.Context(app.logger)

CRAWLER_MANAGER_ENDPOINT = os.environ.get('CRAWLER_MANAGER_ENDPOINT', 'http://crawler-manager:8002')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
DEBUG_MODE = ENVIRONMENT == 'local'
HOSTNAME = os.environ.get('JOB_IP', 'crawler')
MAX_ACTIVE_THREADS = 1  # TODO: increase this to 4?
PORT = 8003 if HOSTNAME == 'crawler' else 80
ENDPOINT = 'http://{}:{}'.format(HOSTNAME, PORT)

executor = concurrent.futures.ThreadPoolExecutor(MAX_ACTIVE_THREADS)


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
    return 'crawler'


@app.route('/kill', methods=['POST'])
def kill():
    @after_this_request
    def maybe_kill(response):
        if ENVIRONMENT == 'local':
            context.logger.info('Not killing crawler because running locally')
        else:
            context.logger.info("Kill confirmed")
            sys.exit()

        return response

    context.logger.info('Kill called for')
    return ""


@app.route('/status', methods=['GET'])
def status():
    return flask.jsonify({'active_threads': context.active_thread_count.get()})


@app.route('/crawl', methods=['POST'])
def crawl():
    url =  flask.request.json['url']
    context.logger.info('Crawling %s', url)
    if context.active_thread_count.get() >= MAX_ACTIVE_THREADS:
        return flask.jsonify({'accepted': False})

    # context.active_thread_count.increment()
    executor.submit(do_crawl, url)
    return flask.jsonify({'accepted': True})
    # TODO: return success and spin off new thread to crawl


def do_crawl(url):
    context.logger.info('Starting crawl thread for %s', url)
    if redis_connect.exists(url):
        context.logger.info('Found %s in cache', url)
        cached_result = redis_connect.get(url)
        s3_uri = cached_result['s3_uri']
        links = cached_result['child_urls']
    else:
        key = 'crawl_pages/{}/{}'.format(str(uuid.uuid4().hex[:6]), os.path.basename(url))
        context.logger.info('Generated key: %s', key)
        try:
            context.logger.info('Sending Get Request')
            response = requests.get(url)
            context.logger.info('Received response for get request')
        except Exception as e:
            context.logger.error('Unable to parse %s. Received %s', url, str(e))
            s3_uri = ''
            links = []
        else:
            # store in s3
            # s3_uri = helpers.store_response_in_s3(response, key)
            # Store in GCS
            try:
                context.logger.info('Attempting to store in GCS')
                s3_uri = helpers.store_response_in_gcs(response, key)
                context.logger.info('uri successfully generated!')
            except Exception as e:
                context.logger.error('Unable to store webpage for %s: %s', url, str(e))
                s3_uri = ''

            context.logger.info('Parsing links...')
            links = helpers.get_links(response)
            context.logger.info('Found links in %s: %s', url, str(links))
            try:
                context.logger.info('Caching s3_uri and child_urls')
                redis_connect.put(url, {'s3_uri': s3_uri, 'child_urls': links})
                context.logger.info('Caching was successful')
            except Exception as e:
                context.logger.error('Unable to cache data for %s: %s', url, str(e))

    links_api = os.path.join(CRAWLER_MANAGER_ENDPOINT, 'links')
    try:
        context.logger.info('Sending response back to crawler manager...')
        requests.post(links_api, json={'main_url': url, 's3_uri': s3_uri, 'child_urls': links})
        context.logger.info('Response sent successfully!')
    except Exception as e:
        context.logger.error("Could not connect to crawler manager: %s", str(e))

    # context.active_thread_count.decrement()


def test_connections():
    redis_connect.test_redis_connection()


def run_flask():
    app.run(debug=DEBUG_MODE, host=HOSTNAME, port=PORT, use_reloader=False)


def setup():
    try:
        requests.post(os.path.join(CRAWLER_MANAGER_ENDPOINT, 'register_crawler'),
                      json={'endpoint': ENDPOINT})
    except Exception as e:
        context.logger.error('Unable to register with crawler manager: %s', str(e))


def ping_manager():
    try:
        r = requests.get(CRAWLER_MANAGER_ENDPOINT)
        return r.text
    except requests.RequestException as rex:
        return "request exception"
    except requests.HTTPException as htex:
        return "http exception"
    except Exception as ex:
        return "general exception"

if __name__ == "__main__":
    ping = ping_manager()

    context.logger.info('ping crawler manager - %s', ping)
    context.logger.info('CRAWLER_MANAGER_ENDPOINT - %s', CRAWLER_MANAGER_ENDPOINT)

    test_connections()
    if ENVIRONMENT == 'local':
        setup()
        run_flask()
    else:
        _thread.start_new_thread(run_flask,())

        context.logger.info('Will kill crawler server after 15s -- endpoint: - %s', ENDPOINT)

        time.sleep(15)
        sys.exit(0)

