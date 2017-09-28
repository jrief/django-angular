# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
import re
from django.core.exceptions import ValidationError
from django.forms import widgets
from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form


def validate_full_name(value):
    pattern = re.compile(r'^\S+\s+\S+')
    if not pattern.match(value):
        raise ValidationError("Please enter a first-, followed by a last name.")

class SubscribeForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'subscribe_data'
    form_name = 'subscribe_form'
    use_required_attribute = False

    sex = fields.ChoiceField(
        choices=[('m', 'Male'), ('f', 'Female')],
        widget=widgets.RadioSelect,
        error_messages={'invalid_choice': 'Please select your sex'},
    )

    full_name = fields.CharField(
        label='Full name',
        validators=[validate_full_name],
        help_text='Must consist of a first- and a last name',
    )

    def clean(self):
        if self.cleaned_data.get('full_name', '').lower() == 'john doe':
            raise ValidationError('The full name "John Doe" is rejected by the server.')
        return super(SubscribeForm, self).clean()

class AddressForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'address_data'
    form_name = 'address_form'
    use_required_attribute = False

    street_name = fields.CharField(label='Street name')
