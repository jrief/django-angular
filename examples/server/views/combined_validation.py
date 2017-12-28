# -*- coding: utf-8 -*-
from server.forms.combined_validation import SubscribeForm, default_subscribe_data
# start tutorial
import json
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.utils.encoding import force_text


class SubscribeView(FormView):
    template_name = 'combined-validation.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')

    def get(self, request, **kwargs):
        if request.is_ajax():
            form = self.form_class(initial=default_subscribe_data)
            return JsonResponse({form.form_name: form.initial})
        return super(SubscribeView, self).get(request, **kwargs)

    def post(self, request, **kwargs):
        assert request.is_ajax()
        return self.ajax(request)

    def ajax(self, request):
        request_data = json.loads(request.body)
        form = self.form_class(data=request_data.get(self.form_class.scope_prefix, {}))
        if form.is_valid():
            return JsonResponse({'success_url': force_text(self.success_url)})
        else:
            return JsonResponse({form.form_name: form.errors}, status=422)
