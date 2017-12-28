# -*- coding: utf-8 -*-
import six

from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import QueryDict
from django.test import override_settings, TestCase, RequestFactory

from djng.middleware import AngularUrlMiddleware

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
    url(r'^home2/$', dummy_view2, name='include1-home2'),
]

urlpatterns = [
    url(r'^$', dummy_view, name='home'),
    url(r'^(\d)/(\d)/(\d)/$', dummy_view, name='home_args'),
    url(r'^(?P<id>\d)/(?P<id2>\d)/(?P<id3>\d)$', dummy_view, name='home_kwargs'),
    url(r'^include/', include(include1)),
]


@override_settings(ROOT_URLCONF=TEST_URLCONF_PATH)
class TestUrlResolverView(TestCase):
    pattern_dict = None

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('test', 'test@example.com', 'password')
        self.middleware = AngularUrlMiddleware()
        self.url_name_arg = 'djng_url_name'
        self.args_prefix = 'djng_url_args'
        self.kwarg_prefix = 'djng_url_kwarg_'
        super(TestUrlResolverView, self).setUp()

    def test_resolver_path_resolution(self):
        """
        Both request.path and request.path_info should be updated to correct url
        """
        url_name = 'home'
        data = {
            self.url_name_arg: url_name
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home'))
        self.assertEqual(request.path_info, reverse('home'))
        self.assertEqual(request.get_full_path(), reverse('home'))

    def test_resolver_path_resolution_include(self):
        url_name = 'include1-home2'
        data = {
            self.url_name_arg: url_name
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse(url_name))

    def test_middleware_request_not_modified(self):
        """
        If request.path != <AngularUrlMiddleware.ANGULAR_REVERSE> request must not be modified
        """
        path = '/some/other/url'
        request = self.factory.get(path)
        self.middleware.process_request(request)
        self.assertEqual(request.path, path)

    def test_request_attributes_retention(self):
        """
        Request attributes, such as .user or .session must not be modified
        """
        url_name = 'include1-home2'
        data = {
            self.url_name_arg: url_name
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        request.user = self.user
        self.middleware.process_request(request)
        self.assertEqual(request.user, self.user)

    def test_get_args_removal(self):
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

        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
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

        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.GET, query_dict)

    def test_get_kwargs_removal(self):
        """
        GET kwarg parameters for url resolution should be removed, others kept
        """
        args = {'test': '123'}
        data = {
            self.url_name_arg: 'home_kwargs',
            self.kwarg_prefix + 'id': 1,
            self.kwarg_prefix + 'id2': 2,
            self.kwarg_prefix + 'id3': 3
        }
        data.update(args)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(args)

        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.GET, query_dict)

    def test_kwargs_resolution(self):
        data = {
            self.url_name_arg: 'home_kwargs',
            self.kwarg_prefix + 'id': 1,
            self.kwarg_prefix + 'id2': 2,
            self.kwarg_prefix + 'id3': 3
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home_kwargs', kwargs={'id': 1, 'id2': 2, 'id3': 3}))

    def test_empty_args_handling(self):
        """Args that are empty strings should be ignored"""
        data = {
            self.url_name_arg: 'home',
            self.args_prefix: ['', ''],
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home'))
        self.assertEqual(request.path_info, reverse('home'))
        self.assertEqual(request.get_full_path(), reverse('home'))

    def test_empty_kwargs_handling(self):
        """Kwargs whose values are empty strings should be ignored"""
        url_name = 'home'
        data = {
            self.url_name_arg: url_name,
            self.kwarg_prefix + 'id': '',
        }
        request = self.factory.get(AngularUrlMiddleware.ANGULAR_REVERSE, data=data)
        self.middleware.process_request(request)
        self.assertEqual(request.path, reverse('home'))
        self.assertEqual(request.path_info, reverse('home'))
        self.assertEqual(request.get_full_path(), reverse('home'))
