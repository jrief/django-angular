# -*- coding: utf-8 -*-
from server.forms.client_validation import SubscribeForm
# start tutorial
from django.urls import reverse_lazy
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'client-validation.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
