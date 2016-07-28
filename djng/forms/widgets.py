# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import format_html, format_html_join


def flatatt(attrs):
    """
    Pilfered from `django.forms.utils`:
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs. In the case of a boolean value, the key will appear
    without a value. Otherwise, the value is formatted through its own dict of `attrs`,
    which can be useful to parametrize Angular directives.
    It is assumed that the keys do not need to be
    XML-escaped. If the passed dictionary is empty, then return an empty
    string.

    The result is passed through 'mark_safe' (by way of 'format_html_join').
    """
    key_value_attrs = []
    boolean_attrs = []
    for attr, value in attrs.items():
        if isinstance(value, bool):
            if value:
                boolean_attrs.append((attr,))
        else:
            try:
                value = value.format(**attrs)
            except KeyError:
                pass
            key_value_attrs.append((attr, value))

    return (
        format_html_join('', ' {}="{}"', sorted(key_value_attrs)) +
        format_html_join('', ' {}', sorted(boolean_attrs))
    )


class ChoiceFieldRenderer(widgets.ChoiceFieldRenderer):
    def render(self):
        """
        Outputs a <ul ng-form="name"> for this set of choice fields to nest an ngForm.
        """
        start_tag = format_html('<ul {0}>', mark_safe(' '.join(self.field_attrs)))
        output = [start_tag]
        for widget in self:
            output.append(format_html('<li>{0}</li>', force_text(widget)))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class CheckboxChoiceInput(widgets.CheckboxChoiceInput):
    def tag(self, attrs=None):
        attrs = attrs or self.attrs
        name = '{0}.{1}'.format(self.name, self.choice_value)
        tag_attrs = dict(attrs, type=self.input_type, name=name, value=self.choice_value)
        if 'id' in attrs:
            tag_attrs['id'] = '{0}_{1}'.format(attrs['id'], self.index)
        if 'ng-model' in attrs:
            tag_attrs['ng-model'] = "{0}['{1}']".format(attrs['ng-model'], self.choice_value)
        if self.is_checked():
            tag_attrs['checked'] = 'checked'
        return format_html('<input{0} />', flatatt(tag_attrs))


class CheckboxFieldRendererMixin(object):
    def __init__(self, name, value, attrs, choices):
        attrs.pop('djng-error', None)
        self.field_attrs = [format_html('ng-form="{0}"', name)]
        if attrs.pop('multiple_checkbox_required', False):
            field_names = [format_html('{0}.{1}', name, choice) for choice, dummy in choices]
            self.field_attrs.append(format_html('validate-multiple-fields="{0}"', json.dumps(field_names)))
        super(CheckboxFieldRendererMixin, self).__init__(name, value, attrs, choices)


class CheckboxFieldRenderer(CheckboxFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput


class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
    """
    Form fields of type 'MultipleChoiceField' using the widget 'CheckboxSelectMultiple' must behave
    slightly different from the original. This widget overrides the default functionality.
    """
    renderer = CheckboxFieldRenderer

    def implode_multi_values(self, name, data):
        """
        Due to the way Angular organizes it model, when Form data is sent via a POST request,
        then for this kind of widget, the posted data must to be converted into a format suitable
        for Django's Form validation.
        """
        mkeys = [k for k in data.keys() if k.startswith(name + '.')]
        mvls = [data.pop(k)[0] for k in mkeys]
        if mvls:
            data.setlist(name, mvls)

    def convert_ajax_data(self, field_data):
        """
        Due to the way Angular organizes it model, when this Form data is sent using Ajax,
        then for this kind of widget, the sent data has to be converted into a format suitable
        for Django's Form validation.
        """
        return [key for key, val in field_data.items() if val]

    def get_field_attrs(self, field):
        return {'multiple_checkbox_required': field.required}


class RadioFieldRendererMixin(object):
    def __init__(self, name, value, attrs, choices):
        attrs.pop('djng-error', None)
        self.field_attrs = []
        if attrs.pop('radio_select_required', False):
            self.field_attrs.append(format_html('validate-multiple-fields="{0}"', name))
        super(RadioFieldRendererMixin, self).__init__(name, value, attrs, choices)


class RadioFieldRenderer(RadioFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = widgets.RadioChoiceInput


class RadioSelect(widgets.RadioSelect):
    """
    Form fields of type 'ChoiceField' using the widget 'RadioSelect' must behave
    slightly different from the original. This widget overrides the default functionality.
    """
    renderer = RadioFieldRenderer

    def get_field_attrs(self, field):
        return {'radio_select_required': field.required}
