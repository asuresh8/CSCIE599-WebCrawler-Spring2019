import atomic
import redis_connect

class Context:
    def __init__(self, logger):
        self.logger = logger
        self.modelrunner = None
        self.active_thread_count = atomic.AtomicCounter()
        self.cache = redis_connect.Cache()

    def set_useroptions(jsonObj):   
        if jsonObj is None:
            return

        self.model_url = jsonObj['model_location']
        self.label_list = jsonObj['labels']
        self.scrape_all = jsonObj['docs_all']
        self.scrape_docx = jsonObj['docs_docx']
        self.scrape_pdf = jsonObj['docs_pdf']

        if self.model_url:
            self.download_model()

    def is_pdf_allowed(self):
        return self.scrape_all or self.scrape_pdf

    def is_docx_allowed(self):
        return self.scrape_all or self.scrape_docx

    def download_model_from_storage(self):
        try:
            r = requests.get(self.base_url, stream=True)
            self.logger.info("request status for downloading model file: %d", r.status_code)
            filepath = 'ml_model'
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(self.chunk_size):
                    fd.write(chunk)
            
            self.modelrunner = ModelRunner(filepath)

        except Exception as e:
            self.logger.info("model file cannot be downloaded: %s", str(e))

    

    
