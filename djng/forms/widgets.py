# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import json
from django.forms import widgets
from django.utils.html import format_html_join

from djng.compat import HAS_CHOICE_FIELD_RENDERER


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


class CheckboxSelectMultipleMixin(widgets.CheckboxSelectMultiple):
    """
    Form fields of type 'MultipleChoiceField' using the widget 'CheckboxSelectMultiple' must behave
    slightly different from the original. This widget overrides the default functionality.
    """
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


if HAS_CHOICE_FIELD_RENDERER:

    from .compat import CheckboxChoiceInput, CheckboxSelectMultiple, RadioSelect  # noqa

else:

    class CheckboxInput(widgets.CheckboxInput):

        def get_context(self, name, value, attrs):
            context = super(CheckboxInput, self).get_context(name, value, attrs)
            if 'checked' in attrs.keys():
                context['widget']['attrs']['checked'] = 'checked'
            return context

    class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
        template_name = 'djng/forms/widgets/checkbox_select.html'

        def get_context(self, name, value, attrs):
            attrs.pop('djng-error', None)
            context = super(CheckboxSelectMultiple, self).get_context(name, value, attrs)
            if context:
                field_names = []
                context['widget']['attrs'].pop('id')
                context['widget']['attrs']['ng-form'] = context['widget']['name']
                context['widget']['attrs'].pop('ng-model', None)
                for optgroup in context['widget']['optgroups']:
                    elm = optgroup[1][0]
                    if elm['selected']:
                        elm['attrs']['checked'] = 'checked'
                    elm['name'] = '{0}.{1}'.format(name, elm['value'])
                    elm['attrs']['id'] = '{}_{}'.format(elm['attrs']['id'], elm['index'])
                    elm['attrs']['ng-model'] = "{0}['{1}']".format(name, elm['value'])
                    field_names.append(elm['name'])
                if attrs.get('required', False):
                    context['widget']['attrs']['validate-multiple-fields'] = json.dumps(field_names)
            return context

    class RadioSelect(widgets.RadioSelect):
        template_name = 'djng/forms/widgets/radio.html'

        def get_context(self, name, value, attrs):
            attrs.pop('djng-error', None)
            if 'checked' in attrs.keys():
                attrs['checked'] = 'checked'
            context = super(RadioSelect, self).get_context(name, value, attrs)
            if attrs.get('required', False):
                context['widget']['attrs']['validate-multiple-fields'] = name
            return context
