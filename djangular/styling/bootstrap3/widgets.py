# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.forms.util import flatatt
from django.forms import widgets
from djangular.forms.widgets import (
    ChoiceFieldRenderer as DjngChoiceFieldRenderer, CheckboxChoiceInput as DjngCheckboxChoiceInput,
    CheckboxFieldRendererMixin, CheckboxSelectMultiple as DjngCheckboxSelectMultiple,
    RadioFieldRendererMixin, RadioSelect as DjngRadioSelect)


class ChoiceFieldRenderer(DjngChoiceFieldRenderer):
    def render(self):
        """
        Outputs a <div ng-form="name"> for this set of choice fields to nest an ngForm.
        """
        start_tag = format_html('<div {0}>', mark_safe(' '.join(self.field_attrs)))
        output = [start_tag]
        for widget in self:
            output.append(force_text(widget))
        output.append('</div>')
        return mark_safe('\n'.join(output))


class CheckboxInput(widgets.CheckboxInput):
    def render(self, name, value, attrs=None):
        attrs = attrs or self.attrs
        label_attrs = ['class="checkbox-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{0}"', self.attrs['id']))
        label_for = mark_safe(' '.join(label_attrs))
        tag = super(CheckboxInput, self).render(name, value, attrs)
        return format_html('<label {0}>{1} {2}</label>', label_for, tag, self.choice_label)


class CheckboxChoiceInput(DjngCheckboxChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        label_attrs = ['class="checkbox-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{0}_{1}"', self.attrs['id'], self.index))
        label_for = mark_safe(' '.join(label_attrs))
        return format_html('<label {0}>{1} {2}</label>', label_for, self.tag(), self.choice_label)


class CheckboxFieldRenderer(CheckboxFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput


class CheckboxSelectMultiple(DjngCheckboxSelectMultiple):
    renderer = CheckboxFieldRenderer


class RadioChoiceInput(widgets.RadioChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        label_attrs = ['class="radio-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{0}_{1}"', self.attrs['id'], self.index))
        label_for = mark_safe(' '.join(label_attrs))
        return format_html('<label {0}>{1} {2}</label>', label_for, self.tag(), self.choice_label)

    def tag(self):
        tag_attrs = dict(self.attrs, type=self.input_type, name=self.name, value=self.choice_value)
        if 'id' in self.attrs:
            tag_attrs['id'] = '{0}_{1}'.format(tag_attrs['id'], self.index)
        if self.is_checked():
            tag_attrs['checked'] = 'checked'
        return format_html('<input{0} />', flatatt(tag_attrs))


class RadioFieldRenderer(RadioFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = RadioChoiceInput


class RadioSelect(DjngRadioSelect):
    renderer = RadioFieldRenderer
