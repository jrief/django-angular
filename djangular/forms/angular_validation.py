# -*- coding: utf-8 -*-
import itertools
from django import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.safestring import SafeData
from djangular.forms.angular_base import NgFormBaseMixin


class SafeTuple(tuple, SafeData):
    pass


class KeyErrorList(object):
    """
    Container class to hold error messages for form validation. This class replaces ErrorList and
    handles some issues which makes it really hard to use Django forms out of the predetermined
    work flow.
    """
    def __init__(self, field_name, errors):
        if not isinstance(errors, (list, tuple)):
            raise AttributeError('KeyErrorList must be initialized with a list or tuple')
        if not isinstance(field_name, str):
            raise AttributeError('field_name must be of type string')
        if errors and not isinstance(errors[0], tuple):
            errors = [('', msg) for msg in errors]
        self._errors = errors
        self.field_name = field_name

    def __iter__(self):
        for e in self._errors:
            yield SafeTuple((self.field_name, e[0], force_text(e[1])))


class TupleErrorList(forms.util.ErrorList):
    def as_ul(self):
        field_name = len(self) and isinstance(self[0], SafeTuple) and self[0][0] or ''
        lis = format_html_join('', '<li ng-show="{0}.$error.{1}">{2}</li>', (e for e in list.__iter__(self)))
        return format_html('<ul class="{0}" ng-hide="{1}.$pristine">{2}</ul>',
                           self.form_error_class, field_name, lis)

    def __iter__(self):
        for e in list.__iter__(self):
            yield isinstance(e, SafeTuple) and force_text(e[1]) or e


def error_property(key, msg, field):
    """
    Map the key, given by Django, for an invalid property to the corresponding AngularJS invalid
    property object member, as used in <field-name>.$error.<property>
    """
    if key == 'min_value':
        return [('min', msg % {'limit_value': field.min_value})]
    if key == 'max_value':
        return [('max', msg % {'limit_value': field.max_value})]
    if key == 'invalid':
        return [('minlength', msg), ('maxlength', msg)]
    return [(key, msg)]


class NgFormValidationMixin(NgFormBaseMixin):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, which shall be
    auto validated using the Angular's validation mechanism.
    """
    def __init__(self, *args, **kwargs):
        self.form_name = kwargs.pop('form_name', 'form')
        self.form_error_class = kwargs.pop('form_error_class', 'djng-form-errors')
        kwargs.update(error_class=type('SafeTupleErrorList', (TupleErrorList,), { 'form_error_class': self.form_error_class }))
        super(NgFormValidationMixin, self).__init__(*args, **kwargs)
        if not hasattr(self, '_errors') or self._errors is None:
            self._errors = forms.util.ErrorDict()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.TextInput):
                errors = list(itertools.chain(*[error_property(key, msg, field)
                              for key, msg in field.default_error_messages.items()]))
                identifier = self.add_prefix(name)
                field_name = '{0}.{1}'.format(self.form_name, identifier)
                self._errors[name] = KeyErrorList(field_name, errors)
                field.widget.attrs.setdefault('ng-model', identifier)
                field.widget.attrs['ng-required'] = str(field.required).lower()
                if hasattr(field, 'min_length'):
                    field.widget.attrs['ng-minlength'] = field.min_length
                if hasattr(field, 'max_length'):
                    field.widget.attrs['ng-maxlength'] = field.max_length
                if hasattr(field, 'min_value'):
                    field.widget.attrs['min'] = field.min_value
                if hasattr(field, 'max_value'):
                    field.widget.attrs['max'] = field.max_value
                if hasattr(field, 'regex'):
                    # Probably Python Regex can't be translated 1:1 into JS regex.
                    # Any hints on how to convert these?
                    field.widget.attrs['ng-pattern'] = '/{0}/'.format(field.regex.pattern)
                if isinstance(field, forms.DecimalField):
                    field.widget.input_type = 'number'

    def name(self):
        return self.form_name
