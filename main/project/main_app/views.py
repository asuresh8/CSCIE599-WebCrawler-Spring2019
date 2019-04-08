from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import CrawlRequest, Profile
from .forms import CrawlRequestForm, ProfileForm

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

import requests, jwt, json, os, zipfile, time, sys

# import the logging library
import logging
logging.basicConfig(level=logging.INFO)
# Get an instance of a logger
logger = logging.getLogger(__name__)
# set logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)
#logger.setLevel(20)

# when the container is running in docker compose, set IMAGE_TAG = 0
# when running on Kubernetes, it is the Pipeline Id, which is used for naming the Docker images in the registry.
IMAGE_TAG = os.environ.get('IMAGE_TAG', '0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')

# store the release timestamps here, like a job id meanwhile
releases = []
JOB_ID = "1"
@login_required()
def home(request):
    user = request.user
    crawl_request = CrawlRequest(user=user)
    form = CrawlRequestForm(instance=crawl_request)
    jobs = CrawlRequest.objects.filter(user=user)
    return render(request, "main_app/home.html", {'form': form, 'jobs': jobs})

@api_view(['GET'])
@permission_classes([AllowAny, ])
def api_ping(request):
    release_date_param = request.GET.get('releaseDate', 'None')
    data = {}
    data['pong'] = f"pang-{release_date_param}"

    requestUrl = "http://crawler-manager:8002"
    if ENVIRONMENT != 'local':
        requestUrl = f"http://crawler-manager-service-{release_date_param}.default/"

    managerPing = crawler_manager_ping(requestUrl)
    logger.info('managerPing - %s', managerPing)

    return JsonResponse(data)

def crawler_manager_ping(requestUrl):
    try:
        manager_url = os.path.join(requestUrl, 'ping')
        logger.info('manager_url === %s', manager_url)
        r = requests.get(manager_url)
        return r.text
    except requests.RequestException as rex:
        return "request exception"
    except requests.HTTPException as htex:
        return "http exception"
    except Exception as ex:
        return "general exception"

# TODO: After implementing jwt tokens, we need to validate this based on the token the crawler manager is passing back
@api_view(['POST'])
@permission_classes([AllowAny, ])
def register_crawler_manager(request):
    logger.info("In Register-Crawl")
    id = request.data['job_id']
    if ENVIRONMENT == 'local':
        id = JOB_ID
    logger.info('JobID main: %s', id)
    endpoint = request.data['endpoint']
    logger.info("In Register-Crawl, jobid: %s, endpoint: %s",id,endpoint)
    job = CrawlRequest.objects.get(pk=id)
    job.crawler_manager_endpoint = endpoint
    job.save()
    return JsonResponse({"JOB_ID":id})

@api_view(['POST'])
@permission_classes([AllowAny, ])
def complete_crawl(request):
    id = request.data['job_id']
    manifest = request.data['manifest']
    logger.info("In Crawl-Complete")
    logger.info('Crawl-Complete id - %s, manifest - %s', id, manifest)
    crawl_request = CrawlRequest.objects.get(pk=id)
    crawl_request.s3_location = manifest
    crawl_request.status = 3
    crawl_request.save()
    data = {"CrawlComplete" : "done"}
    requests.post(os.path.join(crawl_request.crawler_manager_endpoint, 'kill'), json={})
    return JsonResponse(data)


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
    global JOB_ID
    if request.method == "POST":
        crawl_request = CrawlRequest(user=request.user)
        form = CrawlRequestForm(instance=crawl_request, data=request.POST)
        if form.is_valid():
            form.save()
            """
            print("In new_job")
            payload = {}
            payload['jobId'] = crawl_request.id
            payload['url'] = crawl_request.domain
            launch_crawler_manager(payload)
            """
            JOB_ID = crawl_request.id
            logger.info('NewJob created: %s', crawl_request.id)
            api_new_job(crawl_request)
            return redirect('mainapp_home')
    else:
        form = CrawlRequestForm()
    return render(request, "main_app/new_job.html", {'form': form})


@login_required()
def api_new_job(request):
    #logger.error("In API new job")
    if ENVIRONMENT == 'local':
        # Running in docker compose,
        print("Looks like this is not running on a Kuberenetes cluster, ")
        requests.post("http://crawler-manager:8002/crawl")
    else:
        # If ENVIRONMENT is prod, it means it is running in the Kubernetes Cluster
        # Use the Helm command to trigger a new Crawler Manager Instance
        command_status = os.system(getHelmCommand(request))

        print("queued")


# TODO: this function should take the Job ID as a parameter.
# That will be injected into the new Crawler manger Pod
def getHelmCommand(request):
    releaseDate = int(time.time())
    releases.append(releaseDate)

    return f"""helm init --service-account tiller && \\
      helm upgrade --install --wait \\
      --set-string image.tag='{IMAGE_TAG}' \\
      --set-string params.job_id='{request.id}' \\
      --set-string params.releaseDate='{releaseDate}' \\
      \"crawler-manager-{releaseDate}\" ./cluster-templates/chart-manager"""



def launch_crawler_manager(payload):
    print ("In api new job")
    payload = {"jobId" : payload['jobId']}
    res = requests.get("http://localhost:8004/crawl", params=payload)
    print(res.content)

#@login_required()
@api_view(['GET'])
#@permission_classes((IsAuthenticated, ))
def api_job_status(request):
    """
    jobId = request.query_params.get('jobId')
    job = CrawlRequest.objects.get(pk=jobId)
    job.status = 3
    job.docs_collected = request.query_params.get('numUrls')
    job.save()
    """
    response_data = {"Message" : "Status Received"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
def job_details(request, job_id):
    """
        Displays details for a specific job ID
    """
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

@login_required()
def crawl_contents(request, job_id):
    print(job_id)
    try:
        job = CrawlRequest.objects.get(pk=job_id)
    except CrawlRequest.DoesNotExist:
        raise Http404("Job does not exist.")
    current_file = "idletest"
    buffer = BytesIO()
    z= zipfile.ZipFile( buffer, "w" )
    open(current_file, 'w').write("Ansuman")
    z.write( current_file )
    z.close()
    os.remove(current_file)
    """
    byte = BytesIO()
    zf = zipfile.ZipFile(byte, "w")
    zipped_files = []
    """
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=myfile.zip'
    return response
