import unittest
import app
import fakeredis
from crawl_web import *
from crawl_base import *
import google.cloud.storage.blob
from unittest import mock
from crawl_global import CrawlGlobal

""" 
mocking google cloud
def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)
"""

class TestWebScraper(unittest.TestCase):
   

    def setUp(self):
        self.url = "http://quotes.toscrape.com/js/"
        self.key = "abc"
        self.scraper = WebScraper(self.url, self.key)

    def tearDown(self):
        self.scraper = None
    
    def test_is_initialized(self):
        self.assertIs(self.scraper.is_valid(), True)
    
    def test_do_scrape(self):
        bs = BeautifulSoup(self.scraper.do_scrape(), 'html.parser')   
        self.assertEqual(10, len(bs.find_all('div',{"class" : "quote"})))
        
    
    """ def test_store_in_gcs(self):
        
        with patch('crawl_base.google.cloud.storage') as mock:
            mock.return_val
        
        bucket = _Bucket()
        blob = self._make_one(self.key, bucket=bucket)
        
        html = self.scraper.do_scrape()
        uri = self.scraper.store_in_gcs(html) 
        self.assertEquals(uri, blob.public_url)        """
    
    def test_store_in_redis(self):
        CrawlGlobal.context().cache.rediscache = fakeredis.FakeStrictRedis()
        
        links = ["x","y","z"]
        s3uri ="abc"
        self.scraper.store_in_redis(s3uri,links)
        val = CrawlGlobal.context().cache.get(self.url)
        self.assertEqual(val, {"s3_uri": "abc", "child_urls": ["x", "y", "z"]})



    def test_get_links(self):
        links = ['/', '/login', '/js/page/2/', 'https://www.goodreads.com/quotes', 'https://scrapinghub.com']
        res_links = self.scraper.get_links(self.scraper.do_scrape())
        self.assertEqual(links, res_links)


if __name__ == 'main':
    unittest.main()
