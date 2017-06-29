# -*- coding: utf-8 -*-
from django.forms.forms import DeclarativeFieldsMetaclass, BaseForm
from django.forms.models import BaseModelForm, ModelFormMetaclass
from django.utils import six
from .angular_base import BaseFieldsModifierMetaclass, NgFormBaseMixin
from .angular_model import NgModelFormMixin
from .angular_validation import NgFormValidationMixin


class NgDeclarativeFieldsMetaclass(BaseFieldsModifierMetaclass, DeclarativeFieldsMetaclass):
    pass


class NgForm(six.with_metaclass(NgDeclarativeFieldsMetaclass, NgFormBaseMixin, BaseForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.Form`` when declaring
    a form to be used with AngularJS.
    """


class NgModelFormMetaclass(BaseFieldsModifierMetaclass, ModelFormMetaclass):
    pass


class NgModelForm(six.with_metaclass(NgModelFormMetaclass, NgFormBaseMixin, BaseModelForm)):
    """
    Convenience class to be used instead of Django's internal ``forms.ModelForm`` when declaring
    a model form to be used with AngularJS.
    """
