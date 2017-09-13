# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.forms_set import SubscribeForm, AddressForm
# start tutorial
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy


class SubscribeView(TemplateView):
    template_name = 'forms-set.html'
    success_url = reverse_lazy('form_data_valid')

    def get_context_data(self, **kwargs):
        context = super(SubscribeView, self).get_context_data(**kwargs)
        context['subscribe_form'] = SubscribeForm()
        context['address_form'] = AddressForm()
        return context
