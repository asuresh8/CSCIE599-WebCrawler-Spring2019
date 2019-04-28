import io
import logging
import os
import redis
import requests
import uuid
import redis_connect
from bs4 import BeautifulSoup
from google.cloud import storage
from crawl_global import CrawlGlobal

class BaseScraper:
    def __init__(self, base_url, key):
        self.base_url = base_url
        self.file_name = key

    def do_scrape(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            return None

   
    # get_links - parses the url 'a' tags using beautiful soup
    def get_links(self, data):
        if data is None:
            return []

        CrawlGlobal.context().logger.info('Parsing links...')
        try:
            bs_obj = BeautifulSoup(data, 'html.parser')
            links_obj = {}
            for link in bs_obj.find_all('a'):
                if 'href' in link.attrs:
                    links_obj[link.attrs['href']] = 1

        
            links = list(links_obj.keys())
            CrawlGlobal.context().logger.info('Found links in %s: %s', self.base_url, str(links))
            return links
        except Exception as e:
            CrawlGlobal.context().logger.error("Could not list links in url: %s", str(e))
            return []
    
    def store_in_gcs(self, data):
        if data is None:
            return ''

        CrawlGlobal.context().logger.info('Attempting to store in GCS')
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
            blob = bucket.blob(self.file_name)
            blob.upload_from_string(data)
            blob.make_public()
            uri = blob.public_url
            CrawlGlobal.context().logger.info('uri successfully generated!')
            return uri
        except Exception as e:
            CrawlGlobal.context().logger.error('Unable to store webpage for %s: %s', url, str(e))
            return ''
    
    def store_in_redis(self, s3uri, links):
        try:
            CrawlGlobal.context().logger.info('Caching s3_uri and child_urls')
            CrawlGlobal.context().cache.put(self.base_url, {'s3_uri': s3uri, 'child_urls': links})
            CrawlGlobal.context().logger.info('Caching was successful')
        except Exception as e:
            CrawlGlobal.context().logger.error('Unable to cache data for %s: %s', self.base_url, str(e))

