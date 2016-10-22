import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from chalab import errors
from . import models, flow
from .flow import FlowOperationMixin
from .forms import ProtocolForm, DataUpdateAndUploadForm
from .models import ChallengeModel, DatasetModel, TaskModel, MetricModel, ProtocolModel, \
    DocumentationModel, DocumentationPageModel
from .models import challenge_to_mappings, challenge_to_mappings_doc

log = logging.getLogger('wizard.views')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


@login_required
def home(request):
    challenges = ChallengeModel.objects.filter(created_by=request.user)
    return render(request, 'wizard/home.html', context={'object_list': challenges})


class ChallengeDescriptionCreate(CreateView, LoginRequiredMixin):
    template_name = 'wizard/challenge/create.html'
    model = ChallengeModel
    fields = ['title', 'organization_name', 'description', 'logo']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        r = super(ChallengeDescriptionCreate, self).form_valid(form)
        self.object.generate_default_phases()
        return r


class ChallengeDescriptionUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'wizard/challenge/editor.html'
    model = ChallengeModel

    fields = ChallengeDescriptionCreate.fields


class ChallengeDescriptionDetail(FlowOperationMixin, DetailView, LoginRequiredMixin):
    template_name = 'wizard/challenge/detail.html'
    model = ChallengeModel
    context_object_name = 'challenge'
    fields = ['title', 'organization_name', 'description', 'logo']

    def get_context_data(self, challenge=None, **kwargs):
        context = super().get_context_data(challenge=self.object, **kwargs)

        try:
            from bundler.models import BundleTaskModel
            context['bundler'] = BundleTaskModel.objects.filter(challenge=self.object).first()
        except ObjectDoesNotExist:
            pass

        return context


