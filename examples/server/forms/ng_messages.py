# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.core.exceptions import ValidationError
from djangular.forms import NgModelFormMixin, NgFormValidationMixin, NgMessagesMixin

from . import subscribe_form


class SubscribeForm(NgMessagesMixin, NgModelFormMixin, NgFormValidationMixin, subscribe_form.SubscribeForm):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()
