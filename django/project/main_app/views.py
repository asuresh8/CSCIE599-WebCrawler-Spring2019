from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import CrawlRequest
from .forms import CrawlRequestForm


@login_required()
def home(request):
    crawl_request = CrawlRequest(user=request.user)
    form = CrawlRequestForm(instance=crawl_request)
    return render(request, "main_app/home.html", {'form': form})

'''
@login_required()
def new_job(request):
    if request.method == "POST":
        crawl_request = CrawlRequest(user=request.user)
        form = CrawlRequestForm(instance=crawl_request, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('mainapp_home')
    else:
        form = CrawlRequestForm()
    return render(request, "mainapp/new_job.html", {'form': form})
'''
