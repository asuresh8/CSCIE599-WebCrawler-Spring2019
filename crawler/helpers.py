import boto3
import bs4
import config
import flask
from google.cloud import storage
import io
import logging
import os
import redis
import requests
import uuid

import redis_connect


# store page  to  s3
def store_response_in_s3(res, key):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id= config.S3_KEY,
            aws_secret_access_key= config.S3_SECRET_KEY
        )
        fp = io.BytesIO(res.content)
        s3_client.upload_fileobj(fp, config.S3_BUCKET, key)
        s3uri = s3_client.generate_presigned_url('get_object',
                                                 Params={'Bucket' : config.S3_BUCKET, 'Key': key})
        print('s3uri' + s3uri)
    except Exception as e:
        print(e.__traceback__)
        return None

    return s3uri


def store_response_in_gcs(res, key):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    blob = bucket.blob(key)
    blob.upload_from_string(res.text)
    blob.make_public()
    return blob.public_url


# get_links - parses the url 'a' tags using beautiful soup
def get_links(response):
    bs_obj = bs4.BeautifulSoup(response.content, 'html.parser')
    urls = {}
    for link in bs_obj.find_all('a'):
        if 'href' in link.attrs:
            url = link.attrs['href']
            if url.startswith('mailto'):
                continue
            
            if url in urls:
                urls[url] += 1
            else:
                urls[url] = 1

    return list(urls.keys())
