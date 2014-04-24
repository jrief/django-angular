# -*- coding: utf-8 -*-
import json
import warnings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden


def allow_remote_invocation(func, method='auto'):
    """
    All methods which shall be callable through a given Ajax 'action' must be
    decorated with @allowed_action. This is required for safety reasons. It
    inhibits the caller to invoke all available methods of a class.
    """
    setattr(func, 'allow_rmi', method)
    return func


def allowed_action(func):
    warnings.warn("Decorator `@allowed_action` is deprecated. Use `@allow_remote_invocation` instead.", DeprecationWarning)
    return allow_remote_invocation(func)


class JSONResponseException(Exception):
    """
    Exception class for triggering HTTP 4XX responses with JSON content, where expected.
    """
    status_code = 400

    def __init__(self, status=None, *args, **kwargs):
        if status is not None:
            self.status_code = status
        super(JSONResponseException, self).__init__(*args, **kwargs)


class JSONBaseMixin(object):
    """
    Basic mixin for encoding HTTP responses in JSON format.
    """
    content_type = 'application/json;charset=UTF-8'

    def json_response(self, response_data, status=200, **kwargs):
        out_data = json.dumps(response_data, cls=DjangoJSONEncoder, **kwargs)
        response = HttpResponse(out_data, self.content_type, status=status)
        response['Cache-Control'] = 'no-cache'
        return response


class JSONResponseMixin(JSONBaseMixin):
    """
    A mixin that dispatches POST requests containing the keyword 'action' onto
    the method with that name. It renders the returned context as JSON response.
    """
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self._dispatch_super(request, *args, **kwargs)
        if 'action' in kwargs:
            warnings.warn("Using the keyword 'action' in URLresolvers is deprecated. Please use 'invoke_method' instead", DeprecationWarning)
            remote_method = kwargs['action']
        else:
            remote_method = kwargs.get('invoke_method')
        if remote_method:
            # method for invocation is determined programmatically
            handler = getattr(self, remote_method)
        else:
            # method for invocation is determined by HTTP header
            remote_method = request.META.get('HTTP_DJNG_REMOTE_METHOD')
            handler = remote_method and getattr(self, remote_method, None)
            if not callable(handler):
                return self._dispatch_super(request, *args, **kwargs)
            if not hasattr(handler, 'allow_rmi'):
                return HttpResponseForbidden("Method '{0}.{1}' has no decorator '@allow_remote_invocation'"
                                             .format(self.__class__.__name__, remote_method))
        try:
            response_data = handler()
        except JSONResponseException as e:
            return self.json_response(e, e.status_code)
        return self.json_response(response_data)

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self._dispatch_super(request, *args, **kwargs)
        in_data = json.loads(str(request.body))
        if 'action' in in_data:
            warnings.warn("Using the keyword 'action' inside the payload is deprecated. Please use 'djangoRMI' from module 'ng.django.forms'", DeprecationWarning)
            remote_method = in_data.pop('action')
        else:
            remote_method = request.META.get('HTTP_DJNG_REMOTE_METHOD')
        handler = remote_method and getattr(self, remote_method, None)
        if not callable(handler):
            return self._dispatch_super(request, *args, **kwargs)
        if not hasattr(handler, 'allow_rmi'):
            return HttpResponseForbidden("Method '{0}.{1}' has no decorator '@allow_remote_invocation'"
                                         .format(self.__class__.__name__, remote_method), 403)
        try:
            response_data = handler(in_data)
        except JSONResponseException as e:
            return self.json_response(e, e.status_code)
        return self.json_response(response_data)

    def _dispatch_super(self, request, *args, **kwargs):
        base = super(JSONResponseMixin, self)
        handler = getattr(base, request.method.lower(), None)
        if callable(handler):
            return handler(request, *args, **kwargs)
        # HttpResponseNotAllowed expects permitted methods.
        return HttpResponseBadRequest('This view can not handle method {0}'.format(request.method), status=405)
