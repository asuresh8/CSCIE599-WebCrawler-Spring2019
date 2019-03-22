from urllib.request import Request, urlopen
from urllib.error import URLError
from flask import Flask
from flask import g
from bs4 import BeautifulSoup

import boto3
import config
import uuid
import redis


app = Flask(__name__)

@app.route("/<string:url>")
def fetchUrl():
   
   curUrl =  {url}  /*"https://en.wikipedia.org/wiki/Crawler" */
   request = Request(curUrl)
   links = []
   try:
      urlPage = urlopen(request ).read() 
      parsePage(urlPage, links)
      s3loc = storePage(urlPage)
      g.db.put(curUrl, s3uri)

   except URLError as e:
      links = []
   return links

/*
* storePage -   stores the page in configured s3 bucket and returns unique  uri
*/
def storePage(urlPage):
   
   key = "crawlpages/" + str(uuid.uuid4().hex[:6])  + '.html'
   g.s3client.put_object(Bucket = config.S3_BUCKET,
                        Key = key,
                        Body = urlPage)
   /*
     bucket = g.s3client.Bucket(config.S3_BUCKET)
     location = g.s3client.get_bucket_location(Bucket = config.S3_BUCKET)['LocationConstraint']
     s3uri = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket, key)
   */
   s3uri =  g.s3client.generate_presigned_url('get_object', Params = {'Bucket' : config.S3_BUCKET, 'Key': key})
   return s3uri


/*
* parsePage - parses the link tags using beautiful soup
*/
def parsePage(urlPage, links):
   soup = BeautifulSoup(urlPage)
   for link in soup.findall('a', attrs={href:re.compile("^http://")})
       links.append(link)

   return

/*
* connect to redis cache server
*/
def connectToRedis():
   try:
   	return redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
   except redis.ConnectionError as e:
        return None
   return r;

/*
* init function to connect to redis database and creates s3 bucket
* and stores in session data
*/
def main():
   g.db =  connectToRedis()
   g.s3client =boto3.client("s3") 
   g.s3client.create_bucket(config.S3_BUCKET)
     

   
if  __name__== "__main__"
   main()
