# -*- coding: utf-8 -*-
from django import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class KeyErrorList(object):
    def __init__(self, errors=[], ng_model=''):
        if not isinstance(errors, (list, tuple)):
            raise AttributeError('KeyErrorList must be initialized with a list or tuple')
        if errors and not isinstance(errors[0], tuple):
            errors = [('', msg) for msg in errors]
        self._errors = errors
        self.ng_model = ng_model

    def __iter__(self):
        for e in self._errors:
            if self.ng_model:
                yield mark_safe('<span ng-show="{0}.$errors.{1}">{2}</span>'.format(self.ng_model, e[0], force_text(e[1])))
            else:
                yield e[1]

    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        lis = format_html_join('', '<li>{0}</li>', ((force_text(e),) for e in self.__iter__()))
        return format_html('<ul class="my-errs">{0}</ul>', lis)

    def as_text(self):
        return '\n'.join(['* %s' % force_text(e[1]) for e in self._errors])

    def __repr__(self):
        return repr([force_text(e[1]) for e in self._errors])


class NgFormValidationMixin(object):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, if you want to auto
    validate the form using the Angular's validation mechanism.
    """
    def __init__(self, *args, **kwargs):
        kwargs['error_class'] = KeyErrorList
        super(NgFormValidationMixin, self).__init__(*args, **kwargs)
        if self._errors is None:
            self._errors = forms.util.ErrorDict()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.TextInput):
                if hasattr(self, 'scope_prefix') and hasattr(self, 'add_prefix') and callable(self.add_prefix):
                    errors = [(key, msg) for key, msg in field.error_messages.items()]
                    identifier = self.add_prefix(name)
                    ng_model = self.scope_prefix and ('%s.%s' % (self.scope_prefix, identifier)) or identifier
                    self._errors[name] = KeyErrorList(errors, ng_model)
                field.widget.attrs.setdefault('ng-required', field.required)
                if isinstance(field.min_length, int):
                    field.widget.attrs.setdefault('ng-minlength', field.min_length)
                if isinstance(field.max_length, int):
                    field.widget.attrs.setdefault('ng-maxlength', field.max_length)
                if hasattr(field, 'regex'):
                    # Probably Python Regex can't be translated 1:1 into JS regex.
                    # Any hints on how to convert these?
                    field.widget.attrs.setdefault('ng-pattern', '/%s/' % field.regex.pattern)
