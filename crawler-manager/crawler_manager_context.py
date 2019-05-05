# Contains all global variables shared amongst modules
import atomic


class Context:
    def __init__(self, logger):
        self.logger = logger
        # Priority queue containing the urls to be crawled
        self.queued_urls = atomic.AtomicPriorityCountQueue({})
        # Set of registered crawlers
        self.crawlers = atomic.AtomicSet()
        # Set of Urls being processed
        self.in_process_urls = atomic.AtomicSet()
        # Set of Urls already processed
        self.processed_urls = atomic.AtomicCounter()
        # Count of urls not allowed by site Robots.txt
        self.disallowed_urls = atomic.AtomicCounter()
        # Count of urls downloaded into storage
        self.downloaded_pages = atomic.AtomicCounter()
        self.cache = None
        self.parameters = {}
        self.start_time = None

    def reset(self):
        self.queued_urls.reset()
        self.in_process_urls.reset()
        self.processed_urls.reset()
        self.processed_urls.reset()
        self.disallowed_urls.reset()
        self.downloaded_pages.reset()
        if self.cache is not None:
            self.cache.reset()


    
