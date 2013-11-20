# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.template import RequestContext, Template


class TemplateTagsTest(TestCase):
    def test_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        request = client.get('/dummy.html')
        request.META = {}
        template = Template('{% load djangular_tags %}x="{% csrf_token %}"')
        context = RequestContext(request, {'csrf_token': '123'})
        response = template.render(context)
        self.assertInHTML(response, 'x=""')
