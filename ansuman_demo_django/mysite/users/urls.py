from django.conf.urls import url, include
from django.urls import path
from . import views
#from .views import CreateUserAPIView

urlpatterns = [
    #url(r'^create/$', include(views.CreateUserAPIView.as_view())),
    path('create', views.CreateUserAPIView.as_view(), name='apiview'),
    path('obtain_token', views.authenticate_user, name='apiview2'),
    path('update', views.UserRetrieveUpdateAPIView.as_view(), name='apiview3'),
]
