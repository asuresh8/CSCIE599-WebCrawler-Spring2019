import os
import app
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from crawl_base import BaseScraper

class WebScraper(BaseScraper):

    def __init__(self, base_url, key):
        app.context.logger.info("instantiating web scraper")
        BaseScraper.__init__(self,base_url, key)

        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        app.context.logger.info("Chrome driver path: {}".format(dir_path))
        exists = os.path.isfile(dir_path)
        self.is_initialized = False

        if not exists:
            return

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")

        try:
            self.driver = webdriver.Chrome(executable_path= dir_path, options= chrome_options ) 
            app.context.logger.info('browser initialized') 
            self.is_initialized = True              
        except WebDriverException as e:
            app.context.logger.info("could not instantiate browser: {}".format(str(e)))
            self.is_initialized = True
 
    # check if browser is intialized properly
    def is_valid(self):
        return self.is_initialized
         
    def do_scrape(self):
        if not self.is_valid():
            return super(WebScraper,self).do_scrape()

        try:
            app.context.logger.info("Scraping URL: {}".format(self.base_url))
            self.driver.get(self.base_url)     
            return self.driver.page_source
        except Exception as e:
            app.context.logger.info("error in scraping: {}".format(str(e)))
            return None

    