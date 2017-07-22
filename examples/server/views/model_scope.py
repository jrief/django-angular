# -*- coding: utf-8 -*-
from server.forms.model_scope import SubscribeForm
from server.urls import reverse_lazy
# start tutorial
import json
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.utils.encoding import force_text


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
        response_data = {'errors': form.errors, 'success_url': force_text(self.success_url)}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
