# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.renderers import DjangoTemplates


class DjangoAngularTemplates(DjangoTemplates):
    """
    Loads a modified Django template suitable for AngularJS, in case it has to be overridden
    """
    template_mappings = {
        'django/forms/widgets/checkbox.html': 'djng/forms/widgets/checkbox.html',
        'django/forms/widgets/checkbox_select.html': 'djng/forms/widgets/checkbox_select.html',
        'django/forms/widgets/date.html': 'djng/forms/widgets/date.html',
        'django/forms/widgets/datetime.html': 'djng/forms/widgets/datetime.html',
        'django/forms/widgets/email.html': 'djng/forms/widgets/email.html',
        'django/forms/widgets/number.html': 'djng/forms/widgets/number.html',
        'django/forms/widgets/password.html': 'djng/forms/widgets/password.html',
        'django/forms/widgets/radio.html': 'djng/forms/widgets/radio.html',
        'django/forms/widgets/select.html': 'djng/forms/widgets/select.html',
        'django/forms/widgets/text.html': 'djng/forms/widgets/text.html',
        'django/forms/widgets/textarea.html': 'djng/forms/widgets/textarea.html',
    }

    def render(self, template_name, context, request=None):
        template_name = self.template_mappings.get(template_name, template_name)
        template = self.get_template(template_name)
        return template.render(context, request=request).strip()


class DjangoAngularBootstrap3Templates(DjangoAngularTemplates):
    """
    Loads a modified Django template suitable for AngularJS inside Bootstrap3 widgets
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
