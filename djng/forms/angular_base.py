# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from base64 import b64encode

try:
    from collections import UserList
except ImportError:  # Python 2
    from UserList import UserList

import warnings

from django import VERSION as DJANGO_VERSION
from django.forms import forms
from django.http import QueryDict
from django.utils import six
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from django.utils.html import format_html, format_html_join, escape, conditional_escape
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe, SafeText, SafeData
from django.core.exceptions import ValidationError, ImproperlyConfigured

from .fields import DefaultFieldMixin


class SafeTuple(SafeData, tuple):
    """
    Used to bypass escaping of TupleErrorList by the ``conditional_escape`` function in Django's
    form rendering.
    """


@python_2_unicode_compatible
class TupleErrorList(UserList, list):
    """
    A list of errors, which in contrast to Django's ErrorList, can contain a tuple for each item.
    If this TupleErrorList is initialized with a Python list, it behaves like Django's built-in
    ErrorList.
    If this TupleErrorList is initialized with a list of tuples, it behaves differently, suitable
    for AngularJS form validation. Then the tuple of each list item consist of the following fields:
    0: identifier: This is the model name of the field.
    1: The CSS class added to the embedding <ul>-element.
    2: property: '$pristine', '$dirty' or None used by ng-show on the wrapping <ul>-element.
    3: An arbitrary property used by ng-show on the actual <li>-element.
    4: The CSS class added to the <li>-element.
    5: The desired error message. If this contains the magic word '$message' it will be added with
       ``ng-bind`` rather than rendered inside the list item.
    """
    def __init__(self, initlist=None, error_class=None):
        super(TupleErrorList, self).__init__(initlist)

        if error_class is None:
            self.error_class = 'errorlist'
        else:
            self.error_class = 'errorlist {}'.format(error_class)

    def as_data(self):
        return ValidationError(self.data).error_list

    def get_json_data(self, escape_html=False):
        errors = []
        for error in self.as_data():
            message = list(error)[0]
            errors.append({
                'message': escape(message) if escape_html else message,
                'code': error.code or '',
            })
        return errors

    def as_json(self, escape_html=False):
        return json.dumps(self.get_json_data(escape_html))

    def extend(self, iterable):
        """
        django.forms.forms.BaseForm._html_output() extends non_field_errors
        with a string error for each hidden field. The string format is incompatible
        with djng TupleErrorList of SafeTuples causing an exception in as_ul.
        Instead we discard extends containing strings here and add errors in non_field_errors
        for hidden fields in NgFormBaseMixin
        """
        for item in iterable:
            if not isinstance(item, str):
                self.append(item)
        return None

    def as_ul(self):
        if not self:
            return SafeText()
        first = self[0]
        if isinstance(first, tuple):
            error_lists = {'$pristine': [], '$dirty': []}
            for e in self:
                if e[5] == '$message':
                    li_format = '<li ng-show="{0}.{1} && {0}.{3}" class="{2}" ng-bind="{0}.{3}"></li>'
                else:
                    li_format = '<li ng-show="{0}.{1}" class="{2}">{3}</li>'
                err_tuple = (e[0], e[3], e[4], force_text(e[5]))
                error_lists[e[2]].append(format_html(li_format, *err_tuple))
            # renders and combine both of these lists
            dirty_errors, pristine_errors = '', ''
            if len(error_lists['$dirty']) > 0:
                dirty_errors = format_html(
                    '<ul ng-show="{0}.$dirty && !{0}.$untouched" class="{1}" ng-cloak>{2}</ul>',  # duck typing: !...$untouched
                    first[0], first[1], mark_safe(''.join(error_lists['$dirty']))
                )
            if len(error_lists['$pristine']) > 0:
                pristine_errors = format_html(
                    '<ul ng-show="{0}.$pristine" class="{1}" ng-cloak>{2}</ul>',
                    first[0], first[1], mark_safe(''.join(error_lists['$pristine']))
                )
            return format_html('{}{}', dirty_errors, pristine_errors)
        return format_html('<ul class="errorlist">{0}</ul>',
            format_html_join('', '<li>{0}</li>', ((force_text(e),) for e in self)))

    def as_text(self):
        if not self:
            return ''
        if isinstance(self[0], tuple):
            return '\n'.join(['* %s' % force_text(e[5]) for e in self if bool(e[5])])
        return '\n'.join(['* %s' % force_text(e) for e in self])

    def __str__(self):
        return self.as_ul()

    def __repr__(self):
        if self and isinstance(self[0], tuple):
            return repr([force_text(e[5]) for e in self])
        return repr([force_text(e) for e in self])

    def __contains__(self, item):
        return item in list(self)

    def __eq__(self, other):
        return list(self) == other

    def __ne__(self, other):
        return list(self) != other

    def __getitem__(self, i):
        error = self.data[i]
        if isinstance(error, tuple):
            if isinstance(error[5], ValidationError):
                error[5] = list(error[5])[0]
            return error
        if isinstance(error, ValidationError):
            return list(error)[0]
        return force_text(error)


