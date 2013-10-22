# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from django import forms
from djangular.forms import NgModelFormMixin, NgFormValidationMixin


class ValidateMeForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
    first_name = forms.CharField(label='First name', min_length=3, max_length=20)
    middle_name = forms.CharField(label='Middle name', required=False)
    last_name = forms.RegexField(r'^[A-Z][a-z]+', label='Last name')


class NgFormValidationView(TemplateView):
    template_name = 'ng-validate-form.html'

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        form = ValidateMeForm()
        context.update(form=form)
        return context
