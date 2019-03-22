from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from .views import home

urlpatterns = [
    url(r'home$', home, name="mainapp_home"),
    url(r'login$', LoginView.as_view(template_name="main_app/login_form.html"), name="mainapp_login"),
    url(r'logout$', LogoutView.as_view(), name="mainapp_logout"),
]


