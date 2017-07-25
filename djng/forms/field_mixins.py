# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Mixin class methods to be added to django.forms.fields at runtime. These methods add additional
error messages for AngularJS form validation.
"""
import re

from django.forms import fields
from django.forms import widgets
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, ungettext_lazy


class DefaultFieldMixin(object):
    render_label = True

    def has_subwidgets(self):
        return False

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
                    'Ensure this value has at least %(limit_value)d characters',
                    'limit_value')
                errors.append(('$error.minlength', message % {'limit_value': self.min_length}))
            if getattr(item, 'code', None) == 'max_length':
                message = ungettext_lazy(
                    'Ensure this value has at most %(limit_value)d character',
                    'Ensure this value has at most %(limit_value)d characters',
                    'limit_value')
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

    def update_widget_attrs(self, bound_field, attrs):
        """
        Update the dictionary of attributes used  while rendering the input widget
        """
        bound_field.form.update_widget_attrs(bound_field, attrs)
        widget_classes = self.widget.attrs.get('class', None)
        if widget_classes:
            if 'class' in attrs:
                attrs['class'] += ' ' + widget_classes
            else:
                attrs.update({'class': widget_classes})
        return attrs


class CharFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        return errors


class DecimalFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        self.widget.attrs['ng-minlength'] = 1
        if isinstance(self.max_digits, int) and self.max_digits > 0:
            self.widget.attrs['ng-maxlength'] = self.max_digits + 1
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class EmailFieldMixin(DefaultFieldMixin):
    def get_potential_errors(self):
        self.widget.attrs['email-pattern'] = self.get_email_regex()
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('email'))
        return errors

    def get_email_regex(self):
        """
        Return a regex pattern matching valid email addresses. Uses the same
        logic as the django validator, with the folowing exceptions:

        - Internationalized domain names not supported
        - IP addresses not supported
        - Strips lookbehinds (not supported in javascript regular expressions)
        """
        validator = self.default_validators[0]
        user_regex = validator.user_regex.pattern.replace('\Z', '@')
        domain_patterns = ([re.escape(domain) + '$' for domain in
                            validator.domain_whitelist] +
                           [validator.domain_regex.pattern.replace('\Z', '$')])
        domain_regex = '({0})'.format('|'.join(domain_patterns))
        email_regex = user_regex + domain_regex
        return re.sub(r'\(\?\<[^()]*?\)', '', email_regex)  # Strip lookbehinds


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
    render_label = False

    def has_subwidgets(self):
        return True

    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        bound_field.form.update_widget_attrs(bound_field, attrs)
        return attrs

    def update_widget_rendering_context(self, context):
        context['widget'].update(field_label=self.label)
        return context


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
    def has_subwidgets(self):
        return isinstance(self.widget, widgets.RadioSelect)

    def get_potential_errors(self):
        if isinstance(self.widget, widgets.RadioSelect):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        from django import VERSION

        if VERSION < (1, 11) and isinstance(self.widget, widgets.RadioSelect):
            attrs.update(radio_select_required=self.required)
        bound_field.form.update_widget_attrs(bound_field, attrs)
        return attrs


class MultipleChoiceFieldMixin(MultipleFieldMixin):
    def has_subwidgets(self):
        return isinstance(self.widget, widgets.CheckboxSelectMultiple)

    def get_potential_errors(self):
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        bound_field.form.update_widget_attrs(bound_field, attrs)
        return attrs

    def get_converted_widget(self):
        from .widgets import CheckboxSelectMultiple

        assert(isinstance(self, fields.MultipleChoiceField))
        if not isinstance(self.widget, widgets.CheckboxSelectMultiple):
            return
        new_widget = CheckboxSelectMultiple()
        new_widget.__dict__ = self.widget.__dict__
        return new_widget

    def implode_multi_values(self, name, data):
        """
        Due to the way Angular organizes it model, when Form data is sent via a POST request,
        then for this kind of widget, the posted data must to be converted into a format suitable
        for Django's Form validation.
        """
        mkeys = [k for k in data.keys() if k.startswith(name + '.')]
        mvls = [data.pop(k)[0] for k in mkeys]
        if mvls:
            data.setlist(name, mvls)

    def convert_ajax_data(self, field_data):
        """
        Due to the way Angular organizes it model, when this Form data is sent using Ajax,
        then for this kind of widget, the sent data has to be converted into a format suitable
        for Django's Form validation.
        """
        data = [key for key, val in field_data.items() if val]
        return data

    def update_widget_rendering_context(self, context):
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            ng_model = mark_safe(context['widget']['attrs'].pop('ng-model', ''))
            if ng_model:
                validate_fields = []
                for group, options, index in context['widget']['optgroups']:
                    for option in options:
                        option['name'] = format_html('{name}.{value}', **option)
                        validate_fields.append(format_html('"{name}"', **option))
                        option['attrs']['ng-model'] = format_html('{0}[\'{value}\']', ng_model, **option)
                if self.required:
                    context['widget']['attrs']['validate-multiple-fields'] = format_html('[{}]', ', '.join(validate_fields))
        return context


class FileFieldMixin(DefaultFieldMixin):
    def get_converted_widget(self):
        return super(FileFieldMixin, self).get_converted_widget()

    def get_potential_errors(self):
        errors = []
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        return attrs
