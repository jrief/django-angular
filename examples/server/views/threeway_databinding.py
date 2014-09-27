# -*- coding: utf-8 -*-
from server.forms.model_scope import SubscribeForm
# start tutorial
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'three-way-data-binding.html'
    form_class = SubscribeForm
