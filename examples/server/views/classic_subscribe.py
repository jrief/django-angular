# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.subscribe_form import SubscribeForm, SubscribeFormBootstrap4
# start tutorial
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy


class SubscribeView(FormView):
    template_name = 'subscribe-form.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')


class Bootstrap4SubscribeView(FormView):
    template_name = "example-bootstrap4.html"
    form_class = SubscribeFormBootstrap4
    success_url = reverse_lazy('form_data_valid')
