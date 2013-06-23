# -*- coding: utf-8 -*-
import copy
from django.db import models
from django import forms
from django.test import TestCase
from djangular.forms.angular_model import NgModelFormMixin
from djangular.forms.auto_label import AutoLabelFormMixin
from pyquery.pyquery import PyQuery
from lxml import html


CHOICES = (('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C'))


class SubModel(models.Model):
    select_choices = models.CharField(max_length=1, choices=CHOICES, default=CHOICES[0][0])
    radio_choices = models.CharField(max_length=1, choices=CHOICES, default=CHOICES[1][0])
    first_name = models.CharField(max_length=40, blank=True)


class SubForm1(NgModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubModel
        widgets = {'radio_choices': forms.RadioSelect()}


class SubForm2(NgModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubModel
        widgets = {'radio_choices': forms.RadioSelect()}
        ng_models = ['select_choices', 'first_name']


class InvalidForm(NgModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubModel
        ng_models = {}


class DummyForm(NgModelFormMixin, forms.Form):
    email = forms.EmailField('E-Mail')
    onoff = forms.BooleanField(initial=False, required=True)
    scope_prefix = 'dataroot'

    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, ng_class='fieldClass(\'%(identifier)s\')',
                      scope_prefix=self.scope_prefix)
        super(DummyForm, self).__init__(*args, **kwargs)
        self.sub1 = SubForm1(prefix='sub1', **kwargs)
        self.sub2 = SubForm2(prefix='sub2', **kwargs)

    def get_initial_data(self):
        data = super(DummyForm, self).get_initial_data()
        data.update({
            self.sub1.prefix: self.sub1.get_initial_data(),
            self.sub2.prefix: self.sub2.get_initial_data(),
        })
        return data

    def is_valid(self):
        if not self.sub1.is_valid():
            self.errors.update(self.sub1.errors)
        if not self.sub2.is_valid():
            self.errors.update(self.sub2.errors)
        return super(DummyForm, self).is_valid() and self.sub1.is_valid() and self.sub2.is_valid()


class NgModelFormMixinTest(TestCase):
    valid_data = {
        'email': 'john@example.com',
        'onoff': True,
        'sub1': {
            'select_choices': 'c',
            'radio_choices': 'c',
            'first_name': 'Susan',
        },
        'sub2': {
            'select_choices': 'b',
            'radio_choices': 'a',
        },
    }

    def setUp(self):
        # create an unbound form
        self.unbound_form = DummyForm()
        htmlsource = self.unbound_form.as_p() + self.unbound_form.sub1.as_p() + self.unbound_form.sub2.as_p()
        self.dom = PyQuery(htmlsource)
        self.elements = self.dom('input') + self.dom('select')
        #print htmlsource

    def test_unbound_form(self):
        """Check if Angular attributes are added to the unbound form"""
        self.assertTrue(self.elements, 'No input fields in form')
        self.assertFalse(self.unbound_form.is_bound)
        self.check_form_fields(self.unbound_form)
        self.check_form_fields(self.unbound_form.sub1)
        self.check_form_fields(self.unbound_form.sub2)

    def check_form_fields(self, form):
        for name in form.fields.keys():
            identifier = '%s.%s' % (form.prefix, name) if form.prefix else name
            input_fields = [e for e in self.elements if e.name == identifier]
            self.assertTrue(input_fields)
            for input_field in input_fields:
                self.assertIsInstance(input_field, (html.InputElement, html.SelectElement))
                self.assertEqual(input_field.attrib.get('ng-class'), 'fieldClass(\'%s\')' % identifier)
                if identifier == 'sub2.radio_choices':
                    self.assertFalse(input_field.attrib.get('ng-model'))
                else:
                    model = '%s.%s' % (self.unbound_form.scope_prefix, identifier)
                    self.assertEqual(input_field.attrib.get('ng-model'), model)
                if isinstance(input_field, html.InputElement) and input_field.type == 'radio':
                    if input_field.tail.strip() == CHOICES[1][1]:
                        self.assertTrue(input_field.checked)
                    else:
                        self.assertFalse(input_field.checked)
                elif isinstance(input_field, html.SelectElement):
                    self.assertListEqual(input_field.value_options, [c[0] for c in CHOICES])
                    self.assertEqual(input_field.value, CHOICES[0][0])

    def test_valid_form(self):
        bound_form = DummyForm(data=self.valid_data)
        self.assertTrue(bound_form.is_bound)
        self.assertTrue(bound_form.is_valid())

    def test_invalid_form(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['email'] = 'no.email.address'
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('email', None))
        self.assertFalse(bound_form.errors)

    def test_invalid_subform(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['sub1']['select_choices'] = 'X'
        in_data['sub1']['radio_choices'] = 'Y'
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('sub1.select_choices'))
        self.assertTrue(bound_form.errors.pop('sub1.radio_choices'))
        self.assertFalse(bound_form.errors)

    def test_initial_data(self):
        initial_data = self.unbound_form.get_initial_data()
        initial_keys = initial_data.keys()
        initial_keys.sort()
        valid_keys = self.valid_data.keys()
        valid_keys.sort()
        self.assertEqual(initial_keys, valid_keys)
        initial_keys = initial_data['sub1'].keys()
        initial_keys.sort()
        valid_keys = self.valid_data['sub1'].keys()
        valid_keys.sort()
        self.assertEqual(initial_keys, valid_keys)


class InvalidNgModelFormMixinTest(TestCase):
    def test_invalid_form(self):
        # create a form with an invalid Meta class
        self.assertRaises(TypeError, InvalidForm)


class AutoLabelFormMixinTest(TestCase):
    class EmailOnlyForm(AutoLabelFormMixin, forms.Form):
        email = forms.EmailField(label='E-Mail')
        password = forms.CharField(label='Password', widget=forms.PasswordInput)
        radio = forms.Select(choices=CHOICES)

    def setUp(self):
        self.email_form = self.EmailOnlyForm()
        htmlsource = unicode(self.email_form)
        self.dom = PyQuery(htmlsource)

    def test_email_field(self):
        email_field = self.dom('input[name=email]')
        self.assertEqual(len(email_field), 1)
        email_field_attrib = dict(email_field[0].attrib.items())
        self.assertDictContainsSubset({'auto-label': 'E-Mail'}, email_field_attrib)

    def test_password_field(self):
        password_field = self.dom('input[name=password]')
        self.assertEqual(len(password_field), 1)
        email_field_attrib = dict(password_field[0].attrib.items())
        self.assertDictContainsSubset({'auto-label': 'Password'}, email_field_attrib)
