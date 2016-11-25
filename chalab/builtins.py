import logging

from django import template

import chalab

register = template.Library()

log = logging.getLogger('chalab.builtins')


@register.simple_tag
def VERSION():
    return chalab.__version__


@register.inclusion_tag('chalab/_confirm_form.html', takes_context=True)
def confirm_form(context):
    return {}


@register.inclusion_tag('chalab/_wiki_help.html', takes_context=True)
def wiki_help(context):
    request = context['request']

    try:
        suffix = request.resolver_match.url_name
        names = request.resolver_match.namespaces + [suffix]

        names = [x[0].upper() + x[1:] for x in names]
        uri = '-‐-'.join(names)  # /!\ not a dash '-' but an hyphen '‐', avoids gollum issue #764
    except Exception as e:
        log.error("wiki help failed: %s", e)
        uri = None

    return {'uri': uri}
