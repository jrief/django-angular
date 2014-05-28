# -*- coding: utf-8 -*-
from djangular.forms.angular_base import NgFormBaseMixin


class Bootstrap3FormMixin(NgFormBaseMixin):
    WRAPPER_MAP = {
        'default': 'form-group',
        'RadioSelect': 'radio-inline',
        'CheckboxInput': 'checkbox',
        'DjngCheckboxSelectMultiple': 'checkbox-inline',
    }
    WIDGET_MAP = {
        'default': 'form-control',
        'RadioSelect': None,
        'CheckboxInput': None,
        'DjngCheckboxSelectMultiple': None,
    }
    LABEL_MAP = {
        'default': None,
        'RadioSelect': None,
        'CheckboxInput': None,
        'DjngCheckboxSelectMultiple': None,
    }

    def __init__(self, *args, **kwargs):
        field_css_classes = getattr(self, 'field_css_classes', {})
        for name, field in self.base_fields.items():
            extra_classes = field_css_classes.get(name, {}).get('extra_css_classes', '')
            if hasattr(extra_classes, 'split'):
                extra_classes = set(extra_classes.split())
            widget_type = field.widget.__class__.__name__
            wrapper_class = self.WRAPPER_MAP.get(widget_type, self.WRAPPER_MAP['default'])
            extra_classes.add(wrapper_class)
            setattr(field, 'extra_classes', extra_classes)
            widget_class = self.WIDGET_MAP.get(widget_type, self.WIDGET_MAP['default'])
            setattr(field, 'widget_css_classes', widget_class)
            label_class = self.LABEL_MAP.get(widget_type, self.LABEL_MAP['default'])
            setattr(field, 'label_css_classes', label_class)
        super(Bootstrap3FormMixin, self).__init__(*args, **kwargs)

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
