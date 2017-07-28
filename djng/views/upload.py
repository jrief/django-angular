# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import SuspiciousMultipartForm
from django.core import signing
from django.views.generic import View
from django.http import JsonResponse

from djng import app_settings
from djng.forms.fields import FileField, ImageField


class FileUploadView(View):
    storage = app_settings.upload_storage
    thumbnail_size = app_settings.THUMBNAIL_OPTIONS
    signer = signing.Signer()

    def post(self, request, *args, **kwargs):
        if request.POST.get('file_type') == 'file':
            field = FileField
        elif request.POST.get('file_type') == 'image':
            field = ImageField
        else:
            field = ImageField
#            raise SuspiciousMultipartForm("Missing attribute 'file_type' in form data.")
        data = {}
        for name, file_obj in request.FILES.items():
            data[name] = field.preview(file_obj)
        return JsonResponse(data)
