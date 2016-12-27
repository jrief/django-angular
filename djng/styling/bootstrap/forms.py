# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class BootstrapFormMixin(object):
    """
    This is the base mixin to be used for bootstrap3 and bootstrap4
    """
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-form-control-feedback djng-field-errors'
    # wrap non-field-errors into <div>-element to prevent re-boxing
    error_row = '<div class="djng-line-spreader">%s</div>'
    normal_row = '<div%(html_class_attr)s>%(label)s%(field)s%(help_text)s%(errors)s</div>'
    row_ender = '</div>'
    label_as_placeholder = False

    def get_widget_attrs(self, bound_field):
        """
        label_as_placeholder allows you to use the placeholder as a label
        reusing your label definition.
        """
        attrs = super(BootstrapFormMixin, self).get_widget_attrs(bound_field)
        if self.label_as_placeholder:
            attrs["placeholder"] = bound_field.label
        return attrs

    def as_div(self):
        """
        Returns this form rendered as HTML with:
            <div class="*field_css_classes*">
        for each form field.
        """
        div_element = self._html_output(
            normal_row=self.normal_row,
            error_row=self.error_row,
            row_ender=self.row_ender,
            help_text_html=self.help_text_html,
            errors_on_separate_row=False)
        return div_element
