from django.conf.urls import url

from . import views

app_name = 'wizard'
urlpatterns = [
    url(r'^$', views.home, name='home'),

    # Challenges
    url(r'^create$', views.ChallengeDescriptionCreate.as_view(), name='create'),
    url(r'^challenges/(?P<pk>\d+)$', views.ChallengeDescriptionDetail.as_view(), name='challenge'),

    # Challenges -> Config pages
    url(r'^challenges/(?P<pk>\d+)/data/$', views.ChallengeDataUpdate.as_view(), name='data'),
    url(r'^challenges/(?P<pk>\d+)/task/$', views.ChallengeDataUpdate.as_view(), name='task'),
    url(r'^challenges/(?P<pk>\d+)/metric/$', views.ChallengeDataUpdate.as_view(), name='metric'),
    url(r'^challenges/(?P<pk>\d+)/protocol/$',
        views.ChallengeDataUpdate.as_view(),
        name='protocol'),
    url(r'^challenges/(?P<pk>\d+)/baseline/$',
        views.ChallengeDataUpdate.as_view(),
        name='baseline'),
    url(r'^challenges/(?P<pk>\d+)/documentation/$',
        views.ChallengeDataUpdate.as_view(),
        name='documentation'),
    url(r'^challenges/(?P<pk>\d+)/rules/$',
        views.ChallengeDataUpdate.as_view(),
        name='rules'),
]
