# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.forms_set import SubscribeForm, AddressForm
# start tutorial
import json, time
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy


class SubscribeView(TemplateView):
    template_name = 'forms-set.html'
    success_url = reverse_lazy('form_data_valid')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['subscribe_form'] = SubscribeForm()
        context['address_form'] = AddressForm()
        return self.render_to_response(context)

    def put(self, request, *args, **kwargs):
        form_data = json.loads(request.body)
        subscribe_form = SubscribeForm(data=form_data.get(SubscribeForm.scope_prefix, {}))
        address_form = AddressForm(data=form_data.get(AddressForm.scope_prefix, {}))
        response_data = {}

        if form_data.get('delay'):
            time.sleep(1.5)  # emulate a delayed form submission

        # optionally populate the client model
        if form_data.get('set_defaults'):
            response_data.update({
                subscribe_form.form_name: {
                    'models': {
                        'full_name': "John Doe",
                    }
                }
            })

        if subscribe_form.is_valid() and address_form.is_valid():
            response_data.update({'success_url': self.success_url})
            return JsonResponse(response_data)

        # report errors
        response_data.update({
            subscribe_form.form_name: {'errors': subscribe_form.errors},
            address_form.form_name: {'errors': address_form.errors},
        })

        return HttpResponseBadRequest(json.dumps(response_data), status=422, content_type='application/json')
