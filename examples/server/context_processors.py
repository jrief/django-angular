# -*- coding: utf-8 -*-
from django.conf import settings


def default(request):
    context = {
        'CDN_CACHE': settings.DEBUG and settings.STATIC_URL or '//',
    }
    return context
