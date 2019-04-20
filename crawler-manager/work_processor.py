import json
import logging
import os
import redis_connect
import requests
import time
from reppy.robots import Robots


class Processor():
    def __init__(self, context, robotparsers):
        self.context = context
        self.robotparsers = robotparsers

    def run(self):
        self.context.logger.info('Waiting for crawlers')
        while self.context.crawlers.size() == 0:
            time.sleep(10)
        
        self.context.logger.info('Entering processor loop')
        while self.context.queued_urls.size() > 0 or self.context.in_process_urls.size() > 0:
            self.context.logger.info('Entered processor loop')
            rejected_requests = 0
            urls_denied = 0
            crawlers = self.context.crawlers.get()
            self.context.logger.info('Iterating through crawlers: %s', str(crawlers))
            for crawler in crawlers:
                url = self.context.queued_urls.poll()
                url_allowed = True
                self.context.logger.info("Pulled %s from queue", url)
                if url is None:
                    rejected_requests += 1
                    continue
                self.context.logger.info(self.robotparsers)
                
                #Check if any of the parsed robots.txt file disallows this url
                for key, value in self.robotparsers.items():
                    self.context.logger.info(key)
                    self.context.logger.info(value)
                    self.context.logger.info(value.allowed(url))
                    if not value.allowed(url):
                        url_allowed = False
                        break

                #Do not assign to crawler if url is disallowed
                if not url_allowed:
                    self.context.logger.info("%s cannot be crawled as it\'s disallowed by the site robots.txt", url)
                    urls_denied += 1
                    continue
                
                crawl_api = os.path.join(crawler, "crawl")
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
            sleep_time = 0.1  + 1.0 * rejected_requests
            self.context.logger.info('Work processor sleeping %d seconds', sleep_time)
            time.sleep(sleep_time)