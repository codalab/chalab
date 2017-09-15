import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from bundler.models import BundleTaskModel
from chalab import errors
from group.models import GroupModel
from user.models import ProfileModel
from . import models, flow
from .flow import FlowOperationMixin
from .forms import ProtocolForm, DataUpdateAndUploadForm, DataUpdateForm
from .models import ChallengeModel, DatasetModel, TaskModel, MetricModel, \
    ProtocolModel, \
    DocumentationModel, DocumentationPageModel, BaselineModel, \
    InvalidAutomlFormatException
from .models import challenge_to_mappings, challenge_to_mappings_doc

log = logging.getLogger('wizard.views')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

AUTOML_ERROR = \
    """<p>
Processing of the archive failed because of:
<pre>
%s
</pre>
Expected a directory structure with dataname/ at the top, 
did you forget the put all your data files in a directory before zipping?
</p>

<p>
The expected automl archive is of the form:
<pre>
DataName/
    DataName.data
    DataName.solution
</pre>

Or, if data are already splitted, the zip file must contain:
<pre>DataName/
    DataName_train.data
    DataName_train.solution
    DataName_valid.data
    DataName_valid.solution
    DataName_test.data
    DataName_test.solution</pre>

You can check the archive actual content using <code>`unzip -l ./my_archive.zip'</code>.
<p>"""


@login_required
def home(request):
    u = request.user
    bundle_list = list()

    challenges = ChallengeModel.objects.filter(created_by=u).order_by('-created_at')

    for challenge in challenges:
        try:
            bundles = BundleTaskModel.objects.filter(challenge=challenge)  # This is gross...
            if len(bundles) > 1:
                bundle_list.append(bundles.last())
            elif len(bundles) == 1:
                bundle_list.append(bundles)
            else:
                print("No bundles.")

        except ObjectDoesNotExist:
            print("No bundletask for challenge {}".format(challenge.pk))

    profile, created = ProfileModel.objects.get_or_create(user=u)

    context = {
        'object_list': challenges,
        'bundle_list': bundle_list,
        'actual_group': profile.actual_group,
        }

    return render(request, 'wizard/home.html', context=context)


@login_required
def delete_challenge(request, pk):
    u = request.user
    c = get_object_or_404(ChallengeModel, id=pk, created_by=u)

    if request.method == 'POST':
        if request.POST['button'] == 'delete':
            c.delete()
        return home(request)
    else:
        context = {
            'challenge': c,
            'groups': [g.name for g in GroupModel.objects.filter(template=c)]
        }
        return render(request, 'wizard/challenge/delete.html', context=context)


class ChallengeDescriptionCreate(CreateView, LoginRequiredMixin):
    template_name = 'wizard/challenge/create.html'
    model = ChallengeModel
    fields = ['title', 'organization_name', 'description', 'logo']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        r = super(ChallengeDescriptionCreate, self).form_valid(form)
        self.object.generate_default_phases()
        return r


@login_required
def challenge_create_from_group(request, group_id):
    group = get_object_or_404(GroupModel, id=group_id)
    template = group.template

    if template is None:
        template = ChallengeModel(title='New Challenge')
    else:
        template.id = None

    # Initialisation
    template.created_by = request.user
    template.origin_group = group

    # Deep copy
    data = None
    if template.dataset is not None:
        data = template.dataset
        data.id = None
        if not data.input is None:
            data.input = data.input.deep_copy()
        if not data.target is None:
            data.target = data.target.deep_copy()
        data.save()
        template.dataset = data

    if template.task is not None:
        task = template.task.deep_copy()
        task.dataset = data
        task.save()
        template.task = task

    if template.metric is not None:
        met = template.metric
        met.id = None
        met.save()
        template.metric = met

    if template.protocol is not None:
        pro = template.protocol
        pro.id = None
        pro.save()
        template.protocol = pro

    if template.baseline is not None:
        from django.core.files import File
        base = BaselineModel()
        if bool(template.baseline.submission):
            base.submission=File(open(template.baseline.submission.path, 'rb'))
        base.save()
        template.baseline = base

    if template.documentation is not None:
        doc = template.documentation

        pages = DocumentationPageModel.objects.filter(documentation=doc)

        doc.id = None
        doc.save()

        for page in pages:
            page.id = None
            page.documentation = doc
            page.save()

        template.documentation = doc

    template.save()

    return redirect(template.get_absolute_url())


class ChallengeDescriptionUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'wizard/challenge/editor.html'
    model = ChallengeModel

    fields = ChallengeDescriptionCreate.fields


class ChallengeDescriptionDetail(FlowOperationMixin, DetailView,
                                 LoginRequiredMixin):
    template_name = 'wizard/challenge/detail.html'
    model = ChallengeModel
    context_object_name = 'challenge'
    fields = ['title', 'organization_name', 'description', 'logo']

    def get_context_data(self, challenge=None, **kwargs):
        context = super().get_context_data(challenge=self.object, **kwargs)

        try:
            context['bundler'] = BundleTaskModel.objects.filter(
                challenge=self.object).first()
        except ObjectDoesNotExist:
            pass

        return context


class ChallengeBaselineEdit(FlowOperationMixin, LoginRequiredMixin,
                            UpdateView):
    template_name = 'wizard/baseline.html'
    model = BaselineModel
    fields = ['submission']

    current_flow = flow.BaselineFlowItem

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        context['is_ready'] = self.object.is_ready
        return context

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('wizard:challenge:baseline', kwargs={'pk': pk})

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk,
                                               created_by=self.request.user)
        self._runtime_challenge = challenge

        baseline = challenge.baseline

        if baseline is None:
            baseline = BaselineModel.objects.create()
            challenge.baseline = baseline
            challenge.save()

        return baseline


