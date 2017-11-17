# -*- coding: utf-8 -*-
from django.conf import settings


def global_context(request):
    """
    Adds additional context variables to the default context.
    """
    context = {
        'WITH_WS4REDIS': hasattr(settings, 'WEBSOCKET_URL'),
    }
    return context
