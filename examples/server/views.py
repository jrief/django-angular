# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from server.forms import AdultSubscriptionForm


class NgFormValidationView(TemplateView):
    template_name = 'adult-subscription.html'

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        form = AdultSubscriptionForm(scope_prefix='subscribe_data')
        context.update(form=form)
        return context
