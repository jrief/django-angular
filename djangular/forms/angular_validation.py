# -*- coding: utf-8 -*-
import types
from django.conf import settings
from django.forms import forms
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.importlib import import_module
from djangular.forms.angular_base import NgFormBaseMixin

VALIDATION_MAPPING_MODULE = import_module(getattr(settings, 'DJANGULAR_VALIDATION_MAPPING_MODULE', 'djangular.forms.patched_fields'))


class TupleErrorList(list):
    """
    A collection of errors that knows how to display errors for the AngularJS form validation
    engine, in various formats.
    """
    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        if not self:
            return ''
        if getattr(self, '_ng_non_field_errors', False):
            # renders a non-field error
            return format_html('<ul class="djng-form-errors" ng-hide="{0}.{1}" ng-cloak>{2}</ul>',
                self.identifier, self.property, format_html_join('', '<li>{0}</li>', ((force_text(e),) for e in self)))
        # renders a field error
        return format_html('<ul class="djng-form-errors" ng-hide="{0}.{1}" ng-cloak>{2}<li ng-show="{0}.$valid" class="valid"></li></ul>',
            self.identifier, self.property, format_html_join('', '<li ng-show="{0}.{1}" class="invalid">{2}</li>',
                ((self.identifier, e[0], force_text(e[1])) for e in self)))

    def as_text(self):
        if not self:
            return ''
        if getattr(self, '_ng_non_field_errors', False):
            return '\n'.join(['* {0}'.format(force_text(e)) for e in self])
        return '\n'.join(['* {0}'.format(force_text(e[1])) for e in self])


class NgValidationBoundField(forms.BoundField):
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
            lt = super(NgValidationBoundField, self).label_tag(contents, attrs)
        else:
            lt = super(NgValidationBoundField, self).label_tag(contents, attrs, label_suffix)
        return lt + self.ng_errors()


class NgFormValidationMixin(NgFormBaseMixin):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, which shall be
    auto validated using the Angular's validation mechanism.
    """
    form_name = 'form'

    def __init__(self, *args, **kwargs):
        self.form_name = kwargs.pop('form_name', self.form_name)
        self.ValidationErrorClass = kwargs.pop('ng_validation_error_class', TupleErrorList)
        ng_error_class = type('ValidationErrorList', (self.ValidationErrorClass,),
                              {'identifier': self.form_name, 'property': '$dirty'})
        kwargs.setdefault('error_class', ng_error_class)
        super(NgFormValidationMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # add ng-model to each model field
            ng_model = self.add_prefix(name)
            field.widget.attrs.setdefault('ng-model', ng_model)
            setattr(field, 'ng_field_name', '{0}.{1}'.format(self.form_name, ng_model))
            # each field type may have different errors and additional AngularJS specific attributes
            ng_errors_function = '{0}_angular_errors'.format(field.__class__.__name__)
            try:
                ng_errors_function = getattr(VALIDATION_MAPPING_MODULE, ng_errors_function)
                ng_potential_errors = types.MethodType(ng_errors_function, field)()
            except (TypeError, AttributeError):
                ng_errors_function = getattr(VALIDATION_MAPPING_MODULE, 'Default_angular_errors')
                ng_potential_errors = types.MethodType(ng_errors_function, field)()
            ng_error_class = type('ValidationErrorList', (self.ValidationErrorClass,),
                                  {'identifier': field.ng_field_name, 'property': '$pristine'})
            setattr(field, 'ng_potential_errors', ng_error_class(ng_potential_errors))

    def __getitem__(self, name):
        "Returns a NgValidationBoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return NgValidationBoundField(self, field, name)

    def name(self):
        return self.form_name

    def _post_clean(self):
        super(NgFormValidationMixin, self)._post_clean()
        # transfer field errors generated by the server into a special error list managed by Angular
        for name, error_list in self._errors.items():
            try:
                field = self.fields[name]
                ng_error_class = type('ValidationErrorList', (self.ValidationErrorClass,),
                                      {'identifier': field.ng_field_name, 'property': '$dirty'})
                setattr(field, 'ng_detected_errors', ng_error_class(('$pristine', e) for e in error_list))
                setattr(error_list, '_ng_non_field_errors', False)
            except KeyError:
                # presumably this is a non-field error
                setattr(error_list, '_ng_non_field_errors', True)
