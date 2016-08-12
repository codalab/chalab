from django.conf import settings
from django.shortcuts import render, redirect


def home(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'landing/home.html')


def about(request):
    return render(request, 'landing/about.html')
