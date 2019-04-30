import atomic
import requests
import redis_connect
from model_runner import ModelRunner

class Context:
    def __init__(self, logger):
        self.logger = logger
        self.modelrunner = None
        self.active_thread_count = atomic.AtomicCounter()
        self.cache = redis_connect.Cache()

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
        if curval in self.label_list:
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

    

    
