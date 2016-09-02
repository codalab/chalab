from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import UpdateView

from .models import ProfileModel


class ProfileUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'user/editor.html'
    model = ProfileModel

    fields = ['first_name', 'last_name', 'affiliation', 'expertise']

    def get_object(self, queryset=None):
        u = self.request.user

        try:
            return u.profile
        except ProfileModel.DoesNotExist:
            ProfileModel.objects.create(user=u)
            return u.profile
