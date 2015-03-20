from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.utils.decorators import decorator_from_middleware


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
            view, args, kwargs = resolve(url, urlconf=self.urlconf)

            # Set to real path, otherwise this url resolving will be ran again when calling
            # teh actual view, resulting in infinite recursion
            request.path = url

            # Run through all the middlewares when calling actual view
            # MIDDLEWARE_CLASSES must be reversed to maintain correct order of middlewares execution
            # (view function is wrapped with middleware decorators, first one added is executed as last)
            for middleware_path in reversed(settings.MIDDLEWARE_CLASSES):
                view = decorator_from_middleware(self._import_dotted_path(middleware_path))(view)
            return view(request, *args, **kwargs)
