import unittest
import fakeredis
from crawl_file import *
from crawl_base import *
import google.cloud.storage.blob
from unittest import mock
from unittest.mock import patch

class TestFileScraper(unittest.TestCase):
    def setUp(self):
        self.url = "http://www.orimi.com/pdf-test.pdf"
        self.key = "abc"
        self.scraper = FileScraper(self.url, self.key, "pdf")

    def tearDown(self):
        self.scraper = None
    
    def test_do_scrape(self):
        with patch("crawl_file.requests.get") as mock_get:
            mock_get.return_value.ok = True
            fpath = self.scraper.do_scrape()
        self.assertIsNotNone(fpath)

    def test_get_links(self):
        num_links = len(self.scraper.get_links("abc"))
        self.assertEqual(num_links, 0)

    def test_store_in_gcs(self):
        pass
