from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    url(r'home$', views.home, name="mainapp_home"),
    url(r'new_job$', views.new_job, name="mainapp_new_job"),
    url(r'api/new_job', views.api_new_job, name="api_new_job"),
    url(r'settings$', views.settings, name="mainapp_settings"),
    path(r'job/<int:job_id>', views.job_details, name="mainapp_jobdetails"),
    url(r'login$', LoginView.as_view(template_name="main_app/login_form.html"), name="mainapp_login"),
    url(r'logout$', LogoutView.as_view(), name="mainapp_logout"),
]
