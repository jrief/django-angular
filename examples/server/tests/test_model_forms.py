# -*- coding: utf-8 -*-
import unittest
from bs4 import BeautifulSoup

from django import VERSION as DJANGO_VERSION
from django import forms
from django.forms import widgets
from django.test import TestCase

from djng.forms import fields, NgModelFormMixin, NgForm


class EmailForm(NgModelFormMixin, NgForm):
    scope_prefix = 'form_data'

    email = fields.EmailField(label='E-Mail')


class ChoiceForm(NgModelFormMixin, NgForm):
    scope_prefix = 'form_data'

    choose = fields.BooleanField(required=True, label='Choose')


class RadioForm(NgModelFormMixin, NgForm):
    scope_prefix = 'form_data'

    sex = fields.ChoiceField(
        choices=[('m', 'Male'), ('f', 'Female')],
        widget=widgets.RadioSelect,
        required=True,)


class SelectMultipleChoicesForm(NgModelFormMixin, NgForm):
    scope_prefix = 'form_data'

    select_multi = fields.MultipleChoiceField(
        choices=[('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C')])


class CheckboxChoicesForm(NgModelFormMixin, NgForm):
    scope_prefix = 'data'

    check_multi = fields.MultipleChoiceField(
        choices=[('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C')],
        widget=widgets.CheckboxSelectMultiple,)


@unittest.skipIf(DJANGO_VERSION < (1, 10), "earlier django versions break the html")
class NgModelFormMixinTestCase(TestCase):

    def test_email_field(self):
        f = EmailForm(ng_foo="bar")
        self.assertFalse(f.is_valid())
        soup = BeautifulSoup(f.as_p(), 'lxml')
        print(soup.prettify())

        ul = soup.find(attrs={'ng-show': "RW1haWxGb3Jt.$pristine"})
        self.assertListEqual(ul.attrs['class'], ['djng-form-errors'])
        self.assertEquals(ul.li.attrs['ng-show'], 'RW1haWxGb3Jt.$error.rejected && RW1haWxGb3Jt.$message')
        self.assertEquals(ul.li.attrs['ng-bind'], 'RW1haWxGb3Jt.$message')
        self.assertListEqual(ul.li.attrs['class'], ['invalid'])

        elem = soup.find(id='id_email')
        self.assertEquals(elem.attrs['name'], "email")
        self.assertEquals(elem.attrs['ng-model'], "form_data['email']")
        self.assertEquals(elem.attrs['ng-foo'], "bar")

        f = EmailForm(data={'email': 'test@example.com'})
        self.assertTrue(f.is_valid())

    def test_choice_field(self):
        f = ChoiceForm(data={})
        self.assertFalse(f.is_valid())
        self.assertListEqual(f.errors['choose'], ['This field is required.'])
        soup = BeautifulSoup(f.as_p(), 'lxml')

        elem = soup.find(id='id_choose')
        self.assertEquals(elem.attrs['name'], "choose")
        self.assertEquals(elem.attrs['ng-model'], "form_data['choose']")
        self.assertIn('required', elem.attrs)

        f = ChoiceForm(data={'choose': True})
        self.assertTrue(f.is_valid())

    def test_radio_field(self):
        f = RadioForm()
        self.assertFalse(f.is_valid())
        soup = BeautifulSoup(f.as_p(), 'lxml')

        elem = soup.find(id='id_sex_0')
        self.assertTrue(elem.attrs['ng-model'], "form_data['sex']")

        f = RadioForm(data={'sex': 'X'})
        self.assertFalse(f.is_valid())
        self.assertListEqual(f.errors['sex'], ['Select a valid choice. X is not one of the available choices.'])
        f = RadioForm(data={'sex': 'f'})
        self.assertTrue(f.is_valid())

    def test_checkbock_select_multiple_field(self):
        f = SelectMultipleChoicesForm(data={})
        self.assertFalse(f.is_valid())
        self.assertListEqual(f.errors['select_multi'], ['This field is required.'])

        soup = BeautifulSoup(f.as_p(), 'lxml')
        elem = soup.find(id='id_select_multi')
        self.assertTrue(elem.attrs['ng-model'], "form_data['select_multi']")
        self.assertEquals(elem.option.attrs['value'], 'a')

        f = SelectMultipleChoicesForm(data={'select_multi': ['a', 'c']})
        self.assertTrue(f.is_valid())
        soup = BeautifulSoup(f.as_p(), 'lxml')
        elem = soup.find(id='id_select_multi')
        self.assertIn('selected', elem.option.attrs)
        option = elem.option.find_next_sibling('option')
        self.assertNotIn('selected', option.attrs)
        option = option.find_next_sibling('option')
        self.assertIn('selected', option.attrs)

    def test_checkbock_check_mulitple_field(self):
        f = CheckboxChoicesForm(data={})
        self.assertFalse(f.is_valid())
        self.assertListEqual(f.errors['check_multi'], ['This field is required.'])

        soup = BeautifulSoup(f.as_p(), 'lxml')
        elem = soup.find(attrs={'ng-form': "check_multi"})
        self.assertEquals(elem.input.attrs['ng-model'], "data['check_multi']['a']")
        self.assertEquals(elem.input.attrs['name'], 'check_multi.a')
        self.assertEquals(elem.input.attrs['value'], 'a')

        f = CheckboxChoicesForm({'check_multi': {'a': True, 'c': True}})
        self.assertTrue(f.is_valid())
        soup = BeautifulSoup(f.as_p(), 'lxml')

        checkbox = soup.find(id='id_check_multi_0')
        self.assertIn('checked', checkbox.attrs)
        checkbox = soup.find(id='id_check_multi_1')
        self.assertNotIn('checked', checkbox.attrs)
        checkbox = soup.find(id='id_check_multi_2')
        self.assertIn('checked', checkbox.attrs)
