# -*- coding: utf-8 -*-
from django import forms


class AddPlaceholderFormMixin(object):
    """
    Iterate over all fields in a form and add an attribute placeholder containing the current label.
    Use this in Django-1.4, it can be removed with Django-1.5, since there fields are handled in a
    more flexible way.
    """
    def __init__(self, *args, **kwargs):
        super(AddPlaceholderFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.PasswordInput)):
                field.widget.attrs.setdefault('placeholder', field.label)
