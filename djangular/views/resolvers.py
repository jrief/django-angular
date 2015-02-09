# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from django.utils.module_loading import import_string
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import resolve, reverse


class UrlResolverView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        This view reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs

        Using the resolver for a csrf_exempt view would still raise CSRF verification error on UrlResolverView,
        thus the resolver must be csrf_exempt. CSRF/Session/Auth and other middleware checks are done when calling
        the actual view.
        """

        url_name = request.GET.get('djng_url_name')
        url_args = request.GET.getlist('djng_url_args', None)
        url_kwargs = {}

        for param in request.GET:
            if param.startswith('djng_url_kwarg_'):
                url_kwargs[param[15:]] = request.GET[param]  # [15:] to remove 'djng_url_kwarg' prefix

        view, args, kwargs = resolve(reverse(url_name, args=url_args, kwargs=url_kwargs))

        # Run through all the middlewares when calling actual view
        for middleware_path in settings.MIDDLEWARE_CLASSES:
            view = decorator_from_middleware(import_string(middleware_path))(view)
        return view(request, *args, **kwargs)