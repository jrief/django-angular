# -*- coding: utf-8 -*-
from django import forms
from django.test import TestCase
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from pyquery.pyquery import PyQuery


class NgFormValidationMixinTest(TestCase):
    class ValidateMeForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
        first_name = forms.CharField(label='First name', min_length=3, max_length=20)
        middle_name = forms.CharField(label='Middle name', required=False)
        last_name = forms.RegexField(r'^[A-Z][a-z]+', label='Last name')

    def setUp(self):
        post_data = { 'first_name': 'Jo', 'middle_name': '', 'last_name': 'doe' }
        htmlsource = self.ValidateMeForm(scope_prefix='dataroot').as_table()
        #htmlsource = self.ValidateMeForm().as_table()
        print htmlsource
        self.dom = PyQuery(htmlsource)

    def test_ng_length(self):
        first_name = self.dom('input[name=first_name]')
        self.assertEqual(len(first_name), 1)
        attrib = dict(first_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-required': 'True'}, attrib)
        self.assertDictContainsSubset({'ng-minlength': '3'}, attrib)
        self.assertDictContainsSubset({'ng-maxlength': '20'}, attrib)

    def x_test_required(self):
        middle_name = self.dom('input[name=middle_name]')
        self.assertEqual(len(middle_name), 1)
        attrib = dict(middle_name[0].attrib.items())
        self.assertNotIn('required', attrib)
        self.assertDictContainsSubset({'ng-required': 'False'}, attrib)

    def x_test_regex(self):
        last_name = self.dom('input[name=last_name]')
        self.assertEqual(len(last_name), 1)
        attrib = dict(last_name[0].attrib.items())
        self.assertDictContainsSubset({'ng-pattern': '/^[A-Z][a-z]+/'}, attrib)
