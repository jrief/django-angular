# -*- coding: utf-8 -*-
from django import forms


class FloatField(forms.FloatField):
    """
    The internal ``django.forms.FloatField`` does not handle the step value in its number widget.
    """
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super(FloatField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(FloatField, self).widget_attrs(widget)
        attrs.update(step=self.step)
        return attrs
