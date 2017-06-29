# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.renderers import DjangoTemplates
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class DjangoAngularTemplates(DjangoTemplates):
    """
    Loads a modified Django template suitable for AngularJS, in case it has to be overridden
    """
    template_mappings = {
        'django/forms/widgets/checkbox.html': 'djng/forms/widgets/bootstrap3/checkbox.html',
        'django/forms/widgets/checkbox_select.html': 'djng/forms/widgets/bootstrap3/checkbox_select.html',
        'django/forms/widgets/date.html': 'djng/forms/widgets/bootstrap3/date.html',
        'django/forms/widgets/datetime.html': 'djng/forms/widgets/bootstrap3/datetime.html',
        'django/forms/widgets/email.html': 'djng/forms/widgets/bootstrap3/email.html',
        'django/forms/widgets/number.html': 'djng/forms/widgets/bootstrap3/number.html',
        'django/forms/widgets/password.html': 'djng/forms/widgets/bootstrap3/password.html',
        'django/forms/widgets/radio.html': 'djng/forms/widgets/bootstrap3/radio.html',
        'django/forms/widgets/select.html': 'djng/forms/widgets/bootstrap3/select.html',
        'django/forms/widgets/text.html': 'djng/forms/widgets/bootstrap3/text.html',
        'django/forms/widgets/textarea.html': 'djng/forms/widgets/bootstrap3/textarea.html',
    }

    def render(self, template_name, context, request=None):
        template_name = self.template_mappings.get(template_name, template_name)
        if context['widget']['attrs'].pop('multiple_checkbox_required', False):
            ng_model = mark_safe(context['widget']['attrs'].pop('ng-model', ''))
            if ng_model:
                for group, options, index in context['widget']['optgroups']:
                    for option in options:
                        option['attrs']['ng-model'] = format_html('{0}[\'{value}\']', ng_model, **option)
        template = self.get_template(template_name)
        return template.render(context, request=request).strip()
