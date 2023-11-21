# -*- coding: utf-8 -*-

from django.test import override_settings, TestCase
from django.test.client import RequestFactory

from djng.core.urlresolvers import get_all_remote_methods, get_current_remote_methods

from .urls import RemoteMethodsView


TEST_URL_PATH = 'server.tests.urls'


@override_settings(ROOT_URLCONF=TEST_URL_PATH)
class TemplateRemoteMethods(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_current_remote_methods(self):
        view = RemoteMethodsView()
        view.request = self.factory.get('/straight_methods/')
        remote_methods = get_current_remote_methods(view)
        expected = {
            'foo': {'url': '/straight_methods/', 'headers': {'DjNg-Remote-Method': 'foo'}, 'method': 'auto'},
            'bar': {'url': '/straight_methods/', 'headers': {'DjNg-Remote-Method': 'bar'}, 'method': 'auto'},
        }
        self.assertDictEqual(remote_methods, expected)

    def test_get_all_remote_methods(self):
        remote_methods = get_all_remote_methods()
        expected = {
            'urlresolvertags': {'blah': {'url': '/url_resolvers/', 'headers': {'DjNg-Remote-Method': 'blah'}, 'method': 'auto'}},
            'submethods': {
                'app': {'foo': {'url': '/sub_methods/sub/app/', 'headers': {'DjNg-Remote-Method': 'foo'}, 'method': 'auto'},
                        'bar': {'url': '/sub_methods/sub/app/', 'headers': {'DjNg-Remote-Method': 'bar'}, 'method': 'auto'}},
            },
        }
        self.assertDictEqual(remote_methods, expected)
