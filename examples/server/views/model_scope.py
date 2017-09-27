# -*- coding: utf-8 -*-
from server.forms.model_scope import SubscribeForm
# start tutorial
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse_lazy
from django.utils.encoding import force_text
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'model-scope.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(SubscribeView, self).post(request, **kwargs)

    def ajax(self, request):
        request_data = json.loads(request.body)
        form = self.form_class(data=request_data.get(self.form_class.scope_prefix, {}))
        if form.is_valid():
            return JsonResponse({'success_url': force_text(self.success_url)})
        else:
            response_data = {form.form_name: form.errors}
            return HttpResponseBadRequest(json.dumps(response_data), status=422, content_type='application/json')
