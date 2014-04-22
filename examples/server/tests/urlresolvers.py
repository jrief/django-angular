# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from djangular.core.urlresolvers import get_all_remote_methods, get_current_remote_methods


class TemplateRemoteMethods(TestCase):
    urls = 'server.test_urls'

    def test_first(self):
        client = Client.get('/straight_methods/')
        print client

    def test_get_all_remote_methods(self):
        remote_methods = get_all_remote_methods()
        print remote_methods
