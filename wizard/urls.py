from django.conf.urls import url

from . import views

app_name = 'wizard'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^create$', views.ChallengeDescriptionCreate.as_view(), name='create'),
    url(r'^challenges/(?P<pk>\d+)$', views.ChallengeDescriptionDetail.as_view(), name='challenge')
]
