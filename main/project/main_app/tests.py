from django.test import TestCase
#import unittest
from unittest.mock import Mock, patch
from unittest import mock
from main_app import views,utilities
from main_app.models import CrawlRequest, MlModel
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
     
    def test_register_crawler_manager(self):
        user = User.objects.create_user('testUser3', 'test3@user.com', 'testpassword')
        client = APIClient()
        response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser3', 'password' : 'testpassword'}, format="json")
        access_token = response_auth.data['token']
        self.assertNotEqual('', access_token)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        crawl_request = CrawlRequest(user=user)
        crawl_request.urls = "http://abc.com"
        crawl_request.save()
        data = {'job_id' : crawl_request.id, 'endpoint' : 'http://def.com'}
        response = client.post(reverse('api_register_crawler_manager'), data, format="json")
        payload = json.loads(response.content)
        self.assertEqual("http://abc.com", payload["urls"][0])

    def test_crawl_complete(self):
        with patch('main_app.views.requests.post') as mock_post:
            user = User.objects.create_user('testUser4', 'test4@user.com', 'testpassword')
            client = APIClient()
            response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser4', 'password' : 'testpassword'}, format="json")
            access_token = response_auth.data['token']
            self.assertNotEqual('', access_token)
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
            crawl_request = CrawlRequest(user=user)
            crawl_request.urls = "http://abc.com"
            crawl_request.save()
            User.objects.create_user('admin'+str(crawl_request.id), 'test4@user.com', 'testpassword')
            data = {'job_id' : crawl_request.id, 'manifest' : 'http://abc.com', 'csv' : 'http://def.com', 'resources_count' : 20, 'downloaded_pages' : 20}
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

    def test_add_model(self):
        with patch('main_app.views.store_data_in_gcs') as mock_cloud:
            mock_cloud.return_value = b'http://abc.com'
            user = User.objects.create_user('testAddModel', 'testAddModel@user.com', 'testpassword')
            client = Client()
            client.login(username='testAddModel', password='testpassword')
            self.payload = {'name': 'model', 'labels' : '1;2'}
            response = client.post(
                reverse('mainapp_mlmodel'),
                self.payload,
                format="json")
            self.assertEqual(response.status_code, 200)

    def test_ml_model(self):
        user = User.objects.create_user('testModelUser', 'testModel@user.com', 'testpassword')
        ml_model_instance = MlModel(user=user)
        ml_model_instance.name = 'modelTest'
        ml_model_instance.labels = '1;2;3'
        ml_model_instance.s3_location = 'http://s3.com'
        ml_model_instance.save()
        models = MlModel.objects.filter(name='modelTest')
        self.assertEqual(1, len(models))
        self.assertEqual("1 modelTest", str(models[0]))

    def test_crawl_request_model(self):
        user = User.objects.create_user('testCrawlRequestUser', 'testCrawlRequest@user.com', 'testpassword')
        crawl_instance = CrawlRequest(user=user)
        crawl_instance.name = 'crawl_model_test'
        crawl_instance.type = 1
        crawl_instance.domain = 'http://abc.com'
        crawl_instance.urls = 'http://url.com'
        crawl_instance.description = 'Test Crawl Request'
        crawl_instance.docs_all = True
        crawl_instance.docs_html = False
        crawl_instance.docs_docx = False
        crawl_instance.docs_pdf = False
        crawl_instance.docs_xml = False
        crawl_instance.docs_txt = False
        crawl_instance.docs_collected = 10
        crawl_instance.status = 1
        crawl_instance.s3_location = 'http://s3.com'
        crawl_instance.crawler_manager_endpoint = 'http://end.com'
        crawl_instance.manifest = 'http://manifest.com'
        crawl_instance.num_crawlers = 1
        crawl_instance.save()
        crawl_instance.get_absolute_url()
        crawl_instances = CrawlRequest.objects.filter(name='crawl_model_test')
        self.assertEqual(1, len(crawl_instances))
        self.assertEqual("1 crawl_model_test", str(crawl_instances[0]))

    def test_update_job_status(self):
        with patch('main_app.utilities.requests.get') as mock_get:
            user = User.objects.create_user('testUpdateStatus', 'testUpdateStatus@user.com', 'testpassword')
            crawl_request = CrawlRequest(user=user)
            crawl_request.crawler_manager_endpoint = "http://abc.com"
            crawl_request.name = 'test_update_status' 
            crawl_request.save()
            mock_response = mock.Mock()
            resp_string = '{"job_id":' + str(crawl_request.id) + ', "processed_count":10}'
            mock_response.text = resp_string
            mock_get.return_value = mock_response
            utilities.update_job_status(crawl_request)
            crawl_request2 = CrawlRequest(user=user)
            crawl_request2.crawler_manager_endpoint = "http://abc.com"
            crawl_request2.name = 'test_update_status_second' 
            crawl_request2.save()
            utilities.update_job_status(crawl_request)

    def test_ping(self):
        with patch('main_app.views.requests.get') as mock_get:
            client = APIClient()
            response = client.get(reverse('api_ping'), {'releaseDate':'20190501'})
            self.assertEqual(response.status_code, 200)





