from django.shortcuts import render, redirect

def welcome(request):
    if request.user.is_authenticated:
        return redirect('mainapp_home')
    else:
        return render(request, 'webcrawler/welcome.html')