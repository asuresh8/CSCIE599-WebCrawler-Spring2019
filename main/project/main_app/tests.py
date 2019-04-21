from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json
import requests
from main_app import views
from main_app import urls
import time

# Create your tests here.

class MainAppViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testUser', 'test@user.com', 'testpassword')

    def test_generate_token(self):
        # To check if a token is getting generated properly or not.
        token = views.get_manager_token(2)
        self.assertNotEqual('', token)

    def test_full_flow(self):

        # Get Authentication token.
        response_auth = self.client.post(reverse('authenticate_user'), {'username' : 'testUser', 'password' : 'testpassword'}, format="json")
        access_token = response_auth.data['token'].decode('utf-8')
        self.assertNotEqual('', access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # Post request to start a crawl.
        self.payload = {'username': 'testUser', 'name' : 'testJob', 'domain' : 'http://google.com', 'urls' : 'http://bing.com'}
        response = self.client.post(
            reverse('api_create_crawl'),
            self.payload,
            format="json")
        self.assertNotEqual(0, response.data["jobId"])
        
        time.sleep(30)
        
        # Get request to get the crawl contents.
        params = {'JOB_ID' : response.data["jobId"], 'complete_crawl' : 0}
        response_get = self.client.get(reverse('api_crawl_contents'), params)
        self.assertNotEqual('', response_get.data["crawl_contents"])
