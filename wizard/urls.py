from django.conf.urls import url, include

from . import views

app_name = 'wizard'

challenge_wizard = [
    url(r'^data/$', views.ChallengeDataUpdate.as_view(), name='data'),
    url(r'^task/$', views.ChallengeDataUpdate.as_view(), name='task'),
    url(r'^metric/$', views.ChallengeDataUpdate.as_view(), name='metric'),
    url(r'^protocol/$', views.ChallengeDataUpdate.as_view(), name='protocol'),
    url(r'^baseline/$', views.ChallengeDataUpdate.as_view(), name='baseline'),
    url(r'^documentation/$', views.ChallengeDataUpdate.as_view(), name='documentation'),
    url(r'^rules/$', views.ChallengeDataUpdate.as_view(), name='rules'),
]

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^create$', views.ChallengeDescriptionCreate.as_view(), name='create'),
    url(r'^challenges/(?P<pk>\d+)$', views.ChallengeDescriptionDetail.as_view(), name='challenge'),
    url(r'^challenges/(?P<pk>\d+)/', include(challenge_wizard, namespace='challenge'))
]
