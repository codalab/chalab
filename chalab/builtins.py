from django import template

import chalab

register = template.Library()


@register.simple_tag
def VERSION():
    return chalab.__version__


@register.inclusion_tag('chalab/_confirm_form.html', takes_context=True)
def confirm_form(context):
    return {}
