# -*- coding: utf-8 -*-
import json
from django.forms.util import ErrorDict
from django.forms import widgets

class NgModelFormMixin(object):
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
        self.scope_prefix = kwargs.pop('scope_prefix', None)
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
        if kwargs.get('data') and kwargs.get('prefix'):
            self.prefix = kwargs['prefix']
            kwargs['data'] = dict((self.add_prefix(name), value) for name, value in kwargs['data'].get(self.prefix).items())
        super(NgModelFormMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
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
            if isinstance(field.widget, widgets.Select):
                field.widget.attrs['ng-options'] = 'o.key as o.value for o in _' + self.scope_prefix + '.' + ng['identifier']

    def full_clean(self):
        """
        Rewrite the error dictionary, so that its keys correspond to the model fields.
        """
        super(NgModelFormMixin, self).full_clean()
        if self._errors and self.prefix:
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

    def get_form_data(self):
        data = {}
        for name, field in self.fields.items():
            if hasattr(field, 'widget') and 'ng-options' in field.widget.attrs:
                data[name] = [{'key': int(k), 'value': unicode(v)} for k,v in field.choices if k]
        return data

    def add_prefix(self, field_name):
        """
        Rewrite the model keys to use dots instead of dashes, since thats the syntax
        used in Angular models.
        """
        return self.prefix and ('%s.%s' % (self.prefix, field_name)) or field_name
