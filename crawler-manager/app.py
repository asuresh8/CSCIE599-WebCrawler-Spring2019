import flask
import requests
import aiohttp
import asyncio
from parsel import Selector
import time
import uuid
import os, signal, _thread, sys
from redis_connect import testConnectionRedis, testLocalRedis, getVariable, setVariable
from collections import deque
from flask import request, abort, jsonify
import settings
import work_processor
from helper import validateChildURLs, updateRedis, get_domain_name


app = flask.Flask(__name__)
start = time.time()
jobId = os.environ.get('JOB_ID', '')
imageTag = os.environ.get('IMAGE_TAG', '0')
environment = os.environ.get('ENVIRONMENT', 'local')

@app.route('/')
def main():
    return 'Crawler-manager'


#Testing Connections
def testConnections():
    print(testConnectionRedis())
    print(testLocalRedis())



#An POST API call made to main application to register this crawler manager instance

#A get API call made to main application to get the relevant job details
JOB_URL = "http://recurship.com"
DOMAIN_NAME = get_domain_name(JOB_URL)
settings.init()

#Register endpoint
#An endpoint that the crawler will call to register itself once instantiated, ip/dns added to available crawler list.
@app.route('/api/v1.0/register/crawlerID', methods=['POST'])
def register():
   crawlerId = request.json['name']
   crawlerSet.add(crawlerId)
   return "crawler added"

#Result endpoint
#An endpoint that the  crawler calls to respond with the url assigned, it's corresponding S3 Link and the list of child url's
#example JSON
# {
# "main_url":"http://recurship.com/",
# "S3":"https://bucket.s3-aws-region.amazonaws.com/key",
# "child_urls":[ "a", "b", "c" ]
# }
@app.route('/api/v1.0/links', methods=['POST'])
def updateCrawlerResponse():
    if not request.json or not 'main_url' in request.json:
        abort(400)
    main_url = request.json['main_url']
    s3Link = request.json['S3']
    child_urls = request.POST.getlist('child_urls')
    valid_child_urls = validateChildURLs(DOMAIN_NAME,main_url, child_urls)
    updateRedis(main_url, s3Link, valid_child_urls)

    #Adding valid child urls to the queue
    [settings.queuedURLs.put(url) for url in valid_child_urls]

    #Removing url from processingURLs
    settings.processingURLs.remove(main_url)

    #Adding url to processed urls
    settings.processedURLs.add(main_url)

#Returns statistics on the current crawl
@app.route('/api/v1.0/status', methods=['GET'])
def get_status():
  processedCount = settings.processedURLs.__len__
  processingCount = settings.processingURLs.__len__
  queuedCount = settings.queuedURLs.qsize()
  return jsonify({'processedCount' : processedCount, 'processingCount': processingCount, 'queuedCount' : queuedCount})

def deployCrawlers():
  if (environment == 'local'):
    return

  urls = ["https://cnn.com", "https://target.com"]
  for url in urls:
    os.system(getHelmCommand(url))

  return

def getHelmCommand(url):
  return f"""helm init --service-account tiller &&
    helm upgrade --install \\
    --set-string image.tag='{imageTag}' \\
    --set-string params.urls='{url}' \\
    \"crawler-$(date +%s)\" ./cluster-templates/chart-crawler"""

def flaskThread():
  app.run(debug=False, host="0.0.0.0", port=8002, use_reloader=False)

if __name__ == "__main__":
    testConnections()
    _thread.start_new_thread(flaskThread,())
    print('Will kill server after 20s -- jobId', jobId,file=sys.stderr)
    deployCrawlers()
    time.sleep(20)
    os.kill(os.getpid(), signal.SIGTERM)
