# -*- coding: utf-8 -*-
import unittest

import django
from django import forms
from django.test import TestCase

from djng.styling.bootstrap3.forms import Bootstrap3Form

from .test_forms import CHOICES


class EmailForm(Bootstrap3Form):
    email = forms.EmailField(label='E-Mail')

class ChoiceForm(Bootstrap3Form):
    choose = forms.BooleanField(required=True, label='Choose')

class RadioForm(Bootstrap3Form):
    sex = forms.ChoiceField(choices=(('m', 'Male'), ('f', 'Female')), widget=forms.RadioSelect, required=True)

class ChoicesForm(Bootstrap3Form):
    check_multi = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple)

class SelectMultipleChoicesForm(Bootstrap3Form):
    select_multi = forms.MultipleChoiceField(choices=CHOICES)


@unittest.skipIf(django.VERSION < (1, 10), "earlier django versions break the html")
class NgFieldRenderBootstrapTestCase(TestCase):

    def test_email_field(self):
        self.maxDiff = None
        f = EmailForm({'email': 'test@example.com'})
        self.assertHTMLEqual(
            str(f['email']),
            '''\
<input type="email" name="email" value="test@example.com" required id="id_email" class="form-control" />''')

    def test_choice_field(self):
        self.maxDiff = None
        f = ChoiceForm({'choose': True})
        self.assertHTMLEqual(
            str(f['choose']),
            '''\
<label class="checkbox-inline">
    <input type="checkbox" name="choose" checked id="id_choose" required />Choose</label>''')

    def test_radio_field(self):
        self.maxDiff = None
        f = RadioForm({'sex': 'f'})
        self.assertHTMLEqual(
            str(f['sex']),
            '''\
<div>
    <div class="radio">
        <label for="id_sex_0"><input type="radio" name="sex" value="m" required id="id_sex_0_0" /> Male</label>
    </div>
    <div class="radio">
        <label for="id_sex_1"><input type="radio" name="sex" value="f" required checked id="id_sex_1_1" /> Female</label>
    </div>
</div>''')

    def test_checkbock_select_mulitple_field(self):
        self.maxDiff = None
        f = SelectMultipleChoicesForm({'select_multi': ['a', 'c']})
        self.assertHTMLEqual(
            str(f['select_multi']),
            '''\
<select name="select_multi" required multiple="multiple" class="form-control" id="id_select_multi">
    <option value="a" selected>Choice A</option>
    <option value="b">Choice B</option>
    <option value="c" selected>Choice C</option>
    <option value="d">Choice D</option>
</select>
''')

    def test_checkbock_check_mulitple_field(self):
        self.maxDiff = None
        f = ChoicesForm({'check_multi': ['a', 'c']})
        self.assertHTMLEqual(
            str(f['check_multi']),
            '''\
<div ng-form="check_multi">

<label class="checkbox-inline" for="id_check_multi_0_0"><input type="checkbox" name="check_multi.a"  value="a" checked="checked" id="id_check_multi_0_0"/>Choice A</label>

<label class="checkbox-inline" for="id_check_multi_1_1"><input type="checkbox" name="check_multi.b"  value="b" id="id_check_multi_1_1" />Choice B</label>

<label class="checkbox-inline" for="id_check_multi_2_2"><input type="checkbox" name="check_multi.c"  value="c" checked="checked" id="id_check_multi_2_2" />Choice C</label>

<label class="checkbox-inline" for="id_check_multi_3_3"><input type="checkbox" name="check_multi.d"  value="d" id="id_check_multi_3_3" /> Choice D</label>
</div>''')  # noqa
