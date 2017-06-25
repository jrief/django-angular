# -*- coding: utf-8 -*-
from server.forms.image_upload import SubscribeForm
# start tutorial
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'image-upload.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
