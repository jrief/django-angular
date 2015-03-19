# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.test import TestCase, RequestFactory
from djangular.middleware import DjangularUrlMiddleware


def dummy_view(request, *args, **kwargs):
    return {
        'name': 'DummyView',
        'request': request,
        'args': args,
        'kwargs': kwargs
    }


def dummy_view2(request, *args, **kwargs):
    return {
        'name': 'DummyView2',
        'request': request,
        'args': args,
        'kwargs': kwargs
    }

include1 = patterns('',
    url(r'^home2/$', dummy_view2, name='home2')
)

urlpatterns = patterns('',
    url(r'^$', dummy_view, name='home'),
    url(r'^(\d)/(\d)/(\d)/$', dummy_view, name='home_args'),
    url(r'^(?P<id>\d)/(?P<id2>\d)/(?P<id3>\d)$', dummy_view, name='home_kwargs'),
    url(r'^include/', include(include1, namespace='include1'))
)


class TestUrlResolverView(TestCase):
    pattern_dict = None

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DjangularUrlMiddleware(urlconf='server.tests.test_urlresolver_view')
        self.url_name_arg = 'djng_url_name'
        self.args_prefix = 'djng_url_args'
        self.kwarg_prefix = 'djng_url_kwarg_'
        super(TestUrlResolverView, self).setUp()

    def test_request_path(self):
        data = {
            self.url_name_arg: 'home'
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        response = self.middleware.process_request(request)
        self.assertEqual(response['request'].path, '/')

    def test_middleware_return_none(self):
        """
        If request.path != <DjangularUrlMiddleware.ANGULAR_REVERSE> return None, so request is processed normally
        """
        request = self.factory.get('/some/other/url/')
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    def test_resolver_view_resolution(self):
        data = {
            self.url_name_arg: 'home'
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        response = self.middleware.process_request(request)
        self.assertEqual(response['name'], 'DummyView')

    def test_view_resolution_include(self):
        data = {
            self.url_name_arg: 'include1:home2'
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        response = self.middleware.process_request(request)
        self.assertEqual(response['name'], 'DummyView2')

    def test_args(self):
        data = {
            self.url_name_arg: 'home_args',
            self.args_prefix: [1, 2, 3]
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        response = self.middleware.process_request(request)
        self.assertEqual((u'1', u'2', u'3'), response['args'])

    def test_kwargs(self):
        data = {
            self.url_name_arg: 'home_kwargs',
            self.kwarg_prefix + 'id': 1,
            self.kwarg_prefix + 'id2': 2,
            self.kwarg_prefix + 'id3': 3
        }
        expected_view_kwargs = {'id2': u'2', 'id': u'1', 'id3': u'3'}
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        response = self.middleware.process_request(request)
        self.assertEqual(expected_view_kwargs, response['kwargs'])
