from django import template
from django.shortcuts import get_object_or_404
from django.http import Http404

from user.models import ProfileModel

register = template.Library()


@register.simple_tag
def can_create_group(user):
    try:
        profile = get_object_or_404(ProfileModel, user=user)
        if profile is not None:
            return profile.expertise != ProfileModel.EX_NOVICE
    except Http404:
        return False
    return False
