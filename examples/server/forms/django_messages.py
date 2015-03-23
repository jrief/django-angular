import django.contrib.messages
from django import forms

from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3Form



class MessagesForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'my_data'
    form_name = 'my_form'

    LEVELS = ((django.contrib.messages.DEBUG, 'Debug'),
              (django.contrib.messages.INFO, 'Info'),
              (django.contrib.messages.SUCCESS, 'Success'),
              (django.contrib.messages.WARNING, 'Warning'),
              (django.contrib.messages.ERROR, 'Error'),)

    level = forms.ChoiceField(choices=(LEVELS),widget=forms.RadioSelect)

    count = forms.DecimalField(min_value=1, max_value=5)

    message = forms.CharField(label='Message', min_length=10, max_length=30)