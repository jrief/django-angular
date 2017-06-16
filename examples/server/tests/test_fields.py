# -*- coding: utf-8 -*-
from django import forms
from django.test import TestCase
from djng.forms import NgFormValidationMixin, NgForm

from .test_forms import CHOICES


class BaseForm(NgFormValidationMixin, NgForm):
    pass

class EmailForm(BaseForm):
    email = forms.EmailField(label='E-Mail', required=True)

class ChoiceForm(BaseForm):
    choose = forms.BooleanField(label='Choose', widget=forms.CheckboxInput, required=True)

class RadioForm(BaseForm):
    sex = forms.ChoiceField(choices=(('m', 'Male'), ('f', 'Female')), widget=forms.RadioSelect, required=True)

class ChoicesForm(BaseForm):
    check_multi = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple, required=True)

class SelectMultipleChoicesForm(BaseForm):
    select_multi = forms.MultipleChoiceField(choices=CHOICES, required=True)


class NgFieldRenderTestCase(TestCase):

    maxDiff = None

    def test_radio_field(self):
        f = RadioForm({'sex': 'f'})
        self.assertHTMLEqual(
            str(f['sex']),
            '''\
<ul id="id_sex">
    <li>
        <label for="id_sex_0"><input type="radio" name="sex" value="m" required ng-model="sex" id="id_sex_0" />Male</label>
    </li>
    <li>
        <label for="id_sex_1"><input type="radio" name="sex" value="f" required ng-model="sex" id="id_sex_1" checked />Female</label>
    </li>
</ul>''')

    def test_choice_field(self):
        self.maxDiff = None
        f = ChoiceForm({'choose': True})
        self.assertHTMLEqual(
            str(f['choose']),
            '''\
<input checked="checked" id="id_choose" name="choose" ng-model="choose" ng-required="true" type="checkbox" required />''')

    def test_email_field(self):
        import re
        f = EmailForm({'email': 'test@example.com'})
        # remove the email regex
        html = re.sub(r'email-pattern="[^"]+"', '', str(f['email']))
        self.assertHTMLEqual(
            html,
            '''\
<input id="id_email" name="email" ng-model="email" ng-required="true" type="email" value="test@example.com" required />''')  # noqa

    def test_checkbock_check_mulitple_field(self):
        f = ChoicesForm({'check_multi': ['a', 'c']})
        self.assertHTMLEqual(
            str(f['check_multi']),
            '''\
<ul ng-form="check_multi">
    <li>
        <label for="id_check_multi_0_0"><input checked="checked" id="id_check_multi_0_0" name="check_multi.a" ng-model="check_multi[&#39;a&#39;]" type="checkbox" value="a" /> Choice A</label>
    </li>
    <li>
        <label for="id_check_multi_1_1"><input id="id_check_multi_1_1" name="check_multi.b" ng-model="check_multi[&#39;b&#39;]" type="checkbox" value="b" /> Choice B</label>
    </li>
    <li>
        <label for="id_check_multi_2_2"><input checked="checked" id="id_check_multi_2_2" name="check_multi.c" ng-model="check_multi[&#39;c&#39;]" type="checkbox" value="c" />Choice C</label>
    </li>
    <li>
        <label for="id_check_multi_3_3"><input id="id_check_multi_3_3" name="check_multi.d" ng-model="check_multi[&#39;d&#39;]" type="checkbox" value="d" /> Choice D</label>
    </li>
</ul>''')  # noqa


    def test_checkbock_select_mulitple_field(self):
        f = SelectMultipleChoicesForm({'select_multi': ['a', 'c']})
        self.assertHTMLEqual(
            str(f['select_multi']),
            '''\
<select multiple="multiple" id="id_select_multi" name="select_multi" ng-model="select_multi" ng-required="true" required>
    <option value="a" selected="selected">Choice A</option>
    <option value="b">Choice B</option>
    <option value="c" selected="selected">Choice C</option>
    <option value="d">Choice D</option>
</select>''')   # noqa
