# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form


class SubscribeForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'subscribe_data'
    form_name = 'subscribe_form'
    use_required_attribute = False

    full_name = fields.CharField(label='Full name')


class AddressForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    scope_prefix = 'address_data'
    form_name = 'address_form'
    use_required_attribute = False

    street_name = fields.CharField(label='Street name')
