# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from server.forms import SubscriptionForm, SubscriptionFormWithNgModel


class NgFormValidationView(TemplateView):
    template_name = 'subscribe-form.html'
    form = SubscriptionForm(form_name='subscribe_form')

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        context.update(form=self.form)
        return context


class NgFormValidationViewWithNgModel(NgFormValidationView):
    template_name = 'subscribe-form-with-model.html'
    form = SubscriptionFormWithNgModel(scope_prefix='subscribe_data')
