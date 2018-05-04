# -*- coding: utf-8 -*-
from base64 import b64encode
from django import VERSION
from django.utils import six
from django.test import TestCase
from pyquery.pyquery import PyQuery
from server.forms.client_validation import SubscribeForm as ClientValidatedForm
from server.forms.combined_validation import SubscribeForm as CombinedValidatedForm
from djng.forms.angular_base import NgBoundField


class NgFormValidationMixinTest(TestCase):
    def setUp(self):
        self.subscription_form = ClientValidatedForm()
        self.dom = PyQuery(str(self.subscription_form))
        self.form_name = b64encode(six.b(self.subscription_form.__class__.__name__)).rstrip(six.b('=')).decode("utf-8")
        self.maxDiff = None

    def test_form(self):
        self.assertEqual(self.subscription_form.form_name, self.form_name)

    def test_ng_length(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-required': 'true'}, attrib)
        self.assertDictContainsSubset({'ng-minlength': '3'}, attrib)
        self.assertDictContainsSubset({'ng-maxlength': '20'}, attrib)
        lis = self.dom('label[for=id_first_name]').closest('th').next('td').children('ul.djng-field-errors > li')
        if VERSION[1] == 5:
            # Django < 1.6 not not know about minlength and maxlength
            self.assertEqual(len(lis), 2)
        else:
            self.assertEqual(len(lis), 4)
        attrib = dict(lis[0].attrib.items())
        self.assertDictContainsSubset({'ng-show': self.form_name + six.u('[\'first_name\'].$error.required')}, attrib)
        attrib = dict(lis[1].attrib.items())
        self.assertDictContainsSubset({'ng-show': self.form_name + six.u('[\'first_name\'].$error.minlength')}, attrib)

    def test_type(self):
        email_field = self.dom('input[name=email]')
        self.assertEqual(len(email_field), 1)
        attrib = dict(email_field[0].attrib.items())
        self.assertNotIn('required', attrib)
        self.assertDictContainsSubset({'ng-model': 'email'}, attrib)
        if VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'email'}, attrib)

    def test_regex(self):
        last_name = self.dom('input[name=last_name]')
        self.assertEqual(len(last_name), 1)
        attrib = dict(last_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-pattern': '/^[A-Z][a-z -]?/'}, attrib)

    def test_field_as_ul(self):
        bf = self.subscription_form['email']
        ul_dirty = '''<ul ng-show="U3Vic2NyaWJlRm9ybQ['email'].$dirty && !U3Vic2NyaWJlRm9ybQ['email'].$untouched" class="djng-form-control-feedback djng-field-errors" ng-cloak><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$error.required" class="invalid">This field is required.</li><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$error.email" class="invalid">Enter a valid email address.</li><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$valid" class="valid"></li></ul>'''
        self.assertTrue(ul_dirty in bf.errors.as_ul())
        ul_pristine = '''<ul ng-show="U3Vic2NyaWJlRm9ybQ['email'].$dirty && !U3Vic2NyaWJlRm9ybQ['email'].$untouched" class="djng-form-control-feedback djng-field-errors" ng-cloak><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$error.required" class="invalid">This field is required.</li><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$error.email" class="invalid">Enter a valid email address.</li><li ng-show="U3Vic2NyaWJlRm9ybQ['email'].$valid" class="valid"></li></ul>'''
        print(bf.errors.as_ul())
        self.assertTrue(ul_pristine in bf.errors.as_ul())

    def test_field_as_text(self):
        bf = self.subscription_form['email']
        self.assertIsInstance(bf, NgBoundField)
        response = bf.errors.as_text()
        self.assertMultiLineEqual(response, '* This field is required.\n* Enter a valid email address.')


class NgFormValidationWithModelMixinTest(TestCase):
    def setUp(self):
        subscription_form = CombinedValidatedForm(scope_prefix='subscribe_data')
        self.dom = PyQuery(str(subscription_form))

    def test_ng_model(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-model': 'subscribe_data[\'first_name\']'}, attrib)

    def test_decimal_field(self):
        weight = self.dom('input[name=weight]')
        self.assertEqual(len(weight), 1)
        attrib = dict(weight[0].attrib.items())
        if VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'number'}, attrib)
        self.assertDictContainsSubset({'min': '42'}, attrib)
        self.assertDictContainsSubset({'max': '95'}, attrib)
        self.assertDictContainsSubset({'ng-model': 'subscribe_data[\'weight\']'}, attrib)

    def test_float_field(self):
        height = self.dom('input[name=height]')
        self.assertEqual(len(height), 1)
        attrib = dict(height[0].attrib.items())
        if VERSION[1] == 5:
            self.assertDictContainsSubset({'type': 'text'}, attrib)
        else:
            self.assertDictContainsSubset({'type': 'number'}, attrib)
            self.assertDictContainsSubset({'min': '1.48'}, attrib)
            self.assertDictContainsSubset({'max': '1.95'}, attrib)
        self.assertDictContainsSubset({'ng-model': 'subscribe_data[\'height\']'}, attrib)
