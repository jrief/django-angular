import json

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.messages.storage.base import Message

from djangular.middleware import AjaxDjangoMessagesMiddleware
from djangular.core.ajax_messages import process_response, is_not_valid_type
from djangular.core.decorators import add_messages_to_response


try:
    import mock
except ImportError:
    import unittest.mock



def get_messages(request):
    return [Message(25, 'this is my message')]

def get_no_messages(request):
    return []

class DummyCBView(View):
	
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'data': 'success'}),
                            status=200,
                            content_type='application/json')


class DummyDecCBView(View):

    @method_decorator(add_messages_to_response)
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'data': 'success'}),
                            status=200,
                            content_type='application/json')




class MessagesDecoratorTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        content = json.loads(response.content)
        messages = content['django_messages']
        message = messages[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['type'], 'success')
        self.assertEqual(message['level'], 25)
        self.assertEqual(message['message'], 'this is my message')
        self.assertEqual(message['tags'], 'success')
        self.assertEqual(content['data']['data'], 'success')

    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_no_messages_added_to_response(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')


class AjaxDjangoMessagesMiddlewareTest(TestCase):
    urls = 'server.tests.urls'

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AjaxDjangoMessagesMiddleware()
    
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content['django_messages']
        message = messages[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['type'], 'success')
        self.assertEqual(message['level'], 25)
        self.assertEqual(message['message'], 'this is my message')
        self.assertEqual(message['tags'], 'success')
        self.assertEqual(content['data']['data'], 'success')

    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_no_messages_added_to_response(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')
    
    @override_settings(DEBUG=True)
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_debug_tool_url_exempt(self):
        request = self.factory.get('__debug__')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')

    @mock.patch('djangular.middleware.EXEMPT', list(('(submethods_app)',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_exempt_app_name(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')

    @mock.patch('djangular.middleware.EXEMPT', list(('[submethods:sub]',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_exempt_namespace(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')

    @mock.patch('djangular.middleware.EXEMPT', list(('submethods:sub:app',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_exempt_namespace_name(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')

    @mock.patch('djangular.middleware.EXEMPT', list(('straightmethods',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_exempt_name(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')


class AjaxMessagesMethodTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        content = json.loads(response.content)
        messages = content['django_messages']
        message = messages[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['type'], 'success')
        self.assertEqual(message['level'], 25)
        self.assertEqual(message['message'], 'this is my message')
        self.assertEqual(message['tags'], 'success')
        self.assertEqual(content['data']['data'], 'success')

    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_no_messages_added_to_response(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        content = json.loads(response.content)
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')




