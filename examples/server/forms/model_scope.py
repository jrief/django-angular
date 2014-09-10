# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from djangular.forms import NgModelFormMixin
from . import subscribe_form


def reject_addresses(value):
    """Reject email addresses ending with @example..."""
    try:
        value.lower().index('@example.')
        raise ValidationError('Email address "{0}" is rejected by the server.'.format(value))
    except ValueError:
        pass


class SubscribeForm(NgModelFormMixin, subscribe_form.SubscribeForm):
    scope_prefix = 'subscribe_data'
    form_name = 'my_form'

    # Override the email field to add a server-side validator
    email = EmailField(label='E-Mail', validators=[reject_addresses, validate_email],
        help_text='Addresses containing "@example" are rejected by the server.')

    def clean(self):
        if self.cleaned_data.get('first_name') == 'John' and self.cleaned_data.get('last_name') == 'Doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()
