# -*- coding: utf-8 -*-
import six
from base64 import b64encode
from django.forms import forms
from django.forms import fields
from django.forms import widgets
from django.http import QueryDict
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe, SafeData
from djangular.forms.widgets import CheckboxSelectMultiple as DjngCheckboxSelectMultiple


class SafeTuple(SafeData, tuple):
    """
    Used to bypass escaping of TupleErrorList by the ``conditional_escape`` function in Django's form rendering.
    """
    pass


class TupleErrorList(list):
    """
    A list of errors, which in comparison to Django's ErrorList contains a tuple for each item.
    This tuple consists of the following fields:
    0: identifier: This is the model name of the field.
    1: The CSS class added to the embedding <ul>-element.
    2: property: $pristine or $dirty used by ng-show on the wrapping <ul>-element.
    3: An arbitrary property used by ng-show on the actual <li>-element.
    4: The CSS class added to the <li>-element.
    5: The used error message. If this contains the magic word '$message' it will be added with
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
        pristine_list_items = []
        dirty_list_items = []
        for e in self:
            li_format = e[5] == '$message' and self.li_format_bind or self.li_format
            err_tuple = (e[0], e[3], e[4], force_text(e[5]))
            if e[2] == '$pristine':
                pristine_list_items.append(format_html(li_format, *err_tuple))
            else:
                dirty_list_items.append(format_html(li_format, *err_tuple))
        # renders and combine both of these lists
        first = self[0]
        return (pristine_list_items and \
             format_html(self.ul_format, first[0], first[1], '$pristine', mark_safe(''.join(pristine_list_items)))
          or '') + (dirty_list_items and \
             format_html(self.ul_format, first[0], first[1], '$dirty', mark_safe(''.join(dirty_list_items)))
          or '')

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
        # transfer error state from bound field to AngularJS validation
        errors = [e for e in self.errors if e[3] == '$pristine']
        if errors:
            attrs.update({'djng-error': errors[0][4]})
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

    def __init__(self, data=None, *args, **kwargs):
        try:
            form_name = self.form_name
        except AttributeError:
            # if form_name is unset, then generate a pseudo unique name, based upon the class name
            form_name = b64encode(six.b(self.__class__.__name__)).rstrip(six.b('='))
        self.form_name = kwargs.pop('form_name', form_name)
        error_class = kwargs.pop('error_class', TupleErrorList)
        kwargs.setdefault('error_class', error_class)
        data = self.convert_widgets(data)
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
        Return a dictionary of additional widget attributes.
        """
        return {}

    def convert_widgets(self, data):
        """
        During form initialization, some widgets have to be replaced by a counterpart suitable to
        be rendered the AngularJS way.
        """
        for name, field in self.base_fields.items():
            if isinstance(field, fields.MultipleChoiceField) and isinstance(field.widget, widgets.CheckboxSelectMultiple):
                fw_dict = field.widget.__dict__
                field.widget = DjngCheckboxSelectMultiple()
                field.widget.__dict__ = fw_dict
                if isinstance(data, QueryDict):
                    data = field.widget.implode_multi_values(name, data.copy())
        return data
