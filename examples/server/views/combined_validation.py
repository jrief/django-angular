# -*- coding: utf-8 -*-
from server.forms.combined_validation import SubscribeForm, default_subscribe_data
# start tutorial
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.utils.encoding import force_text


class SubscribeView(FormView):
    template_name = 'combined-validation.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')

    def post(self, request, **kwargs):
        assert request.is_ajax()
        return self.ajax(request)

    def ajax(self, request):
        request_data = json.loads(request.body)
        set_defaults = request_data.pop('set_defaults', False)
        if set_defaults:
            form = self.form_class(initial=default_subscribe_data)
        else:
            form = self.form_class(data=request_data.get(self.form_class.scope_prefix, {}))
        if form.is_valid():
            return JsonResponse({'success_url': force_text(self.success_url)})
        elif set_defaults:
            return JsonResponse({form.form_name: form.initial})
        else:
            response_data = {form.form_name: form.errors}
            return HttpResponseBadRequest(json.dumps(response_data), status=422, content_type='application/json')
