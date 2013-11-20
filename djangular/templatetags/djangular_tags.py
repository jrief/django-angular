# -*- coding: utf-8 -*-
from django.template import Library
from django.template.base import Node
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

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
