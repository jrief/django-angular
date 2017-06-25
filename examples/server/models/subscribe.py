# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.db import models
from djng.models.fields import ImageField


class SubscribeUser(models.Model):
    first_name = models.CharField(
        'First name',
        blank=False,
        max_length=20)

    last_name = models.CharField(
        'Last name',
        blank=False,
        max_length=50)

    avatar = ImageField(
        'Your Avatar')
