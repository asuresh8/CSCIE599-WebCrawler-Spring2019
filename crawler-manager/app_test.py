import json
import fakeredis
import unittest
 
import app
import redis_connect
 
class TestCrawlerManagerApp(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        app.context.cache = redis_connect.RedisClient(fakeredis.FakeStrictRedis())
        app.context.parameters = {
            'domain': 'http://garbage.com',
            'docs_all': True,
            'docs_html': False,
            'docs_pdf': False,
            'docs_docx': False,
            'model_location': '',
            'labels': [],
        }
        self.app = app.app.test_client()
        self.app.testing = True
    
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Crawler Manager')
 
    def test_ping(self):
         response = self.app.get('/ping')
         self.assertEqual(response.status_code, 200)
         self.assertEqual(response.data, b'PONG')
    
    def test_kill(self):
        response = self.app.post('/kill')
        self.assertEqual(response.status_code, 200)
    
    def test_register_crawler(self):
        endpoint = 'http://0.0.0.0'
        response = self.app.post('/register_crawler', json={'endpoint': endpoint})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(app.context.crawlers.contains(endpoint))

    def test_post_links(self):
        main_url = 'http://garbage.com'
        s3_uri = 'https://s3.amazonaws.com/garbage-bucket/garbage-key'
        child_urls = ['http://garbage.com/1', 'http://garbage.com/2', '/3']
        response = self.app.post('/links', json={
            'main_url': main_url, 's3_uri': s3_uri, 'child_urls': child_urls})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/1'))
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/2'))
        self.assertTrue(app.context.queued_urls.contains('http://garbage.com/3'))
        self.assertTrue(app.context.cache.exists(main_url))
        self.assertEqual(app.context.cache.get(main_url), s3_uri)

    def test_get_status(self):
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertTrue('processed_count' in response_json)
        self.assertTrue('processing_count' in response_json)
        self.assertTrue('queued_count' in response_json)

 
if __name__ == '__main__':
    unittest.main()
