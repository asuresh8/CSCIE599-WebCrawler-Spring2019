# crawler_manager_context.py
# contains all global variables shared amongst modules
import atomic


class Context:
    def __init__(self, logger):
        self.logger = logger
        # self.queued_urls = atomic.AtomicQueue()
        self.queued_urls = atomic.AtomicPriorityCountQueue({})
        self.crawlers = atomic.AtomicSet()
        self.in_process_urls = atomic.AtomicSet()
        self.processed_urls = atomic.AtomicCounter()
        self.disallowed_urls = atomic.AtomicCounter()
        self.cache = None
        self.parameters = {}
        self.start_time = None

    def reset(self):
        self.queued_urls.reset()
        self.in_process_urls.reset()
        self.processed_urls.reset()
        self.processed_urls.reset()
        self.disallowed_urls.reset()
        if self.cache is not None:
            self.cache.reset()


    
