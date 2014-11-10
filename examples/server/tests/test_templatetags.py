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

    def test_load_all_urls(self):
        client = Client()
        response = client.get('/url_resolvers/')
        self.assertIn('"submethods:sub:app": "/sub_methods/sub/app/"', str(response.content))
        self.assertIn('"straightmethods": "/straight_methods/"', str(response.content))

    def test_load_self_urls(self):
        client = Client()
        response = client.get('/sub_methods/sub/app/', {'load': 'self_urls'})
        self.assertIn('"submethods:sub:app": "/sub_methods/sub/app/"', str(response.content))
        self.assertNotIn('"straightmethods": "/straight_methods/"', str(response.content))

    def test_load_root_urls(self):
        client = Client()
        response = client.get('/url_resolvers/', {'load': 'root_urls'})
        self.assertNotIn('"submethods:sub:app": "/sub_methods/sub/app/"', str(response.content))
        self.assertIn('"straightmethods": "/straight_methods/"', str(response.content))
