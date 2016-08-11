from django.shortcuts import render

render = render


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')
