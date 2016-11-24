from wsgiref.util import FileWrapper

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils.text import slugify

from chalab import errors
from wizard.models import ChallengeModel
from .models import BundleTaskModel
from .tasks import bundle


def err(request, template, status, **kwargs):
    return render(request, template, status=status, context=kwargs)


@login_required
def build(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)

    if not c.is_ready:
        return err(request, 'wizard/http400.html', 400,
                   challenge=c,
                   message='The challenge is not ready to be bundled.')

    b = BundleTaskModel.objects.filter(challenge=c).first()

    if b is None or b.done:
        b = BundleTaskModel.create(c)
        bundle.delay(b)
    else:
        raise errors.HTTP400Exception('wizard/challenge/error.html', 'build is in progress',
                                      """The bundle is already being built.""",
                                      challenge=c)

    return redirect(reverse('wizard:challenge:build',
                            kwargs={'pk': pk}))


@login_required
def download(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)
    b = BundleTaskModel.objects.filter(challenge=c, state=BundleTaskModel.FINISHED).first()

    if b is None:
        raise Http404('No bundle successfully built available for download')

    return redirect(
        reverse('wizard:challenge:bundler:download_zip',
                kwargs={'pk': pk, 'task_id': b.pk})
        + "#complete-panel")


@login_required
def download_zip(request, pk, task_id):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)

    b = get_object_or_404(BundleTaskModel, challenge=c, pk=task_id)
    closed = b.closed

    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(b.output, chunk_size),
                                     content_type='application/zip')
    response['Content-Length'] = b.output.size

    name = 'bundle_%s_%s.zip' % (slugify(c.title), closed.strftime('%Y-%m-%d_%H:%M'))
    response['Content-Disposition'] = "attachment; filename=%s" % name
    return response


@login_required
def logs(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)
    b = BundleTaskModel.objects.filter(challenge=c).first()

    if b is None:
        raise Http404('Bundler not found')

    return render(request, 'bundler/logs.html', dict(task=b))


@login_required
def status_json(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)
    b = BundleTaskModel.objects.filter(challenge=c).first()

    return JsonResponse({'state': b.state,
                         'created': b.created,
                         'closed': b.closed})