class NgWidgetMixin(object):
    def get_context(self, name, value, attrs):
        """
        Some widgets require a modified rendering context, if they contain angular directives.
        """
        context = super(NgWidgetMixin, self).get_context(name, value, attrs)
        if callable(getattr(self._field, 'update_widget_rendering_context', None)):
            self._field.update_widget_rendering_context(context)
        return context


class NgBoundField(forms.BoundField):
    @property
    def errors(self):
        """
        Returns a TupleErrorList for this field. This overloaded method adds additional error lists
        to the errors as detected by the form validator.
        """
        if not hasattr(self, '_errors_cache'):
            self._errors_cache = self.form.get_field_errors(self)
        return self._errors_cache

    def css_classes(self, extra_classes=None):
        """
        Returns a string of space-separated CSS classes for the wrapping element of this input field.
        """
        if hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        # field_css_classes is an optional member of a Form optimized for django-angular
        field_css_classes = getattr(self.form, 'field_css_classes', None)
        if hasattr(field_css_classes, 'split'):
            extra_classes.update(field_css_classes.split())
        elif isinstance(field_css_classes, (list, tuple)):
            extra_classes.update(field_css_classes)
        elif isinstance(field_css_classes, dict):
            extra_field_classes = []
            for key in ('*', self.name):
                css_classes = field_css_classes.get(key)
                if hasattr(css_classes, 'split'):
                    extra_field_classes = css_classes.split()
                elif isinstance(css_classes, (list, tuple)):
                    if '__default__' in css_classes:
                        css_classes.remove('__default__')
                        extra_field_classes.extend(css_classes)
                    else:
                        extra_field_classes = css_classes
            extra_classes.update(extra_field_classes)
        return super(NgBoundField, self).css_classes(extra_classes)

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        """
        Renders the field.
        """
        if not widget:
            widget = self.field.widget

        if DJANGO_VERSION > (1, 10):
            # so that we can refer to the field when building the rendering context
            widget._field = self.field
            # Make sure that NgWidgetMixin is not already part of the widget's bases so it doesn't get added twice.
            if not isinstance(widget, NgWidgetMixin):
                widget.__class__ = type(widget.__class__.__name__, (NgWidgetMixin, widget.__class__), {})
        return super(NgBoundField, self).as_widget(widget, attrs, only_initial)

    def build_widget_attrs(self, attrs, widget=None):
        if not widget:
            widget = self.field.widget
        attrs = super(NgBoundField, self).build_widget_attrs(attrs, widget=widget)
        if callable(getattr(self.field, 'update_widget_attrs', None)):
            self.field.update_widget_attrs(self, attrs)
        return attrs

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        if self.field.render_label is False:
            return ''  # label shall be rendered by the widget
        attrs = attrs or {}
        css_classes = getattr(self.field, 'label_css_classes', None)
        if hasattr(css_classes, 'split'):
            css_classes = css_classes.split()
        css_classes = set(css_classes or [])
        label_css_classes = getattr(self.form, 'label_css_classes', None)
        if hasattr(label_css_classes, 'split'):
            css_classes.update(label_css_classes.split())
        elif isinstance(label_css_classes, (list, tuple)):
            css_classes.update(label_css_classes)
        elif isinstance(label_css_classes, dict):
            for key in (self.name, '*',):
                extra_label_classes = label_css_classes.get(key)
                if hasattr(extra_label_classes, 'split'):
                    extra_label_classes = extra_label_classes.split()
                extra_label_classes = set(extra_label_classes or [])
                css_classes.update(extra_label_classes)
        if css_classes:
            attrs.update({'class': ' '.join(css_classes)})
        return super(NgBoundField, self).label_tag(contents, attrs, label_suffix='')


class BaseFieldsModifierMetaclass(type):
    """
    Metaclass that reconverts Field attributes from the dictionary 'base_fields' into Fields
    with additional functionality required for AngularJS's Form control and Form validation.
    """
    def __new__(cls, name, bases, attrs):
        attrs.update(formfield_callback=cls.formfield_callback)
        new_class = super(BaseFieldsModifierMetaclass, cls).__new__(cls, name, bases, attrs)
        cls.validate_formfields(new_class)
        return new_class

    @classmethod
    def formfield_callback(cls, modelfield, **kwargs):
        # first get the default formfield for this modelfield
        formfield = modelfield.formfield(**kwargs)

        if formfield:
            # use the same class name to load the corresponding inherited formfield
            try:
                formfield_class = import_string('djng.forms.fields.' + formfield.__class__.__name__)
            except ImportError: # form field not declared by Django
                formfield_class = type(str(formfield.__class__.__name__), (DefaultFieldMixin, formfield.__class__), {})

            # recreate the formfield using our customized field class
            if hasattr(formfield, 'choices'):
                kwargs.update(choices_form_class=formfield_class)
            kwargs.update(form_class=formfield_class)
            formfield = modelfield.formfield(**kwargs)
        return formfield

    @classmethod
    def validate_formfields(cls, new_class):
        msg = "Please use the corresponding form fields from 'djng.forms.fields' for field '{} = {}(...)' " \
              "in form '{}', which inherits from 'NgForm' or 'NgModelForm'."
        for name, field in new_class.base_fields.items():
            if not isinstance(field, DefaultFieldMixin):
                raise ImproperlyConfigured(msg.format(name, field.__class__.__name__, new_class))


