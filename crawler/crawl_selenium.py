import os
import app
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class ScraperObject(object):

    def __init__(self, base_url):
    
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        app.context.logger.info("Chrome driver path: {}".format(dir_path))
        exists = os.path.isfile(dir_path)
        self.is_initialized = False
        self.base_url = base_url
        if exists :
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-debugging-port=9222")
            try:
                self.driver = webdriver.Chrome(executable_path= dir_path, options= chrome_options ) 
                app.context.logger.info('browser initialized')
                
            except WebDriverException as e:
                app.context.logger.info("could not instantiate browser: {}".format(str(e)))
        else :
            self.is_initialized = True
 
    # check if browser is intialized properly
    def is_valid(self):
        return self.is_initialized

    # get_links - parses the url 'a' tags using beautiful soup
    def get_links(html):
        bs_obj = bs4.BeautifulSoup(html, 'html.parser')
        links_obj = {}
        for link in bs_obj.find_all('a'):
            if 'href' in link.attrs:
                links_obj[link.attrs['href']] = 1

        try:
            return list(links_obj.keys())
        except Exception as e:
            app.context.logger.error("Could not list links in url: %s", str(e))
            return []
            
    def do_scrape(self, url):
        try:
            self.driver.get(url)
            app.context.logger.info("Scraping URL: {}".format(self.base_url))
            return self.driver.page_source
        except Exception as e:
            print("error")
            return

    def store_in_gcs(html, key):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
        blob = bucket.blob(key)
        blob.upload_from_string(html)
        blob.make_public()
        return blob.public_url