class ChallengeDataEdit(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/data/editor.html'
    model = DatasetModel
    form_class = DataUpdateAndUploadForm

    current_flow = flow.DataFlowItem

    @property
    def disabled(self):
        return self.object.owner != self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        for f in form.fields.keys():
            form.fields[f].disabled = self.disabled
        form.disabled = self.disabled

        return form

    def form_valid(self, form):
        if self.disabled:
            raise errors.HTTP400Exception('wizard/challenge/error.html',
                                          "Forbidden edit on a dataset",
                                          """You can't edit a dataset that you do not own.""")
        else:

            if not self.disabled and self.request.FILES:
                u = self.request.FILES.get('automl_upload', None)
                self.object.update_from_chalearn(u)

            r = super().form_valid(form)

            return r

    def get_success_url(self):
        return reverse('wizard:challenge:data', kwargs={'pk': self.pk})

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        context['is_ready'] = self.object.is_ready
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']
        self.pk = pk

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

    fields = ['name', 'train_ratio', 'test_ratio', 'valid_ratio']
    current_flow = flow.TaskFlowItem

    @property
    def disabled(self):
        return self.object.owner != self.request.user

    def get_success_url(self):
        return reverse('wizard:challenge:task',
                       kwargs={'pk': self.kwargs['pk']})

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        for f in form.fields.keys():
            form.fields[f].disabled = self.disabled
        form.disabled = self.disabled

        return form

    def form_valid(self, form):
        if self.disabled:
            raise errors.HTTP400Exception('wizard/challenge/error.html',
                                          "Forbidden edit on a dataset",
                                          """You can't edit a dataset that you do not own.""")
        else:
            r = super().form_valid(form)
            return r

    def get_challenge(self, pk=None, **_):
        pk = self.kwargs['pk']
        return ChallengeModel.objects.get(id=pk, created_by=self.request.user)

    def get_object(self, **kwargs):
        o = self.get_challenge(**kwargs).task
        self.object = o
        return o

    def get_context_data(self, **kwargs):
        c = self.get_challenge(**kwargs)
        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        context['is_ready'] = self.object.is_ready
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.get_object(**kwargs) is None:
            challenge = self.get_challenge(**kwargs)

            if challenge.dataset is None:
                return redirect('wizard:challenge:data.pick', pk=kwargs['pk'])
            else:
                challenge.create_initial_task()
                return redirect('wizard:challenge:task', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


def data_picker(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

    if request.method == 'POST':
        k = request.POST['kind']

        if k == 'public':
            ds = request.POST['dataset']

            d = get_object_or_404(DatasetModel, is_public=True, id=ds)
            c.dataset = d

            t = get_object_or_404(TaskModel, dataset=d)
            c.task = t

            c.save()
        elif k == 'create':
            name = request.POST['name']
            c.dataset = DatasetModel.create(name, request.user)
            c.save()
        else:
            assert False, "unsupported k=%s" % k

        return redirect('wizard:challenge:data', pk=pk)
    else:
        pds = models.DatasetModel.objects.all().filter(is_public=True)
        context = {'public_datasets': pds,
                   'challenge': c,
                   'flow': flow.Flow(flow.DataFlowItem, c)}
        return render(request, 'wizard/data/picker.html', context=context)


def metric_picker(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

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
        context = {'challenge': c, 'public_metrics': public_metrics,
                   'flow': flow.Flow(flow.MetricFlowItem, c)}
        return render(request, 'wizard/metric/picker.html', context=context)


class ChallengeMetricUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/metric/editor.html'
    model = MetricModel
    context_object_name = 'metric'

    fields = ['name']
    current_flow = flow.MetricFlowItem

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        for f in self.fields:
            form.fields[f].disabled = True
        form.disabled = True

        return form

    def form_valid(self, form):
        raise errors.HTTP400Exception('wizard/challenge/error.html',
                                      "Forbidden edit on a metric",
                                      """You can't edit a metric that you do not own.""")

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
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


class ChallengeProtocolUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/protocol.html'
    model = ProtocolModel
    form_class = ProtocolForm
    context_object_name = 'protocol'

    # Hacky way to pass back the challenge from get_object to get_success_url
    _runtime_challenge = None

    current_flow = flow.ProtocolFlowItem

    def get_success_url(self):
        return reverse('wizard:challenge:protocol', kwargs={'pk': self._runtime_challenge.pk})

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        self._runtime_challenge = challenge

        protocol = challenge.protocol

        if protocol is None:
            protocol = ProtocolModel.objects.create()
            challenge.protocol = protocol
            challenge.save()

        return protocol


def documentation(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)
    doc = c.documentation

    if doc is None:
        doc = DocumentationModel.create()
        c.documentation = doc
        c.save()

    current = 'overview'
    current_page = doc.pages.filter(name=current).first()

    context = {'challenge': c, 'doc': doc, 'pages': doc.pages,
               'current': 'overview', 'current_page': current_page,
               'flow': flow.Flow(flow.DocumentationFlowItem, c)}

    return render(request, "wizard/documentation/detail.html", context=context)


def documentation_page(request, pk, page_id):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)
    p = get_object_or_404(DocumentationPageModel, documentation=c.documentation, id=page_id)
    doc = c.documentation

    context = {'challenge': c, 'doc': doc, 'pages': doc.pages,
               'current': p.name, 'current_page': p,
               'flow': flow.Flow(flow.DocumentationFlowItem, c)}

    return render(request, "wizard/documentation/detail.html", context=context)


class DocumentationPageUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/documentation/editor.html'
    model = DocumentationPageModel
    context_object_name = 'page'

    # Hacky way to pass back the challenge from get_object to get_success_url
    _runtime_challenge = None

    fields = ['name', 'content']

    current_flow = flow.DocumentationFlowItem

    def get_success_url(self):
        return reverse('wizard:challenge:documentation.page',
                       kwargs={'pk': self._runtime_challenge.pk,
                               'page_id': self.object.pk})

    def mappings_all(self):
        return challenge_to_mappings(self._runtime_challenge)

    def mappings_doc(self):
        return challenge_to_mappings_doc(self._runtime_challenge)

    def form_valid(self, form):
        r = super().form_valid(form)

        page = self.object

        mapping = self.mappings_all()
        page.render(mapping)
        return r

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        context['template_doc'] = self.mappings_doc()
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']
        page_id = self.kwargs['page_id']

        challenge = ChallengeModel.objects.get(id=pk, created_by=self.request.user)
        page = get_object_or_404(DocumentationPageModel, id=page_id,
                                 documentation=challenge.documentation)

        self._runtime_challenge = challenge

        return page
