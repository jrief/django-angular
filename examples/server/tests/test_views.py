# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.views.generic import View
from djng.views.mixins import JSONResponseMixin, allow_remote_invocation, allowed_action


class JSONResponseView(JSONResponseMixin, View):
    @allow_remote_invocation
    def method_allowed(self, in_data=None):
        return {'success': True}

    @allow_remote_invocation
    def method_echo(self, in_data=None):
        return {'success': True, 'echo': in_data}

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

    def test_post_method_echo(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_DJNG_REMOTE_METHOD='method_echo',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        out_data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(out_data['success'])
        self.assertDictEqual(out_data['echo'], self.data)

    def test_csrf_exempt_dispatch(self):
        request = self.factory.post('/dummy.json')
        response = JSONResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('utf-8'), 'This view can not handle method POST')

    def test_post_method_undefined(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('utf-8'), 'This view can not handle method POST')

    def test_post_method_not_callable(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_DJNG_REMOTE_METHOD='no_such_method',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('utf-8'), 'This view can not handle method POST')

    def test_post_method_is_forbidden(self):
        request = self.factory.post('/dummy.json',
            data=json.dumps(self.data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_DJNG_REMOTE_METHOD='method_forbidden',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode('utf-8'), "Method 'JSONResponseView.method_forbidden' has no decorator '@allow_remote_invocation'")

    def test_get_method_forbidden_ok(self):
        request = self.factory.get('/dummy.json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request, invoke_method='method_forbidden')
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        out_data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(out_data['success'])

    def test_get_method_forbidden_fail(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='method_forbidden',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode('utf-8'), "Method 'JSONResponseView.method_forbidden' has no decorator '@allow_remote_invocation'")

    def test_get_method_not_callable(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='no_such_method',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('utf-8'), "This view can not handle method GET")

    def test_get_method_allowed(self):
        request = self.factory.get('/dummy.json',
            HTTP_DJNG_REMOTE_METHOD='method_allowed',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        out_data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(out_data['success'])

    def test_post_pass_through(self):
        request = self.factory.post('/dummy.json', data=self.data)
        response = DummyResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'bar')

    def test_get_pass_through(self):
        request = self.factory.get('/dummy.json')
        response = DummyResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'GET OK')
