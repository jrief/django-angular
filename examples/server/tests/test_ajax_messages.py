import json

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.messages.storage.base import Message

from djng.middleware import AjaxDjangoMessagesMiddleware
from djng.core.ajax_messages import process_response, is_not_valid_type
from djng.core.decorators import add_messages_to_response


try:
    import mock
except ImportError:
    import unittest.mock


def get_messages(request):
    return [Message(25, 'this is my message')]


def get_no_messages(request):
    return []


class DummyCBView(View):

    def __init__(self, content_type='application/json', **kwargs):
        super(DummyCBView, self).__init__(**kwargs)
        self.content_type = content_type

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'data': 'success'}),
                            status=200,
                            content_type=self.content_type)


class DummyDecCBView(DummyCBView):

    @method_decorator(add_messages_to_response)
    def get(self, request, *args, **kwargs):
        return super(DummyDecCBView, self).get(request, *args, **kwargs)


class MessagesTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def assertResponseContainsMessages(self, response):
        content = json.loads(response.content.decode('utf8'))
        messages = content['django_messages']
        message = messages[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['type'], 'success')
        self.assertEqual(message['level'], 25)
        self.assertEqual(message['message'], 'this is my message')
        self.assertEqual(message['tags'], 'success')
        self.assertEqual(content['data']['data'], 'success')

    def assertResponseDoesNotContainMessages(self, response):
        content = json.loads(response.content.decode('utf8'))
        messages = content.get('django_messages')
        self.assertEqual(messages, None)
        self.assertEqual(content['data'], 'success')


class AjaxMessagesMethodTest(MessagesTestCase):

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response_when_they_exist(self):
        request = self.factory.get('/')
        response = DummyCBView().get(request)
        response = process_response(request, response)
        self.assertResponseContainsMessages(response)

    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_messages_not_added_to_response_when_there_are_none(self):
        request = self.factory.get('/')
        response = DummyCBView().get(request)
        response = process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response_when_they_exist2(self):
        request = self.factory.get('/')
        response = DummyCBView('text/html').get(request)
        response = process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)
        self.assertEqual(response['Content-Type'], 'text/html')

    def test_is_not_valid_type_with_json(self):
        request = self.factory.get('/')
        response = DummyCBView().get(request)
        self.assertFalse(is_not_valid_type(request, response))

    def test_is_not_valid_type_with_json2(self):
        request = self.factory.get('/')
        response = DummyCBView('text/html').get(request)
        self.assertTrue(is_not_valid_type(request, response))


class MessagesDecoratorTest(MessagesTestCase):

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response_when_they_exist(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        self.assertResponseContainsMessages(response)

    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_messages_not_added_to_response_when_there_are_none(self):
        request = self.factory.get('/')
        response = DummyDecCBView().get(request)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response_when_they_exist2(self):
        request = self.factory.get('/')
        response = DummyDecCBView('text/html').get(request)
        self.assertResponseDoesNotContainMessages(response)
        self.assertEqual(response['Content-Type'], 'text/html')


class AjaxDjangoMessagesMiddlewareTest(MessagesTestCase):
    urls = 'server.tests.urls'

    def setUp(self):
        super(AjaxDjangoMessagesMiddlewareTest, self).setUp()
        self.middleware = AjaxDjangoMessagesMiddleware()

    @mock.patch('djng.middleware.EXEMPT', list(('(submethods_app)',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_added_to_response_when_url_is_not_exempt_and_they_exist(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseContainsMessages(response)

    @mock.patch('djng.middleware.EXEMPT', list(('(submethods_app)',)))
    @mock.patch('django.contrib.messages.get_messages', get_no_messages)
    def test_messages_not_added_to_response_when_url_is_not_exempt_and_there_are_none(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @override_settings(DEBUG=True)
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_not_added_to_response_as_debug_tool_url_exempt(self):
        request = self.factory.get('__debug__')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('djng.middleware.EXEMPT', list(('(submethods_app)',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_not_added_to_response_as_exempt_app_name(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('djng.middleware.EXEMPT', list(('[submethods:sub]',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_not_added_to_response_as_exempt_namespace(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('djng.middleware.EXEMPT', list(('submethods:sub:app',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_not_added_to_response_as_exempt_namespace_name(self):
        request = self.factory.get('sub_methods/sub/app/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)

    @mock.patch('djng.middleware.EXEMPT', list(('straightmethods',)))
    @mock.patch('django.contrib.messages.get_messages', get_messages)
    def test_messages_not_added_to_response_as_exempt_name(self):
        request = self.factory.get('straight_methods/')
        response = DummyCBView().get(request)
        response = self.middleware.process_response(request, response)
        self.assertResponseDoesNotContainMessages(response)
