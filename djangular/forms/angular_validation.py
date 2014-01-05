# -*- coding: utf-8 -*-
import types
from django import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.safestring import SafeData
from django.utils.importlib import import_module
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
        patched_form_fields_module = import_module('djangular.forms.patched_fields')
        for name, field in self.fields.items():
            # add ng-model to each model field
            identifier = self.add_prefix(name)
            field.widget.attrs.setdefault('ng-model', identifier)
            # each field type may have different errors and additional AngularJS specific attributes
            ng_errors_function = '{0}_angular_errors'.format(field.__class__.__name__)
            try:
                ng_errors_function = getattr(patched_form_fields_module, ng_errors_function)
                errors = types.MethodType(ng_errors_function, field)()
            except (TypeError, AttributeError):
                ng_errors_function = getattr(patched_form_fields_module, 'Default_angular_errors')
                errors = types.MethodType(ng_errors_function, field)()
            field_name = '{0}.{1}'.format(self.form_name, identifier)
            self._errors[name] = KeyErrorList(field_name, errors)

    def name(self):
        return self.form_name
