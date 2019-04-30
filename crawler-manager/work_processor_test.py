import logging
import os
import responses
import threading
import time
import unittest

import crawler_manager_context
import work_processor


class MockRobotsFetcher:
    
    def __init__(self, validator):
        self.validator = validator

    def fetch(self, url):
        return self.validator


class TestCrawlerManagerWorkProcessor(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        self.context = crawler_manager_context.Context(logging.getLogger())
        self.processor = work_processor.Processor(self.context, None)
    
    def tearDown(self):
        pass
    
    @responses.activate
    def test_work_processor_basic(self):
        self.processor.robots_txt_fetcher = MockRobotsFetcher(work_processor.SimpleValidator())
        crawler = 'http://dummy-crawler'
        url = 'http://dummy.com'
        responses.add(responses.POST, os.path.join(crawler, 'crawl'),
                      json={'accepted': True}, status=200)
        self.context.queued_urls.add(url)
        self.context.crawlers.add(crawler)
        processor_thread = threading.Thread(target=self.processor.run)
        processor_thread.start()
        time.sleep(1)
        self.context.in_process_urls.remove(url)
        processor_thread.join()
 

if __name__ == '__main__':
    unittest.main()