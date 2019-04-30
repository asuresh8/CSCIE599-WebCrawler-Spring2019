import logging
import unittest
from unittest import mock
import crawler_context
 
class TestCrawlerContext(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        self.context = crawler_context.Context(logging.getLogger())

    def tearDown(self):
        pass
    
    def test_is_pdf_allowed(self):
        self.context.scrape_all = False
        self.context.scrape_pdf = True
        self.assertIs(self.context.is_pdf_allowed(), True)

    def test_is_docx_allowed(self):
        self.context.scrape_all = False
        self.context.scrape_docx = False
        self.assertIs(self.context.is_docx_allowed(), False)

    def test_download_model_from_storage(self):
        #with patch('crawler_context.requests.get') as mock_get:
        pass

    # TODO: delete this noop test and write actual unit tests
    def test_context_thread_count_functionality(self):
        self.assertEqual(self.context.active_thread_count.get(), 0)
        self.context.active_thread_count.increment()
        self.assertEqual(self.context.active_thread_count.get(), 1)
        self.context.active_thread_count.decrement()
        self.assertEqual(self.context.active_thread_count.get(), 0)
 
 
if __name__ == '__main__':
    unittest.main()