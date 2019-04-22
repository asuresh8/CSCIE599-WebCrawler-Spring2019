from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urldefrag, urljoin
from bs4 import BeautifulSoup
import os

class SeleniumTask(object):

    def __init__(self, base_url):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path + "/chromedriver"
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(dir_path, options= options ) 
        self.base_url = base_url
 
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
            self.browser.get(url)
            context.logger.info("Scraping URL: {}".format(self.base_url))
            return self.browser.page_source
        except Exception as e:
            print("error")
            return

    def store_response_in_gcs(html, key):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
        blob = bucket.blob(key)
        blob.upload_from_string(html)
        blob.make_public()
        return blob.public_url