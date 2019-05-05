from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from main_app.models import CrawlRequest, Profile
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.utils import jwt_payload_handler
from django.conf import settings
from django.contrib.auth.signals import user_logged_in

from django.http import JsonResponse
from django.http import HttpRequest
from django.http import HttpResponse
from io import BytesIO
from google.cloud import storage

import requests, jwt, json, os, zipfile, time, sys, uuid

# import the logging library
import logging
logging.basicConfig(level=logging.INFO)
# Get an instance of a logger
logger = logging.getLogger(__name__)


def store_data_in_gcs(filename, model_id):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    key = 'crawl_models/{}'.format(str(uuid.uuid4()))
    blob = bucket.blob(key)
    blob.upload_from_filename(filename)
    blob.make_public()
    return blob.public_url


def get_google_cloud_manifest_contents(manifest):
    client = storage.Client()
    bucket = client.get_bucket(os.environ['GCS_BUCKET'])
    blob = storage.Blob(manifest, bucket)
    content = blob.download_as_string()
    return content


def update_job_status(job):
    if (job.status != 3 and job.status != 4):
        logger.info('Getting status from crawler-manager')
        jobs = CrawlRequest.objects.filter(user=job.user)
        last_job = True
        if (len(jobs) > 0):
            for j in jobs:
                if (j.id > job.id):
                    logger.info('Marking it failed because it doesnt have finished status yet.')
                    job.status = 4
                    job.save()
                    last_job = False
        if (last_job == True):
            try:
                if (job.crawler_manager_endpoint != ""):
                    resp = requests.get(job.crawler_manager_endpoint+'/status')
                    logger.info('Received status response')
                    logger.info('response content:{}'.format(resp.text))
                    payload = json.loads(resp.text)
                    logger.info('job id: {}'.format(payload["job_id"]))
                    if (payload["job_id"] == job.id):
                        job.docs_collected = payload["processed_count"]
                        job.save()
            except Exception as ex:
                logger.info('Exception in getting status')


def check_user_password(current_password, incoming_password):
    salt = current_password.split('$')[2]
    hashed_password = make_password(incoming_password, salt)
    return current_password == hashed_password


def check_post_authentication(request):
    if ('token' not in request.data):
        return True
    if ('token' in request.data):
        token = request.data['token']
        payload = jwt.decode(token, settings.SECRET_KEY)
        if (User.objects.get(username=payload['username']) is not None):
            return True
    return False


def check_get_authentication(request):
    if ('token' not in request.query_params):
        return True
    if ('token' in request.query_params):
        token = request.query_params.get('token')
        payload = jwt.decode(token, settings.SECRET_KEY)
        print(payload)
        if (User.objects.get(username=payload['username']) is not None):
            return True
    return False
