# -*- coding: utf-8 -*-
from server.forms.subscribe_form import SubscribeForm
# start tutorial
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'subscribe-form.html'
    form_class = SubscribeForm
