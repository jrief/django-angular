# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic import View
from djangular.views.mixins import JSONResponseMixin, allowed_action


class JSONResponseView(JSONResponseMixin, View):
    @allowed_action
    def action_one(self, in_data):
        return { 'success': True }

    def action_two(self):
        """
        decorator @allowed_action is missing
        """
        return { 'success': True }


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

    def test_csrf_exempt_dispatch(self):
        request = self.factory.post('/dummy.json')
        response = JSONResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_action_undefined(self):
        data = {'foo': 'bar'}
        request = self.factory.post('/dummy.json',
            data=json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_action_not_callable(self):
        data = {'foo': 'bar', 'action': 'blah'}
        request = self.factory.post('/dummy.json',
            data=json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'This view can not handle method POST')

    def test_action_is_callable(self):
        data = {'foo': 'bar', 'action': 'action_one'}
        request = self.factory.post('/dummy.json',
            data=json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        out_data = json.loads(response.content)
        self.assertTrue(out_data['success'])

    def test_action_is_forbidden(self):
        data = {'foo': 'bar', 'action': 'action_two'}
        request = self.factory.post('/dummy.json',
            data=json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'Method "action_two" is not decorated with @allowed_action')

    def test_ajax_get_action(self):
        request = self.factory.get('/dummy.json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().get(request, action='action_two')
        self.assertIsInstance(response, HttpResponse)
        out_data = json.loads(response.content)
        self.assertTrue(out_data['success'])

    def test_post_pass_through(self):
        request = self.factory.post('/dummy.json', data={'foo': 'bar'})
        response = DummyResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content, 'bar')

    def test_get_pass_through(self):
        request = self.factory.get('/dummy.json')
        response = DummyResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content, 'GET OK')
