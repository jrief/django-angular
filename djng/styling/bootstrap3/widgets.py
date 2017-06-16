# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from djng.compat import HAS_CHOICE_FIELD_RENDERER
from djng.forms.widgets import (
    CheckboxSelectMultiple as DjngCheckboxSelectMultiple,
    RadioSelect as DjngRadioSelect
)

if HAS_CHOICE_FIELD_RENDERER:

    from .compat import CheckboxInput, CheckboxSelectMultiple, RadioSelect

else:
    from djng.forms.widgets import CheckboxInput as DjngCheckboxInput

    class CheckboxInput(DjngCheckboxInput):
        template_name = 'djng/forms/widgets/checkbox.html'

        def __init__(self, label, attrs=None, check_test=None):
            # the label is rendered by the Widget class rather than by BoundField.label_tag()
            self.choice_label = label
            super(CheckboxInput, self).__init__(attrs, check_test)

        def get_context(self, name, value, attrs):
            context = super(CheckboxInput, self).get_context(name, value, attrs)
            if context:
                context['label'] = self.choice_label
            return context

    class CheckboxSelectMultiple(DjngCheckboxSelectMultiple):
        template_name = 'djng/styling/bootstrap3/checkbox_select.html'
        option_template_name = 'djng/forms/widgets/checkbox_option.html'

        def get_context(self, name, value, attrs):
            validate_fields = []
            context = super(CheckboxSelectMultiple, self).get_context(name, value, attrs)
            if context:
                for optgroup in context['widget']['optgroups']:
                    elm = optgroup[1][0]
                    # elm['attrs']['ng-model'] = "{}['{}']".format(elm['name'], elm['value'])
                    elm['attrs'].pop('ng-model')
                    validate_fields.append(elm['name'])
                context['widget']['validate_fields'] = validate_fields
            return context

    class RadioSelect(DjngRadioSelect):
        template_name = 'djng/styling/bootstrap3/radio.html'
        option_template_name = 'djng/forms/widgets/radio_option.html'

        def get_context(self, name, value, attrs):
            context = super(RadioSelect, self).get_context(name, value, attrs)
            if context:
                for optgroup in context['widget']['optgroups']:
                    elm = optgroup[1][0]
                    elm['for_id'] = elm['attrs']['id']
                    elm['attrs']['id'] += '_{}'.format(elm['index'])
            return context
