# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.core.urlresolvers import reverse_lazy
from djng.forms import NgModelFormMixin
from djng.forms.fields import ImageField
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm
from ..models.subscribe import SubscribeUser

class SubscribeForm(NgModelFormMixin, Bootstrap3ModelForm):
#    use_required_attribute = False
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    avatar = ImageField(
        label='Your Avatar',
        fileupload_url=reverse_lazy('fileupload'),
        area_label='Drop image here or click to upload')

    class Meta:
        model = SubscribeUser
        fields = ['first_name', 'last_name', 'avatar']
