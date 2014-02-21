# -*- coding: utf-8 -*-
import datetime

from django.db import models


class DummyModel(models.Model):
    name = models.CharField(max_length=255)
    model2 = models.ForeignKey('DummyModel2')
    timefield = models.DateTimeField(default=datetime.datetime.now)


class DummyModel2(models.Model):
    name = models.CharField(max_length=255)