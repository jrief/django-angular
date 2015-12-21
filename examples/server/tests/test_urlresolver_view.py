# -*- coding: utf-8 -*-
import six
from django.conf.urls import url, include
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase, RequestFactory
from djangular.middleware import DjangularUrlMiddleware

TEST_URLCONF_PATH = 'server.tests.test_urlresolver_view'


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


include1 = [
    url(r'^home2/$', dummy_view2, name='home2'),
]

urlpatterns = [
    url(r'^$', dummy_view, name='home'),
    url(r'^(\d)/(\d)/(\d)/$', dummy_view, name='home_args'),
    url(r'^(?P<id>\d)/(?P<id2>\d)/(?P<id3>\d)$', dummy_view, name='home_kwargs'),
    url(r'^include/', include(include1, namespace='include1')),
]


class TestUrlResolverView(TestCase):
    pattern_dict = None
    urls = 'server.tests.test_urlresolver_view'

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DjangularUrlMiddleware()
        self.url_name_arg = 'djng_url_name'
        self.args_prefix = 'djng_url_args'
        self.kwarg_prefix = 'djng_url_kwarg_'
        super(TestUrlResolverView, self).setUp()

    def test_resolver_path_resolution(self):
        url_name = 'home'
        data = {
            self.url_name_arg: url_name
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home'))

    def test_resolver_path_resolution_include(self):
        url_name = 'include1:home2'
        data = {
            self.url_name_arg: url_name
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse(url_name))

    def test_middleware_request_not_modified(self):
        """
        If request.path != <DjangularUrlMiddleware.ANGULAR_REVERSE> request must not be modified
        """
        path = '/some/other/url'
        request = self.factory.get(path)
        self.middleware.process_request(request)
        self.assertEqual(request.path, path)

    def test_get_args(self):
        """
        GET parameters for url resolution should be removed, others kept
        """
        args = {'test': '123'}
        data = {
            self.url_name_arg: 'home_args',
            self.args_prefix: [1, 2, 3],
        }
        data.update(args)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(args)

        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.GET, query_dict)

    def test_get_args_with_encoding(self):
        """
        Similar test to test_with_args but with special characters.
        """
        if six.PY3:
            args = {'params': 'åäö'}
        else:
            args = {'param': u'åäö'}
        data = {
            self.url_name_arg: 'home_args',
            self.args_prefix: [1, 2, 3],
        }
        data.update(args)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(args)

        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.GET, query_dict)

    def test_kwargs_resolution(self):
        data = {
            self.url_name_arg: 'home_kwargs',
            self.kwarg_prefix + 'id': 1,
            self.kwarg_prefix + 'id2': 2,
            self.kwarg_prefix + 'id3': 3
        }
        request = self.factory.get(DjangularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home_kwargs', kwargs={'id': 1, 'id2': 2, 'id3': 3}))
