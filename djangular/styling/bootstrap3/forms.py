# -*- coding: utf-8 -*-
from django.forms import widgets
from django.http import QueryDict
from djangular.forms.angular_base import NgFormBaseMixin
from . import widgets as bs3widgets


class Bootstrap3FormMixin(NgFormBaseMixin):
    field_css_classes = 'form-group'
    widget_css_classes = 'form-control'

    def __init__(self, data=None, *args, **kwargs):
        for field in self.base_fields.values():
            if not hasattr(field, 'extra_classes'):
                setattr(field, 'extra_classes', self.field_css_classes)
            if not hasattr(field, 'widget_css_classes'):
                setattr(field, 'widget_css_classes', self.widget_css_classes)
        super(Bootstrap3FormMixin, self).__init__(data, *args, **kwargs)

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
                    field.widget.choice_label = field.label
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
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s%(field)s%(help_text)s%(errors)s</div>',
            error_row='<div class="alert alert-danger">%s</div>',
            row_ender='</div>',
            help_text_html='<span class="help-block">%s</span>',
            errors_on_separate_row=False)
