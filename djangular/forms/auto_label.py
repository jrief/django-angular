# -*- coding: utf-8 -*-
from django import forms


class AutoLabelFormMixin(object):
    """
    Forms with auto-label's are useful, if you want to display the field's label
    inside the input element rather than prefixing the element - this can can
    considerably reduce the amount of space needed to display a form.

    When such an input field is empty, the label is displayed using the special
    class 'empty'. Now, when such an input field gains focus, the label is removed
    and the field behaves as usual. When the user removes input focus from the
    field, the entered text remains. When the user removes input focus from an
    empty field, the auto-label is re-added using class 'empty'.

    In HTML, this mixin requires to load the Angular module ngDjango:
    <script src="{{STATIC_URL}}angular-django.js"></script>
    ...
    angular.module('MyAwesomeModule', [...other dependencies..., 'ngDjango']);
    """

    def __init__(self, *args, **kwargs):
        super(AutoLabelFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.PasswordInput)):
                field.widget.attrs['auto-label'] = field.label
                field.error_messages = {'required': field.label, 'invalid': field.label}

    def __unicode__(self):
        return self.as_ul_with_autolabel()

    def as_ul_with_autolabel(self):
        "Returns this form rendered as HTML <li>s with input fields using auto-labels."
        return self._html_output(
            normal_row=u'<li%(html_class_attr)s>%(field)s</li>',
            error_row=u'%s',
            row_ender='</li>',
            help_text_html=u'<span class="helptext">%s</span>',
            errors_on_separate_row=False)
