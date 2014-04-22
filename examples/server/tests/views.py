# -*- coding: utf-8 -*-
import json
import warnings
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic import View
from djangular.views.mixins import JSONResponseMixin, allow_remote_invocation, allowed_action


class JSONResponseView(JSONResponseMixin, View):
    @allow_remote_invocation
    def method_allowed(self, in_data=None):
        return {'success': True}

    def method_forbidden(self, in_data=None):
        """
        decorator @allow_remote_invocation is missing
        """
        return {'success': True}

    @allowed_action
    def deprecated_action(self, in_data):
        return {'success': True}


class DummyView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('GET OK')

    def post(self, request, *args, **kwargs):
        return HttpResponse(request.POST.get('foo'))


class DummyResponseView(JSONResponseMixin, DummyView):
    pass


class JSONResponseMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.data = {'foo': 'bar'}

    def test_csrf_exempt_dispatch(self):
        request = self.factory.post('/dummy.json')
        response = JSONResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_post_method_undefined(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_post_method_not_callable(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_DJNG_REMOTE_METHOD='no_such_method',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_post_method_is_forbidden(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_DJNG_REMOTE_METHOD='method_forbidden',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, "Method 'JSONResponseView.method_forbidden' has no decorator '@allow_remote_invocation'")

    def test_post_deprecated_action(self):
        with warnings.catch_warnings(record=True) as w:
            data = {'foo': 'bar', 'action': 'deprecated_action'}
            request = self.factory.post('/dummy.json',
                data=json.dumps(data, cls=DjangoJSONEncoder),
                content_type='application/json; charset=utf-8;',
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            response = JSONResponseView().post(request)
            self.assertIsInstance(response, HttpResponse)
            out_data = json.loads(response.content)
            self.assertTrue(out_data['success'])
            self.assertEqual(w[0].message[0], "Using the keyword 'action' inside the payload is deprecated. Please use 'djangoRMI' from module 'ng.django.forms'")

    def test_get_method_forbidden_ok(self):
        request = self.factory.get('/dummy.json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request, invoke_method='method_forbidden')
        self.assertIsInstance(response, HttpResponse)
        out_data = json.loads(str(response.content))
        self.assertTrue(out_data['success'])

    def test_get_deprecated_action(self):
        with warnings.catch_warnings(record=True) as w:
            request = self.factory.get('/dummy.json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            response = JSONResponseView().get(request, action='method_forbidden')
            self.assertIsInstance(response, HttpResponse)
            out_data = json.loads(response.content)
            self.assertTrue(out_data['success'])
            self.assertEqual(w[0].message[0], "Using the keyword 'action' in URLresolvers is deprecated. Please use 'invoke_method' instead")

    def test_get_method_forbidden_fail(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='method_forbidden',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, "Method 'JSONResponseView.method_forbidden' has no decorator '@allow_remote_invocation'")

    def test_get_method_not_callable(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='no_such_method',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        with self.assertRaises(ValueError):
            JSONResponseView().get(request)

    def test_get_method_allowed(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='method_allowed',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request)
        self.assertIsInstance(response, HttpResponse)
        out_data = json.loads(str(response.content))
        self.assertTrue(out_data['success'])

    def test_post_pass_through(self):
        request = self.factory.post('/dummy.json', data=self.data)
        response = DummyResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(str(response.content), 'bar')

    def test_get_pass_through(self):
        request = self.factory.get('/dummy.json')
        response = DummyResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(str(response.content), 'GET OK')
