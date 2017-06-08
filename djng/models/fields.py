# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import files


if 'easy_thumbnails' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("'FileUploadView' can only be used in combination with 'easy_thumbnails'")


class ImageField(files.ImageField):
    def formfield(self, **kwargs):
        defaults = {'help_text': self.help_text, 'required': not self.blank, 'label': self.verbose_name}
        defaults.update(kwargs)
        return fields.ImageField(**defaults)
from djng.forms import fields
