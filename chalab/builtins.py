from django import template

import chalab

register = template.Library()


@register.simple_tag
def VERSION():
    return chalab.__version__
