# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from djangular.forms import NgModelFormMixin
from djangular.forms.fields import FloatField
from djangular.styling.bootstrap3.forms import Bootstrap3FormMixin


def reject_addresses(value):
    """Reject email addresses ending with @example..."""
    try:
        value.lower().index('@example.')
        raise ValidationError('Email address \'{0}\' is rejected by the server.'.format(value))
    except ValueError:
        pass


class SubscribeForm(NgModelFormMixin, Bootstrap3FormMixin, forms.Form):
    scope_prefix = 'subscribe_data'
    form_name = 'valid_form'

    CONTINENT_CHOICES = (('am', 'America'), ('eu', 'Europe'), ('as', 'Asia'), ('af', 'Africa'),
                         ('au', 'Australia'), ('oc', 'Oceania'), ('an', 'Antartica'),)
    TRAVELLING_BY = (('foot', 'Foot'), ('bike', 'Bike'), ('mc', 'Motorcycle'), ('car', 'Car'),
                     ('public', 'Public Transportation'), ('train', 'Train'), ('air', 'Airplane'),)
    NOTIFY_BY = (('email', 'EMail'), ('phone', 'Phone'), ('sms', 'SMS'), ('postal', 'Postcard'),)

    first_name = forms.CharField(label='First name', min_length=3, max_length=20)
    last_name = forms.RegexField(r'^[A-Z][a-z -]?', label='Last name',
        error_messages={'invalid': 'Last names shall start in upper case'})
    sex = forms.ChoiceField(choices=(('m', 'Male'), ('f', 'Female')),
        widget=forms.RadioSelect, error_messages={'invalid_choice': 'Please select your sex'})
    email = forms.EmailField(label='E-Mail', validators=[reject_addresses, validate_email],
        help_text='Addresses containing ‘@example’ are rejected by the server.')
    subscribe = forms.BooleanField(initial=False, label='Subscribe Newsletter', required=False)
    phone = forms.RegexField(r'^\+?[0-9 .-]{4,25}$', label='Phone number',
        error_messages={'invalid': 'Phone number have 4-25 digits and may start with +'})
    birth_date = forms.DateField(label='Date of birth',
        widget=forms.DateInput(attrs={'validate-date': '^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
        help_text='Allowed date format: yyyy-mm-dd')
    continent = forms.ChoiceField(choices=CONTINENT_CHOICES, label='Living on continent',
        error_messages={'invalid_choice': 'Please select your continent'})
    weight = forms.IntegerField(min_value=42, max_value=95, label='Weight in kg',
        error_messages={'min_value': 'You are too lightweight'})
    height = FloatField(min_value=1.48, max_value=1.95, step=0.05, label='Height in meters',
        error_messages={'max_value': 'You are too tall'})
    traveling = forms.MultipleChoiceField(choices=TRAVELLING_BY, label='Traveling by')
    notifyme = forms.MultipleChoiceField(choices=NOTIFY_BY, label='Notify by', required=False,
        widget=forms.CheckboxSelectMultiple)
    annotation = forms.CharField(required=False, label='Annotation',
        widget=forms.Textarea(attrs={'cols': '80', 'rows': '3'}))
    confirmation_key = forms.CharField(max_length=40, required=True, widget=forms.HiddenInput(),
        initial='hidden value')

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name \'John Doe\' is rejected by the server.')
        return super(SubscribeForm, self).clean()
