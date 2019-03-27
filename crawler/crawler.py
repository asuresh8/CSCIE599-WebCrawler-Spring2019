import redis
import boto3
import re
import uuid
import json
import requests
import config
from io import BytesIO
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

def crawlUrl(url):
    try:
       response = requests.get(url)
       print("url is:" + url)
       s3uri = store_s3(response)
       links = get_links(response)
       print(links)
       add_key_cache(url, s3uri)
       return json.dumps(links)
    except HTTPError as e:
       return {}

# store -
def store_s3(r):  
    try:
      s3_client = boto3.client('s3', aws_access_key_id= config.S3_KEY, 
                                     aws_secret_access_key= config.S3_SECRET_KEY)
      key = 'crawl_pages/' + str(uuid.uuid4().hex[:6])  + '.html'
      fp = BytesIO(r.content)
      s3_client.upload_fileobj(fp, config.S3_BUCKET, key)
      s3uri = s3_client.generate_presigned_url('get_object', 
                                               Params = {'Bucket' : config.S3_BUCKET, 'Key': key})  
      print ('s3uri' + s3uri)    
    except Exception as e:
      print(e.__traceback__)
      return None
    
    return s3uri

# get_links - parses the url 'a' tags using beautiful soup
def get_links(r):
    links =[]
    bsObj = BeautifulSoup(r.content, 'html.parser')
    for link in bsObj.find_all('a'):
        if 'href' in link.attrs:
           links.append(link.attrs['href'])
    return links

def add_key_cache(url,s3uri):
    try:
        r = redis.StrictRedis(host=config.REDIS_HOST, port= config.REDIS_PORT)
        r.set(url,s3uri)
    except Exception as e:
        print(e.with_traceback)
    return


""" 
def write_file(url):
    
    fname = str(uuid.uuid4().hex[:6])  + '.html' 
    with open(fname, 'wb') as fp:
        for chunk in r.iter_content(chunk_size=512):
            fp.write(chunk)
    return fname  
"""


