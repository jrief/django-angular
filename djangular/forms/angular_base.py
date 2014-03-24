# -*- coding: utf-8 -*-
from django.forms import forms


class NgFormBaseMixin(object):
    def add_prefix(self, field_name):
        """
        Rewrite the model keys to use dots instead of dashes, since thats the syntax
        used in Angular models.
        """
        return self.prefix and ('%s.%s' % (self.prefix, field_name)) or field_name


class NgBoundField(forms.BoundField):
    def ng_errors(self):
        """
        Returns an unsorted list of detected and potential errors, which may occur while validating
        an input field, using AngularJS's form validation.
        """
        if hasattr(self.field, 'ng_detected_errors'):
            return self.field.ng_detected_errors.as_ul() + self.field.ng_potential_errors.as_ul()
        return self.field.ng_potential_errors.as_ul()

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
