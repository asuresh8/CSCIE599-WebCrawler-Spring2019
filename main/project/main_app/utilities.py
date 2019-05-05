from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from main_app.models import CrawlRequest
from rest_framework import status
from django.conf import settings
from google.cloud import storage

import requests, jwt, json, os, time, sys, uuid

# import the logging library
import logging
logging.basicConfig(level=logging.INFO)
# Get an instance of a logger
logger = logging.getLogger(__name__)


def store_data_in_gcs(request):
    myfile = request.FILES['myfile']
    filename = 'tmp_file'
    data = myfile.read()
    with open(filename, 'wb') as f:
        f.write(data)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ['GCS_BUCKET'])
    key = 'crawl_models/{}'.format(str(uuid.uuid4()))
    blob = bucket.blob(key)
    blob.upload_from_filename(filename)
    blob.make_public()
    os.remove(filename)
    return blob.public_url


def get_google_cloud_manifest_contents(manifest):
    client = storage.Client()
    bucket = client.get_bucket(os.environ['GCS_BUCKET'])
    blob = storage.Blob(manifest, bucket)
    content = blob.download_as_string()
    return content

def get_google_cloud_crawl_pages(manifest):
    client = storage.Client()
    bucket = client.get_bucket(os.environ['GCS_BUCKET'])
    content = {}
    links = manifest.decode().split('\n')
    for link in links:
        logger.info('link: %s', link)
        link_arr = link.split(',')
        if (len(link_arr) <= 1):
            continue
        url = link_arr[0]
        file_location = link_arr[1]
        logger.info('url: %s, file_location: %s', url, file_location)
        if (url.endswith('.docx') or url.endswith('.pdf')):
            content[url] = file_location
        else:
            file_location_arr = file_location.split('/')
            directory = file_location_arr[-2].strip()
            file_name = file_location_arr[-1].strip()
            file_name = directory + "/" + file_name
            logger.info('file_name: %s', file_name)
            blob = storage.Blob(file_name, bucket)
            content[url] = blob.download_as_string()
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
                        job.docs_uploaded = payload["uploaded_pages"]
                        job.save()
            except Exception as ex:
                logger.info('Exception in getting status')


def check_user_password(current_password, incoming_password):
    salt = current_password.split('$')[2]
    hashed_password = make_password(incoming_password, salt)
    return current_password == hashed_password
