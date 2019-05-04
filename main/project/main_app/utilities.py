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

import requests, jwt, json, os, zipfile, time, sys

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
