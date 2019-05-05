from django.contrib.auth.models import User
from main_app.models import CrawlRequest
from main_app.views import launch_crawler_manager
from main_app.utilities import get_google_cloud_manifest_contents
from main_app.utilities import get_google_cloud_crawl_pages
from main_app import utilities
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.utils import jwt_payload_handler
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.http import JsonResponse

import requests, jwt, json, os, time, sys

# import the logging library
import logging
logging.basicConfig(level=logging.INFO)
# Get an instance of a logger
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def get_api_job_status(request):
    try:
        job = CrawlRequest.objects.get(pk=request.data['job_id'])
        job_info = {
            "name": job.name,
            "type": job.type,
            "domain": job.domain,
            "urls": job.urls,
            "status": job.status
        }
    except CrawlRequest.DoesNotExist:
        raise Http404("Job does not exist.")

    return JsonResponse(job_info)

@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        username = request.data['username']
        password = request.data['password']
        user = User.objects.get(username=username)
        if user:# and check_user_password(user.password, password):
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY).decode('utf-8')
                user_details = {}
                user_details['name'] = "%s %s" % (user.first_name, user.last_name)
                user_details['token'] = token
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)

@api_view(['POST'])
#@permission_classes((IsAuthenticated, ))
@permission_classes([AllowAny, ])
def api_create_crawl(request):
    logger.info('In api new job')
    username = request.data['username']
    user_obj = User.objects.get(username=username)
    crawl_request = CrawlRequest(user=user_obj)
    crawl_request.name = request.data['name']
    crawl_request.domain = request.data['domain']
    crawl_request.urls = request.data['urls']
    crawl_request.save()
    logger.info('NewJob created: %s', crawl_request.id)
    logger.info('Received urls: %s', crawl_request.urls)
    launch_crawler_manager(crawl_request, crawl_request.id)
    payload = {}
    payload['jobId'] = crawl_request.id
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
#@permission_classes((IsAuthenticated, ))
@permission_classes([AllowAny, ])
def api_crawl_contents(request):
    jobId = request.query_params.get('JOB_ID')
    content = ""
    payload = {}
    complete_crawl = request.query_params.get('complete_crawl')
    job = CrawlRequest.objects.get(pk=jobId)
    manifest = job.storage_location.split('/')[-1]
    payload['jobId'] = jobId
    if complete_crawl == "1":
        content = get_google_cloud_manifest_contents(manifest)
        content = get_google_cloud_crawl_pages(content)
    else:
        try:
            content = get_google_cloud_manifest_contents(manifest)
        except Exception as e:
            logger.info('Unable to read manifest contents: %s', str(e))
            content = 'Unable to read manifest contents'
    payload['crawl_contents'] = content
    return Response(payload, status=status.HTTP_200_OK)
