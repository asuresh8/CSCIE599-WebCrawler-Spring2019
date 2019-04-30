import io
import logging
import os
import requests
import uuid
from crawl_global import CrawlGlobal
from crawl_base import BaseScraper
from google.cloud import storage


class FileScraper(BaseScraper):

    def __init__(self, base_url, key, ext):
        BaseScraper.__init__(self,base_url, key)
        CrawlGlobal.context().logger.info("instantiating file scraper")
        self.file_ext = ext
        self.chunk_size =  2000
    
    def do_scrape(self):
        try:
            CrawlGlobal.context().logger.info("Scraping URL: {}".format(self.base_url))
            r = requests.get(self.base_url, stream=True)
            CrawlGlobal.context().logger.info("request status: %d", r.status_code)

            tmpfile = self.file_name
            if (self.file_name.startswith('crawl_pages/')):
                tmpfile = self.file_name[len('crawl_pages/'):]

            fpath = '/tmp/' + tmpfile + self.file_ext
            CrawlGlobal.context().logger.info("file path is: %s",  fpath)
            with open(fpath, 'wb') as fd:
                for chunk in r.iter_content(self.chunk_size):
                    fd.write(chunk)

            return fpath
        except Exception as e:
            CrawlGlobal.context().logger.info("error in writing file: %s", str(e))
            return None
    
    def get_links(self, data):
        return []
        
    def store_in_gcs(self,fpath):
        CrawlGlobal.context().logger.info('Attempting to store in GCS')
        if not fpath:
            CrawlGlobal.context().logger.info('no file to store in GCS')
            return

        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
            blob = bucket.blob(self.file_name + self.file_ext)
            CrawlGlobal.context().logger.info('Got the blob in GCS')
            blob.upload_from_filename(fpath)
            blob.make_public()
            uri = blob.public_url
            CrawlGlobal.context().logger.info('uri successfully generated!')
            return uri
        except Exception as e:
            CrawlGlobal.context().logger.error('Unable to store webpage for %s: %s', self.base_url, str(e))
            return ''
    