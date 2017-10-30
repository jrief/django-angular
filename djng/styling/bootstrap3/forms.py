# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import with_metaclass
import warnings

from django import VERSION as DJANGO_VERSION
from django.forms.forms import BaseForm
from django.forms.models import BaseModelForm
from djng.forms import NgDeclarativeFieldsMetaclass, NgModelFormMetaclass, NgFormBaseMixin


if DJANGO_VERSION >= (1, 11):
    warnings.warn("Since Django-1.11 `djng.styling.bootstrap3` is deprecated.", PendingDeprecationWarning)


class Bootstrap3FormMixin(object):
    field_css_classes = 'form-group has-feedback'
    widget_css_classes = 'form-control'
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-form-control-feedback djng-field-errors'
    widgets_module = 'djng.styling.bootstrap3.widgets'
    label_css_classes = 'control-label'

    def as_div(self):
        """
        Returns this form rendered as HTML with <div class="form-group">s for each form field.
        """
        # wrap non-field-errors into <div>-element to prevent re-boxing
        error_row = '<div class="djng-line-spreader">%s</div>'
        div_element = self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s%(field)s%(help_text)s%(errors)s</div>',
            error_row=error_row,
            row_ender='</div>',
            help_text_html='<span class="help-block">%s</span>',
            errors_on_separate_row=False)
        return div_element


class Bootstrap3Form(with_metaclass(NgDeclarativeFieldsMetaclass, Bootstrap3FormMixin, NgFormBaseMixin, BaseForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.Form`` when declaring
    a form to be used with AngularJS and Bootstrap3 styling.
    """


class Bootstrap3ModelForm(with_metaclass(NgModelFormMetaclass, Bootstrap3FormMixin, NgFormBaseMixin, BaseModelForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.ModelForm`` when declaring
    a model form to be used with AngularJS and Bootstrap3 styling.
    """
