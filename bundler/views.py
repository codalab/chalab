from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404

from wizard.models import ChallengeModel
from .models import BundleTaskModel
from .tasks import bundle


@login_required
def build(request, pk):
    c = get_object_or_404(ChallengeModel, created_by=request.user, pk=pk)

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
