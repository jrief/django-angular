# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
from base64 import b64encode
from django.forms import forms
from django.http import QueryDict
from django.utils.importlib import import_module
from django.utils.html import format_html
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.safestring import mark_safe, SafeData


class SafeTuple(SafeData, tuple):
    """
    Used to bypass escaping of TupleErrorList by the ``conditional_escape`` function in Django's form rendering.
    """
    pass


@python_2_unicode_compatible
class TupleErrorList(list):
    """
    A list of errors, which in contrast to Django's ErrorList, contains a tuple for each item.
    This tuple consists of the following fields:
    0: identifier: This is the model name of the field.
    1: The CSS class added to the embedding <ul>-element.
    2: property: '$pristine', '$dirty' or None used by ng-show on the wrapping <ul>-element.
    3: An arbitrary property used by ng-show on the actual <li>-element.
    4: The CSS class added to the <li>-element.
    5: The desired error message. If this contains the magic word '$message' it will be added with
       ``ng-bind`` rather than rendered inside the list item.
    """
    ul_format = '<ul class="{1}" ng-show="{0}.{2}" ng-cloak>{3}</ul>'
    li_format = '<li ng-show="{0}.{1}" class="{2}">{3}</li>'
    li_format_bind = '<li ng-show="{0}.{1}" class="{2}" ng-bind="{0}.{3}"></li>'

    def __str__(self):
        return self.as_ul()

    def __repr__(self):
        return repr([force_text(e[5]) for e in self])

    def as_ul(self):
        if not self:
            return ''
        error_lists = {'$pristine': [], '$dirty': []}
        for e in self:
            li_format = e[5] == '$message' and self.li_format_bind or self.li_format
            err_tuple = (e[0], e[3], e[4], force_text(e[5]))
            error_lists[e[2]].append(format_html(li_format, *err_tuple))
        # renders and combine both of these lists
        first = self[0]
        return mark_safe(''.join([format_html(self.ul_format, first[0], first[1], prop,
                    mark_safe(''.join(list_items))) for prop, list_items in error_lists.items()]))

    def as_text(self):
        if not self:
            return ''
        return '\n'.join(['* %s' % force_text(e[5]) for e in self if bool(e[5])])


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
        Returns a string of space-separated CSS classes for this field.
        """
        if hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        extra_classes.update(getattr(self.form, 'field_css_classes', '').split())
        return super(NgBoundField, self).css_classes(extra_classes)

    def as_widget(self, widget=None, attrs=None, **kwargs):
        """
        Renders the field.
        """
        attrs = attrs or {}
        attrs.update(self.form.get_widget_attrs(self))
        if hasattr(self.field, 'widget_css_classes'):
            css_classes = self.field.widget_css_classes
        else:
            css_classes = getattr(self.form, 'widget_css_classes', None)
        if css_classes:
            attrs.update({'class': css_classes})
        return super(NgBoundField, self).as_widget(widget, attrs, **kwargs)

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        css_classes = getattr(self.field, 'label_css_classes', None)
        if css_classes:
            attrs.update({'class': css_classes})
        return super(NgBoundField, self).label_tag(contents, attrs, label_suffix='')


class NgFormBaseMixin(object):
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-field-errors'
    field_mixins_module = field_mixins_fallback_module = 'djangular.forms.field_mixins'

    def __new__(cls, **kwargs):
        field_mixins_module = import_module(cls.field_mixins_module)
        field_mixins_fallback_module = import_module(cls.field_mixins_fallback_module)
        new_cls = super(NgFormBaseMixin, cls).__new__(cls)
        # add additional methods to django.form.fields at runtime
        for field in new_cls.base_fields.values():
            FieldMixinName = field.__class__.__name__ + 'Mixin'
            try:
                FieldMixin = getattr(field_mixins_module, FieldMixinName)
            except AttributeError:
                try:
                    FieldMixin = getattr(field_mixins_fallback_module, FieldMixinName)
                except AttributeError:
                    FieldMixin = field_mixins_fallback_module.DefaultFieldMixin
            field.__class__ = type(field.__class__.__name__, (field.__class__, FieldMixin), {})
        return new_cls

    def __init__(self, data=None, *args, **kwargs):
        try:
            form_name = self.form_name
        except AttributeError:
            # if form_name is unset, then generate a pseudo unique name, based upon the class name
            form_name = b64encode(six.b(self.__class__.__name__)).rstrip(six.b('='))
        self.form_name = kwargs.pop('form_name', form_name)
        error_class = kwargs.pop('error_class', TupleErrorList)
        kwargs.setdefault('error_class', error_class)
        self.convert_widgets()
        if isinstance(data, QueryDict):
            data = self.rectify_multipart_form_data(data.copy())
        elif isinstance(data, dict):
            data = self.rectify_ajax_form_data(data.copy())
        super(NgFormBaseMixin, self).__init__(data, *args, **kwargs)

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
        return self.prefix and ('%s.%s' % (self.prefix, field_name)) or field_name

    def get_field_errors(self, field):
        """
        Return server side errors. Shall be overridden by derived forms to add their extra errors for AngularJS.
        """
        identifier = format_html('{0}.{1}', self.form_name, field.name)
        errors = self.errors.get(field.name, [])
        return self.error_class([SafeTuple(
            (identifier, self.field_error_css_classes, '$pristine', '$pristine', 'invalid', e)) for e in errors])

    def non_field_errors(self):
        errors = super(NgFormBaseMixin, self).non_field_errors()
        return self.error_class([SafeTuple(
            (self.form_name, self.form_error_css_classes, '$pristine', '$pristine', 'invalid', e)) for e in errors])

    def get_widget_attrs(self, bound_field):
        """
        Return a dictionary of additional attributes which shall be added to the widget,
        used to render this field.
        """
        return {}

    def convert_widgets(self):
        """
        During form initialization, some widgets have to be replaced by a counterpart suitable to
        be rendered the AngularJS way.
        """
        for field in self.base_fields.values():
            try:
                new_widget = field.get_converted_widget()
            except AttributeError:
                pass
            else:
                if new_widget:
                    field.widget = new_widget

    def rectify_multipart_form_data(self, data):
        """
        If a widget was converted and the Form data was submitted through a multipart request,
        then these data fields must be converted to suit the Django Form validation
        """
        for name, field in self.base_fields.items():
            try:
                field.widget.implode_multi_values(name, data)
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
                data[name] = field.widget.convert_ajax_data(data.get(name, {}))
            except AttributeError:
                pass
        return data
