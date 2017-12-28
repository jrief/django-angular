# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from inspect import isclass

from django.utils import six
from django.urls import (get_resolver, get_urlconf, resolve, reverse, NoReverseMatch)
from django.core.exceptions import ImproperlyConfigured

try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string

from djng.views.mixins import JSONResponseMixin


def _get_remote_methods_for(view_object, url):
    # view_object can be a view class or instance
    result = {}
    for field in dir(view_object):
        member = getattr(view_object, field, None)
        if callable(member) and hasattr(member, 'allow_rmi'):
            config = {
                'url': url,
                'method': getattr(member, 'allow_rmi'),
                'headers': {'DjNg-Remote-Method': field},
            }
            result.update({field: config})
    return result


def get_all_remote_methods(resolver=None, ns_prefix=''):
    """
    Returns a dictionary to be used for calling ``djangoCall.configure()``, which itself extends the
    Angular API to the client, offering him to call remote methods.
    """
    if not resolver:
        resolver = get_resolver(get_urlconf())
    result = {}
    for name in resolver.reverse_dict.keys():
        if not isinstance(name, six.string_types):
            continue
        try:
            url = reverse(ns_prefix + name)
            resmgr = resolve(url)
            ViewClass = import_string('{0}.{1}'.format(resmgr.func.__module__, resmgr.func.__name__))
            if isclass(ViewClass) and issubclass(ViewClass, JSONResponseMixin):
                result[name] = _get_remote_methods_for(ViewClass, url)
        except (NoReverseMatch, ImproperlyConfigured):
            pass
    for namespace, ns_pattern in resolver.namespace_dict.items():
        sub_res = get_all_remote_methods(ns_pattern[1], ns_prefix + namespace + ':')
        if sub_res:
            result[namespace] = sub_res
    return result


def get_current_remote_methods(view):
    if isinstance(view, JSONResponseMixin):
        return _get_remote_methods_for(view, view.request.path_info)
