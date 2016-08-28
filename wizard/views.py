import logging
from collections import namedtuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from . import models
from .models import ChallengeModel, DatasetModel, TaskModel, MetricModel

log = logging.getLogger('wizard.views')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


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
    model = DatasetModel

    fields = ['name']
    current_flow = Flow.Data

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']

        context = super().get_context_data(**kwargs)
        context['challenge'] = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return challenge.dataset

    def dispatch(self, request, *args, **kwargs):
        if self.get_object(**kwargs) is None:
            return redirect('wizard:challenge:data.pick', pk=kwargs['pk'])
        else:
            return super().dispatch(request, *args, **kwargs)


class ChallengeTaskUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/task.html'
    model = TaskModel
    context_object_name = 'task'

    fields = ['name']
    current_flow = Flow.Task

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']

        context = super().get_context_data(**kwargs)
        context['challenge'] = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return challenge.task

    def dispatch(self, request, *args, **kwargs):
        if self.get_object(**kwargs) is None:
            return redirect('wizard:challenge:data.pick', pk=kwargs['pk'])
        else:
            return super().dispatch(request, *args, **kwargs)


def data_picker(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

    if c.dataset is not None:
        return redirect('wizard:challenge:data', pk=pk)

    if request.method == 'POST':
        k = request.POST['kind']
        assert k == 'public'

        ds = request.POST['metric']

        d = get_object_or_404(DatasetModel, is_public=True, id=ds)
        c.dataset = d

        t = get_object_or_404(TaskModel, dataset=d)
        c.task = t

        c.save()

        return redirect('wizard:challenge:metric', pk=pk)
    else:
        pds = models.DatasetModel.objects.all().filter(is_public=True)
        context = {'public_datasets': pds}
        return render(request, 'wizard/data/picker.html', context=context)


def metric_picker(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

    if c.metric is not None:
        return redirect('wizard:challenge:metric', pk=pk)

    if request.method == 'POST':
        k = request.POST['kind']
        assert k == 'public'

        mc = request.POST['metric']
        m = get_object_or_404(MetricModel, is_public=True, id=mc)
        c.metric = m
        c.save()
        return redirect('wizard:challenge:metric', pk=pk)
    else:
        public_metrics = MetricModel.objects.all().filter(is_public=True, is_ready=True)
        context = {'challenge': c, 'public_metrics': public_metrics}
        return render(request, 'wizard/metric/picker.html', context=context)


class ChallengeMetricUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/metric/detail.html'
    model = MetricModel
    context_object_name = 'metric'

    fields = ['name']
    current_flow = Flow.Metric

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']

        context = super().get_context_data(**kwargs)
        context['challenge'] = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        return challenge.metric

    def dispatch(self, request, *args, **kwargs):
        if self.get_object(**kwargs) is None:
            return redirect('wizard:challenge:metric.pick', pk=kwargs['pk'])
        else:
            return super().dispatch(request, *args, **kwargs)
