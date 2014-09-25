# -*- coding: utf-8 -*-
"""
Mixin class methods to be added to django.forms.fields at runtime. These methods add additional
error messages for AngularJS form validation.
"""
from __future__ import unicode_literals
from django.forms import fields
from django.forms import widgets
from django.utils.translation import gettext_lazy, ungettext_lazy
from .widgets import CheckboxSelectMultiple as DjngCheckboxSelectMultiple


class DefaultFieldMixin(object):
    def get_potential_errors(self):
        return self.get_input_required_errors()

    def get_input_required_errors(self):
        errors = []
        if self.required:
            self.widget.attrs['ng-required'] = 'true'
            for key, msg in self.error_messages.items():
                if key == 'required':
                    errors.append(('$error.required', msg))
        return errors

    def get_min_max_length_errors(self):
        errors = []
        if getattr(self, 'min_length', None):
            self.widget.attrs['ng-minlength'] = self.min_length
        if getattr(self, 'max_length', None):
            self.widget.attrs['ng-maxlength'] = self.max_length
        for item in self.validators:
            if getattr(item, 'code', None) == 'min_length':
                message = ungettext_lazy(
                    'Ensure this value has at least %(limit_value)d character',
                    'Ensure this value has at least %(limit_value)d characters')
                errors.append(('$error.minlength', message % {'limit_value': self.min_length}))
            if getattr(item, 'code', None) == 'max_length':
                message = ungettext_lazy(
                    'Ensure this value has at most %(limit_value)d character',
                    'Ensure this value has at most %(limit_value)d characters')
                errors.append(('$error.maxlength', message % {'limit_value': self.max_length}))
        return errors

    def get_min_max_value_errors(self):
        errors = []
        if isinstance(getattr(self, 'min_value', None), int):
            self.widget.attrs['min'] = self.min_value
        if isinstance(getattr(self, 'max_value', None), int):
            self.widget.attrs['max'] = self.max_value
        errkeys = []
        for key, msg in self.error_messages.items():
            if key == 'min_value':
                errors.append(('$error.min', msg))
                errkeys.append(key)
            if key == 'max_value':
                errors.append(('$error.max', msg))
                errkeys.append(key)
        for item in self.validators:
            if getattr(item, 'code', None) == 'min_value' and 'min_value' not in errkeys:
                errors.append(('$error.min', item.message % {'limit_value': self.min_value}))
                errkeys.append('min_value')
            if getattr(item, 'code', None) == 'max_value' and 'max_value' not in errkeys:
                errors.append(('$error.max', item.message % {'limit_value': self.max_value}))
                errkeys.append('max_value')
        return errors

    def get_invalid_value_errors(self, ng_error_key):
        errors = []
        errkeys = []
        for key, msg in self.error_messages.items():
            if key == 'invalid':
                errors.append(('$error.{0}'.format(ng_error_key), msg))
                errkeys.append(key)
        for item in self.validators:
            if getattr(item, 'code', None) == 'invalid' and 'invalid' not in errkeys:
                errmsg = getattr(item, 'message', gettext_lazy('This input self does not contain valid data.'))
                errors.append(('$error.{0}'.format(ng_error_key), errmsg))
                errkeys.append('invalid')
        return errors


class CharFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        return errors


class DecimalFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        self.widget.attrs['ng-minlength'] = 1
        if hasattr(self, 'max_digits') and self.max_digits > 0:
            self.widget.attrs['ng-maxlength'] = self.max_digits + 1
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class EmailFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('email'))
        return errors


class DateFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('date'))
        return errors


class FloatFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class IntegerFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class SlugFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        return errors


class RegexFieldMixin(DefaultFieldMixin):
    # Presumably Python Regex can't be translated 1:1 into JS regex. Any hints on how to convert these?
    def get_potential_errors(self):
        self.widget.attrs['ng-pattern'] = '/{0}/'.format(self.regex.pattern)
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        errors.extend(self.get_invalid_value_errors('pattern'))
        return errors


class BooleanFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        return errors


class MultipleFieldMixin(DefaultFieldMixin):
    def get_multiple_choices_required(self):
        """
        Add only the required message, but no 'ng-required' attribute to the input fields,
        otherwise all Checkboxes of a MultipleChoiceField would require the property "checked".
        """
        errors = []
        if self.required:
            for key, msg in self.error_messages.items():
                if key == 'required':
                    errors.append(('$error.required', msg))
        return errors


class ChoiceFieldMixin(MultipleFieldMixin):
    def get_potential_errors(self):
        if isinstance(self.widget, widgets.RadioSelect):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors


class MultipleChoiceFieldMixin(MultipleFieldMixin):
    def get_potential_errors(self):
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors

    def get_converted_widget(self):
        assert(isinstance(self, fields.MultipleChoiceField))
        if not isinstance(self.widget, widgets.CheckboxSelectMultiple):
            return
        new_widget = DjngCheckboxSelectMultiple()
        new_widget.__dict__ = self.widget.__dict__
        return new_widget
