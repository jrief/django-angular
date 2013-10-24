# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from server.forms import AdultSubscriptionForm, AdultSubscriptionFormWithNgModel


class NgFormValidationView(TemplateView):
    template_name = 'adult-subscription.html'
    form = AdultSubscriptionForm()

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        context.update(form=self.form)
        return context


class NgFormValidationViewWithNgModel(NgFormValidationView):
    template_name = 'adult-subscription-with-model.html'
    form = AdultSubscriptionFormWithNgModel(scope_prefix='subscribe_data')
