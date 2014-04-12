# -*- coding: utf-8 -*-
import json
from django.template import Library
from django.template.base import Node
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from djangular.core.urlresolvers import get_remote_methods
register = Library()


class CsrfValueNode(Node):
    def render(self, context):
        csrf_token = context.get('csrf_token', None)
        if not csrf_token:
            raise ImproperlyConfigured('Template must be rendered using a RequestContext')
        if csrf_token == 'NOTPROVIDED':
            return mark_safe('')
        else:
            return mark_safe(csrf_token)


@register.tag(name='csrf_value')
def render_csrf_value(parser, token):
    return CsrfValueNode()


@register.simple_tag(name='djng_rmi_config')
def djng_rmi_config():
    return mark_safe(json.dumps(get_remote_methods()))