class ChallengeDataEdit(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/data/editor.html'
    model = DatasetModel
    form_class = DataUpdateAndUploadForm

    current_flow = flow.DataFlowItem

    @property
    def disabled(self):
        dataset_users = len(ChallengeModel.objects.filter(dataset=self.object))
        return self.object.owner != self.request.user or (
            self.object.is_ready and dataset_users > 1)

    def get_form(self, form_class=None):
        if self.object.is_public:
            form = super().get_form(form_class=DataUpdateForm)
        else:
            form = super().get_form(form_class=form_class)

        for f in form.fields.keys():
            form.fields[f].disabled = self.disabled
        form.disabled = self.disabled

        if 'name' in form.fields:
            form.fields['name'].disabled = True

        return form

    def form_valid(self, form):
        if self.disabled:
            raise errors.HTTP400Exception('wizard/challenge/error.html',
                                          "Forbidden edit on a dataset",
                                          """You can't edit a dataset that you do not own.""")
        else:

            if not self.disabled and self.request.FILES:
                u = self.request.FILES.get('automl_upload', None)

                try:
                    total, pre_split, useless = self.object.update_from_chalearn(u)

                    if pre_split:
                        text = 'Already split dataset'
                    else:
                        text = 'Dataset'

                    text += ' successfully uploaded'
                    messages.add_message(self.request, messages.INFO, text)

                    if len(useless) > 0:
                        messages.add_message(self.request, messages.WARNING,
                                             'Some files have been ignored : '
                                              + str(useless))

                except InvalidAutomlFormatException as e:
                    raise errors.HTTP400Exception(
                        'wizard/challenge/error.html',
                        "Invalid Automl archive",
                        AUTOML_ERROR % (e,))

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

        challenge = ChallengeModel.objects.get(id=pk,
                                               created_by=self.request.user)
        return challenge.dataset

    def dispatch(self, request, *args, **kwargs):
        if self.get_object(**kwargs) is None:
            return redirect('wizard:challenge:data.pick', pk=kwargs['pk'])
        else:
            return super().dispatch(request, *args, **kwargs)


class ChallengeTaskUpdate(FlowOperationMixin, LoginRequiredMixin, UpdateView):
    template_name = 'wizard/split.html'
    model = TaskModel
    context_object_name = 'split'

    fields = ['train_ratio', 'valid_ratio', 'test_ratio']
    current_flow = flow.SplitFlowItem

    @property
    def disabled(self):
        return self.object.owner != self.request.user or \
               (self.object.dataset is not None and self.object.dataset.fixed_split)

    def get_success_url(self):
        return reverse('wizard:challenge:split',
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
            if r:
                self.object.is_ready = True
                self.object.save()
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

        if self.get_challenge(**kwargs).dataset.input:
            context['rows'] = self.get_challenge(**kwargs).dataset.input.rows.count
        else:
            context['rows'] = None

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
                return redirect('wizard:challenge:split', pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)


# Clean way to update the dataset
# (prevent to have some useless row in the database, like unreferenced task)
def update_chalenge_dataset(chalenge, new_dataset):
    old_dataset = chalenge.dataset
    old_task = chalenge.task

    # Update dataset and task
    chalenge.dataset = new_dataset
    chalenge.task = None

    if new_dataset.fixed_split or new_dataset.is_public:
        chalenge.task = get_object_or_404(TaskModel, dataset=new_dataset.id)

    chalenge.save()

    if old_dataset is None:
        return

    # Remove garbage
    if old_dataset.input is None:
        old_dataset.delete()
        print("delete dataset")

    if not old_dataset.fixed_split and not old_task is None:
        old_task.delete()
        print("delete task")

    chalenge.save()


@login_required
def data_picker(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

    if request.method == 'POST':
        k = request.POST['kind']

        if k == 'public':
            ds = request.POST['dataset']

            d = get_object_or_404(DatasetModel, is_public=True, id=ds)

            update_chalenge_dataset(c, d)

            c.metric = d.default_metric

            c.save()
        elif k == 'private':
            ds = request.POST['dataset']

            if request.POST['button'] == 'delete':

                try:
                    models.DatasetModel.objects.filter(
                        is_public=False, owner=request.user.id, id=ds
                    ).delete()
                except ProtectedError:
                    messages.error(request, "This dataset can't be deleted: "
                                   "another challenge use it.")

                # refresh
                request.method = ''
                return data_picker(request, pk)

            d = get_object_or_404(
                DatasetModel, is_public=False, owner=request.user.id, id=ds)

            update_chalenge_dataset(c, d)

            c.save()
        elif k == 'create':
            d = DatasetModel.create("new dataset", request.user)
            update_chalenge_dataset(c, d)
            c.save()
        else:
            assert False, "unsupported k=%s" % k

        return redirect('wizard:challenge:data', pk=pk)
    else:

        if c.origin_group is not None:
            pubds = c.origin_group.default_dataset.all()
        else:
            pubds = models.DatasetModel.objects.all().filter(is_public=True)
            
        prids = models.DatasetModel.objects.all().filter(
            is_public=False, owner=request.user.id).exclude(input=None)

        context = {'public_datasets': pubds,
                   'private_datasets': prids,
                   'challenge': c,
                   'flow': flow.Flow(flow.DataFlowItem, c)}

        return render(request, 'wizard/data/picker.html', context=context)


def metric(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)

    if request.method == 'POST':
        k = request.POST['kind']

        assert k == 'public'

        if request.POST['button'] == 'save':
            new_metric = MetricModel()

            # If it's here first metric or a default one, we create a new one
            if (not c.metric is None) and (not c.metric.is_default):
                new_metric = get_object_or_404(MetricModel, id=c.metric.id)
            else:
                new_metric.owner = request.user

            new_metric.name = request.POST['name']
            new_metric.description = request.POST['description']
            new_metric.code = request.POST['code']

            # TODO Verify if the code is ok (static analyse) before validate it
            if True:
                new_metric.is_ready = True
            else:
                new_metric.is_ready = False
                messages.error(request,
                               "There is something wrong with your code"
                               "(static analyse)")

            new_metric.save()

            c.metric = new_metric
            c.save()

        elif request.POST['button'] == 'delete':
            utilise = models.ChallengeModel.objects.filter(
                metric=request.POST['metricPrivate'])

            if len(utilise) > 0:
                messages.error(request,
                               "This metric can't be deleted: "
                               "another challenge use it.")
            else:
                models.MetricModel.objects.filter(
                    is_public=False, owner=request.user.id,
                    id=request.POST['metricPrivate']
                ).delete()
    else:
        pass

    if c.origin_group is not None:
        public_metrics = c.origin_group.default_metric.all()
    else:
        public_metrics = MetricModel.objects.all().filter(is_public=True,
                                                      is_ready=True)

    private_metric = MetricModel.objects.all().filter(owner=request.user)

    if c.metric is not None:
        private_metric = private_metric.exclude(id=c.metric.id)

    context = {'challenge': c, 'public_metrics': public_metrics,
               'flow': flow.Flow(flow.MetricFlowItem, c),
               'metric': c.metric, 'private_metric': private_metric}

    # Load a default metric if necessary
    if c.metric is None:
        context['metric'] = get_object_or_404(MetricModel,
                                              name='example', is_default=True)
        context['is_ready'] = False
    else:
        context['is_ready'] = context['metric'].is_ready

    return render(request, 'wizard/metric/editor.html', context)


@login_required
def get_metric(request, pk):
    from django.http import JsonResponse
    metric_id = request.GET.get('metric_id', None)

    metric = get_object_or_404(MetricModel, id=metric_id)

    data = {
        'name': metric.name,
        'description': metric.description,
        'code': metric.code
    }

    return JsonResponse(data)


class ChallengeProtocolUpdate(FlowOperationMixin, LoginRequiredMixin,
                              UpdateView):
    template_name = 'wizard/protocol.html'
    model = ProtocolModel
    form_class = ProtocolForm
    context_object_name = 'protocol'

    # Hacky way to pass back the challenge from get_object to get_success_url
    _runtime_challenge = None

    current_flow = flow.ProtocolFlowItem

    def get_success_url(self):
        return reverse('wizard:challenge:protocol',
                       kwargs={'pk': self._runtime_challenge.pk})

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        c = ChallengeModel.objects.get(id=pk, created_by=self.request.user)

        context = super().get_context_data(challenge=c, **kwargs)
        context['challenge'] = c
        context['is_ready'] = self.object.is_ready
        return context

    def get_object(self, **kwargs):
        pk = self.kwargs['pk']

        challenge = ChallengeModel.objects.get(id=pk,
                                               created_by=self.request.user)
        self._runtime_challenge = challenge

        protocol = challenge.protocol

        if protocol is None:
            protocol = ProtocolModel.objects.create()
            challenge.protocol = protocol
            challenge.save()

        return protocol

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        for f in form.fields.keys():
            form.fields[f].phase_num = 1 if f.startswith('dev') else 2

        return form


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
    p = get_object_or_404(DocumentationPageModel,
                          documentation=c.documentation, id=page_id)
    doc = c.documentation

    context = {'challenge': c, 'doc': doc, 'pages': doc.pages,
               'current': p.name, 'current_page': p,
               'flow': flow.Flow(flow.DocumentationFlowItem, c)}

    return render(request, "wizard/documentation/detail.html", context=context)


def build_page(request, pk):
    c = get_object_or_404(ChallengeModel, id=pk, created_by=request.user)
    context = {'challenge': c}

    try:
        context['bundler'] = BundleTaskModel.objects.filter(
            challenge=c).first()
    except ObjectDoesNotExist:
        pass

    return render(request, "wizard/challenge/build.html", context=context)


class DocumentationPageUpdate(FlowOperationMixin, LoginRequiredMixin,
                              UpdateView):
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

        challenge = ChallengeModel.objects.get(id=pk,
                                               created_by=self.request.user)
        page = get_object_or_404(DocumentationPageModel, id=page_id,
                                 documentation=challenge.documentation)

        self._runtime_challenge = challenge

        return page
