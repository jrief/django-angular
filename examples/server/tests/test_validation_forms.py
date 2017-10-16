# -*- coding: utf-8 -*-
import unittest
from bs4 import BeautifulSoup

from django import VERSION as DJANGO_VERSION
from django.forms import widgets
from django.test import TestCase

from djng.forms import fields, NgFormValidationMixin, NgForm


class EmailForm(NgFormValidationMixin, NgForm):
    email = fields.EmailField(label='E-Mail')


class ChoiceForm(NgFormValidationMixin, NgForm):
    choose = fields.BooleanField(required=True, label='Choose')


class RadioForm(NgFormValidationMixin, NgForm):
    sex = fields.ChoiceField(
        choices=[('m', 'Male'), ('f', 'Female')],
        widget=widgets.RadioSelect,
        required=True,)


class SelectMultipleChoicesForm(NgFormValidationMixin, NgForm):
    select_multi = fields.MultipleChoiceField(
        choices=[('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C')])


class CheckboxChoicesForm(NgFormValidationMixin, NgForm):
    check_multi = fields.MultipleChoiceField(
        choices=[('a', 'Choice A'), ('b', 'Choice B'), ('c', 'Choice C')],
        widget=widgets.CheckboxSelectMultiple,)


@unittest.skipIf(DJANGO_VERSION < (1, 10), "earlier django versions break the html")
class NgFormValidationMixinTestCase(TestCase):

    def test_email_field(self):
        f = EmailForm({'email': 'test@example.com'})
        soup = BeautifulSoup(f.as_p(), 'lxml')

        ul = soup.find(attrs={'ng-show': "RW1haWxGb3Jt['email'].$dirty && !RW1haWxGb3Jt['email'].$untouched"})
        self.assertHTMLEqual(str(ul.li), '<li class="invalid" ng-show="RW1haWxGb3Jt[\'email\'].$error.required">This field is required.</li>')
        self.assertHTMLEqual(str(ul.li.nextSibling), '<li class="invalid" ng-show="RW1haWxGb3Jt[\'email\'].$error.email">Enter a valid email address.</li>')
        self.assertHTMLEqual(str(ul.li.nextSibling.nextSibling), '<li class="valid" ng-show="RW1haWxGb3Jt[\'email\'].$valid"></li>')

        ul = soup.find(attrs={'ng-show': "RW1haWxGb3Jt['email'].$pristine"})
        self.assertHTMLEqual(str(ul.li), '<li class="valid" ng-show="RW1haWxGb3Jt[\'email\'].$valid"></li>')

        self.assertEquals(soup.input.attrs['name'], "email")
        self.assertEquals(soup.input.attrs['ng-model'], "email")
        self.assertEquals(soup.input.attrs['ng-required'], "true")
        self.assertEquals(soup.input.attrs['email-pattern'], '(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*@|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"@)(localhost$|((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+)(?:[A-Z0-9-]{2,63})$)')
        self.assertEquals(soup.input.attrs['value'], "test@example.com")

    def test_choice_field(self):
        f = ChoiceForm({'choose': True})
        soup = BeautifulSoup(f.as_p(), 'lxml')

        ul = soup.find(attrs={'ng-show': "Q2hvaWNlRm9ybQ['choose'].$dirty && !Q2hvaWNlRm9ybQ['choose'].$untouched"})
        self.assertHTMLEqual(str(ul.li), '<li class="invalid" ng-show="Q2hvaWNlRm9ybQ[\'choose\'].$error.required">This field is required.</li>')
        self.assertHTMLEqual(str(ul.li.nextSibling), '<li class="valid" ng-show="Q2hvaWNlRm9ybQ[\'choose\'].$valid"></li>')

        ul = soup.find(attrs={'ng-show': "Q2hvaWNlRm9ybQ['choose'].$pristine"})
        self.assertHTMLEqual(str(ul.li), '<li class="valid" ng-show="Q2hvaWNlRm9ybQ[\'choose\'].$valid"></li>')

        self.assertEquals(soup.input.attrs['name'], "choose")
        self.assertEquals(soup.input.attrs['ng-model'], "choose")
        self.assertEquals(soup.input.attrs['ng-required'], "true")

    @unittest.skipIf(DJANGO_VERSION < (1, 11), "currently disabled for Django-1.10 (overridden RadioSelect does not use RadioFieldRendererMixin)")
    def test_radio_field(self):
        f = RadioForm({'sex': 'f'})
        soup = BeautifulSoup(f.as_p(), 'lxml')

        ul = soup.find(attrs={'ng-show': "UmFkaW9Gb3Jt['sex'].$dirty && !UmFkaW9Gb3Jt['sex'].$untouched"})
        self.assertHTMLEqual(str(ul.li.attrs['ng-show']), 'UmFkaW9Gb3Jt[\'sex\'].$error.multifield')
        self.assertHTMLEqual(str(ul.li.text), 'At least one checkbox has to be selected.')
        self.assertHTMLEqual(str(ul.li.nextSibling.attrs['ng-show']), 'UmFkaW9Gb3Jt[\'sex\'].$valid')

        ul = soup.find(attrs={'ng-show': "UmFkaW9Gb3Jt['sex'].$pristine"})
        self.assertHTMLEqual(str(ul.li.attrs['ng-show']), 'UmFkaW9Gb3Jt[\'sex\'].$valid')

        self.assertEquals(soup.label.text, "Sex")

        elem = soup.find(id="id_sex")
        self.assertEquals(elem.label.text.strip(), "Male")
        self.assertEquals(elem.label.input.attrs['id'], "id_sex_0")
        self.assertEquals(elem.label.input.attrs['name'], "sex")
        self.assertEquals(elem.label.input.attrs['value'], "m")
        self.assertEquals(elem.label.input.attrs['ng-model'], "sex")
        self.assertIn('required', elem.label.input.attrs)

        label = elem.label.find_next_sibling('label')
        self.assertEquals(label.text.strip(), "Female")
        self.assertEquals(label.input.attrs['id'], "id_sex_1")
        self.assertEquals(label.input.attrs['name'], "sex")
        self.assertEquals(label.input.attrs['value'], "f")
        self.assertEquals(label.input.attrs['ng-model'], "sex")
        self.assertIn('required', label.input.attrs)

    def test_checkbock_select_multiple_field(self):
        f = SelectMultipleChoicesForm({'select_multi': ['a', 'c']})
        soup = BeautifulSoup(f.as_p(), 'lxml')

        ul = soup.find(attrs={'ng-show': "U2VsZWN0TXVsdGlwbGVDaG9pY2VzRm9ybQ['select_multi'].$dirty && !U2VsZWN0TXVsdGlwbGVDaG9pY2VzRm9ybQ['select_multi'].$untouched"})
        self.assertListEqual(ul.attrs['class'], ["djng-field-errors"])
        self.assertHTMLEqual(ul.li.attrs['ng-show'], "U2VsZWN0TXVsdGlwbGVDaG9pY2VzRm9ybQ['select_multi'].$error.required")
        self.assertHTMLEqual(ul.li.text, 'This field is required.')

        ul = soup.find(attrs={'ng-show': "U2VsZWN0TXVsdGlwbGVDaG9pY2VzRm9ybQ['select_multi'].$pristine"})
        self.assertHTMLEqual(ul.li.attrs['ng-show'], "U2VsZWN0TXVsdGlwbGVDaG9pY2VzRm9ybQ['select_multi'].$valid")

        self.assertEquals(soup.label.text, "Select multi")
        self.assertEquals(soup.label.attrs['for'], "id_select_multi")

        select = soup.find('select')
        self.assertEquals(select.attrs['id'], "id_select_multi")
        self.assertEquals(select.attrs['name'], "select_multi")
        self.assertEquals(select.attrs['multiple'], "multiple")
        self.assertEquals(select.attrs['ng-model'], "select_multi")
        self.assertEquals(select.attrs['ng-required'], "true")

        self.assertEquals(select.option.attrs['value'], "a")
        self.assertEquals(select.option.text, "Choice A")
        option = select.option.find_next_sibling('option')
        self.assertEquals(option.attrs['value'], "b")
        self.assertEquals(option.text, "Choice B")
        option = option.find_next_sibling('option')
        self.assertEquals(option.attrs['value'], "c")
        self.assertIn('selected', option.attrs)
        self.assertEquals(option.text, "Choice C")

    def test_checkbock_check_mulitple_field(self):
        f = CheckboxChoicesForm({'check_multi': ['a', 'c']})
        soup = BeautifulSoup(f.as_p(), 'lxml')

        ul = soup.find(attrs={'ng-show': "Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$dirty && !Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$untouched"})
        self.assertListEqual(ul.attrs['class'], ["djng-field-errors"])
        self.assertHTMLEqual(str(ul.li.attrs['ng-show']), "Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$error.multifield")
        self.assertHTMLEqual(str(ul.li.text), 'At least one checkbox has to be selected.')
        self.assertHTMLEqual(str(ul.li.nextSibling.attrs['ng-show']), "Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$valid")

        ul = soup.find(attrs={'ng-show': "Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$pristine"})
        self.assertListEqual(ul.attrs['class'], ["djng-field-errors"])
        self.assertHTMLEqual(str(ul.li.attrs['ng-show']), "Q2hlY2tib3hDaG9pY2VzRm9ybQ['check_multi'].$valid")

        self.assertEquals(soup.label.text, "Check multi")
        elem = soup.find(attrs={'ng-form': "check_multi"})
        self.assertTrue(elem.attrs['djng-multifields-required'])

        label = elem.find(attrs={'for': 'id_check_multi_0'})
        self.assertEquals(label.text.strip(), "Choice A")
        self.assertEquals(label.input.attrs['id'], "id_check_multi_0")
        self.assertEquals(label.input.attrs['name'], "check_multi.a")
        self.assertEquals(label.input.attrs['value'], "a")
        self.assertEquals(label.input.attrs['ng-model'], "check_multi['a']")
        self.assertIn('checked', label.input.attrs)

        label = elem.find(attrs={'for': 'id_check_multi_1'})
        self.assertEquals(label.input.attrs['id'], "id_check_multi_1")
        self.assertEquals(label.input.attrs['name'], "check_multi.b")
        self.assertEquals(label.input.attrs['value'], "b")
        self.assertEquals(label.input.attrs['ng-model'], "check_multi['b']")
        self.assertNotIn('checked', label.input.attrs)

        label = elem.find(attrs={'for': 'id_check_multi_2'})
        self.assertEquals(label.input.attrs['id'], "id_check_multi_2")
        self.assertEquals(label.input.attrs['name'], "check_multi.c")
        self.assertEquals(label.input.attrs['value'], "c")
        self.assertEquals(label.input.attrs['ng-model'], "check_multi['c']")
        self.assertIn('checked', label.input.attrs)
