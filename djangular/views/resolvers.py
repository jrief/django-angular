# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from django.utils.module_loading import import_string
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import resolve, reverse


class UrlResolverView(View):

    def __init__(self, **kwargs):
        """
        If djng_url_resolver is set, the DjangularUrlMiddleware will return response immediately and no middlewares
        will be ran for UrlResolverView.
        """
        self.djng_url_resolver = True
        super(UrlResolverView, self).__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        This view reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs
        No middleware processing is done for UrlResolverView, middlewares are applied to the actual view function.
        Thus the final result is exactly the same as if the request was for the resolved view.
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