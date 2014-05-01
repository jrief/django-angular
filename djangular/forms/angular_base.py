# -*- coding: utf-8 -*-
import six
from base64 import b64encode
from django.forms import forms
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe, SafeData


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
    1: property: $pristine or $dirty used by ng-show on the wrapping <ul>-element.
    2: A arbitrary property used by ng-show on the actual <li>-element.
    3: The CSS class added to the <li>-element.
    4: The used error message. If this contains the magic word '$message' it will be added with
       ``ng-bind`` rather than rendered inside the list item.
    """
    ul_format = '<ul class="djng-form-errors" ng-show="{0}.{1}" ng-cloak>{2}</ul>'
    li_format = '<li ng-show="{0}.{1}" class="{2}">{3}</li>'
    li_format_bind = '<li ng-show="{0}.{1}" class="{2}" ng-bind="{0}.{3}"></li>'

    def __str__(self):
        return self.as_ul()

    def __repr__(self):
        return repr([force_text(e[4]) for e in self])

    def as_ul(self):
        if not self:
            return ''
        pristine_list_items = []
        dirty_list_items = []
        for e in self:
            li_format = e[4] == '$message' and self.li_format_bind or self.li_format
            err_tuple = (e[0], e[2], e[3], force_text(e[4]))
            if e[1] == '$pristine':
                pristine_list_items.append(format_html(li_format, *err_tuple))
            else:
                dirty_list_items.append(format_html(li_format, *err_tuple))
        # renders and combine both of these lists
        return (pristine_list_items and
                format_html(self.ul_format, self[0][0], '$pristine', mark_safe(''.join(pristine_list_items))) or '') + \
            (dirty_list_items and
             format_html(self.ul_format, self[0][0], '$dirty', mark_safe(''.join(dirty_list_items))) or '')

    def as_text(self):
        if not self:
            return ''
        return '\n'.join(['* %s' % force_text(e[4]) for e in self if bool(e[4])])


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


class NgFormBaseMixin(object):
    def __init__(self, *args, **kwargs):
        try:
            form_name = self.form_name
        except AttributeError:
            # if form_name is unset, then generate a pseudo unique name, based upon the class name
            form_name = b64encode(six.b(self.__class__.__name__)).rstrip(six.b('='))
        self.form_name = kwargs.pop('form_name', form_name)
        error_class = kwargs.pop('error_class', TupleErrorList)
        kwargs.setdefault('error_class', error_class)
        super(NgFormBaseMixin, self).__init__(*args, **kwargs)

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
        return self.error_class([SafeTuple((identifier, '$pristine', '$pristine', 'invalid', e))
                         for e in self.errors.get(field.name, [])])

    def non_field_errors(self):
        errors = super(NgFormBaseMixin, self).non_field_errors()
        return self.error_class([SafeTuple((self.form_name, '$pristine', '$pristine', 'invalid', e))
                         for e in errors])
