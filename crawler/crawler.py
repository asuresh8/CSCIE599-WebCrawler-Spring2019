import redis
import boto3
import re
import uuid
import requests
import config
from io import BytesIO
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import redis_connect

def crawlUrl(url):
    links = []
    # connect to redis 
    #r = redis.StrictRedis(host=config.REDIS_HOST, port= config.REDIS_PORT)
    try:
       if is_crawled(url) == True :
          return  (None, None) 
       else:
          #get web page
          response = requests.get(url)
          print("url is:" + url)
          # store to s3
          s3uri = store_s3(response)
          get_links(response, links)
          print(links)
          #add key to redis
          add_key_cache(url, s3uri)
          return (s3uri, links)
    except HTTPError as e:
       return (None, None)

# store page  to  s3
def store_s3(res):  
    try:
      s3_client = boto3.client('s3', aws_access_key_id= config.S3_KEY, 
                                     aws_secret_access_key= config.S3_SECRET_KEY)
      key = 'crawl_pages/' + str(uuid.uuid4().hex[:6])  + '.html'
      fp = BytesIO(res.content)
      s3_client.upload_fileobj(fp, config.S3_BUCKET, key)
      s3uri = s3_client.generate_presigned_url('get_object', 
                                               Params = {'Bucket' : config.S3_BUCKET, 'Key': key})  
      print ('s3uri' + s3uri)    
    except Exception as e:
      print(e.__traceback__)
      return None
    
    return s3uri

# get_links - parses the url 'a' tags using beautiful soup
def get_links(r, links):
    bsObj = BeautifulSoup(r.content, 'html.parser')
    for link in bsObj.find_all('a'):
        if 'href' in link.attrs:
           links.append(url_for(link.attrs['href'], _external = True))
    return 

# add url and s3 location to central redis cache
def add_key_cache(url,s3uri):
    if redis_connect.redisConnect is None:
       return
    try:
        redis_connect.redisConnect.set(url,s3uri)
    except Exception as e:
        print(e.with_traceback)
    return

# is_crawled - checks redis for existing of key
def is_crawled(url):
    return redis_connect.redisConnect != None and redis_connect.redisConnect.exists(url) ? True: False

""" 
def write_file(url):
    
    fname = str(uuid.uuid4().hex[:6])  + '.html' 
    with open(fname, 'wb') as fp:
        for chunk in r.iter_content(chunk_size=512):
            fp.write(chunk)
    return fname  
"""


