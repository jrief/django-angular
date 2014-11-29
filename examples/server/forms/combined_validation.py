# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.core.exceptions import ValidationError
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from . import subscribe_form


class SubscribeForm(NgModelFormMixin, NgFormValidationMixin, subscribe_form.SubscribeForm):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    def get_widget_attrs(self, bound_field):
        attrs = super(SubscribeForm, self).get_widget_attrs(bound_field)
        attrs['ng-model-options'] = "{ debounce : { 'default' : 500, blur : 0 } }"
        return attrs

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()


