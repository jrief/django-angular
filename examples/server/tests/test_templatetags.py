# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import Client


class TemplateTagsTest(TestCase):
    urls = 'server.tests.urls'

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
