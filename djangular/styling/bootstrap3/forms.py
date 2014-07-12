# -*- coding: utf-8 -*-
from django.forms import widgets
from django.http import QueryDict
from django.utils.encoding import force_text
from djangular.forms.angular_base import NgFormBaseMixin
from . import widgets as bs3widgets


class Bootstrap3FormMixin(NgFormBaseMixin):
    field_css_classes = 'form-group has-feedback'
    widget_css_classes = 'form-control'
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-form-control-feedback djng-field-errors'

    def convert_widgets(self, data):
        """
        During initialization, some widgets have to be replaced by a counterpart suitable for
        rendering labels, input fields and select element the "Bootstrap way".
        """
        for name, field in self.base_fields.items():
            fw_dict = field.widget.__dict__
            if isinstance(field.widget, widgets.CheckboxSelectMultiple):
                if not isinstance(field.widget, bs3widgets.CheckboxSelectMultiple):
                    field.widget = bs3widgets.CheckboxSelectMultiple()
                    field.widget.__dict__ = fw_dict
                if isinstance(data, QueryDict):
                    data = field.widget.implode_multi_values(name, data.copy())
                setattr(field, 'widget_css_classes', None)
            elif isinstance(field.widget, widgets.CheckboxInput):
                if not isinstance(field.widget, bs3widgets.CheckboxInput):
                    field.widget = bs3widgets.CheckboxInput()
                    field.widget.__dict__ = fw_dict
                    # the label shall be rendered by the Widget class rather than using BoundField.label_tag()
                    field.widget.choice_label = force_text(field.label)
                    field.label = ''
                setattr(field, 'widget_css_classes', None)
            elif isinstance(field.widget, widgets.RadioSelect):
                if not isinstance(field.widget, bs3widgets.RadioSelect):
                    field.widget = bs3widgets.RadioSelect()
                    field.widget.__dict__ = fw_dict
                setattr(field, 'widget_css_classes', None)
        return data

    def as_div(self):
        """
        Returns this form rendered as HTML with <div class="form-group">s for each form field.
        """
        # wrap non-field-errors into <div>-element to prevent re-boxing
        error_row = '<div class="djng-line-spreader">%s</div>'
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s%(field)s%(help_text)s%(errors)s</div>',
            error_row=error_row,
            row_ender='</div>',
            help_text_html='<span class="help-block">%s</span>',
            errors_on_separate_row=False)
