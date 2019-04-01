from flask import Flask
from flask import request
from redis_connect import testConnectionRedis
from crawler import crawlUrl
import os, signal, _thread, sys, time

app = Flask(__name__)
urls = os.environ.get('URLS', '')

@app.route('/')
def main():
    hname =  request.host_url
    try:
       
       requests.post('http://localhost:8002' + '/api/v1.0/register/crawlerID', json ={'name': hname})
       #requests.post(os.environ.get('manager') + '/api/v1.0/register/crawlerID', json ={'name': hname})
       return "crawler"
    except  requests.RequestException as rex:
       return "request exception"
    except requests.HTTPException as hex:
       return "http exception"
    except Exception as ex:
       return "general exception"

@app.route('/crawl/')
def do_crawl():
    curUrl =  request.args.get('crawlurl')
    print("start crawling")
    s3uri , links =  crawlUrl(curUrl)
    if links is None:
	json_data = { 'main_url' : curUrl, 's3uri': "" ,  'child_urls': []}
    else:
        json_data = { 'main_url' : curUrl, 's3uri': s3uri ,  'child_urls':  json.dumps(links)}
    try :
       r = requests.post('http://localhost:8002' + '/api/v1.0/links', json=  json_data)
       #r = requests.post(os.environ.get("manager") + '/api/v1.0/links', json=  json_data)
       return  "ok"
    except  requests.RequestException as rex:
       return "request exception"
    except requests.HTTPException as hex:
       return "http exception"
    except Exception as ex:
       return "general exception"
     

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
