from flask import Flask
from flask import request
from redis_connect import testConnectionRedis
from crawler import crawlUrl
import os, signal, _thread, sys, time

app = Flask(__name__)
urls = os.environ.get('URLS', '')

@app.route('/')
def main():
    return 'Crawler'

@app.route('/crawl/')
def do_crawl():
    curUrl =  request.args.get('crawlurl')
    print("start crawling")
    return crawlUrl(curUrl)

def testConnections():
    print(testConnectionRedis())

def flaskThread():
  app.run(debug=False, host="0.0.0.0", port=8003, use_reloader=False)

if __name__ == "__main__":
    testConnections()
    _thread.start_new_thread(flaskThread,())
    print('Will kill crawler server after 15s -- urls', urls,file=sys.stderr)
    time.sleep(15)
    os.kill(os.getpid(), signal.SIGTERM)
