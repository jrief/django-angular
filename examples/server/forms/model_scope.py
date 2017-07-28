# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.core.exceptions import ValidationError
from djng.forms import NgModelFormMixin
from djng.forms.fields import FileField, ImageField
from . import subscribe_form


class SubscribeForm(NgModelFormMixin, subscribe_form.SubscribeForm):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    avatar = ImageField(label='Photo of yourself')

    permit = FileField(label='Your permit', accept='application/pdf')

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()
