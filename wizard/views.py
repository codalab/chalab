from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView

from .models import ChallengeModel


@login_required
def home(request):
    challenges = ChallengeModel.objects.filter(created_by=request.user)
    return render(request, 'wizard/home.html', context={'object_list': challenges})


class ChallengeDescriptionCreate(CreateView, LoginRequiredMixin):
    template_name = 'wizard/create.html'
    model = ChallengeModel
    fields = ['title', 'organization_name', 'description']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(ChallengeDescriptionCreate, self).form_valid(form)


class ChallengeDescriptionDetail(DetailView, LoginRequiredMixin):
    template_name = 'wizard/detail.html'
    model = ChallengeModel
    fields = ['title', 'organization_name', 'description']
