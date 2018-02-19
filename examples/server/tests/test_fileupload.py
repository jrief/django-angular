# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, json

from django.conf import settings
from django.urls import reverse
from django.core import signing
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.test import override_settings, TestCase
from django.test.client import Client

from pyquery.pyquery import PyQuery

from djng import app_settings
from djng.forms import NgModelFormMixin, NgForm
from djng.forms.fields import ImageField


class TestUploadForm(NgModelFormMixin, NgForm):
    scope_prefix = 'my_data'
    form_name = 'my_form'

    avatar = ImageField()



class FileUploadTest(TestCase):
    signer = signing.Signer()
    storage = app_settings.upload_storage

    def tearDown(self):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, 'upload_temp/sample-image.jpg'))
        except:
            pass

    def upload_image(self):
        client = Client()
        upload_filename = os.path.join(os.path.dirname(__file__), 'sample-image.jpg')
        with open(upload_filename, 'rb') as fp:
            upload_url = reverse('fileupload')
            response = client.post(upload_url, {'file:0': fp, 'filetype': 'image'})
        self.assertEquals(response.status_code, 200)
        return json.loads(response.content.decode('utf-8'))

    def test_upload(self):
        content = self.upload_image()
        self.assertTrue('file:0' in content)
        self.assertTrue(content['file:0']['url'].startswith('url(data:application/octet-stream;base64,/9j/4AAQSkZJRgABA'))
        self.assertEquals(content['file:0']['file_name'], 'sample-image.jpg')
        self.assertEquals(content['file:0']['content_type'], 'image/jpeg')
        self.assertEquals(self.signer.unsign(content['file:0']['temp_name']), 'sample-image.jpg')

    def test_render_widget(self):
        form = TestUploadForm()
        htmlsource = form.as_p()
        dom = PyQuery(htmlsource)
        textarea = dom('div.drop-box textarea')
        self.assertEquals(textarea.attr('djng-fileupload-url'), reverse('fileupload'))
        self.assertEquals(textarea.attr('ngf-drop'), 'uploadFile($file, "image", "id_avatar", "my_data[\'avatar\']")')
        self.assertEquals(textarea.attr('ngf-select'), 'uploadFile($file, "image", "id_avatar", "my_data[\'avatar\']")')

        delete_button = dom('div.drop-box img.djng-btn-trash')
        self.assertEquals(delete_button.attr('src'), '/static/djng/icons/image/trash.svg')
        self.assertEquals(delete_button.attr('djng-fileupload-button'), '')
        self.assertEquals(delete_button.attr('ng-click'), 'deleteImage("id_avatar", "my_data[\'avatar\']")')

    def test_receive_small_image(self):
        content = self.upload_image()
        content['file:0'].pop('url')
        data = {'avatar': content['file:0']}
        form = TestUploadForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['avatar'], InMemoryUploadedFile)
        self.assertEquals(form.cleaned_data['avatar'].name, "sample-image.jpg")

        # TODO: delete this image again
        # stored_image = self.storage.save('persisted.jpg', form.cleaned_data['avatar'].file)
        # initial = {'avatar': stored_image}
        # form = TestUploadForm(initial=initial)
        # htmlsource = form.as_p()

    @override_settings(FILE_UPLOAD_MAX_MEMORY_SIZE=50000)
    def test_receive_large_image(self):
        content = self.upload_image()
        content['file:0'].pop('url')
        data = {'avatar': content['file:0']}
        form = TestUploadForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data['avatar'], TemporaryUploadedFile)
        self.assertEquals(form.cleaned_data['avatar'].name, "sample-image.jpg")
