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

from crawl_job import CrawlerJob
import _thread
from crawl_global import CrawlGlobal

app = flask.Flask(__name__)
app.logger.setLevel(logging.INFO)
context = crawler_context.Context(app.logger)
CrawlGlobal.set_context(context)

CRAWLER_MANAGER_ENDPOINT = os.environ.get('CRAWLER_MANAGER_ENDPOINT', 'http://crawler-manager:8002')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
URL = os.environ.get('URL', 'https://google.com')
DEBUG_MODE = ENVIRONMENT == 'local'
HOSTNAME = os.environ.get('JOB_IP', 'crawler')
CRAWLER_HOSTNAME = os.environ.get('CRAWLER_HOSTNAME', 'crawler')
RELEASE_DATE = os.environ.get('RELEASE_DATE', '0')
NAMESPACE = os.environ.get('NAMESPACE', 'default')
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
    if ENVIRONMENT == 'local':
        CrawlGlobal.context().logger.info('Not killing crawler because running locally')
    else:
        CrawlGlobal.context().logger.info("Will kill flask server in 3 seconds")
        kill_thread = threading.Thread(target=kill_main_thread)
        kill_thread.start()

    CrawlGlobal.context().logger.info('Kill called')
    return "ok"

def kill_main_thread():
    time.sleep(3)
    CrawlGlobal.context().logger.info("Kill confirmed")
    os._exit(0)

@app.route('/status', methods=['GET'])
def status():
    return flask.jsonify({'active_threads': CrawlGlobal.context().active_thread_count.get()})

@app.route('/dev_crawl', methods=['POST'])
def dev_crawl():
    dev_crawl_thread = threading.Thread(target=setup)
    dev_crawl_thread.start()
    return ''

@app.route('/crawl', methods=['POST'])
def crawl():
    url =  flask.request.json['url']
    CrawlGlobal.context().logger.info('Crawling %s', url)
    if CrawlGlobal.context().active_thread_count.get() >= MAX_ACTIVE_THREADS:
        return flask.jsonify({'accepted': False})

    CrawlGlobal.context().active_thread_count.increment()
    crawljob = CrawlerJob(url)
    executor.submit(crawljob.execute, CRAWLER_MANAGER_ENDPOINT)
    return flask.jsonify({'accepted': True})

@app.route('/crawler/')
def do_crawl():
    url =  flask.request.args.get('crawlurl')
    CrawlGlobal.context().logger.info('Crawling %s', url)
    if CrawlGlobal.context().active_thread_count.get() >= MAX_ACTIVE_THREADS:
        return flask.jsonify({'accepted': False})

    CrawlGlobal.context().active_thread_count.increment()
    crawljob = CrawlerJob(url,)
    executor.submit(crawljob.execute,CRAWLER_MANAGER_ENDPOINT)
    return flask.jsonify({'accepted': True})


def test_connections():
    try:
        CrawlGlobal.context().cache.ping()
        CrawlGlobal.context().logger.info('connected to redis successfully')
    except Exception as e:
        CrawlGlobal.context().logger.info('could not initialize redis: %s', str(e))


def run_flask():
    CrawlGlobal.context().logger.info("start flask with host: %s", CRAWLER_HOSTNAME)
    app.run(debug=DEBUG_MODE, host=CRAWLER_HOSTNAME, port=PORT, use_reloader=False)


def setup():
    try:
        CrawlGlobal.context().logger.info("crawler end point: %s", ENDPOINT)
        CrawlGlobal.context().logger.info("crawler manager end point: %s",CRAWLER_MANAGER_ENDPOINT)
        res = requests.post(os.path.join(CRAWLER_MANAGER_ENDPOINT, 'register_crawler'),
                      json={'endpoint': ENDPOINT})
        CrawlGlobal.context().logger.info("Registreed successfully with crawler manager")
        CrawlGlobal.context().set_useroptions(res.json())
    except Exception as e:
        CrawlGlobal.context().logger.info('Unable to register with crawler manager: %s', str(e))


def ping_crawler_manager():
    try:
        CrawlGlobal.context().logger.info('pinging CRAWLER_MANAGER_ENDPOINT - %s', CRAWLER_MANAGER_ENDPOINT)
        response = requests.get(CRAWLER_MANAGER_ENDPOINT)
        response.raise_for_status()
        CrawlGlobal.context().logger.info('ping successful!')
    except Exception as e:
        CrawlGlobal.context().logger.error("Could not connect to crawler manager: %s", str(e))


if __name__ == "__main__":
    ping_crawler_manager()
    test_connections()
    CrawlGlobal.context().logger.info('ENVIRONMENT -- %s ', ENVIRONMENT)
    CrawlGlobal.context().logger.info('starting flask app in separate thread')
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    if ENVIRONMENT != 'local':
        setup()
