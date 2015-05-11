# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse


class DjangularUrlMiddleware(object):
    """
    If the request path is <ANGULAR_REVERSE> it should be resolved to actual view, otherwise return
    ``None`` and continue as usual.
    This must be the first middleware in the MIDDLEWARE_CLASSES tuple!
    Urlconf property is overridden in tests
    """
    ANGULAR_REVERSE = '/angular/reverse/'
    urlconf = None

    def __init__(self, urlconf=None):
        self.urlconf = urlconf
        super(DjangularUrlMiddleware, self).__init__()

    def process_request(self, request):
        """
        Reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs
        Since the view function is called directly, it isn't ran through middlewares, so the middlewares must
        be added manually
        The final result is exactly the same as if the request was for the resolved view.
        """
        if request.path == self.ANGULAR_REVERSE:
            url_name = request.GET.get('djng_url_name')
            url_args = request.GET.getlist('djng_url_args', None)
            url_kwargs = {}

            # Read kwargs
            for param in request.GET:
                if param.startswith('djng_url_kwarg_'):
                    url_kwargs[param[15:]] = request.GET[param]  # [15:] to remove 'djng_url_kwarg' prefix

            url = reverse(url_name, args=url_args, kwargs=url_kwargs, urlconf=self.urlconf)
            assert not url.startswith(self.ANGULAR_REVERSE), "Prevent recursive requests"

            # rebuild the request object with a different environ
            request.environ['PATH_INFO'] = url
            query = request.GET.copy()
            query.pop('djng_url_name', None)
            query.pop('djng_url_args', None)
            request.environ['QUERY_STRING'] = query.urlencode()
            new_request = WSGIRequest(request.environ)
            request.__dict__ = new_request.__dict__
