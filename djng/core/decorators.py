# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

from django.utils.decorators import available_attrs

from djng.core.ajax_messages import process_response


def add_messages_to_response(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        return process_response(request, response)
    return _wrapped_view
