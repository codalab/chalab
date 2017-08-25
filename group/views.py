from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from bundler.models import BundleTaskModel
from group.models import GroupModel

from django.contrib.auth.models import User
from django.http import JsonResponse

from wizard.models import ChallengeModel, DatasetModel, MetricModel


@login_required
def change_user_in_group(request, group_id):
    u = request.user
    current_group = get_object_or_404(GroupModel, id=group_id, admins=u)

    if request.GET.get('action', None) == 'add':
        asked_users = request.GET.get('add_user', None)

        list_users = [x.strip() for x in asked_users.split(',')]

        list_users_added = []
        list_users_unknow = []

        for user in list_users:
            find_user = User.objects.filter(Q(username__iexact=user) | Q(email=user))
            if find_user.exists():
                find_user = find_user.first()
                if not current_group.users.filter(id=find_user.id):
                    current_group.users.add(find_user)
                    list_users_added.append({
                        'user_id': find_user.id,
                        'user_name': find_user.username,
                        'user_email': find_user.email
                    })
            else:
                list_users_unknow.append(user)
        current_group.save()
        data = {
            'done': True,
            'added': list_users_added,
            'unknown': list_users_unknow
        }
        return JsonResponse(data)
    elif request.GET.get('action', None) == 'remove':
        if request.GET.get('all', None) == 'true':
            current_group.users.clear()
        else:
            asked_user = get_object_or_404(User, id=request.GET.get('user', None))
            current_group.users.remove(asked_user)
        current_group.save()
        return JsonResponse({'done': True})
    else:
        return JsonResponse({'done': False, 'error': 'Invalide request'})


def redirect_groups(request, *args):
    u = request.user
    all = u.admin_of_group.all()

    if all.exists():
        return redirect(all.first())
    else:
        return render(request, 'group/editor.html', context={'groups': []})


@login_required
def create_new_group(request):
    u = request.user
    new_group = GroupModel()
    new_group.save()
    new_group.admins.add(u)
    for dataset in DatasetModel.objects.filter(is_public=True):
        new_group.default_dataset.add(dataset)
    for metric in MetricModel.objects.filter(is_default=True):
        new_group.default_metric.add(metric)
    return redirect(new_group)


@login_required
def groups(request, group_id):
    u = request.user
    current_group = get_object_or_404(GroupModel, id=group_id, admins=u)

    if request.method == 'POST':
        if request.POST['button'] == 'update':
            print(request.POST)
            current_group.public = request.POST['visibility'] == 'public'

            current_group.name = request.POST['name']

            current_group.default_dataset.clear()
            if 'id_default_datasets' in request.POST.dict():
                for id_dataset in request.POST.getlist('id_default_datasets'):
                    current_group.default_dataset.add(get_object_or_404(DatasetModel, id=id_dataset))

            current_group.default_metric.clear()
            if 'id_default_metrics' in request.POST.dict():
                for id_metric in request.POST.getlist('id_default_metrics'):
                    current_group.default_metric.add(get_object_or_404(MetricModel, id=id_metric))

            if request.POST['id_template']:
                current_group.template = get_object_or_404(ChallengeModel, id=request.POST['id_template'])
            else:
                current_group.template = None
            current_group.save()
        elif request.POST['button'] == 'delete':
            current_group.delete()
            return redirect_groups(request)

    all_template = [(c, not BundleTaskModel.objects.filter(challenge=c).first() is None) for c in ChallengeModel.objects.filter(created_by=u.id)]

    big_list_users = list(current_group.users.all())

    context = {'groups': u.admin_of_group.order_by('id'),
               'current': int(group_id),
               'current_group': current_group,
               'users': big_list_users,

               'default_datasets': [('Default', DatasetModel.objects.filter(is_public=True)),
                                    ('My datasets', DatasetModel.objects.filter(is_public=False, owner=u))],
               'selected_datasets': current_group.default_dataset.all(),

               'default_metrics': [('Default', MetricModel.objects.filter(is_default=True)),
                                    ('My metrics', MetricModel.objects.filter(is_default=False, owner=u))],
               'selected_metrics': current_group.default_metric.all(),

               'all_template': all_template}

    return render(request, 'group/editor.html', context=context)
