import io
import logging
import os
import requests
import uuid
import app
from crawl_base import BaseScraper
from google.cloud import storage


class FileScraper(BaseScraper):

    def __init__(self, base_url, key, ext):
        BaseScraper.__init__(self,base_url, key)
        self.file_ext = ext
    
    def do_scrape(self):
        try:
            app.context.logger.info("Scraping URL: {}".format(self.base_url))
            r = requests.get(self.base_url, stream=True)
            fpath = '/tmp/' + self.file_name

            with open(fpath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)

            return fpath
        except Exception as e:
            print("error")
            return None
    
    def get_links(self, data):
        return []
        
    def store_in_gcs(self,fpath):
        if data is None:
            return

        app.context.logger.info('Attempting to store in GCS')
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
            blob = bucket.blob(self.file_name)
            blob.upload_from_file_name(fpath)
            blob.make_public()
            uri = blob.public_url
            context.logger.info('uri successfully generated!')
            return uri
        except Exception as e:
            context.logger.error('Unable to store webpage for %s: %s', url, str(e))
            return ''
    