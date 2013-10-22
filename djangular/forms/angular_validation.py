# -*- coding: utf-8 -*-
from django import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.safestring import SafeData
import djangular


class SafeTuple(tuple, SafeData):
    pass


class KeyErrorList(object):
    """
    Container class to hold error messages for form validation. This class replaces ErrorList and
    handles some issues which makes it really hard to use Django forms out of the predetermined
    work flow.
    """
    def __init__(self, ng_model, errors):
        if not isinstance(errors, (list, tuple)):
            raise AttributeError('KeyErrorList must be initialized with a list or tuple')
        if not isinstance(ng_model, str):
            raise AttributeError('ng_model must be of type string')
        if errors and not isinstance(errors[0], tuple):
            errors = [('', msg) for msg in errors]
        self._errors = errors
        self.ng_model = ng_model

    def __iter__(self):
        for e in self._errors:
            yield SafeTuple((self.ng_model, e[0], force_text(e[1])))


class TupleErrorList(forms.util.ErrorList):
    def as_ul(self):
        ng_model = len(self) > 0 and self[0][0] or ''
        lis = format_html_join('', '<li ng-show="{0}.$error.{1}">{2}</li>', (e for e in list.__iter__(self)))
        return format_html('<ul class="{0}" ng-show="{1}.$dirty && {1}.$invalid">{2}</ul>',
                           self.form_error_class, ng_model, lis)

    def __iter__(self):
        for e in list.__iter__(self):
            yield isinstance(e, tuple) and force_text(e[1]) or e


class NgFormValidationMixin(object):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, which shall be
    auto validated using the Angular's validation mechanism.
    """
    def __init__(self, *args, **kwargs):
        form_error_class = kwargs.pop('form_error_class', 'djng-form-errors')
        kwargs.update(error_class=type('SafeTupleErrorList', (TupleErrorList,), { 'form_error_class': form_error_class }))
        super(NgFormValidationMixin, self).__init__(*args, **kwargs)
        if not hasattr(self, '_errors') or self._errors is None:
            self._errors = forms.util.ErrorDict()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.TextInput):
                if isinstance(self, djangular.forms.NgModelFormMixin):
                    errors = [(key, msg) for key, msg in field.error_messages.items()]
                    identifier = self.add_prefix(name)
                    ng_model = self.scope_prefix and '{0}.{1}'.format(self.scope_prefix, identifier) or identifier
                    self._errors[name] = KeyErrorList(ng_model, errors)
                field.widget.attrs.setdefault('ng-required', field.required)
                if isinstance(field.min_length, int):
                    field.widget.attrs.setdefault('ng-minlength', field.min_length)
                if isinstance(field.max_length, int):
                    field.widget.attrs.setdefault('ng-maxlength', field.max_length)
                if hasattr(field, 'regex'):
                    # Probably Python Regex can't be translated 1:1 into JS regex.
                    # Any hints on how to convert these?
                    field.widget.attrs.setdefault('ng-pattern', '/{0}/'.format(field.regex.pattern))
