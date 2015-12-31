# -*- coding: utf-8 -*-
from django.test import TestCase
from django import forms
from pyquery.pyquery import PyQuery
from djangular.forms import NgForm, NgFormValidationMixin, NgMessagesMixin


class MessagesForm(NgMessagesMixin, NgForm):
    form_name = 'messages_form'
    email = forms.EmailField(label='E-Mail', required=True)


class MessagesValidationForm(NgMessagesMixin, NgFormValidationMixin, NgForm):
    form_name = 'messages_form'
    email = forms.EmailField(label='E-Mail', required=True)


class NgMessagesMixinTest(TestCase):
    def setUp(self):
        self.form = MessagesForm()
        self.dom = PyQuery(str(self.form))

    def test_validate_rejected_directive_present(self):
        email = self.dom('input[name=email]')
        self.assertEqual(len(email), 1)
        attrib = dict(email[0].attrib.items())
        self.assertEqual(attrib.get('djng-rejected'), 'validator')

    def test_ng_messages_directive_present(self):
        messages = self.dom('ul[ng-messages]')
        self.assertEqual(len(messages), 1)
        attrib = dict(messages[0].attrib.items())
        self.assertEqual(attrib.get('class'), 'djng-field-errors')
        self.assertEqual(attrib.get('ng-messages'), 'messages_form.email.$error')
        self.assertEqual(attrib.get('ng-show'), 'messages_form.$submitted || messages_form.email.$dirty')

    def test_rejected_message_direcive_present(self):
        message = self.dom('ul[ng-messages]').children()
        self.assertEqual(len(message), 1)
        attrib = dict(message[0].attrib.items())
        self.assertEqual(attrib.get('ng-message'), 'rejected')
        span = message.children()
        attrib = dict(span[0].attrib.items())
        self.assertEqual(attrib.get('ng-bind'), 'messages_form.email.$message')

    def test_form_valid_ul_present(self):
        ul = self.dom('ul')
        self.assertEqual(len(ul), 2)
        attrib = dict(ul[0].attrib.items())
        self.assertEqual(attrib.get('class'), 'djng-field-errors')
        self.assertEqual(attrib.get('ng-show'), 'messages_form.$submitted || messages_form.email.$dirty')
        self.assertIsNone(attrib.get('ng-messages'))


class NgMessagesMixinWithValidationTest(TestCase):
    def setUp(self):
        self.form = MessagesValidationForm()
        self.dom = PyQuery(str(self.form))

    def test_correct_input_directives_present(self):
        email = self.dom('input[name=email]')
        self.assertEqual(len(email), 1)
        attrib = dict(email[0].attrib.items())
        self.assertEqual(attrib.get('djng-rejected'), 'validator')
        self.assertEqual(attrib.get('ng-required'), 'true')

    def test_ng_messages_directive_present(self):
        messages = self.dom('ul[ng-messages]')
        self.assertEqual(len(messages), 1)
        attrib = dict(messages[0].attrib.items())
        self.assertEqual(attrib.get('class'), 'djng-field-errors')
        self.assertEqual(attrib.get('ng-messages'), 'messages_form[\'email\'].$error')
        # ask jRobb: self.assertEqual(attrib.get('ng-show'), 'messages_form.$submitted || messages_form[\'email\'].$dirty')
        self.assertEqual(attrib.get('ng-show'), '.$submitted || messages_form[\'email\'].$dirty')

    def test_rejected_message_direcive_present(self):
        message = self.dom('ul[ng-messages]').children('li[ng-message=rejected]')
        self.assertEqual(len(message), 1)
        attrib = dict(message[0].attrib.items())
        self.assertEqual(attrib.get('ng-message'), 'rejected')
        span = message.children()
        attrib = dict(span[0].attrib.items())
        self.assertEqual(attrib.get('ng-bind'), 'messages_form.email.$message')

    def test_all_correct_message_directives_present(self):
        message = self.dom('ul[ng-messages]').children()
        self.assertEqual(len(message), 3)
        rejected = message('li[ng-message=rejected]')
        self.assertEqual(len(rejected), 1)
        required = message('li[ng-message=required]')
        self.assertEqual(len(required), 1)
        email = message('li[ng-message=email]')
        self.assertEqual(len(email), 1)

    def test_form_valid_ul_present(self):
        ul = self.dom('ul')
        self.assertEqual(len(ul), 2)
        attrib = dict(ul[0].attrib.items())
        self.assertEqual(attrib.get('class'), 'djng-field-errors')
        # ask jRobb: self.assertEqual(attrib.get('ng-show'), 'messages_form.$submitted || messages_form[\'email\'].$dirty')
        self.assertEqual(attrib.get('ng-show'), '.$submitted || messages_form[\'email\'].$dirty')
        self.assertIsNone(attrib.get('ng-messages'))

    def test_form_valid_li_present(self):
        ul = PyQuery(self.dom('ul')[0])
        li = ul.children()
        self.assertEqual(len(li), 1)
        attrib = dict(li[0].attrib.items())
        self.assertEqual(attrib.get('ng-show'), 'messages_form[\'email\'].$valid')


class BoundNgMessagesMixinFormTest(TestCase):
    def setUp(self):
        self.form = MessagesForm(data={'email': 'james'})
        self.dom = PyQuery(str(self.form))

    def test_bound_form_input_for_djng_error(self):
        email = self.dom('input[name=email]')
        self.assertEqual(len(email), 1)
        attrib = dict(email[0].attrib.items())
        self.assertEqual(attrib.get('value'), 'james')
        self.assertEqual(attrib.get('djng-error'), 'bound-msgs-field')
        self.assertEqual(attrib.get('djng-error-msg'), 'Enter a valid email address.')
