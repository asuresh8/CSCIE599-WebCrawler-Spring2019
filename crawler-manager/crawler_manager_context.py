# crawler_manager_context.py
# contains all global variables shared amongst modules
import atomic


class Context:
    def __init__(self, logger):
        self.logger = logger
        self.queued_urls = atomic.AtomicQueue()
        self.crawlers = atomic.AtomicSet()
        self.in_process_urls = atomic.AtomicSet()
        self.processed_urls = atomic.AtomicCounter()
        self.disallowed_urls = atomic.AtomicCounter()
        self.cache = None
        self.parameters = {}
        self.start_time = None


    
