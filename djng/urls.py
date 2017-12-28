import warnings
from django.urls import reverse
from django.conf.urls import url
from django.http.response import HttpResponsePermanentRedirect


warnings.warn("Reversing URL's using urlpatterns is deprecated. Please use the middleware instead",
    DeprecationWarning)


def angular_reverse(request, *args, **kwargs):
    url_name = request.GET.get('djng_url_name')
    url_args = request.GET.getlist('djng_url_args', None)
    url_kwargs = {}

    prefix = 'djng_url_kwarg_'
    for param in request.GET:
        if param.startswith(prefix):
            url_kwargs[param[len(prefix):]] = request.GET[param]

    url = reverse(url_name, args=url_args, kwargs=url_kwargs)
    return HttpResponsePermanentRedirect(url)


urlpatterns = [
    url(r'^reverse/$', angular_reverse),
]
