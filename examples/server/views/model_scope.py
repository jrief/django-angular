# -*- coding: utf-8 -*-
from server.forms.model_scope import SubscribeForm
# start tutorial
import json
from django.http import HttpResponse, HttpResponseBadRequest
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
        form = self.form_class(data=json.loads(request.body))
        if form.is_valid():
            response_data = {'success_url': force_text(self.success_url)}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            response_data = {form.form_name: {'errors': form.errors}}
            return HttpResponseBadRequest(json.dumps(response_data), status=422, content_type='application/json')
