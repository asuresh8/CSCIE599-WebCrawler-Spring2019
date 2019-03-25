from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from .views import home, new_job, settings, api_new_job

urlpatterns = [
    url(r'home$', home, name="mainapp_home"),
    url(r'new_job$', new_job, name="mainapp_new_job"),
    url(r'api/new_job', api_new_job, name="api_new_job"),
    url(r'settings$', settings, name="mainapp_settings"),
    url(r'login$', LoginView.as_view(template_name="main_app/login_form.html"), name="mainapp_login"),
    url(r'logout$', LogoutView.as_view(), name="mainapp_logout"),
]
