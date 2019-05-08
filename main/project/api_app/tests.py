import unittest
from unittest.mock import Mock, patch
from unittest import mock
from api_app import views
from main_app.models import CrawlRequest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json
import time

# Tests for code in api_app.

class ApiAppViewsTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_authenticate(self):
        """
        Test to check jwt token generation code using authenticate end-point.
        """
        user = User.objects.create_user('testUser5', 'test5@user.com', 'testpassword')
        client = APIClient()
        response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser5', 'password' : 'testpassword'}, format="json")
        access_token = response_auth.data['token']
        self.assertNotEqual('', access_token)

    def test_api_create_crawl(self):
        """
        Test to create a new crawl request for an external user using an API end-point directly.
        """
        with patch('api_app.views.launch_crawler_manager') as mock_launch:
            user = User.objects.create_user('testUser', 'test@user.com', 'testpassword')
            client = APIClient()
            response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser', 'password' : 'testpassword'}, format="json")
            access_token = response_auth.data['token']
            self.assertNotEqual('', access_token)
            client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + access_token)

            # Post request to start a crawl.
            self.payload = {'username': 'testUser', 'name' : 'testJob', 'domain' : 'http://google.com', 'urls' : 'http://bing.com'}
            response = client.post(
                reverse('api_create_crawl'),
                self.payload,
                format="json")
            self.assertNotEqual(0, response.data["jobId"])

    def test_api_crawl_contents(self):
        """
        Test to get crawl contents using an API end-point.
        """
        with patch('api_app.views.get_google_cloud_manifest_contents') as mock_cloud:
            mock_cloud.return_value = "Test"
            user = User.objects.create_user('testUser2', 'test2@user.com', 'testpassword')
            crawl_request = CrawlRequest(user=user)
            crawl_request.storage_location = "abc/def"
            crawl_request.save()
            id = crawl_request.id
            client = APIClient()
            response_auth = client.post(reverse('authenticate_user'), {'username' : 'testUser2', 'password' : 'testpassword'}, format="json")
            access_token = response_auth.data['token']
            self.assertNotEqual('', access_token)
            client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + access_token)
            params = {'JOB_ID' : id, 'complete_crawl' : 0}
            response_get = client.get(reverse('api_crawl_contents'), params)
            self.assertNotEqual('', response_get.data["crawl_contents"])

    def test_api_get_job_status(self):
        """
        Test to get status of a job using an API end-point.
        """
        user = User.objects.create_user('testStatusUser', 'testStatusUser@user.com', 'testpassword')
        client = APIClient()
        crawl_request = CrawlRequest(user=user)
        crawl_request.name = 'test'
        crawl_request.urls = "http://abc.com"
        crawl_request.save()
        data = {'job_id' : crawl_request.id}
        response = client.post(reverse('api_job_status'), data, format="json")
        payload = json.loads(response.content)
        self.assertEqual("test", payload["name"])
