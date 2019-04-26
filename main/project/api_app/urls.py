from django.conf.urls import url
from django.urls import path
from api_app import views

urlpatterns = [
    url(r'authenticate_user$', views.authenticate_user, name="authenticate_user"),
    url(r'api/create_crawl', views.api_create_crawl, name="api_create_crawl"),
    url(r'api/crawl_contents', views.api_crawl_contents, name="api_crawl_contents"),
    url(r'api/get_job_status', views.get_api_job_status, name="api_job_status")
]
