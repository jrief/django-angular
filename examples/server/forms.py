# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from djangular.forms import NgFormValidationMixin, NgModelFormMixin


def reject_addresses(value):
    try:
        value.lower().index('@example.')
        raise ValidationError(u'Email address \'{0}\' is rejected by the server.'.format(value))
    except ValueError:
        pass


class SubscriptionForm(forms.Form):
    CONTINENT_CHOICES = (('am', 'America'), ('eu', 'Europe'), ('as', 'Asia'), ('af', 'Africa'),
                         ('au', 'Australia'), ('oc', 'Oceania'), ('an', 'Antartica'),)
    TRAVELLING_VEHICLES = (('bike', 'Bike'), ('mc', 'Motorcycle'), ('car', 'Car'), ('bus', 'Bus'),
        ('taxi', 'Taxi'), ('tram', 'Tram'), ('sw', 'Subway'), ('train', 'Train'), ('boat', 'Boat'),
        ('air', 'Airplane'),)

    first_name = forms.CharField(label='First name', min_length=3, max_length=20)
    last_name = forms.RegexField(r'^[A-Z][a-z -]?', label='Last name',
        error_messages={'invalid': 'Last names shall start in upper case'},
        help_text=u'The name ‘John Doe’ is rejected by the server.')
    sex = forms.ChoiceField(choices=(('m', 'Male'), ('f', 'Female')),
        widget=forms.RadioSelect,
        error_messages={'invalid_choice': 'Please select your sex'})
    email = forms.EmailField(label='E-Mail', validators=[reject_addresses, validate_email],
        help_text=u'Addresses containing ‘@example’ are rejected by the server.')
    subscribe = forms.BooleanField(initial=False, label='Subscribe Newsletter', required=False)
    phone = forms.RegexField(r'^\+?[0-9 .-]{4,25}$', label='Phone number',
        error_messages={'invalid': 'Phone number have 4-25 digits and may start with +'})
    birth_date = forms.DateField(label='Date of birth',
        widget=forms.widgets.DateInput(attrs={'validate-date': '^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
        help_text=u'Allowed date format: yyyy-mm-dd.')
    continent = forms.ChoiceField(choices=CONTINENT_CHOICES, label='Living on continent',
         error_messages={'invalid_choice': 'Please select your continent'})
    weight = forms.IntegerField(min_value=42, max_value=95, label='Weight in kg',
        error_messages={'min_value': 'You are too lightweight'})
    height = forms.FloatField(min_value=1.48, max_value=1.95, label='Height in meters',
        error_messages={'max_value': 'You are too tall'})
    traveling = forms.MultipleChoiceField(choices=TRAVELLING_VEHICLES, label='Traveling by')
    annotation = forms.CharField(required=False, label='Annotation',
        widget=forms.Textarea(attrs={'cols': '80', 'rows': '3'}))

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError(u'The full name \'John Doe\' is rejected by the server.')
        return super(SubscriptionForm, self).clean()


class SubscriptionFormWithNgValidation(NgFormValidationMixin, SubscriptionForm):
    form_name = 'valid_form'
    pass


class SubscriptionFormWithNgModel(NgModelFormMixin, SubscriptionForm):
    form_name = 'valid_form'
    scope_prefix = 'subscribe_data'


class SubscriptionFormWithNgValidationAndModel(NgModelFormMixin, NgFormValidationMixin, SubscriptionForm):
    form_name = 'valid_form'
    scope_prefix = 'subscribe_data'
