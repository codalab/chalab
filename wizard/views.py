import logging
from collections import namedtuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

log = logging.getLogger('wizard.views')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

from .models import ChallengeModel, ChallengeDataModel


class Flow(object):
    Data = 'Data'
    Task = 'Task'
    Metric = 'Metric'
    Protocol = 'Protocol'
    Baseline = 'Baseline'
    Documentation = 'Documentation'
    Rules = 'Rules'

    FlowItem = namedtuple('FlowItem', ['slug', 'name', 'active', 'url', 'descr_template'])

    FLOW = [Data, Task, Metric, Protocol, Baseline, Documentation, Rules]

    @classmethod
    def list(cls, current):
        return [cls.FlowItem(slug=x.lower(),
                             name=x, active=current == x, url='wizard:challenge:' + x.lower(),
                             descr_template='wizard/flow/descr/_%s.html' % x.lower())
                for x in cls.FLOW]


class FlowOperationMixin:
    current_flow = None

    def get_context_data(self, **kwargs):
        context = super(FlowOperationMixin, self).get_context_data(**kwargs)
        context['flow'] = Flow.list(self.current_flow)
        return context


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


class ChallengeDescriptionDetail(FlowOperationMixin, DetailView, LoginRequiredMixin):
    template_name = 'wizard/detail.html'
    model = ChallengeModel
    fields = ['title', 'organization_name', 'description']


class ChallengeDataUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/data/detail.html'
    model = ChallengeDataModel

    fields = ['name', 'kind']
    current_flow = Flow.Data

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        if challenge.data.count() == 0:
            return ChallengeDataModel.objects.create(challenge=challenge)
        else:
            return challenge.data.first()
