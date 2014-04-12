# -*- coding: utf-8 -*-
import json
import warnings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest


def allowed_action(func, method='auto'):
    """
    All methods which shall be callable through a given Ajax 'action' must be
    decorated with @allowed_action. This is required for safety reasons. It
    inhibits the caller to invoke all available methods of a class.
    """
    setattr(func, 'is_allowed_action', method)
    return func


class JSONResponseMixin(object):
    """
    A mixin that dispatches POST requests containing the keyword 'action' onto
    the method with that name. It renders the returned context as JSON response.
    """

    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self._dispatch_super(request, *args, **kwargs)
        action = request.META.get('HTTP_DJNG_REMOTE_METHOD', kwargs.get('action'))
        handler = action and getattr(self, action, None)
        if not callable(handler):
            return self._dispatch_super(request, *args, **kwargs)
        out_data = json.dumps(handler(), cls=DjangoJSONEncoder)
        response = HttpResponse(out_data)
        response['Content-Type'] = 'application/json;charset=UTF-8'
        response['Cache-Control'] = 'no-cache'
        return response

    def post(self, request, *args, **kwargs):
        try:
            if not request.is_ajax():
                return self._dispatch_super(request, *args, **kwargs)
            in_data = json.loads(str(request.body))
            if 'action' in in_data:
                warnings.warn("Using the keyword 'action' inside the payload is deprecated. Please use 'djangoAction' from module 'ng.django.forms'", DeprecationWarning)
                action = in_data.pop('action', kwargs.get('action'))
            else:
                action = request.META.get('HTTP_DJNG_REMOTE_METHOD', kwargs.get('action'))
            handler = action and getattr(self, action, None)
            if not callable(handler):
                return self._dispatch_super(request, *args, **kwargs)
            if not hasattr(handler, 'is_allowed_action'):
                raise ValueError('Method "%s" is not decorated with @allowed_action' % action)
            out_data = json.dumps(handler(in_data), cls=DjangoJSONEncoder)
            return HttpResponse(out_data, content_type='application/json;charset=UTF-8')
        except ValueError as err:
            return HttpResponseBadRequest(err)

    def _dispatch_super(self, request, *args, **kwargs):
        base = super(JSONResponseMixin, self)
        handler = getattr(base, request.method.lower(), None)
        if callable(handler):
            return handler(request, *args, **kwargs)
        raise ValueError('This view can not handle method %s' % request.method)
