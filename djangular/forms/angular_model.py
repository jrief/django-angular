# -*- coding: utf-8 -*-
from django.forms.util import ErrorDict
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from djangular.forms.angular_base import NgFormBaseMixin


class NgModelFormMixin(NgFormBaseMixin):
    """
    Add this NgModelFormMixin to every class derived from forms.Form, if
    you want to manage that form through an Angular controller.
    It adds attributes ng-model, and optionally ng-change, ng-class and ng-style
    to each of your input fields.
    If form validation fails, the ErrorDict is rewritten in a way, so that the
    Angular controller can access the error strings using the same key values as
    for its models.
    """

    def __init__(self, *args, **kwargs):
        self.scope_prefix = kwargs.pop('scope_prefix', getattr(self, 'scope_prefix', None))
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'ng_models'):
            if not isinstance(self.Meta.ng_models, list):
                raise TypeError('Meta.ng_model is not of type list')
            ng_models = self.Meta.ng_models
        else:
            ng_models = None
        directives = {}
        for key in kwargs.keys():
            if key.startswith('ng_'):
                fmtstr = kwargs.pop(key)
                directives[key.replace('_', '-')] = fmtstr
        if ng_models is None and 'ng-model' not in directives:
            directives['ng-model'] = '%(model)s'
        self.prefix = kwargs.get('prefix')
        if self.prefix and kwargs.get('data'):
            kwargs['data'] = dict((self.add_prefix(name), value) for name, value in kwargs['data'].get(self.prefix).items())
        for name, field in self.base_fields.items():
            identifier = self.add_prefix(name)
            ng = {
                'name': name,
                'identifier': identifier,
                'model': self.scope_prefix and ('%s.%s' % (self.scope_prefix, identifier)) or identifier
            }
            if ng_models and name in ng_models:
                field.widget.attrs['ng-model'] = ng['model']
            for key, fmtstr in directives.items():
                field.widget.attrs[key] = fmtstr % ng
        super(NgModelFormMixin, self).__init__(*args, **kwargs)
        if self.scope_prefix == self.name():
            raise ValueError("The form's name may not be identical with its scope_prefix")
        for name, field in self.base_fields.items():
            if not hasattr(field, 'ng_field_name'):
                ng_model = self.add_prefix(name)
                setattr(field, 'ng_field_name', '{0}.{1}'.format(self.name(), ng_model))
            # to each field, add an empty <ul>-element which may be filled with form errors
            # detected during run time, for instance through an Ajax submission
            extra_list_item = format_html('<li ng-show="{0}.$invalid" class="invalid" ng-bind="{0}.$message"></li>',
                                          field.ng_field_name)
            ng_error_class = type('NgErrorList', (self.NgErrorClass,),
                {'identifier': field.ng_field_name, 'property': '$dirty', 'extra_list_item': extra_list_item})
            setattr(field, 'ng_potential_errors', ng_error_class())

    def _clean_fields(self):
        """
        Rewrite the error dictionary, so that its keys correspond to the model fields.
        """
        super(NgModelFormMixin, self)._clean_fields()
        if self.prefix:
            self._errors = ErrorDict((self.add_prefix(name), value) for name, value in self._errors.items())

    def get_initial_data(self):
        """
        Return a dictionary specifying the defaults for this form. This dictionary
        shall be used to inject the initial values for an Angular controller using
        the directive 'ng-init={{thisform.get_initial_data|js|safe}}'.
        """
        data = {}
        for name, field in self.fields.items():
            if hasattr(field, 'widget') and 'ng-model' in field.widget.attrs:
                data[name] = self.initial and self.initial.get(name) or field.initial
        return data
