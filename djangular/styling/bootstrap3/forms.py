# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms.forms import BaseForm
from django.forms.models import BaseModelForm
from django.utils import six
from djangular.forms import NgDeclarativeFieldsMetaclass, NgModelFormMetaclass, NgFormBaseMixin


class Bootstrap3FormMixin(object):
    field_css_classes = 'form-group has-feedback'
    widget_css_classes = 'form-control'
    form_error_css_classes = 'djng-form-errors'
    field_error_css_classes = 'djng-form-control-feedback djng-field-errors'
    field_mixins_module = 'djangular.styling.bootstrap3.field_mixins'
    # Adding attribute to create horizontal form
    # horizontal_container_classes = 'col-xs-12 col-sm-12 col-md-12 col-lg-12'
    horizontal_container_classes = None
    label_css_classes = 'control-label'

    def as_div(self):
        """
        Returns this form rendered as HTML with <div class="form-group">s for each form field.
        """
        # wrap non-field-errors into <div>-element to prevent re-boxing
        error_row = '<div class="djng-line-spreader">%s</div>'
        #
        field_html = '%(field)s%(help_text)s%(errors)s'
        if(self.horizontal_container_classes is not None):
            field_html = '<div class="{0}">{1}</div>'.format(self.horizontal_container_classes, field_html)
        div_element = self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s{0}</div>'.format(field_html),
            error_row=error_row,
            row_ender='</div>',
            help_text_html='<span class="help-block">%s</span>',
            errors_on_separate_row=False)
        return div_element


class Bootstrap3Form(six.with_metaclass(NgDeclarativeFieldsMetaclass, Bootstrap3FormMixin, NgFormBaseMixin, BaseForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.Form`` when declaring
    a form to be used with AngularJS and Bootstrap3 styling.
    """


class Bootstrap3ModelForm(six.with_metaclass(NgModelFormMetaclass, Bootstrap3FormMixin, NgFormBaseMixin, BaseModelForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.ModelForm`` when declaring
    a model form to be used with AngularJS and Bootstrap3 styling.
    """
