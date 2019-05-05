from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User

from .models import CrawlRequest, Profile, MlModel
from .forms import CrawlRequestForm, ProfileForm, MlModelForm
from .utilities import store_data_in_gcs
from .utilities import get_google_cloud_manifest_contents
from .utilities import update_job_status

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.utils import jwt_payload_handler
from django.conf import settings

from django.http import JsonResponse
from django.http import HttpRequest
from django.http import HttpResponse
from io import BytesIO
from google.cloud import storage

import requests, jwt, json, os, zipfile, time, sys

# import the logging library
import logging
logging.basicConfig(level=logging.INFO)
# Get an instance of a logger
logger = logging.getLogger(__name__)
# set logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)
#logger.setLevel(20)

NAMESPACE = os.environ.get('NAMESPACE', 'default')
IMAGE_TAG = os.environ.get('IMAGE_TAG', '0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
CRAWLER_MANAGER_USER_PREFIX = 'admin'
NUM_CRAWL_PAGES_LIMIT = 10
CRAWL_LIBRARY = 'selenium'

# store the release timestamps here, like a job id meanwhile
releases = []
@login_required()
def home(request):
    user = request.user
    crawl_request = CrawlRequest(user=user)
    form = CrawlRequestForm(instance=crawl_request)
    jobs = CrawlRequest.objects.filter(user=user)
    for job in jobs:
        update_job_status(job)
    return render(request, "main_app/home.html", {'form': form, 'jobs': jobs})


@login_required()
def ml_model(request):
    user = request.user
    ml_model_instance = MlModel(user=user)
    if request.method == "POST":
        form = MlModelForm(instance=ml_model_instance, data=request.POST)
        if form.is_valid():
            form_model = form.save(commit=False)
            form_model.user = request.user
            form_model.save() 
            s3_url = store_data_in_gcs(request)
            form_model.s3_location = s3_url
            logger.info("Cloud_Url: {}".format(s3_url))
            form_model.save()

    form = MlModelForm(instance=ml_model_instance)
    models = MlModel.objects.filter(user=user)
    return render(request, "main_app/ml_model.html", {'form': form, 'models': models})


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


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def register_crawler_manager(request):
    logger.info("In Register-Crawl")
    id = request.data['job_id']
    logger.info('JobID main: %s', id)
    endpoint = request.data['endpoint']
    logger.info("In Register-Crawl, jobid: %s, endpoint: %s",id,endpoint)
    job = CrawlRequest.objects.get(pk=id)
    job.crawler_manager_endpoint = endpoint
    job.save()
    model_url = ""
    if (job.model != None):
        models = MlModel.objects.filter(name=job.model.name)
        if (len(models) > 0):
            model_url = models[0].s3_location
    logger.info('Model url: %s', model_url)
    payload = {
        'job_id': id,
        'domain': job.domain.split(';'),
        'urls': job.urls.split(';'),
        'docs_all': job.docs_all,
        'docs_html': job.docs_html,
        'docs_pdf': job.docs_pdf,
        'docs_docx': job.docs_docx,
        'num_crawlers': job.num_crawlers,
        'model_location': model_url,
        'labels': job.model_labels.split(';'),
        'num_crawl_pages_limit' : NUM_CRAWL_PAGES_LIMIT,
        'crawl_library' : CRAWL_LIBRARY
    }
    return JsonResponse(payload)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def complete_crawl(request):
    id = request.data['job_id']
    manifest = request.data['manifest']
    resources_count = request.data['resources_count']
    downloaded_pages = request.data['downloaded_pages']

    logger.info("In Crawl-Complete")
    logger.info('Crawl-Complete id - %s, manifest - %s, pages - %d', id, manifest, downloaded_pages)
    crawl_request = CrawlRequest.objects.get(pk=id)
    crawl_request.s3_location = manifest
    crawl_request.manifest = manifest
    crawl_request.status = 3
    crawl_request.docs_collected = resources_count
    crawl_request.save()
    data = {"CrawlComplete" : "done"}
    requests.post(os.path.join(crawl_request.crawler_manager_endpoint, 'kill'), json={})
    user = User.objects.get(username=(CRAWLER_MANAGER_USER_PREFIX + str(id)))
    user.delete()
    return JsonResponse(data)


def get_manager_token(jobId):
    username = CRAWLER_MANAGER_USER_PREFIX + str(jobId)
    email = CRAWLER_MANAGER_USER_PREFIX + str(jobId) + '@' + CRAWLER_MANAGER_USER_PREFIX + '.com'
    password = username
    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password)
    payload = jwt_payload_handler(user)
    token = jwt.encode(payload, settings.SECRET_KEY)
    return token


@login_required()
def new_job(request):
    if request.method == "POST":
        crawl_request = CrawlRequest(user=request.user)
        form = CrawlRequestForm(instance=crawl_request, data=request.POST)
        if form.is_valid():
            form.save()
            logger.info('NewJob created: %s', crawl_request.id)
            logger.info('Received urls: %s', crawl_request.urls)
            launch_crawler_manager(crawl_request, crawl_request.id)
            crawl_request.status = 2
            crawl_request.save()
            return redirect('mainapp_home')
    else:
        form = CrawlRequestForm()
    return render(request, "main_app/new_job.html", {'form': form})


def launch_crawler_manager(request, jobId):
    if ENVIRONMENT == 'local' or ENVIRONMENT == 'test':
        # Running in docker compose,
        print("Looks like this is not running on a Kuberenetes cluster, ")
        token = get_manager_token(jobId).decode("utf-8")
        requests.post("http://crawler-manager:8002/crawl", json={"job_id" : jobId, "token" : token})
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
    token = get_manager_token(request.id).decode("utf-8")

    return f"""helm init --service-account tiller && \\
      helm upgrade --install --wait \\
      --set-string image.tag='{IMAGE_TAG}' \\
      --set-string params.job_id='{request.id}' \\
      --set-string params.releaseDate='{releaseDate}' \\
      --set-string params.authToken='{token}' \\
      --set-string params.domain='{request.domain}' \\
      --set-string params.initialUrls='{request.urls}' \\
      --set-string application.namespace='{NAMESPACE}' \\
      \"crawler-manager-{releaseDate}\" ./cluster-templates/chart-manager"""


@login_required()
def job_details(request, job_id):
    """
        Displays details for a specific job ID
    """
    try:
        job = CrawlRequest.objects.get(pk=job_id)
        update_job_status(job)
    except CrawlRequest.DoesNotExist:
        raise Http404("Job does not exist.")
    return render(request, "main_app/job_details.html", {"job": job})


@login_required()
def crawl_contents(request, job_id):
    print(job_id)
    try:
        job = CrawlRequest.objects.get(pk=job_id)
    except CrawlRequest.DoesNotExist:
        raise Http404("Job does not exist.")
    manifest = job.manifest.split('/')[-1]
    logger.info('Manifest: %s', manifest)
    manifest_file = "manifest.json"
    buffer = BytesIO()
    z= zipfile.ZipFile(buffer, "w")

    # Read manifest content from cloud
    content = get_google_cloud_manifest_contents(manifest)
    with open(manifest_file, 'wb') as f:
        f.write(content)
    z.write(manifest_file)
    z.close()
    os.remove(manifest_file)

    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=manifest.zip'
    return response
