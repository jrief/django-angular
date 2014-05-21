# -*- coding: utf-8 -*-
import json
from django.template import Library
from django.template.base import Node
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from djangular.core.urlresolvers import get_all_remote_methods, get_current_remote_methods
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


@register.simple_tag(name='djng_all_rmi')
def djng_all_rmi():
    """
    Returns a dictionary of all methods for all Views available for this project, marked with the
    ``@allow_remote_invocation`` decorator. The return string can be used directly to initialize
    the AngularJS provider, such as ``djangoRMIProvider.configure({­% djng_rmi_configs %­});``
    """
    return mark_safe(json.dumps(get_all_remote_methods()))


@register.simple_tag(name='djng_current_rmi', takes_context=True)
def djng_current_rmi(context):
    """
    Returns a dictionary of all methods for the current View of this request, marked with the
    @allow_remote_invocation decorator. The return string can be used directly to initialize
    the AngularJS provider, such as ``djangoRMIProvider.configure({­% djng_current_rmi %­});``
    """
    return mark_safe(json.dumps(get_current_remote_methods(context['view'])))


@register.simple_tag(name='djng_canonical_url', takes_context=True)
def djng_canonical_url(context):
    """
    Return the canonical URL for the current view. Note: When using partial views, this is not
    equivalent with ``request.path_info``, since ui-router works with URLs which are not propagated
    to the backend.
    """
    canonical_url = reverse(context['request'].resolver_match.url_name)
    return mark_safe(canonical_url)
