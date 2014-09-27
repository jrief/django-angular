# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.html import format_html
from django.utils.encoding import force_text
from .angular_base import NgFormBaseMixin, SafeTuple


class NgFormValidationMixin(NgFormBaseMixin):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, which shall be
    auto validated using the Angular's validation mechanism.
    """
    add_djng_error = True

    def __init__(self, *args, **kwargs):
        super(NgFormValidationMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # add ng-model to each model field
            ng_model = self.add_prefix(name)
            field.widget.attrs.setdefault('ng-model', ng_model)

    def get_field_errors(self, bound_field):
        """
        Determine the kind of input field and create a list of potential errors which may occur
        during validation of that field. This list is returned to be displayed in '$dirty' state
        if the field does not validate for that criteria.
        """
        errors = super(NgFormValidationMixin, self).get_field_errors(bound_field)
        if bound_field.is_hidden:
            return errors
        identifier = format_html('{0}.{1}', self.form_name, self.add_prefix(bound_field.name))
        potential_errors = bound_field.field.get_potential_errors()
        errors.extend([SafeTuple((identifier, self.field_error_css_classes, '$dirty', pe[0], 'invalid', force_text(pe[1])))
                       for pe in potential_errors])
        if not isinstance(bound_field.field.widget, widgets.PasswordInput):
            errors.append(SafeTuple((identifier, self.field_error_css_classes, '$dirty', '$valid', 'valid', '')))  # for valid fields
            if bound_field.value():
                # valid bound fields shall display OK tick, even in pristine state
                errors.append(SafeTuple((identifier, self.field_error_css_classes, '$pristine', '$valid', 'valid', '')))
        return errors

    def get_widget_attrs(self, bound_field):
        attrs = super(NgFormValidationMixin, self).get_widget_attrs(bound_field)
        # transfer error state from bound field to AngularJS validation
        errors = [e for e in bound_field.errors if e[3] == '$pristine']
        if errors and self.add_djng_error:
            attrs.update({'djng-error': 'bound-field'})
        # some fields require special directives to work with AngularJS
        try:
            attrs.update(bound_field.field.widget.get_field_attrs(bound_field.field))
        except AttributeError:
            pass
        return attrs
