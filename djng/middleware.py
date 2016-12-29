# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import six

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.utils.http import unquote
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from djng.core.ajax_messages import process_response, is_not_valid_type


DJANGULAR_MESSAGES_EXCLUDE_URLS = getattr(
    settings,
    "DJANGULAR_MESSAGES_EXCLUDE_URLS",
    ()
)

EXEMPT = list(DJANGULAR_MESSAGES_EXCLUDE_URLS)


class AngularUrlMiddleware(MiddlewareMixin):
    """
    If the request path is <ANGULAR_REVERSE>
    it should be resolved to actual view, otherwise return ``None``
    and continue as usual.
    This must be the first middleware in the MIDDLEWARE_CLASSES tuple!
    """
    ANGULAR_REVERSE = '/angular/reverse/'

    def process_request(self, request):
        """
        Reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs
        Since the view function is called directly, it isn't ran through middlewares, so the middlewares must
        be added manually
        The final result is exactly the same as if the request was for the resolved view.

        Parametrized urls:
        djangoUrl.reverse can be used with parametrized urls of $resource
        In that case the reverse url is something like: /angular/reverse/?djng_url_name=orders&djng_url_kwarg_id=:id
        $resource can either replace the ':id' part with say 2 and we can proceed as usual,
        reverse with reverse('orders', kwargs={'id': 2}).

        If it's not replaced we want to reverse to url we get a request to url
        '/angular/reverse/?djng_url_name=orders&djng_url_kwarg_id=' which
        gives a request.GET QueryDict {u'djng_url_name': [u'orders'], u'djng_url_kwarg_id': [u'']}

        In that case we want to ignore the id param and only reverse to url with name 'orders' and no params.
        So we ignore args and kwargs that are empty strings.
        """
        if request.path == self.ANGULAR_REVERSE:
            url_name = request.GET.get('djng_url_name')
            url_args = request.GET.getlist('djng_url_args', [])
            url_kwargs = {}

            # Remove falsy values (empty strings)
            url_args = filter(lambda x: x, url_args)

            # Read kwargs
            for param in request.GET:
                if param.startswith('djng_url_kwarg_'):
                    # Ignore kwargs that are empty strings
                    if request.GET[param]:
                        url_kwargs[param[15:]] = request.GET[param]  # [15:] to remove 'djng_url_kwarg' prefix

            url = unquote(reverse(url_name, args=url_args, kwargs=url_kwargs))
            assert not url.startswith(self.ANGULAR_REVERSE), "Prevent recursive requests"

            # rebuild the request object with a different environ
            request.path = request.path_info = url
            request.environ['PATH_INFO'] = url
            query = request.GET.copy()
            for key in request.GET:
                if key.startswith('djng_url'):
                    query.pop(key, None)
            if six.PY3:
                request.environ['QUERY_STRING'] = query.urlencode()
            else:
                request.environ['QUERY_STRING'] = query.urlencode().encode('utf-8')

            # Reconstruct GET QueryList in the same way WSGIRequest.GET function works
            request.GET = http.QueryDict(request.environ['QUERY_STRING'])


class AjaxDjangoMessagesMiddleware(object):
    """
    Exclusion method adapted from
    https://github.com/pydanny/dj-stripe/blob/master/djstripe/middleware.py

    Rules:

        * "(app_name)" means everything from this app is exempt
        * "[namespace]" means everything with this name is exempt
        * "namespace:name" means this namespaced URL is exempt
        * "name" means this URL is exempt
        * If settings.DEBUG is True, then django-debug-toolbar is exempt

    Example::

        DJANGULAR_MESSAGES_EXCLUDE_URLS = (
            "(myapp)",  # anything in the myapp URLConf
            "[blogs]",  # Anything in the blogs namespace
            "accounts:detail",  # An AccountDetail view you wish to exclude
            "home",  # Site homepage
        )
    """
    def process_response(self, request, response):
        if is_not_valid_type(request, response):
            return response
        if self._is_debug_toolbar(request.path):
            return response
        if self._is_exempt(request.path):
            return response
        return process_response(request, response)

    def _is_debug_toolbar(self, path):
        return settings.DEBUG and path.startswith("/__debug__")

    def _is_exempt(self, path):
        is_match = False
        try:
            match = resolve(path)
        except Resolver404:
            return False

        if (
            "({0})".format(match.app_name) in EXEMPT or
            "[{0}]".format(match.namespace) in EXEMPT or
            "{0}:{1}".format(match.namespace, match.url_name) in EXEMPT or
            match.url_name in EXEMPT
        ):
            is_match = True

        return is_match
