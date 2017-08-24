from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.views.generic import UpdateView
from django.db.models import Q

from group.models import GroupModel
from .models import ProfileModel


class ProfileFormUpdate(ModelForm):

    class Meta:
        model = ProfileModel
        fields = ['first_name', 'last_name', 'affiliation', 'expertise', 'actual_group']

    def __init__(self, *args, **kwargs):
        super(ProfileFormUpdate, self).__init__(*args, **kwargs)
        if self.instance:
            if not self.instance.expertise == self.Meta.model.EX_NOVICE:
                u = self.instance.user
                self.fields['actual_group'].queryset = GroupModel.objects.filter(
                    (Q(public=True) | Q(admins=u) | Q(users=u))).order_by('-public', 'name')
                #  & Q(template__isnull=False)


class ProfileUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'user/editor.html'
    model = ProfileModel
    form_class = ProfileFormUpdate

    def get_object(self, queryset=None):
        u = self.request.user

        try:
            return u.profile
        except ProfileModel.DoesNotExist:
            ProfileModel.objects.create(user=u)
            return u.profile
