# -*- coding: utf-8 -*-
from django.test import TestCase
from pyquery.pyquery import PyQuery
from server.forms import AdultSubscriptionForm


class NgFormValidationMixinTest(TestCase):
    def setUp(self):
        post_data = { 'first_name': 'Jo', 'middle_name': '', 'last_name': 'doe' }
        subscription_form = AdultSubscriptionForm()
        print subscription_form
        self.dom = PyQuery(str(subscription_form))

    def test_ng_length(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-required': 'true'}, attrib)
        self.assertDictContainsSubset({'ng-minlength': '3'}, attrib)
        self.assertDictContainsSubset({'ng-maxlength': '20'}, attrib)

    def x_test_required(self):
        middle_name = self.dom('input[name=middle_name]')
        self.assertEqual(len(middle_name), 1)
        attrib = dict(middle_name[0].attrib.items())
        self.assertNotIn('required', attrib)
        self.assertDictContainsSubset({'ng-required': 'false'}, attrib)

    def x_test_regex(self):
        last_name = self.dom('input[name=last_name]')
        self.assertEqual(len(last_name), 1)
        attrib = dict(last_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-pattern': '/^[A-Z][a-z]+/'}, attrib)
