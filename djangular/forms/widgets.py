# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.html import format_html
from django.forms.util import flatatt


class CheckboxChoiceInput(widgets.CheckboxChoiceInput):
    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        if 'ng-model' in self.attrs:
            self.attrs['ng-model'] = '%s.%s' % (self.attrs['ng-model'], self.choice_value)
        name = '%s.%s' % (self.name, self.choice_value)
        final_attrs = dict(self.attrs, type=self.input_type, name=name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return format_html('<input{0} />', flatatt(final_attrs))


class CheckboxFieldRenderer(widgets.ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput


class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
    """
    Form fields of type 'MultipleChoiceField' using the widget 'CheckboxSelectMultiple' must behave
    slightly different from the original. This widget overrides the default functionality.
    """
    renderer = CheckboxFieldRenderer

    def implode_multi_values(self, name, data):
        """
        Fields for CheckboxSelectMultiple are converted to a list by this method, if sent through
        POST data.
        """
        mkeys = [k for k in data.keys() if k.startswith(name + '.')]
        mvls = [data.pop(k)[0] for k in mkeys]
        if mvls:
            data.setlist(name, mvls)
        return data
