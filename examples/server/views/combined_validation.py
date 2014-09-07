# -*- coding: utf-8 -*-
from server.forms.combined_validation import SubscribeForm
# start tutorial
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'combined-validation.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
