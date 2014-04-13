# -*- coding: utf-8 -*-
"""
Class methods to be added to form fields such as django.forms.fields. These methods add additional
error messages for AngularJS form validation.
"""
from django.utils.translation import gettext_lazy, ungettext_lazy


def _input_required(field):
    field.widget.attrs['ng-required'] = str(field.required).lower()
    errors = []
    for key, msg in field.error_messages.items():
        if key == 'required':
            errors.append(('$error.required', msg))
    return errors


def _min_max_length_errors(field):
    errors = []
    if hasattr(field, 'min_length') and field.min_length > 0:
        field.widget.attrs['ng-minlength'] = field.min_length
    if hasattr(field, 'max_length') and field.max_length > 0:
        field.widget.attrs['ng-maxlength'] = field.max_length
    for item in field.validators:
        if getattr(item, 'code', None) == 'min_length':
            message = ungettext_lazy(
                'Ensure this value has at least %(limit_value)d character',
                'Ensure this value has at least %(limit_value)d characters')
            errors.append(('$error.minlength', message % {'limit_value': field.min_length}))
        if getattr(item, 'code', None) == 'max_length':
            message = ungettext_lazy(
                'Ensure this value has at most %(limit_value)d character',
                'Ensure this value has at most %(limit_value)d characters')
            errors.append(('$error.maxlength', message % {'limit_value': field.max_length}))
    return errors


def _min_max_value_errors(field):
    errors = []
    if isinstance(getattr(field, 'min_value', None), int):
        field.widget.attrs['min'] = field.min_value
    if isinstance(getattr(field, 'max_value', None), int):
        field.widget.attrs['max'] = field.max_value
    errkeys = []
    for key, msg in field.error_messages.items():
        if key == 'min_value':
            errors.append(('$error.min', msg))
            errkeys.append(key)
        if key == 'max_value':
            errors.append(('$error.max', msg))
            errkeys.append(key)
    for item in field.validators:
        if getattr(item, 'code', None) == 'min_value' and 'min_value' not in errkeys:
            errors.append(('$error.min', item.message % {'limit_value': field.min_value}))
            errkeys.append('min_value')
        if getattr(item, 'code', None) == 'max_value' and 'max_value' not in errkeys:
            errors.append(('$error.max', item.message % {'limit_value': field.max_value}))
            errkeys.append('max_value')
    return errors


def _invalid_value_errors(field, ng_error_key):
    errors = []
    errkeys = []
    for key, msg in field.error_messages.items():
        if key == 'invalid':
            errors.append(('$error.{0}'.format(ng_error_key), msg))
            errkeys.append(key)
    for item in field.validators:
        if getattr(item, 'code', None) == 'invalid' and 'invalid' not in errkeys:
            errmsg = getattr(item, 'message', gettext_lazy('This input field does not contain valid data.'))
            errors.append(('$error.{0}'.format(ng_error_key), errmsg))
            errkeys.append('invalid')
    return errors


def DecimalField_angular_errors(field):
    errors = _input_required(field)
    field.widget.attrs['ng-minlength'] = 1
    if hasattr(field, 'max_digits') and field.max_digits > 0:
        field.widget.attrs['ng-maxlength'] = field.max_digits + 1
    errors.extend(_min_max_value_errors(field))
    return errors


def CharField_angular_errors(field):
    errors = _input_required(field)
    errors.extend(_min_max_length_errors(field))
    return errors


def EmailField_angular_errors(field):
    errors = _input_required(field)
    errors.extend(_invalid_value_errors(field, 'email'))
    return errors


def DateField_angular_errors(field):
    errors = _input_required(field)
    errors.extend(_invalid_value_errors(field, 'date'))
    return errors


def FloatField_angular_errors(field):
    errors = _input_required(field)
    errors.extend(_min_max_value_errors(field))
    return errors


def IntegerField_angular_errors(field):
    errors = _input_required(field)
    errors.extend(_min_max_value_errors(field))
    return errors


def SlugField_angular_errors(field):
    errors = _input_required(field)
    return errors


def RegexField_angular_errors(field):
    # Probably Python Regex can't be translated 1:1 into JS regex. Any hints on how to convert these?
    field.widget.attrs['ng-pattern'] = '/{0}/'.format(field.regex.pattern)
    errors = _input_required(field)
    errors.extend(_min_max_length_errors(field))
    errors.extend(_invalid_value_errors(field, 'pattern'))
    return errors


def Default_angular_errors(field):
    errors = _input_required(field)
    return errors
