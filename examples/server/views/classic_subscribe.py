# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.subscribe_form import SubscribeForm
# start tutorial
from django.views.generic.edit import FormView
from django.urls import reverse_lazy


class SubscribeView(FormView):
    template_name = 'subscribe-form.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
