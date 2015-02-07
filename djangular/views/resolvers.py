# -*- coding: utf-8 -*-
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.urlresolvers import resolve, reverse


class UrlResolverView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        This view reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs

        Using the resolver for a csrf_exempt view would still raise CSRF verification error on UrlResolverView,
        thus the resolver must be csrf_exempt. CSRF verification is done on resolved view, if it isn't csrf_exempt
        """

        url_name = request.GET.get('djng_url_name')
        url_args = request.GET.getlist('djng_url_args', None)
        url_kwargs = {}

        for param in request.GET:
            if param.startswith('djng_url_kwarg_'):
                url_kwargs[param[15:]] = request.GET[param]  # [15:] to remove 'djng_url_kwarg' prefix

        view, args, kwargs = resolve(reverse(url_name, args=url_args, kwargs=url_kwargs))

        # Return csrf_protected view if it isn't csrf_exempt
        if hasattr(view, 'csrf_exempt'):
            if view.csrf_exempt:
                return view(request, *args, **kwargs)
        return csrf_protect(view)(request, *args, **kwargs)