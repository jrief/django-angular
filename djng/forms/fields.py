# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .widgets import DropFileInput


class FloatField(forms.FloatField):
    """
    The internal ``django.forms.FloatField`` does not handle the step value in its number widget.
    """
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super(FloatField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(FloatField, self).widget_attrs(widget)
        attrs.update(step=self.step)
        return attrs


class ImageField(forms.Field):
    storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'upload_temp'))

    def __init__(self, *args, **kwargs):
        accept = kwargs.pop('accept', 'image/*')
        fileupload_url = kwargs.pop('fileupload_url', reverse_lazy('fileupload'))
        button_label = kwargs.pop('button_label', _("Drop or click here to upload"))
        attrs = {
            'accept': accept,
            'ngf-pattern': accept,
            'fileupload-url': fileupload_url,
        }
        kwargs.update(widget=DropFileInput(attrs=attrs, button_label=button_label))
        super(ImageField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        return value

    def to_python(self, value):
        if not (isinstance(value, dict) and 'temp_name' in value):
            return
        try:
            file = self.storage.open(value['temp_name'], 'rb')
            file_size = self.storage.size(value['temp_name'])
            if file_size < settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                return InMemoryUploadedFile(
                    file=file,
                    field_name=None,
                    name=value['image_name'],
                    charset=value['charset'],
                    content_type=value['content_type'],
                    content_type_extra=value['content_type_extra'],
                    size=file_size,
                )
            else:
                return TemporaryUploadedFile(
                    value['image_name'],
                    value['content_type'],
                    0,
                    value['charset'],
                    content_type_extra=value['content_type_extra'],
                )
        except Exception as excp:
            raise ValidationError("File upload failed. {}: {}".format(excp.__class__.__name__, excp))
