# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from server.forms.subscribe_form import SubscribeForm
# start tutorial
from django.template.context import RequestContext
from django.template.loader import get_template
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy


class ComponentView(TemplateView):
    template_name = 'a-subcomponent.html'

    @classmethod
    def as_component(cls):
        return cls()

    def dispatch(cls, request):
        template = get_template(cls.template_name)
        context = RequestContext(request, {})
        html = template.render(context)
        return html


class SubscribeView(FormView):
    template_name = 'subscribe-form.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('form_data_valid')
    component = ComponentView

    def get_context_data(self, **kwargs):
        context = super(SubscribeView, self).get_context_data(**kwargs)
        context.update(my_component=self.component)
        return context
