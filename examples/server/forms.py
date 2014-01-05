# -*- coding: utf-8 -*-
from django import forms
from djangular.forms import NgFormValidationMixin, NgModelFormMixin


class SubscriptionForm(NgFormValidationMixin, forms.Form):
    first_name = forms.CharField(label='First name', min_length=3, max_length=20)
    last_name = forms.RegexField(r'^[A-Z][a-z -]+', label='Last name',
        error_messages={'invalid': 'Surnames shall start in upper case'})
    email = forms.EmailField(label='E-Mail')
    phone = forms.RegexField(r'^\+?[0-9 .-]{4,25}$', label='Phone number',
        error_messages={'invalid': 'Phone number have 4-25 digits and may start with +'})
    birth_date = forms.DateField(label='Date of birth')
    weight = forms.IntegerField(min_value=42, max_value=95, label='Weight in kg',
        error_messages={'min_value': 'You are too lightweight'})
    height = forms.FloatField(min_value=1.48, max_value=1.95, label='Height in meters',
        error_messages={'max_value': 'You are too tall'})


class SubscriptionFormWithNgModel(NgModelFormMixin, SubscriptionForm):
    pass
