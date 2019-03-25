from django.contrib import admin

from .models import CrawlRequest, Profile

admin.site.register(CrawlRequest)
admin.site.register(Profile)
