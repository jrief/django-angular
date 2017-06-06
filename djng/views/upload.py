# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.views.generic import View
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import data_uri


class FileUploadView(View):
    storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'upload_temp'))

    def post(self, request, *args, **kwargs):
        size = int(request.POST.get('width', '200px').rstrip('px')), int(request.POST.get('height', '200px').rstrip('px'))
        thumbnail_options = {'crop': True, 'size': size}
        data = {}
        prefix = get_random_string(length=16, allowed_chars='abcdefghijklmnopqrstuvwxyz')  # prevent filename guessing
        for name, file_obj in request.FILES.items():
            available_name = self.storage.get_available_name(os.path.join(prefix, file_obj.name.lower()))
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
