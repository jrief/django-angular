# -*- coding: utf-8 -*-
from django.db import models

class DummyModel(models.Model):
    name = models.CharField(max_length=255)