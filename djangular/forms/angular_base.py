# -*- coding: utf-8 -*-
from base64 import b64encode
from django.forms import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class TupleErrorList(list):
    """
    A collection of errors that knows how to display errors for the AngularJS form validation
    engine, in various formats.
    """
    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        extra_list_item = mark_safe(getattr(self, 'extra_list_item', ''))
        if not self and not extra_list_item:
            return ''
        if getattr(self, '_ng_non_field_errors', False):
            # renders a non-field error
            return format_html('<ul class="djng-form-errors" ng-hide="{0}.{1}" ng-cloak>{2}</ul>',
                self.identifier, self.property, format_html_join('', '<li class="invalid">{0}</li>',
                                                                 ((force_text(e),) for e in self)))
        # renders a field error
        list_items = format_html_join('', '<li ng-show="{0}.{1}" class="invalid">{2}</li>',
                        ((self.identifier, e[0], force_text(e[1])) for e in self)) + extra_list_item
        return format_html('<ul class="djng-form-errors" ng-hide="{0}.{1}" ng-cloak>{2}</ul>',
                           self.identifier, self.property, list_items)

    def as_text(self):
        if not self:
            return ''
        if getattr(self, '_ng_non_field_errors', False):
            return '\n'.join(['* {0}'.format(force_text(e)) for e in self])
        return '\n'.join(['* {0}'.format(force_text(e[1])) for e in self])


class NgBoundField(forms.BoundField):
    def ng_errors(self):
        """
        Returns an unsorted list of detected and potential errors, which may occur while validating
        an input field, using AngularJS's form validation.
        """
        uls = []
        if hasattr(self.field, 'ng_detected_errors'):
            uls.append(self.field.ng_detected_errors.as_ul())
        if hasattr(self.field, 'ng_potential_errors'):
            uls.append(self.field.ng_potential_errors.as_ul())
        return mark_safe(''.join(uls))

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        """
        Overload method which inserts AngularJS form validation elements just after the <label> tag.
        """
        from django import VERSION
        if VERSION[1] <= 5:
            lt = super(NgBoundField, self).label_tag(contents, attrs)
        else:
            lt = super(NgBoundField, self).label_tag(contents, attrs, label_suffix)
        return lt + self.ng_errors()


class NgFormBaseMixin(object):
    form_name = None

    def __init__(self, *args, **kwargs):
        self._form_name = kwargs.pop('form_name', self.form_name)
        self.NgErrorClass = kwargs.pop('ng_error_class', TupleErrorList)
        ng_error_class = type('NgErrorList', (self.NgErrorClass,),
                              {'identifier': self.form_name, 'property': '$dirty'})
        kwargs.setdefault('error_class', ng_error_class)
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

    def name(self):
        if not self._form_name:
            # generate a pseudo unique form name, based upon the class name
            self._form_name = b64encode(self.__class__.__name__).rstrip('=')
        return self._form_name
