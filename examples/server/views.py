# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView
from django.conf import settings
from server.forms import SubscriptionForm, SubscriptionFormWithNgModel


class NgFormValidationView(TemplateView):
    template_name = 'subscribe-form.html'
    form = SubscriptionForm(form_name='subscribe_form')

    def __init__(self, **kwargs):
        super(NgFormValidationView, self).__init__(**kwargs)
        self.form.fields['height'].widget.attrs['step'] = 0.05  # Ugly hack to set step size

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        context.update(form=self.form, with_ws4redis=hasattr(settings, 'WEBSOCKET_URL'))
        return context


class NgFormValidationViewWithNgModel(NgFormValidationView):
    template_name = 'subscribe-form-with-model.html'
    form = SubscriptionFormWithNgModel(scope_prefix='subscribe_data')


class Ng3WayDataBindingView(NgFormValidationViewWithNgModel):
    template_name = 'three-way-data-binding.html'
