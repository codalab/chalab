from django.conf.urls import url

from . import views

app_name = 'bundler'

urlpatterns = [
    url(r'^logs$', views.logs, name='logs'),
    url(r'^build$', views.build, name='build'),
    url(r'^download$', views.download, name='download'),
]
