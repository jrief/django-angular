# -*- coding: utf-8 -*-
from server.forms.client_validation import SubscribeForm
# start tutorial
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'subscribe-client-validation.html'
    form_class = SubscribeForm
