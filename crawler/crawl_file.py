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
        app.context.logger.info("instantiating file scraper")
        self.file_ext = ext
        self.chunk_size =  2000
    
    def do_scrape(self):
        try:
            app.context.logger.info("Scraping URL: {}".format(self.base_url))
            r = requests.get(self.base_url, stream=True)
            app.context.logger.info("request status: %d", r.status_code)

            tmpfile = self.file_name
            if (self.file_name.startswith('crawl_pages/')):
                tmpfile = self.file_name[len('crawl_pages/'):]

            fpath = '/tmp/' + tmpfile + self.file_ext
            app.context.logger.info("file path is: %s",  fpath)
            with open(fpath, 'wb') as fd:
                for chunk in r.iter_content(self.chunk_size):
                    fd.write(chunk)

            return fpath
        except Exception as e:
            app.context.logger.info("error in writing file: %s", str(e))
            return None
    
    def get_links(self, data):
        return []
        
    def store_in_gcs(self,fpath):
        app.context.logger.info('Attempting to store in GCS')
        if not fpath:
            app.context.logger.info('no file to store in GCS')
            return

        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
            blob = bucket.blob(self.file_name+self.file_ext)
            app.context.logger.info('Got the blob in GCS')
            blob.upload_from_filename(fpath)
            blob.make_public()
            uri = blob.public_url
            app.context.logger.info('uri successfully generated!')
            return uri
        except Exception as e:
            app.context.logger.error('Unable to store webpage for %s: %s', self.base_url, str(e))
            return ''
    
