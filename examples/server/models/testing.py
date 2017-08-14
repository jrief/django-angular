# -*- coding: utf-8 -*-
import datetime
from django.db import models


class DummyModel(models.Model):
    name = models.CharField(max_length=255)
    model2 = models.ForeignKey('DummyModel2', on_delete=models.CASCADE)
    timefield = models.DateTimeField(default=datetime.datetime.now)


class DummyModel2(models.Model):
    name = models.CharField(max_length=255)


class SimpleModel(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)


class M2MModel(models.Model):
    dummy_models = models.ManyToManyField(DummyModel2)
