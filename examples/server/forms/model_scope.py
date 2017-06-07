# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from djng.forms import NgModelFormMixin
from djng.forms.fields import ImageField
from . import subscribe_form


class SubscribeForm(NgModelFormMixin, subscribe_form.SubscribeForm):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    avatar = ImageField(
        label='Photo of yourself',
        fileupload_url=reverse_lazy('fileupload'),
        area_label='Drop image here or click to upload',
        required=True)

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()
