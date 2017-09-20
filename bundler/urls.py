from django.conf.urls import url

from . import views

app_name = 'bundler'

urlpatterns = [
    url(r'^status\.json$', views.status_json, name='status_json'),
    url(r'^logs$', views.logs, name='logs'),
    url(r'^build$', views.build, name='build'),
    url(r'^cancel$', views.cancel, name='cancel'),
    url(r'^download$', views.download, name='download'),
    url(r'^download/(?P<task_id>\d+).zip$', views.download_zip, name='download_zip'),
]
