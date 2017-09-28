# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form


class SubscribeForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'
    use_required_attribute = False

    full_name = fields.CharField(
        label='Full name',
        min_length=3,
        max_length=99,
        required=True,
    )

    avatar = fields.ImageField(
        label='Photo of yourself',
        required=True,
    )

    permit = fields.FileField(
        label='Your permit as PDF',
        accept='application/pdf',
        required=False,
    )

    def clean_avatar(self):
        """
        For instance, here you can move the temporary file stored in
        `self.cleaned_data['avatar'].file` to a permanent location.
        """
        self.cleaned_data['avatar'].file
