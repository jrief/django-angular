# -*- coding: utf-8 -*-
from server.forms.client_validation import SubscribeForm
from server.urls import reverse_lazy
# start tutorial
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'client-validation.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
