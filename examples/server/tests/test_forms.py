# -*- coding: utf-8 -*-
import copy
from django.db import models
from django.forms import forms, widgets
from django.http import QueryDict
from django.test import TestCase
from django.utils import six
from djng.forms import fields, NgModelFormMixin, NgForm, NgModelForm, NgDeclarativeFieldsMetaclass, NgFormValidationMixin
from pyquery.pyquery import PyQuery
import unittest
from lxml import html


CHOICES = (('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C'), ('d', 'Choice D'),)


class SubModel(models.Model):
    select_choices = models.CharField(max_length=1, choices=CHOICES, default=CHOICES[0][0])
    radio_choices = models.CharField(max_length=1, choices=CHOICES, default=CHOICES[1][0])
    first_name = models.CharField(max_length=40, blank=True)


class SubForm1(NgModelFormMixin, NgModelForm):
    class Meta:
        model = SubModel
        widgets = {'radio_choices': widgets.RadioSelect()}
        fields = '__all__'


class SubForm2(NgModelFormMixin, NgModelForm):
    class Meta:
        model = SubModel
        widgets = {'radio_choices': widgets.RadioSelect()}
        ng_models = ['select_choices', 'first_name']
        fields = '__all__'


class InvalidForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = SubModel
        ng_models = {}
        fields = '__all__'


class DummyForm(NgModelFormMixin, NgForm):
    email = fields.EmailField(label='E-Mail')
    onoff = fields.BooleanField(initial=False, required=True)
    sex = fields.ChoiceField(choices=(('m', 'Male'), ('f', 'Female')), widget=widgets.RadioSelect)
    select_multi = fields.MultipleChoiceField(choices=CHOICES)
    check_multi = fields.MultipleChoiceField(choices=CHOICES, widget=widgets.CheckboxSelectMultiple)
    hide_me = fields.CharField(widget=widgets.HiddenInput)
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


class CustomArgsForm(forms.Form):
    field1 = fields.CharField(widget=widgets.HiddenInput)
    field2 = fields.CharField(widget=widgets.HiddenInput)

    def __init__(self, custom_arg1=None, custom_arg2=None, *args, **kwargs):
        self.custom_arg1 = custom_arg1
        self.custom_arg2 = custom_arg2
        super(CustomArgsForm, self).__init__(*args, **kwargs)


class NgCustomArgsForm(six.with_metaclass(NgDeclarativeFieldsMetaclass, NgFormValidationMixin, CustomArgsForm)):
    pass


