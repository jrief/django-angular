# -*- coding: utf-8 -*-
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest


def allowed_action(func):
    """
    All methods which shall be callable through a given Ajax 'action' must be
    decorated with @allowed_action. This is required for safety reasons. It
    inhibits the caller to invoke all available methods of a class.
    """
    setattr(func, 'is_allowed_action', None)
    return func


class JSONResponseMixin(object):
    """
    A mixin that dispatches POST requests containing the keyword 'action' onto
    the method with that name. It renders the returned context as JSON response.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest('Expected an XMLHttpRequest')
        try:
            in_data = json.loads(request.raw_post_data)
            action = in_data.pop('action', kwargs.get('action'))
            action = action and getattr(self, action, None)
            if not (callable(action) and hasattr(action, 'is_allowed_action')):
                raise ValueError('action="%s" is undefined or not callable' % action)
            out_data = json.dumps(action(in_data), cls=DjangoJSONEncoder)
            return HttpResponse(out_data, content_type='application/json;charset=UTF-8')
        except ValueError as e:
            return HttpResponseBadRequest('POST data is not valid JSON: %s' % e.message)
