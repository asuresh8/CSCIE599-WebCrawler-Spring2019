from flask import Flask
from flask import request
from redis_connect import testConnectionRedis
from crawler import crawlUrl

app = Flask(__name__)

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


if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8003)
