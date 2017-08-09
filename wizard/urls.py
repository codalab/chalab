from django.conf.urls import url, include

from bundler import urls as bundler_urls
from . import views

app_name = 'wizard'

challenge_wizard = [
    url(r'^edit$', views.ChallengeDescriptionUpdate.as_view(), name='edit'),

    url(r'^data/pick$', views.data_picker, name='data.pick'),
    url(r'^data/$', views.ChallengeDataEdit.as_view(), name='data'),

    url(r'^split/$', views.ChallengeTaskUpdate.as_view(), name='split'),

    url(r'^metric$', views.metric, name='metric'),
    url(r'^metric/ajax/get_metric/$', views.get_metric, name='get_metric'),

    url(r'^protocol/$', views.ChallengeProtocolUpdate.as_view(), name='protocol'),

    url(r'^build/$', views.build_page, name='build'),

    url(r'^documentation/$', views.documentation, name='documentation'),
    url(r'^documentation/(?P<page_id>\d+)$', views.documentation_page, name='documentation.page'),
    url(r'^documentation/(?P<page_id>\d+)/edit$', views.DocumentationPageUpdate.as_view(),
        name='documentation.page.edit'),

    url(r'^baseline/$', views.ChallengeBaselineEdit.as_view(), name='baseline'),
    url(r'^rules/$', views.ChallengeDataEdit.as_view(), name='rules'),

    url(r'^bundler/', include(bundler_urls, namespace='bundler'))
]

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^create$', views.ChallengeDescriptionCreate.as_view(), name='create'),
    url(r'^create/group_(?P<group_id>\d+)$', views.challenge_create_from_group, name='create_from_group'),
    url(r'^challenges/(?P<pk>\d+)$', views.ChallengeDescriptionDetail.as_view(), name='challenge'),
    url(r'^challenges/(?P<pk>\d+)/', include(challenge_wizard, namespace='challenge'))
]
