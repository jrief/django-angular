# -*- coding: utf-8 -*-
from django import forms
from djangular.forms import NgModelFormMixin, NgFormValidationMixin


class AdultSubscriptionForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
    first_name = forms.CharField(label='First name', min_length=3, max_length=20)
    middle_name = forms.CharField(label='Middle name', required=False)
    last_name = forms.RegexField(r'^[A-Z][a-z]+', label='Last name')
    age = forms.DecimalField(min_value=18, max_value=99)
