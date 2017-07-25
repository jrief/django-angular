# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.html import format_html

from djng import app_settings


class DropFileWidget(widgets.Widget):
    signer = signing.Signer()

    def __init__(self, attrs=None, area_label=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        self.area_label = area_label
        self.attrs.update({
            'ng-class': 'getClass()',
            'ngf-drop': 'uploadFiles($files)',
            'ngf-select': 'uploadFiles($files)',
        })

    def render(self, name, value, attrs=None):
        extra_attrs = dict(attrs, name=name)
        if value:
            extra_attrs.update(style='background-image: url({});'.format(self.get_background_url(value)))
            extra_attrs.update(previous_image=self.signer.sign(value.name))
        final_attrs = self.build_attrs(self.attrs, extra_attrs=extra_attrs)
        delete_button = format_html('<span djng-fileupload-button="{}" ng-click="deleteImage()" ng-hide="isEmpty()"></span>',
                                    attrs['ng-model'])
        drag_area = format_html('<textarea {}>{}</textarea>', flatatt(final_attrs), self.area_label)
        return format_html('<div class="drop-box">{}{}</div>', drag_area, delete_button)

    def get_background_url(self, value):
        return ''  # render an icon, depending on the file type


class DropImageWidget(DropFileWidget):
    thumbnail_size = app_settings.THUMBNAIL_SIZE

    def __init__(self, **kwargs):
        if 'easy_thumbnails' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("'djng.forms.fields.ImageField' requires 'easy-thubnails' to be installed")
        super(DropImageWidget, self).__init__(**kwargs)

    def get_background_url(self, value):
        from easy_thumbnails.files import get_thumbnailer

        thumbnail_options = {'crop': True, 'size': self.thumbnail_size}
        thumbnailer = get_thumbnailer(value)
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        return thumbnail.url
