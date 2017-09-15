# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
To be used in Sekizai's render_block to postprocess AngularJS module dependenies
"""

import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

if 'sekizai' not in settings.INSTALLED_APPS:
    msg = "Install django-sekizai when using these postprocessors"
    raise ImproperlyConfigured(msg)


def module_list(context, data, namespace):
    warnings.warn("This postprocessor is deprecated. Read on how to resolve AngularJS dependencies using `{% with_data \"ng-requires\" ... %}`")
    modules = set(m.strip(' "\'') for m in data.split())
    text = format_html_join(', ', '"{0}"', ((m,) for m in modules))
    return text


def module_config(context, data, namespace):
    warnings.warn("This postprocessor is deprecated. Read on how to resolve AngularJS dependencies using `{% with_data \"ng-config\" ... %}`")
    configs = [(mark_safe(c),) for c in data.split('\n') if c]
    text = format_html_join('', '.config({0})', configs)
    return text
