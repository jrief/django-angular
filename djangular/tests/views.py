# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic import View
from djangular.views.mixins import JSONResponseMixin, allowed_action


class JSONResponseView(JSONResponseMixin, View):
    @allowed_action
    def action_one(self, in_data):
        return {'success': True}


class JSONResponseMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_csrf_exempt_dispatch(self):
        request = self.factory.post('/dummy.json')
        response = JSONResponseView.as_view()(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'Expected an XMLHttpRequest')

    def test_action_undefined(self):
        data = {'foo': 'bar'}
        request = self.factory.post('/dummy.json',
            data=simplejson.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'POST data is not valid JSON: action="None" is undefined or not callable')

    def test_action_not_callable(self):
        data = {'foo': 'bar', 'action': 'blah'}
        request = self.factory.post('/dummy.json',
            data=simplejson.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        self.assertEqual(response.content, 'POST data is not valid JSON: action="None" is undefined or not callable')

    def test_action_is_callable(self):
        data = {'foo': 'bar', 'action': 'action_one'}
        request = self.factory.post('/dummy.json',
            data=simplejson.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json; charset=utf-8;',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = JSONResponseView().post(request)
        self.assertIsInstance(response, HttpResponse)
        out_data = simplejson.loads(response.content)
        self.assertTrue(out_data['success'])
