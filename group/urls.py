from django.conf.urls import url

from group import views

app_name = 'group'

urlpatterns = [
    url(r'^(edit)?$', views.redirect_groups, name='group'),
    url(r'^create$', views.create_new_group, name='create'),
    url(r'^edit/(?P<group_id>\d+)$', views.groups, name='edit'),
    url(r'^ajax/(?P<group_id>\d+)/add_user/$', views.add_user_to_group, name='add_user'),
]
