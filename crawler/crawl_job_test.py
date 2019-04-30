import os
import unittest
import fakeredis
from unittest import mock
from crawl_job import *
from unittest.mock import patch
from crawl_global import CrawlGlobal

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

    def do_mock_response(self, content='CONTENT'):
        mock_resp = mock.Mock()
        # set content
        mock_resp.content = content
        return mock_resp


      
    def test_send_response_to_manager(self):
       with patch ("crawl_job.requests.post") as mock_post: 
            mock_resp = self.do_mock_response('success')
            mock_post.return_value = mock_resp
            manager = os.environ.get('CRAWLER_MANAGER_ENDPOINT', 'http://crawler-manager:8002')
            res = self.crawljob.send_response_to_manager(manager)
            
            self.assertEqual(res.content, 'success')
    
    
    """ def test_execute(self):
        app.cache.rediscache = fakeredis.FakeStrictRedis()
        self.crawljob.execute() """
        
    def test_is_cached(self):
        CrawlGlobal.context().cache.rediscache = fakeredis.FakeStrictRedis()
        retval = self.crawljob.is_cached()
        self.assertIs(retval, False)


if __name__ == 'main':
    unittest.main()