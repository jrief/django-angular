# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from django.views.generic import View
from django.core.urlresolvers import resolve, reverse


class DjangularUrlResolverView(View):
    urlconf = None  # urlconf for reverse() and resolve(), overridden in tests

    @staticmethod
    def _import_dotted_path(path):
        """
        Imports dotted path, e.g. django.middleware.common.CommonMiddleware
        There are some django utils for this (import_string, import_by_path), but only available in 1.6 and 1.7
        :param path: dotted path
        :return: imported class
        """
        path = path.split('.')
        package_path = '.'.join(path[:-1])
        module = path[-1]
        package = __import__(package_path, fromlist=[module])
        return getattr(package, module)

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

        # Read kwargs
        for param in request.GET:
            if param.startswith('djng_url_kwarg_'):
                url_kwargs[param[15:]] = request.GET[param]  # [15:] to remove 'djng_url_kwarg' prefix

        url = reverse(url_name, args=url_args, kwargs=url_kwargs, urlconf=self.urlconf)
        view, args, kwargs = resolve(url, urlconf=self.urlconf)

        # Run through all the middlewares when calling actual view
        # MIDDLEWARE_CLASSES must be reversed to maintain correct order of middlewares execution
        # (view function is wrapped with middleware decorators, first one added is executed as last)
        for middleware_path in reversed(settings.MIDDLEWARE_CLASSES):
            view = decorator_from_middleware(self._import_dotted_path(middleware_path))(view)
        return view(request, *args, **kwargs)