import unittest

from helpers import *
 
class TestCrawlerManagerHelpers(unittest.TestCase):
    """
    Test the helper methods found in helpers.py
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_expand_url(self):
        self.assertEqual(expand_url('http://www.test.com/', '/me'),'http://www.test.com/me', "Does not convert /me properly")
        # self.assertEqual(expand_url('http://www.test.com/abc', 'test'),'http://www.test.com/abc/test', "Does not convert test properly")
        self.assertEqual(expand_url('http://www.test.com/', './../me'),'http://www.test.com/me', "Does not convert ./../me properly")
        self.assertEqual(expand_url('http://www.test.com/abc', './../../test'),'http://www.test.com/test', "Does not convert ./../../test properly")

    def test_get_domain_name(self):
        self.assertEqual(get_domain_name('https://www.test.com/abc/'),'www.test.com','Correct domain name not returned')
        self.assertEqual(get_domain_name('https://www.test.com/'),'www.test.com','Correct domain name not returned')
        self.assertEqual(get_domain_name('https://www.test.com/abc/def/123/ghi'),'www.test.com','Correct domain name not returned')
    
    def test_get_root_url(self):
        self.assertEqual(get_root_url('https://www.test.com/abc/'),'https://www.test.com/','Correct domain name not returned')
        self.assertEqual(get_root_url('https://www.test.com/'),'https://www.test.com/','Correct domain name not returned')
        self.assertEqual(get_root_url('https://www.test.com/abc/def/123/ghi'),'https://www.test.com/','Correct domain name not returned')
    
    def test_is_absolute_url(self):
        self.assertEqual(is_absolute_url('https://www.test.com/abc/'),True,'Absolute url not detected')
        self.assertEqual(is_absolute_url('https://www.test.com/'),True,'Absolute url not detected')
        self.assertEqual(is_absolute_url('https://www.test.com/abc/def/123/ghi'),True,'Absolute url not detected')
        self.assertEqual(is_absolute_url('abc/'),False,'Relative url not detected')
        self.assertEqual(is_absolute_url('www.test.com/'),False,'Relative url not detected')
        self.assertEqual(is_absolute_url('/abc/123/def'),False,'Relative url not detected')

    def test_is_root_url(self):
        self.assertEqual(is_root_url('/'),True,'Root url not detected')
        self.assertEqual(is_root_url('https://www.test.com/'),True,'Root url not detected')
        self.assertEqual(is_root_url('https://www.test.com/abc/def/123/ghi'),False,'Incorrect root url')
        self.assertEqual(is_root_url('www.test.com/'),False,'Incorrect root url')
        self.assertEqual(is_root_url('/abc'),False,'Incorrect root url')

    def test_strip_protocol_from_url(self):
        self.assertEqual(strip_protocol_from_url('https://www.test.com'),'test.com','https not stripped')
        self.assertEqual(strip_protocol_from_url('https://www.test.com/abc'),'test.com/abc','https not stripped')
        self.assertEqual(strip_protocol_from_url('http://www.test.com'),'test.com','http not stripped properly')
        self.assertEqual(strip_protocol_from_url('ftp://www.test.com'),'test.com','ftp not stripped properly')
        self.assertEqual(strip_protocol_from_url('www.test.com'),'test.com','www not stripped properly')   
        self.assertEqual(strip_protocol_from_url('ftps://www.test.com'),'ftps://test.com','incorrect replacement')
    
    
 
 
if __name__ == '__main__':
    unittest.main()