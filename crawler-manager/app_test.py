import fakeredis
from unittest import mock
import unittest
 
import app
 
class TestCrawlerManagerApp(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def tearDown(self):
        pass
    
    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Crawler Manager')
 
    def test_ping(self):
         response = self.client.get('/ping')
         self.assertEqual(response.status_code, 200)
         self.assertEqual(response.data, b'Crawler Manager PING')
    
    def test_kill(self):
        response = self.client.post('/kill')
        self.assertEqual(response.status_code, 200)
    
    def test_register_crawler(self):
        endpoint = 'http://0.0.0.0'
        response = self.client.post('/register_crawler', json={'endpoint': endpoint})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(app.context.crawlers.contains(endpoint))
    
    @mock.patch('redis.Redis')
    def test_post_links(self, mock_redis_constructor):
        mock_redis_instance = fakeredis.FakeRedis()
        mock_redis_constructor.side_effect = mock_redis_instance
        main_url = 'http://garbage.com'
        s3_uri = 'https://s3.amazonaws.com/garbage-bucket/garbage-key'
        child_urls = ['http://garbage.com/1', 'http://garbage.com/2', '/3']
        response = self.client.post('/links', json={
            'main_url': main_url, 's3_uri': s3_uri, 'child_urls': child_urls})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/1'))
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/2'))
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/3'))




 
if __name__ == '__main__':
    unittest.main()