from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from group.models import GroupModel

from django.contrib.auth.models import User
from django.http import JsonResponse

from wizard.models import ChallengeModel


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
def create_new_group(request):
    u = request.user
    new_group = GroupModel()
    new_group.save()
    new_group.admins.add(u)
    new_group.users.add(u)
    return redirect(new_group.get_absolute_url())


@login_required
def groups(request, group_id):
    u = request.user
    current_group = get_object_or_404(GroupModel, id=group_id)

    if request.method == 'POST':
        current_group.name = request.POST['name']
        if request.POST['id_template']:
            current_group.template = get_object_or_404(ChallengeModel, id=request.POST['id_template'])
        else:
            current_group.template = None
        current_group.save()
        print(request.POST)

    context = {'groups': u.admin_of_group.all(),
               'current': int(group_id),
               'current_group': current_group,
               'users': current_group.users.all(),
               'default_datasets': current_group.default_dataset.all(),
               'default_metric': current_group.default_metric.all(),
               'actual_template': current_group.template,
               'all_template': list(ChallengeModel.objects.filter(created_by=u.id))}

    return render(request, 'group/editor.html', context=context)
