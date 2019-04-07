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

 
if __name__ == '__main__':
    unittest.main()