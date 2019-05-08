import logging
import unittest

import crawler_manager_context
 
class TestCrawlerManagerContext(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        self.context = crawler_manager_context.Context(logging.getLogger())

    def tearDown(self):
        pass
    
    def test_context_queued_url_functionality(self):
        url = 'http://garbage.com'
        self.context.queued_urls.add(url)
        self.assertEqual(self.context.queued_urls.poll(), (1, 'http://garbage.com'))
        self.assertFalse(self.context.queued_urls.contains(url))

    def test_context_crawlers_functionality(self):
        crawler = 'http://0.0.0.0:80'
        self.context.crawlers.add(crawler)
        self.assertTrue(self.context.crawlers.contains(crawler))
        self.context.crawlers.remove(crawler)
        self.assertFalse(self.context.crawlers.contains(crawler))

    def test_context_in_process_urls_functionality(self):
        url = 'http://garbage.com'
        self.context.in_process_urls.add(url)
        self.assertTrue(self.context.in_process_urls.contains(url))
        self.context.in_process_urls.remove(url)
        self.assertFalse(self.context.in_process_urls.contains(url))
    
    def test_context_processed_urls_functionality(self):
        self.assertEqual(self.context.processed_urls.get(), 0)
        self.context.processed_urls.increment()
        self.assertEqual(self.context.processed_urls.get(), 1)
 
 
if __name__ == '__main__':
    unittest.main()