class NgModelFormMixinTest(TestCase):
    valid_data = {
        'email': 'john@example.com',
        'onoff': True,
        'sex': 'f',
        'select_multi': ['a', 'd'],
        'check_multi': ['b', 'c'],
        'sub1': {
            'select_choices': 'c',
            'radio_choices': 'c',
            'first_name': 'Susan',
        },
        'sub2': {
            'select_choices': 'b',
            'radio_choices': 'a',
        },
        'hide_me': 'hidden string',
    }

    def setUp(self):
        # create an unbound form
        self.unbound_form = DummyForm()
        htmlsource = self.unbound_form.as_p() + self.unbound_form.sub1.as_p() + self.unbound_form.sub2.as_p()
        self.dom = PyQuery(htmlsource)
        self.elements = self.dom('input') + self.dom('select')

    def test_widget_mro(self):
        # render a widget twice to test mro with NgWidgetMixin
        mro_form = DummyForm()
        mro_form.as_p()
        mro_form.as_p()

    def test_form_with_custom_args(self):
        form_post_data = {'field1': 'value1', 'field2': 'value2'}

        custom_args_form = CustomArgsForm(data=form_post_data, custom_arg1=1, custom_arg2=2)
        custom_args_form.full_clean()

        self.assertEqual(form_post_data, custom_args_form.data, 'lost data')
        self.assertEqual(custom_args_form.cleaned_data.get('field1'), 'value1', 'lost field1 value')
        self.assertEqual(custom_args_form.cleaned_data.get('field2'), 'value2', 'lost field2 value')
        self.assertEqual(1, custom_args_form.custom_arg1, 'lost custom arg1')
        self.assertEqual(2, custom_args_form.custom_arg2, 'lost custom arg2')

        ng_custom_args_form = NgCustomArgsForm(data=form_post_data, custom_arg1=1, custom_arg2=2)
        ng_custom_args_form.full_clean()

        self.assertEqual(form_post_data, ng_custom_args_form.data, 'lost data')
        self.assertEqual(ng_custom_args_form.cleaned_data.get('field1'), 'value1', 'lost field1 value')
        self.assertEqual(ng_custom_args_form.cleaned_data.get('field2'), 'value2', 'lost field2 value')
        self.assertEqual(1, ng_custom_args_form.custom_arg1, 'lost custom arg1')
        self.assertEqual(2, ng_custom_args_form.custom_arg2, 'lost custom arg2')

    @unittest.skip
    # TODO: refactor test to use BeautifulSoup
    def test_unbound_form(self):
        """Check if Angular attributes are added to the unbound form"""
        self.assertTrue(self.elements, 'No input fields in form')
        self.assertFalse(self.unbound_form.is_bound)
        self.check_form_fields(self.unbound_form)
        self.check_form_fields(self.unbound_form.sub1)
        self.check_form_fields(self.unbound_form.sub2)

    def check_form_fields(self, form):
        for name in form.fields.keys():
            identifier = '{0}.{1}'.format(form.prefix, name) if form.prefix else name
            input_fields = [e for e in self.elements if e.name.startswith(identifier)]
            self.assertTrue(input_fields)
            for input_field in input_fields:
                self.assertIsInstance(input_field, (html.InputElement, html.SelectElement))
                self.assertEqual(input_field.attrib.get('ng-class'), 'fieldClass(\'%s\')' % identifier)
                if identifier == 'sub2.radio_choices':
                    self.assertFalse(input_field.attrib.get('ng-model'))
                elif identifier == 'check_multi':
                    model = '{0}[\'{1}\'][\'{2}\']'.format(self.unbound_form.scope_prefix, *input_field.name.split('.'))
                    self.assertEqual(input_field.attrib.get('ng-model'), model)
                else:
                    model = '{0}[\'{1}\']'.format(self.unbound_form.scope_prefix, identifier)
                    self.assertEqual(input_field.attrib.get('ng-model'), model)
                if isinstance(input_field, html.InputElement):
                    if input_field.type == 'radio':
                        if input_field.tail.strip() == CHOICES[1][1]:
                            self.assertTrue(input_field.checked)
                        else:
                            #import pdb; pdb.set_trace()
                            self.assertFalse(input_field.checked)
                    elif input_field.type == 'checkbox':
                        self.assertFalse(input_field.checked)
                elif isinstance(input_field, html.SelectElement):
                    choices_keys = [c[0] for c in CHOICES]
                    self.assertListEqual(input_field.value_options, choices_keys)
                    if input_field.multiple:
                        self.assertIsInstance(input_field.value, html.MultipleSelectOptions)
                        choices_field = [o.values()[0] for o in input_field.value.options]
                        self.assertListEqual(choices_field, choices_keys)
                    else:
                        self.assertEqual(input_field.value, CHOICES[0][0])

    def test_valid_form(self):
        query = QueryDict('')
        query = query.copy()
        in_data = copy.deepcopy(self.valid_data)
        select_multi = in_data.pop('select_multi')
        check_multi = in_data.pop('check_multi')
        query.update(in_data)
        query.setlist('select_multi', select_multi)
        query.setlist('check_multi', check_multi)
        bound_form = DummyForm(data=query)
        self.assertTrue(bound_form.is_bound)
        self.assertTrue(bound_form.is_valid())

    def test_invalid_email(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['email'] = 'no.email.address'
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('email', None))
        self.assertFalse(bound_form.errors)

    def test_invalid_sex(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['sex'] = 'X'
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('sex', None))
        self.assertFalse(bound_form.errors)

    def test_invalid_select(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['select_multi'].append('X')
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('select_multi', None))
        self.assertFalse(bound_form.errors)

    def test_invalid_checkmulti(self):
        in_data = copy.deepcopy(self.valid_data)
        in_data['check_multi'].append('X')
        bound_form = DummyForm(data=in_data)
        self.assertTrue(bound_form.is_bound)
        self.assertFalse(bound_form.is_valid())
        self.assertTrue(bound_form.errors.pop('check_multi', None))
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
        initial_keys = list(initial_data.keys())
        initial_keys.sort()
        valid_keys = list(self.valid_data.keys())
        valid_keys.sort()
        self.assertEqual(initial_keys, valid_keys)
        initial_keys = list(initial_data['sub1'].keys())
        initial_keys.sort()
        valid_keys = list(self.valid_data['sub1'].keys())
        valid_keys.sort()
        self.assertEqual(initial_keys, valid_keys)


class InvalidNgModelFormMixinTest(TestCase):
    def test_invalid_form(self):
        # create a form with an invalid Meta class
        self.assertRaises(TypeError, InvalidForm)
