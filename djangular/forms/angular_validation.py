# -*- coding: utf-8 -*-
import types
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.html import format_html
from django.utils.encoding import force_text
from djangular.forms.angular_base import NgFormBaseMixin, SafeTuple

VALIDATION_MAPPING_MODULE = import_module(getattr(settings, 'DJANGULAR_VALIDATION_MAPPING_MODULE', 'djangular.forms.patched_fields'))


class NgFormValidationMixin(NgFormBaseMixin):
    """
    Add this NgFormValidationMixin to every class derived from forms.Form, which shall be
    auto validated using the Angular's validation mechanism.
    """
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
        identifier = format_html('{0}.{1}', self.form_name, self.add_prefix(bound_field.name))
        errors_function = '{0}_angular_errors'.format(bound_field.field.__class__.__name__)
        try:
            errors_function = getattr(VALIDATION_MAPPING_MODULE, errors_function)
            potential_errors = types.MethodType(errors_function, bound_field.field)()
        except (TypeError, AttributeError):
            errors_function = getattr(VALIDATION_MAPPING_MODULE, 'Default_angular_errors')
            potential_errors = types.MethodType(errors_function, bound_field.field)()
        errors.append(SafeTuple((identifier, '$dirty', '$valid', 'valid', '')))  # for valid fields
        errors.extend([SafeTuple((identifier, '$dirty', pe[0], 'invalid', force_text(pe[1])))
                       for pe in potential_errors])
        return errors
