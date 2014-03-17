# -*- coding: utf-8 -*-
import django
from django.test import TestCase
from pyquery.pyquery import PyQuery
from server.forms import SubscriptionForm, SubscriptionFormWithNgModel


class NgFormValidationMixinTest(TestCase):
    def setUp(self):
        self.subscription_form = SubscriptionForm()
        self.dom = PyQuery(str(self.subscription_form))

    def test_form(self):
        self.assertEqual(self.subscription_form.name(), 'subscribe_form')

    def test_ng_length(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-required': 'true'}, attrib)
        self.assertDictContainsSubset({'ng-minlength': '3'}, attrib)
        self.assertDictContainsSubset({'ng-maxlength': '20'}, attrib)
        lis = self.dom('label[for=id_first_name]').next('ul.djng-form-errors').children('li')
        if django.VERSION[1] == 5:
            self.assertEqual(len(lis), 1)
        else:
            self.assertEqual(len(lis), 3)
        attrib = dict(lis[0].attrib.items())
        self.assertDictContainsSubset({'ng-show': 'subscribe_form.first_name.$error.required'}, attrib)

    def test_type(self):
        email_field = self.dom('input[name=email]')
        self.assertEqual(len(email_field), 1)
        attrib = dict(email_field[0].attrib.items())
        self.assertNotIn('required', attrib)
        self.assertDictContainsSubset({'ng-model': 'email'}, attrib)
        if django.VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'email'}, attrib)

    def test_regex(self):
        last_name = self.dom('input[name=last_name]')
        self.assertEqual(len(last_name), 1)
        attrib = dict(last_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-pattern': '/^[A-Z][a-z -]?/'}, attrib)

    def test_field_as_ul(self):
        html = ''.join((
            '<ul class="djng-form-errors" ng-hide="subscribe_form.email.$pristine" ng-cloak>',
            '<li ng-show="subscribe_form.email.$error.required">This field is required.</li>',
            '<li ng-show="subscribe_form.email.$error.email">Enter a valid email address.</li>',
            '</ul>'))
        self.assertHTMLEqual(self.subscription_form['email'].ng_errors(), html)

    def test_field_as_text(self):
        response = self.subscription_form['email'].field.ng_potential_errors.as_text()
        self.assertMultiLineEqual(response, '* This field is required.\n* Enter a valid email address.')


class NgFormValidationWithModelMixinTest(TestCase):
    def setUp(self):
        subscription_form = SubscriptionFormWithNgModel(scope_prefix='subscribe_data')
        self.dom = PyQuery(str(subscription_form))

    def test_ng_model(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-model': 'subscribe_data.first_name'}, attrib)

    def test_decimal_field(self):
        weight = self.dom('input[name=weight]')
        self.assertEqual(len(weight), 1)
        attrib = dict(weight[0].attrib.items())
        if django.VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'number'}, attrib)
        self.assertDictContainsSubset({'min': '42'}, attrib)
        self.assertDictContainsSubset({'max': '95'}, attrib)
        self.assertDictContainsSubset({'ng-model': 'subscribe_data.weight'}, attrib)

    def test_float_field(self):
        height = self.dom('input[name=height]')
        self.assertEqual(len(height), 1)
        attrib = dict(height[0].attrib.items())
        if django.VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'number'}, attrib)
            self.assertDictContainsSubset({'min': '1.48'}, attrib)
            self.assertDictContainsSubset({'max': '1.95'}, attrib)
        self.assertDictContainsSubset({'ng-model': 'subscribe_data.height'}, attrib)
