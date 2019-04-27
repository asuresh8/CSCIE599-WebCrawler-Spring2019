import unittest
import app
from unittest import mock
from crawl_job import *
from unittest.mock import patch

class TestCrawlerJob(unittest.TestCase):

    def setUp(self):
        self.url = "http://quotes.toscrape.com/js/"
        self.crawljob = CrawlerJob(self.url)

    def tearDown(self):
        self.crawljob = None
    
    def test_get_extension(self):
        self.base_url = "http://www.orimi.com/pdf-test.pdf"
        ext = self.crawljob.get_extension(self.base_url)
        self.assertEqual(ext, ".pdf")

    def do_mock_response(self, status=200):
        mock_resp = mock.Mock()
        # set status code and content
        mock_resp.status_code.side_effect = status
        return mock_resp


    def test_send_response_to_manager(self):
        pass
       """  with patch ("crawl_job.requests.post") as mock_post: 
            mock_post.return_value = self.do_mock_response()
            res = self.crawljob.send_response_to_manager()
            self.assertEqual(res.status_code, 200) """
        
    
    def test_execute(self):
        pass
        
    def test_is_cached(self):
        pass

if __name__ == 'main':
    unittest.main()