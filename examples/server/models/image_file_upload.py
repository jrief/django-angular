# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.db import models
from djng.forms import NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm


class SubscribeUser(models.Model):
    full_name = models.CharField(
        "Full name",
        max_length=99)

    avatar = models.ImageField("Avatar", blank=False, null=True)

    permit = models.FileField("Permit", blank=True, null=True)


class SubscribeForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    use_required_attribute = False
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    class Meta:
        model = SubscribeUser
        fields = ['full_name', 'avatar', 'permit']
