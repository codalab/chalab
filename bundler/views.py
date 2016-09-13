from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404, render

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

    try:
        b = BundleTaskModel.objects.get(challenge=c)
        raise Exception()
    except ObjectDoesNotExist:
        b = BundleTaskModel.create(c)
        bundle.delay(b)

    return redirect(c.get_absolute_url())


@login_required
def download(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)
    b = get_object_or_404(BundleTaskModel, state=BundleTaskModel.FINISHED, challenge=c)
    return redirect(b.output.url)
