from django.conf.urls import url, include

from . import views

app_name = 'wizard'

challenge_wizard = [
    url(r'^data/pick$', views.data_picker, name='data.pick'),
    url(r'^data/$', views.ChallengeDataUpdate.as_view(), name='data'),

    url(r'^task/$', views.ChallengeTaskUpdate.as_view(), name='task'),

    url(r'^metric/pick$', views.metric_picker, name='metric.pick'),
    url(r'^metric$', views.ChallengeMetricUpdate.as_view(), name='metric'),

    url(r'^protocol/$', views.ChallengeProtocolUpdate.as_view(), name='protocol'),

    url(r'^documentation/$', views.documentation, name='documentation'),
    url(r'^documentation/(?P<page_id>\d+)$', views.documentation_page, name='documentation.page'),

    url(r'^baseline/$', views.ChallengeDataUpdate.as_view(), name='baseline'),
    url(r'^rules/$', views.ChallengeDataUpdate.as_view(), name='rules'),
]

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^create$', views.ChallengeDescriptionCreate.as_view(), name='create'),
    url(r'^challenges/(?P<pk>\d+)$', views.ChallengeDescriptionDetail.as_view(), name='challenge'),
    url(r'^challenges/(?P<pk>\d+)/', include(challenge_wizard, namespace='challenge'))
]