class NgFormBaseMixin(object):
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-field-errors'

    def __init__(self, *args, **kwargs):
        try:
            form_name = self.form_name
        except AttributeError:
            # if form_name is unset, then generate a pseudo unique name, based upon the class name
            form_name = b64encode(six.b(self.__class__.__name__)).rstrip(six.b('='))
            if six.PY3:
                form_name = form_name.decode('utf-8')
        self.form_name = kwargs.pop('form_name', form_name)
        error_class = kwargs.pop('error_class', TupleErrorList)
        kwargs.setdefault('error_class', error_class)
        if DJANGO_VERSION < (1, 11):
            self.convert_widgets()
        super(NgFormBaseMixin, self).__init__(*args, **kwargs)
        if isinstance(self.data, QueryDict):
            self.data = self.rectify_multipart_form_data(self.data.copy())
        elif isinstance(self.data, dict) and self.data:
            self.data = self.rectify_ajax_form_data(self.data.copy())

    def __getitem__(self, name):
        "Returns a NgBoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return NgBoundField(self, field, name)

    def add_prefix(self, field_name):
        """
        Rewrite the model keys to use dots instead of dashes, since thats the syntax
        used in Angular models.
        """
        return ('%s.%s' % (self.prefix, field_name)) if self.prefix else field_name

    def get_field_errors(self, field):
        """
        Return server side errors. Shall be overridden by derived forms to add their
        extra errors for AngularJS.
        """
        identifier = format_html('{0}[\'{1}\']', self.form_name, field.name)
        errors = self.errors.get(field.html_name, [])
        return self.error_class([SafeTuple(
            (identifier, self.field_error_css_classes, '$pristine', '$pristine', 'invalid', e)) for e in errors])

    def non_field_errors(self):
        # See TupleErrorList.extend for an explanation
        hidden_field_errors = []
        for name, field in self.fields.items():
            bf = self[name]
            bf_errors = [conditional_escape(error) for error in bf.errors]
            if bf.is_hidden and bf_errors:
                hidden_field_errors += [SafeTuple(
                    (self.form_name, self.form_error_css_classes, '$pristine', '{}.$isEmpty()'.format(name), 'invalid',
                        '(Hidden field {}) {}'.format(name, e[5])) ) for e in bf_errors]
        errors = super(NgFormBaseMixin, self).non_field_errors()
        return self.error_class(hidden_field_errors + [SafeTuple(
            (self.form_name, self.form_error_css_classes, '$pristine', '$pristine', 'invalid', e)) for e in errors])

    def update_widget_attrs(self, bound_field, attrs):
        """
        Updated the widget attributes which shall be added to the widget when rendering this field.
        """
        if bound_field.field.has_subwidgets() is False:
            widget_classes = getattr(self, 'widget_css_classes', None)
            if widget_classes:
                if 'class' in attrs:
                    attrs['class'] += ' ' + widget_classes
                else:
                    attrs.update({'class': widget_classes})
        return attrs

    def convert_widgets(self):
        """
        During form initialization, some widgets have to be replaced by a counterpart suitable to
        be rendered the AngularJS way.
        """
        warnings.warn("Will be removed after dropping support for Django-1.10", PendingDeprecationWarning)
        widgets_module = getattr(self, 'widgets_module', 'djng.widgets')
        for field in self.base_fields.values():
            if hasattr(field, 'get_converted_widget'):
                new_widget = field.get_converted_widget(widgets_module)
                if new_widget:
                    field.widget = new_widget

    def rectify_multipart_form_data(self, data):
        """
        If a widget was converted and the Form data was submitted through a multipart request,
        then these data fields must be converted to suit the Django Form validation
        """
        for name, field in self.base_fields.items():
            try:
                field.implode_multi_values(name, data)
            except AttributeError:
                pass
        return data

    def rectify_ajax_form_data(self, data):
        """
        If a widget was converted and the Form data was submitted through an Ajax request,
        then these data fields must be converted to suit the Django Form validation
        """
        for name, field in self.base_fields.items():
            try:
                data[name] = field.convert_ajax_data(data.get(name, {}))
            except AttributeError:
                pass
        return data
