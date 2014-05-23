# -*- coding: utf-8 -*-
from django import forms
from django.utils.html import format_html
from django.forms.util import flatatt
from django.forms.widgets import (RendererMixin, ChoiceFieldRenderer, CheckboxChoiceInput,
                                  SelectMultiple)


class DjngCheckboxChoiceInput(CheckboxChoiceInput):
    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        self.attrs['ng-model'] = '%s.%s' % (self.attrs['ng-model'], self.choice_value)
        name = '%s.%s' % (self.name, self.choice_value)
        final_attrs = dict(self.attrs, type=self.input_type, name=name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return format_html('<input{0} />', flatatt(final_attrs))


class DjngCheckboxFieldRenderer(ChoiceFieldRenderer):
    choice_input_class = DjngCheckboxChoiceInput


class DjngCheckboxSelectMultiple(RendererMixin, SelectMultiple):
    renderer = DjngCheckboxFieldRenderer
    _empty_value = []


class DjngMultipleCheckboxField(forms.MultipleChoiceField):
    widget = DjngCheckboxSelectMultiple

    def implode_multi_values(self, name, data):
        mkeys = [k for k in data.keys() if k.startswith(name + '.')]
        mvls = [data.pop(k)[0] for k in mkeys]
        if mvls:
            data.setlist(name, mvls)
        return data
