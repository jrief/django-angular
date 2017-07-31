# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjangoAngularConfig(AppConfig):
    name = 'djng'

    def ready(self):
        from django import VERSION
        from django.forms.widgets import RadioSelect

        if VERSION >= (1, 11):
            RadioSelect.add_id_index = False
