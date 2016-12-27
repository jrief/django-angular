# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms.forms import BaseForm
from django.forms.models import BaseModelForm
from django.utils import six

from djng.forms import NgDeclarativeFieldsMetaclass, NgFormBaseMixin, NgModelFormMetaclass

from ..bootstrap.forms import BootstrapFormMixin


class Bootstrap4FormMixin(BootstrapFormMixin):
    field_css_classes = 'form-group row has-feedback'
    widget_css_classes = 'form-control'
    label_css_classes = 'form-control-label'
    field_mixins_module = 'djng.styling.bootstrap4.field_mixins'


class Bootstrap4Form(six.with_metaclass(NgDeclarativeFieldsMetaclass, Bootstrap4FormMixin, NgFormBaseMixin, BaseForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.Form`` when declaring
    a form to be used with AngularJS and Bootstrap4 styling.
    """


class Bootstrap4ModelForm(six.with_metaclass(NgModelFormMetaclass, Bootstrap4FormMixin, NgFormBaseMixin, BaseModelForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.ModelForm`` when declaring
    a model form to be used with AngularJS and Bootstrap4 styling.
    """
