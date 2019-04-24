import unittest
from unittest.mock import Mock, patch
from unittest import mock
from main_app import views
from main_app.models import CrawlRequest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json
import time

# Create your tests here.

class MainAppViewsTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_generate_token(self):
        # To check if a token is getting generated properly or not.
        token = views.get_manager_token(100)
        self.assertNotEqual('', token)
     
 
    """ 
    def test_register_crawler_manager(self):
        user = User.objects.create_user('testUser3', 'test3@user.com', 'testpassword')
        client = APIClient()
        response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser3', 'password' : 'testpassword'}, format="json")
        access_token = response_auth.data['token'].decode('utf-8')
        self.assertNotEqual('', access_token)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        crawl_request = CrawlRequest(user=user)
        crawl_request.urls = "http://abc.com"
        crawl_request.save()
        data = {'job_id' : crawl_request.id, 'endpoint' : 'http://def.com'}
        response = client.post(reverse('api_register_crawler_manager'), data, format="json")
        payload = json.loads(response.content)
        self.assertEqual("http://abc.com", payload["URLS"])
    """
    def test_crawl_complete(self):
        with patch('main_app.views.requests.post') as mock_post:
            user = User.objects.create_user('testUser4', 'test4@user.com', 'testpassword')
            client = APIClient()
            response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser4', 'password' : 'testpassword'}, format="json")
            access_token = response_auth.data['token'].decode('utf-8')
            self.assertNotEqual('', access_token)
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
            crawl_request = CrawlRequest(user=user)
            crawl_request.urls = "http://abc.com"
            crawl_request.save()
            User.objects.create_user('admin'+str(crawl_request.id), 'test4@user.com', 'testpassword')
            data = {'job_id' : crawl_request.id, 'manifest' : 'http://abc.com', 'csv' : 'http://def.com', 'resources_count' : 20}
            response = client.post(reverse('api_complete_crawl'), data, format="json")
            payload = json.loads(response.content)
            self.assertEqual("done", payload["CrawlComplete"])


