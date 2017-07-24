from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from group.models import GroupModel

from django.contrib.auth.models import User
from django.http import JsonResponse


@login_required
def add_user_to_group(request):
    asked_user = request.GET.get('add_user', None)

    data = {
        'is_taken': User.objects.filter(username__iexact=asked_user).exists()
    }
    return JsonResponse(data)


def redirect_groups(request, *args):
    u = request.user
    all = u.admin_of_group.all()

    if all.exists() == 0:
        return redirect('/')
    else:
        return redirect(all.first())


@login_required
def groups(request, group_id):
    u = request.user

    if request.method == 'POST':
        pass

    current_group = get_object_or_404(GroupModel, id=group_id)

    context = {'groups': u.admin_of_group.all(),
               'current': int(group_id),
               'current_group': current_group,
               'users': current_group.users.all(),
               'default_datasets': current_group.default_dataset.all(),
               'default_metric': current_group.default_metric.all()}

    return render(request, 'group/editor.html', context=context)
