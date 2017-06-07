# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from django.http import JsonResponse

if 'easy_thumbnails' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("'FileUploadView' can only be used in combination with 'easy_thumbnails'")

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import data_uri

from djng import app_settings


class FileUploadView(View):
    storage = app_settings.upload_storage
    thumbnail_size = app_settings.THUMBNAIL_SIZE

    def post(self, request, *args, **kwargs):
        thumbnail_options = {'crop': True, 'size': self.thumbnail_size}
        data = {}
        for name, file_obj in request.FILES.items():
            available_name = self.storage.get_available_name(file_obj.name)
            temp_name = self.storage.save(available_name, file_obj)
            thumbnailer = get_thumbnailer(self.storage.path(temp_name), relative_name=available_name)
            thumbnail = thumbnailer.generate_thumbnail(thumbnail_options)
            data[name] = {
                'url': 'url({})'.format(data_uri(thumbnail)),
                'temp_name': temp_name,
                'image_name': file_obj.name,
                'image_size': file_obj.size,
                'charset': file_obj.charset,
                'content_type': file_obj.content_type,
                'content_type_extra': file_obj.content_type_extra,
            }
        return JsonResponse(data)
