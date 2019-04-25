from django.test import TestCase
#import unittest
from unittest.mock import Mock, patch
from unittest import mock
from main_app import views
from main_app.models import CrawlRequest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test.client import Client
from rest_framework import status
from django.urls import reverse
from django.test.client import RequestFactory
import json
import time

# Create your tests here.

class MainAppViewsTestCase(TestCase):
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
        self.assertEqual("http://abc.com", payload["urls"][0])
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

    def test_welcome(self):
        user = User.objects.create_user('testWelcome', 'testWelcome@user.com', 'testpassword')
        client = Client()
        response = client.get(reverse('webcrawler_welcome'))
        self.assertContains(response, 'This is a scalable webcrawler application')
        self.assertEqual(response.status_code, 200)
        client.login(username='testWelcome', password='testpassword')
        response = client.get(reverse('webcrawler_welcome'))
        self.assertEqual(response.status_code, 302)

    def test_home(self):
        user = User.objects.create_user('testHome', 'testHome@user.com', 'testpassword')
        client = Client()
        client.login(username='testHome', password='testpassword')
        response = client.get(reverse('mainapp_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'These are all the current jobs for user')

    def test_new_job(self):
        with patch('main_app.views.launch_crawler_manager') as mock_launch:
            user = User.objects.create_user('testNewJob', 'testNewJob@user.com', 'testpassword')
            client = Client()
            client.login(username='testNewJob', password='testpassword')
            self.payload = {'username': 'testUser', 'name' : 'testJob', 'domain' : 'http://google.com', 'urls' : 'http://bing.com'}
            response = client.post(
                reverse('mainapp_new_job'),
                self.payload,
                format="json")
            self.assertEqual(response.status_code, 200)


    def test_launch_crawler_manager(self):
        with patch('main_app.views.requests.post') as mock_post:
            rf = RequestFactory()
            request = rf.get('/hello/')
            ret_code = views.launch_crawler_manager(request, 1)
            self.assertEqual(ret_code, None)

    def test_job_details(self):
        user = User.objects.create_user('testJobDetails', 'testJobDetails@user.com', 'testpassword')
        crawl_request = CrawlRequest(user=user)
        crawl_request.urls = "http://abc.com"
        crawl_request.save()
        client = Client()
        client.login(username='testJobDetails', password='testpassword')
        response = client.get(reverse('mainapp_jobdetails', kwargs={'job_id':crawl_request.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Job Details for crawl job')

    def test_crawl_contents(self):
        with patch('main_app.views.get_google_cloud_manifest_contents') as mock_cloud:
            mock_cloud.return_value = b'Test'
            user = User.objects.create_user('testCrawlContents', 'testCrawlContents@user.com', 'testpassword')
            crawl_request = CrawlRequest(user=user)
            crawl_request.s3_location = "abc/def"
            crawl_request.save()
            id = crawl_request.id
            client = Client()
            client.login(username='testCrawlContents', password='testpassword')
            response = client.get(reverse('mainapp_crawlcontents', kwargs={'job_id':crawl_request.id}))
            self.assertEqual(response.status_code, 200)





