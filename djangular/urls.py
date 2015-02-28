from django.core.urlresolvers import resolve, reverse
from django.conf.urls import patterns, url


def angular_reverse(request, *args, **kwargs):
    url_name = request.GET.get('djng_url_name')
    url_args = request.GET.getlist('djng_url_args', None)
    url_kwargs = {}

    prefix = 'djng_url_kwarg_'
    for param in request.GET:
        if param.startswith(prefix):
            url_kwargs[param[len(prefix):]] = request.GET[param]

    url = reverse(url_name, args=url_args, kwargs=url_kwargs)
    view, args, kwargs = resolve(url)
    response = view(request, *args, **kwargs)
    return response


urlpatterns = patterns('',
    url(r'^(.*)', angular_reverse),
)
