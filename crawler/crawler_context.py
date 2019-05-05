import os
import atomic
import requests
import redis_connect
import threading
from model_runner import ModelRunner
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

class Context:
    def __init__(self, logger):
        self.logger = logger
        self.modelrunner = None
        self.active_thread_count = atomic.AtomicCounter()
        self.cache = redis_connect.Cache()
        self.driver = None
        self.initialize_driver()
        self._lock = threading.Lock()
        

    def initialize_driver(self):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver"
        self.logger.info("Chrome driver path: {}".format(dir_path))
        exists = os.path.isfile(dir_path)
    
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
            self.logger.info('browser initialized')   
        except WebDriverException as e:
            self.driver = None
            self.logger.info("could not instantiate browser: {}".format(str(e)))

   
    def get_driver(self):
        return self.driver

    def get_data(self, url):
        with self._lock:
            self.driver.get(url)
            return self.driver.page_source

    def set_useroptions(self, jsonObj):   
        if jsonObj is None:
            return

        self.model_url = jsonObj['model_location']
        self.label_list = jsonObj['labels']
        self.scrape_all = jsonObj['docs_all']
        self.scrape_docx = jsonObj['docs_docx']
        self.scrape_pdf = jsonObj['docs_pdf']

        if self.model_url:
            self.download_model_from_storage()

    def is_pdf_allowed(self):
        return self.scrape_all or self.scrape_pdf

    def is_docx_allowed(self):
        return self.scrape_all or self.scrape_docx

    def has_model(self):
        return self.modelrunner != None

    def has_label(self, curval):
        if str(curval) in self.label_list:
            return True
        else:
            return False

    

    def download_model_from_storage(self):
        if len(self.model_url) == 0:
            return
        try:
            self.logger.info("request for downloading model file: %s", self.model_url)
            r = requests.get(self.model_url, stream=True)
            self.logger.info("request status for downloading model file: %d", r.status_code)
            filepath = 'ml_model'
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
            
            self.modelrunner = ModelRunner(filepath)

        except Exception as e:
            self.logger.info("model file cannot be downloaded: %s", str(e))

    

    
