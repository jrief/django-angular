# -*- coding: utf-8 -*-
from django.forms.util import ErrorDict


class AngularFormMixin(object):
    """
    Add AngularFormMixin to every class derived from forms.ModelForm, if you want
    to manage that form through an Angular controller.
    It adds attributes ng-model, and optionally ng-change, ng-class and ng-style
    to each of your input fields.
    If form validation fails, the ErrorDict is rewritten in a way, so that the
    Angular controller can access the error strings using the same key values as
    for its models.
    """
    input_directives = ['ng-change', 'ng-class', 'ng-style']

    def __init__(self, data=None, ng_scope_varname=None, prefix=None, **kwargs):
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'ng_models'):
            if not isinstance(self.Meta.ng_models, list):
                raise TypeError('Meta.ng_model is not of type list')
            ng_models = self.Meta.ng_models
        else:
            ng_models = None
        directives = {}
        for key in self.input_directives:
            fmtstr = kwargs.pop(key.replace('-', '_'), None)
            if fmtstr:
                directives[key] = fmtstr
        if data and prefix:
            self.prefix = prefix
            data = dict((self.add_prefix(name), value) for name, value in data.get(prefix).items())
        super(AngularFormMixin, self).__init__(data, prefix=prefix, **kwargs)
        for name, field in self.fields.items():
            identifier = self.add_prefix(name)
            ng = {
                'name': name,
                'identifier': identifier,
                'model': ng_scope_varname and ('%s.%s' % (ng_scope_varname, identifier)) or identifier
            }
            if ng_models is None or name in ng_models:
                field.widget.attrs['ng-model'] = ng['model']
            for key, fmtstr in directives.items():
                field.widget.attrs[key] = fmtstr % ng

    def full_clean(self):
        """
        Rewrite the error dictionary, so that its keys correspond to the model fields.
        """
        super(AngularFormMixin, self).full_clean()
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
                data[name] = field.initial
        return data

    def add_prefix(self, field_name):
        """
        Rewrite the model keys to use dots instead of dashes, since thats the syntax
        used in Angular models.
        """
        return self.prefix and ('%s.%s' % (self.prefix, field_name)) or field_name
