# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import resolve
from django.test import TestCase
from django.test.client import Client
from django.template import RequestContext, Template


class TemplateTagsTest(TestCase):
    urls = 'server.tests.urls'

    def test_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        request = client.get('/straight_methods/')
        request.META = {}
        request.is_secure = lambda: False
        request.get_host = lambda: 'localhost'
        template = Template('{% load djangular_tags %}x="{% csrf_token %}"')
        context = RequestContext(request, {'csrf_token': '123'})
        response = template.render(context)
        self.assertInHTML(response, 'x=""')

    def test_load_all_urls(self):
        client = Client()
        request = client.get('/sub_methods/sub/app/')
        template = Template("{% load djangular_tags %}{% load_djng_urls %}")
        context = RequestContext(request)
        response = template.render(context)
        self.assertIn('"submethods:sub:app": "/sub_methods/sub/app/"', response)
        self.assertIn('"straightmethods": "/straight_methods/"', response)

    def test_load_self_urls(self):
        client = Client()
        request = client.get('/sub_methods/sub/app/')
        template = Template("{% load djangular_tags %}{% load_djng_urls 'SELF' %}")
        context = RequestContext(request)
        # Currently the test request does not include a ResolverMatch object:
        # https://code.djangoproject.com/ticket/16087
        request.resolver_match = resolve('/sub_methods/sub/app/')
        response = template.render(context)
        self.assertIn('"submethods:sub:app": "/sub_methods/sub/app/"', response)
        self.assertNotIn('"straightmethods": "/straight_methods/"', response)

    def test_load_root_urls(self):
        client = Client()
        request = client.get('/sub_methods/sub/app/')
        template = Template("{% load djangular_tags %}{% load_djng_urls None '' %}")
        context = RequestContext(request)
        response = template.render(context)
        self.assertNotIn('"submethods:sub:app": "/sub_methods/sub/app/"', response)
        self.assertIn('"straightmethods": "/straight_methods/"', response)
