from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    url(r'home$', views.home, name="mainapp_home"),
    url(r'new_job$', views.new_job, name="mainapp_new_job"),
    path(r'job/<int:job_id>', views.job_details, name="mainapp_jobdetails"),
    path(r'contents/<int:job_id>', views.crawl_contents, name="mainapp_crawlcontents"),
    url(r'login$', LoginView.as_view(template_name="main_app/login_form.html"), name="mainapp_login"),
    url(r'logout$', LogoutView.as_view(), name="mainapp_logout"),
    url(r'api/register_crawler_manager$', views.register_crawler_manager, name="api_register_crawler_manager"),
    url(r'api/crawl_complete$', views.complete_crawl, name="api_complete_crawl"),
    url(r'api/ping$', views.api_ping, name="api_ping"),
    url(r'ml_models$', views.ml_model, name="mainapp_mlmodel"),
]
