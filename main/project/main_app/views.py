from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# import the logging library
import logging

from .models import CrawlRequest, Profile
from .forms import CrawlRequestForm, ProfileForm

from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.utils import jwt_payload_handler
import jwt
from django.conf import settings
from django.contrib.auth.signals import user_logged_in

import requests
from django.http import HttpResponse
import json
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)
imageTag = os.environ.get('IMAGE_TAG', '0')

@login_required()
def home(request):
    user = request.user
    crawl_request = CrawlRequest(user=user)
    form = CrawlRequestForm(instance=crawl_request)
    jobs = CrawlRequest.objects.filter(user=user)
    return render(request, "main_app/home.html", {'form': form, 'jobs': jobs})


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):

    try:
        username = request.data['username']
        password = request.data['password']
        hashed_pass = make_password(password)
        user = User.objects.get(username=username, password=hashed_pass)
        #user = User.objects.get(username=username)
        if user:
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
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


@login_required()
def new_job(request):
    if request.method == "POST":
        crawl_request = CrawlRequest(user=request.user)
        form = CrawlRequestForm(instance=crawl_request, data=request.POST)
        if form.is_valid():
            form.save()
            print("In new_job")
            api_new_job(request)
            return redirect('mainapp_home')
    else:
        form = CrawlRequestForm()
    return render(request, "main_app/new_job.html", {'form': form})


@login_required()
def api_new_job(request):
    logger.error(" === In API new job === ")
    if imageTag == '0':
        res = requests.request("GET", "http://crawler-manager:8002")
        print(res.content)
    else:
        command_status = os.system(getHelmCommand())
        logger.error("command status", command_status)
        print("queued")


def getHelmCommand():
    return f"""helm init --service-account tiller &&
      helm upgrade --install --wait \\
      --set-string image.tag='{imageTag}' \\
      --set-string params.url='https://www.google.com' \\
      'crawler-manager' ./cluster-templates/chart-manager"""

#@login_required()
#@api_view(['GET'])
#@permission_classes((IsAuthenticated, ))
def api_job_status(request):
    print("In api job status")
    response_data = {"Message" : "Status Received"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
def job_details(request, job_id):
    """
        Displays details for a specific job ID
    """
    logger.info('I am now in job DETAILS!')
    try:
        job = CrawlRequest.objects.get(pk=job_id)
    except CrawlRequest.DoesNotExist:
        raise Http404("Job does not exist.")
    return render(request, "main_app/job_details.html", {"job": job})


@login_required()
def profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('mainapp_home')
    else:
        form = ProfileForm(instance=profile)
    return render(request, "main_app/settings.html", {'form': form})
