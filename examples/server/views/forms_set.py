# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.forms_set import SubscribeForm, AddressForm
# start tutorial
import json
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class SubscribeView(TemplateView):
    template_name = 'forms-set.html'
    success_url = reverse_lazy('form_data_valid')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['subscribe_form'] = SubscribeForm()
        context['address_form'] = AddressForm()
        return self.render_to_response(context)

    def put(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        subscribe_form = SubscribeForm(data=request_data.get(SubscribeForm.scope_prefix, {}))
        address_form = AddressForm(data=request_data.get(AddressForm.scope_prefix, {}))
        response_data = {}

        if subscribe_form.is_valid() and address_form.is_valid():
            response_data.update({'success_url': self.success_url})
            return JsonResponse(response_data)

        # otherwise report form validation errors
        response_data.update({
            subscribe_form.form_name: subscribe_form.errors,
            address_form.form_name: address_form.errors,
        })
        return JsonResponse(response_data, status=422)
