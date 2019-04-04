import json
import logging
import os
import redis_connect
import requests
import time


class Processor():
    def __init__(self, context):
        self.context = context
    
    def run(self):
        self.context.logger.info('Waiting for crawlers')
        while self.context.crawlers.size() == 0:
            time.sleep(10)
        
        self.context.logger.info('Entering processor loop')
        while self.context.queued_urls.size() != 0 and self.context.in_process_urls.size() != 0:
            rejected_requests = 0
            crawlers = self.context.crawler_set.get()
            for crawler in crawlers:
                crawl_api = os.path.join(crawler, "crawl")
                url = self.context.queued_urls.poll()
                try:
                    self.context.logger.info("Attempting to send %s to %s", url, crawler)
                    response = requests.post(crawl_api, json={'url': url})
                    self.context.logger.info('Received response from %s for %s', crawler, url)
                except Exception as e:
                    self.context.logger.error('Unable to send crawl request to crawler %s: %s', crawler, str(e))
                else:
                    if json.loads(response.text)['accepted']:
                        self.context.logger.info('Crawler %s accepted request', crawler)
                        self.context.in_process_urls.add(url)
                    else:
                        self.context.logger.warning('Crawler %s rejected request', crawler)
                        rejected_requests += 1
                        self.context.queued_urls.add(url)
            
            # TODO: eliminate this. This is completely arbitrary
            time.sleep(0.1  + 1.0 * rejected_requests)