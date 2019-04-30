import os
import uuid
import requests
import redis_connect
from crawl_web import WebScraper
from crawl_file import FileScraper
from crawl_base import BaseScraper
from crawl_global import CrawlGlobal

ALLOWABLE_EXTENSIONS = [".pdf", ".doc", ".docx", ""]

class CrawlerJob(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.s3_uri = ''
        self.links = []

    def get_extension(self, url):
        CrawlGlobal.context().logger.info('url is: %s', self.base_url)
        ext =  list(filter(lambda x: url.lower().endswith(x), ALLOWABLE_EXTENSIONS))[0]
        CrawlGlobal.context().logger.info('extension is: %s', ext)
        return ext

    def is_cached(self):
        CrawlGlobal.context().logger.info('connecting to redis')
        if CrawlGlobal.context().cache.exists(self.base_url):
            cache_val =  CrawlGlobal.context().cache.get(self.base_url)
            if cache_val != None and 's3_uri' in cache_val and 'child_urls' in cache_val:
                self.s3_uri = cache_val['s3_uri']
                self.links = cache_val['child_urls']
                if (self.s3_uri is None):
                    CrawlGlobal.context().logger.info('Error condition. s3_uri None for cached url: %s', self.base_url)
                    self.s3_uri = ''
                if (self.links is None):
                    CrawlGlobal.context().logger.info('Error condition. links None for cached url: %s', self.base_url)
                    self.links = []
                return True
            else:
                return False
        return False

    def execute(self, endpoint):
        CrawlGlobal.context().logger.info('Starting crawl thread for %s', self.base_url)     
        try:
            if not self.is_cached():
               self.start_scrape()
            else:
                CrawlGlobal.context().logger.info('Url %s already cached', self.base_url)
            
            # callback manager
            self.send_response_to_manager(endpoint)
        except Exception as e:
            CrawlGlobal.context().logger.info("exception: {}".format(str(e)))

        CrawlGlobal.context().active_thread_count.decrement()

    
    def start_scrape(self):
        url = self.base_url
        CrawlGlobal.context().logger.info('start scraping')
        key = 'crawl_pages/{}'.format(str(uuid.uuid4()))
        CrawlGlobal.context().logger.info('Generated key: %s', key)
        
        file_ext = self.get_extension(url)
        
        # scraper object is decided (FileScraper, WebScraper, BaseScraper)
        if file_ext:
            scraper = FileScraper(url, key, file_ext)
        else:
            scraper = WebScraper(url, key)
        
        # scrape the page
        self.data = scraper.do_scrape()
        
        #CrawlGlobal.context().logger.info(self.data)
        # store
        if self.do_store(file_ext):
            self.s3_uri = scraper.store_in_gcs(self.data)
            
        # get child urls
        self.links = scraper.get_links(self.data)
        # put in cache
        scraper.store_in_redis(self.s3_uri, self.links)


    def do_store(self, ext):
        if ext or not CrawlGlobal.context().has_model():
            CrawlGlobal.context().logger.info("need to store the data for ext %s", ext)
            return True
        else:
            cur_pred = CrawlGlobal.context().modelrunner.run(self.data)
            return cur_pred == -1 or CrawlGlobal.context().has_label(cur_pred)


    def send_response_to_manager(self, endpoint):
        links_api = os.path.join(endpoint, 'links')
        CrawlGlobal.context().logger.info('Endpoint on Crawler manager: %s', links_api)
        try:
            CrawlGlobal.context().logger.info('Sending response back to crawler manager...')
            response = requests.post(
                                        links_api,
                                        json={'main_url':self.base_url, 
                                              's3_uri': self.s3_uri, 
                                              'child_urls': self.links}
                                    )
            response.raise_for_status()
            CrawlGlobal.context().logger.info('Response sent successfully!')
            return response
        except Exception as e:
            CrawlGlobal.context().logger.error("Could not connect to crawler manager: %s", str(e))
            return None
