# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django import forms
from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.models import Source, Thumbnail

from djng import app_settings
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
    storage = app_settings.upload_storage
    signer = signing.Signer()

    def __init__(self, *args, **kwargs):
        accept = kwargs.pop('accept', 'image/*')
        fileupload_url = kwargs.pop('fileupload_url', reverse_lazy('fileupload'))
        area_label = kwargs.pop('area_label', _("Drop or click here to upload"))
        attrs = {
            'accept': accept,
            'ngf-pattern': accept,
            'fileupload-url': fileupload_url,
        }
        kwargs.update(widget=DropFileInput(attrs=attrs, area_label=area_label))
        super(ImageField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            if value['temp_name'] is False and value['previous_image']:
                # Delete previous image
                previous_image = self.signer.unsign(value['previous_image'])
                self.remove_images(previous_image)
                return False
            if value['temp_name'] is None or value['temp_name'] is True:
                # Nothing changed
                return
        except (KeyError, TypeError, signing.BadSignature) as excp:
            raise ValidationError("Got bogous upstream data")
        try:
            temp_file = self.storage.open(value['temp_name'], 'rb')
            file_size = self.storage.size(value['temp_name'])
            if file_size < settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                obj = InMemoryUploadedFile(
                    file=temp_file,
                    field_name=None,
                    name=value['image_name'],
                    charset=value['charset'],
                    content_type=value['content_type'],
                    content_type_extra=value['content_type_extra'],
                    size=file_size,
                )
            else:
                obj = TemporaryUploadedFile(
                    value['image_name'],
                    value['content_type'],
                    0,
                    value['charset'],
                    content_type_extra=value['content_type_extra'],
                )
                while True:
                    chunk = temp_file.read(0x10000)
                    if not chunk:
                        break
                    obj.file.write(chunk)
                obj.file.seek(0)
                obj.file.size = file_size
        except IOError:
            obj = None
        except Exception as excp:
            raise ValidationError("File upload failed. {}: {}".format(excp.__class__.__name__, excp))
        else:
            self.storage.delete(value['temp_name'])
        return obj

    def remove_images(self, image_name):
        try:
            source = Source.objects.get(name=image_name)
            for thumb in Thumbnail.objects.filter(source=source):
                default_storage.delete(thumb.name)
                thumb.delete()
            source.delete()
        except Source.DoesNotExist:
            pass
        default_storage.delete(image_name)
