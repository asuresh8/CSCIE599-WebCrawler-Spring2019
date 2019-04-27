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
from crawl_job import CrawlerJob
import _thread


app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_context.Context(app.logger)
cache = redis_connect.Cache()

CRAWLER_MANAGER_ENDPOINT = os.environ.get('CRAWLER_MANAGER_ENDPOINT', 'http://crawler-manager:8002')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
URL = os.environ.get('URL', 'https://google.com')
DEBUG_MODE = ENVIRONMENT == 'local'
HOSTNAME = os.environ.get('JOB_IP', 'crawler')
MAX_ACTIVE_THREADS = 4
PORT = 8003
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

    context.active_thread_count.increment() 
    crawljob = CrawlerJob(url)
    executor.submit(crawljob.execute)
    return flask.jsonify({'accepted': True})

@app.route('/crawler/')
def do_crawl():
    url =  flask.request.args.get('crawlurl')
    context.logger.info('Crawling %s', url)
    if context.active_thread_count.get() >= MAX_ACTIVE_THREADS:
        return flask.jsonify({'accepted': False})

    context.active_thread_count.increment()
    crawljob = CrawlerJob(url)
    executor.submit(crawljob.execute)
    return flask.jsonify({'accepted': True})


def test_connections():
    try:
        cache.ping()
        context.logger.info('connected to redis successfully')
    except Exception as e:
        context.logger.info('could not initialize redis: %s', str(e))


def run_flask():
    app.run(debug=DEBUG_MODE, host=HOSTNAME, port=PORT, use_reloader=False)


def setup():
    try:
        requests.post(os.path.join(CRAWLER_MANAGER_ENDPOINT, 'register_crawler'),
                      json={'endpoint': ENDPOINT})
    except Exception as e:
        context.logger.info('Unable to register with crawler manager: %s', str(e))


def ping_crawler_manager():
    try:
        context.logger.info('pinging CRAWLER_MANAGER_ENDPOINT - %s', CRAWLER_MANAGER_ENDPOINT)
        response = requests.get(CRAWLER_MANAGER_ENDPOINT)
        response.raise_for_status()
        context.logger.info('ping successful!')
    except Exception as e:
        context.logger.error("Could not connect to crawler manager: %s", str(e))


if __name__ == "__main__":
    ping_crawler_manager()
    test_connections()
    if ENVIRONMENT == 'local':
        setup()
        run_flask()
    else:
        _thread.start_new_thread(run_flask,())
        crawljob = CrawlerJob(URL)
        executor.submit(crawljob.execute, URL)
        sys.exit(0)