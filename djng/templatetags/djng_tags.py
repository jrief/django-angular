# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import warnings
from django.template import Library
from django.template.base import Node, NodeList, TextNode, VariableNode
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from djng.core.urlresolvers import get_all_remote_methods, get_current_remote_methods

register = Library()


class CsrfValueNode(Node):
    def render(self, context):
        warnings.warn("Instead of {% csrf_value %}, please use {{ csrf_token }}")
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
    return mark_safe(json.dumps(get_current_remote_methods(context.get('view'))))


@register.simple_tag(name='load_djng_urls', takes_context=True)
def djng_urls(context, *namespaces):
    raise DeprecationWarning(
        "load_djng_urls templatetag is deprecated and has been removed from this version of django-angular."
        "Please refer to documentation for updated way to manage django urls in angular.")


class AngularJsNode(Node):
    def __init__(self, django_nodelist, angular_nodelist, variable):
        self.django_nodelist = django_nodelist
        self.angular_nodelist = angular_nodelist
        self.variable = variable

    def render(self, context):
        if self.variable.resolve(context):
            return self.angular_nodelist.render(context)
        return self.django_nodelist.render(context)


@register.tag
def angularjs(parser, token):
    """
    Conditionally switch between AngularJS and Django variable expansion for ``{{`` and ``}}``
    keeping Django's expansion for ``{%`` and ``%}``

    Usage::

        {% angularjs 1 %} or simply {% angularjs %}
            {% process variables through the AngularJS template engine %}
        {% endangularjs %}

        {% angularjs 0 %}
            {% process variables through the Django template engine %}
        {% endangularjs %}

        Instead of 0 and 1, it is possible to use a context variable.
    """
    bits = token.contents.split()
    if len(bits) < 2:
        bits.append('1')
    values = [parser.compile_filter(bit) for bit in bits[1:]]
    django_nodelist = parser.parse(('endangularjs',))
    angular_nodelist = NodeList()
    for node in django_nodelist:
        # convert all occurrences of VariableNode into a TextNode using the
        # AngularJS double curly bracket notation
        if isinstance(node, VariableNode):
            # convert Django's array notation into JS array notation
            tokens = node.filter_expression.token.split('.')
            token = tokens[0]
            for part in tokens[1:]:
                if part.isdigit():
                    token += '[%s]' % part
                else:
                    token += '.%s' % part
            node = TextNode('{{ %s }}' % token)
        angular_nodelist.append(node)
    parser.delete_first_token()
    return AngularJsNode(django_nodelist, angular_nodelist, values[0])
