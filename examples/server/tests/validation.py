# -*- coding: utf-8 -*-
from django.test import TestCase
from pyquery.pyquery import PyQuery
from server.forms import AdultSubscriptionForm, AdultSubscriptionFormWithNgModel


class NgFormValidationMixinTest(TestCase):
    def setUp(self):
        subscription_form = AdultSubscriptionForm()
        self.dom = PyQuery(str(subscription_form))

    def test_ng_length(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-required': 'true'}, attrib)
        self.assertDictContainsSubset({'ng-minlength': '3'}, attrib)
        self.assertDictContainsSubset({'ng-maxlength': '20'}, attrib)
        lis = self.dom('label[for=id_first_name]').parent().next().children('ul.djng-form-errors > li')
        self.assertEqual(len(lis), 3)
        attrib = dict(lis[0].attrib.items())
        self.assertDictContainsSubset({'ng-show': 'form.first_name.$error.required'}, attrib)

    def test_required(self):
        middle_name = self.dom('input[name=middle_name]')
        self.assertEqual(len(middle_name), 1)
        attrib = dict(middle_name[0].attrib.items())
        self.assertNotIn('required', attrib)
        self.assertDictContainsSubset({'ng-model': 'middle_name'}, attrib)
        self.assertDictContainsSubset({'ng-required': 'false'}, attrib)

    def test_regex(self):
        last_name = self.dom('input[name=last_name]')
        self.assertEqual(len(last_name), 1)
        attrib = dict(last_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-pattern': '/^[A-Z][a-z]+/'}, attrib)


class NgFormValidationWithModelMixinTest(TestCase):
    def setUp(self):
        subscription_form = AdultSubscriptionFormWithNgModel(scope_prefix='subscribe_data')
        self.dom = PyQuery(str(subscription_form))

    def test_ng_model(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-model': 'subscribe_data.first_name'}, attrib)

    def test_decimal_field(self):
        age = self.dom('input[name=age]')
        self.assertEqual(len(age), 1)
        attrib = dict(age[0].attrib.items())
        self.assertDictContainsSubset({'type': 'number'}, attrib)
        self.assertDictContainsSubset({'min': '18'}, attrib)
        self.assertDictContainsSubset({'max': '99'}, attrib)
        self.assertDictContainsSubset({'ng-model': 'subscribe_data.age'}, attrib)
