# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms.forms import BaseForm
from django.forms.models import BaseModelForm
from django.utils import six

from djng.forms import NgDeclarativeFieldsMetaclass, NgModelFormMetaclass, NgFormBaseMixin

from ..bootstrap.forms import BootstrapFormMixin


class Bootstrap3FormMixin(BootstrapFormMixin):
    field_css_classes = 'form-group has-feedback'
    widget_css_classes = 'form-control'
    label_css_classes = 'control-label'
    field_mixins_module = 'djng.styling.bootstrap3.field_mixins'


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
