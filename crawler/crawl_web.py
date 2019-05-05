
from crawl_base import BaseScraper
from crawl_global import CrawlGlobal

class WebScraper(BaseScraper):

    def __init__(self, base_url, key):
        CrawlGlobal.context().logger.info("instantiating web scraper")
        BaseScraper.__init__(self, base_url, key)

 
    # check if browser is intialized properly
    def is_valid(self):
        return True if CrawlGlobal.context().get_driver() else False
         
    def do_scrape(self):
        if not self.is_valid():
            return super(WebScraper,self).do_scrape()

        try:
            CrawlGlobal.context().logger.info("Scraping URL: {}".format(self.base_url))    
            return CrawlGlobal.context().get_data(self.base_url)
        except Exception as e:
            CrawlGlobal.context().logger.info("error in scraping: {}".format(str(e)))
            return None

    