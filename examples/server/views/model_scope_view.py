# -*- coding: utf-8 -*-
from server.forms.model_scope import SubscribeForm
# start tutorial
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import FormView


class SubscribeView(FormView):
    template_name = 'model-scope.html'
    form_class = SubscribeForm

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request.body)
        form = self.form(request.POST)
        if form.is_valid():
            return redirect('form_data_valid')
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def ajax(self, request_body):
        in_data = json.loads(request_body)
        form = self.form(data=in_data)
        response_data = {'errors': form.errors}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
