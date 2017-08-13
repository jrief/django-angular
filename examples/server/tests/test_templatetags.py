# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import override_settings, TestCase
from django.test.client import Client


TEST_URL_PATH = 'server.tests.urls'


@override_settings(ROOT_URLCONF=TEST_URL_PATH)
class TemplateTagsTest(TestCase):

    def test_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/straight_methods/')
        self.assertContains(response, '<script>var x="')

    def test_angularon_tag(self):
        client = Client()
        response = client.get('/angular_tag/', {'switch': ''})
        self.assertContains(response, 'Hello World')
        response = client.get('/angular_tag/', {'switch': 'yes'})
        self.assertNotContains(response, 'Hello World')
        response = client.get('/angular_tag/', {'switch': '', 'tmpl_id': 'expand_object'})
        self.assertNotContains(response, 'expandme.foo')
        response = client.get('/angular_tag/', {'switch': 'yes', 'tmpl_id': 'expand_object'})
        self.assertContains(response, 'expandme.foo')
        response = client.get('/angular_tag/', {'switch': 'yes', 'tmpl_id': 'expand_array'})
        self.assertContains(response, 'expandme[1].foo')
        response = client.get('/angular_tag/', {'switch': '', 'tmpl_id': 'expand_array'})
        self.assertContains(response, 'one')

    @override_settings(USE_I18N=True, LANGUAGE_CODE='de')
    def test_locale_script_german(self):
        client = Client()
        response = client.get('/locale_script_tag/')
        self.assertContains(response, 'angular-locale_de.js')

    def test_locale_script_default(self):
        client = Client()
        response = client.get('/locale_script_tag/')
        self.assertContains(response, 'angular-locale_en.js')
