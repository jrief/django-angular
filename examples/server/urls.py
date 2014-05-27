# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from server.views import (SubscribeFormView, SubscribeViewWithFormValidation,
        SubscribeViewWithModelForm, SubscribeViewWithModelFormAndValidation, Ng3WayDataBindingView,
        NgFormDataValidView)


urlpatterns = patterns('',
    url(r'^base_form/$', SubscribeFormView.as_view(),
        name='djng_base_form'),
    url(r'^form_validation/$', SubscribeViewWithFormValidation.as_view(),
        name='djng_form_validation'),
    url(r'^model_form/$', SubscribeViewWithModelForm.as_view(),
        name='djng_model_form'),
    url(r'^model_form_validation/$', SubscribeViewWithModelFormAndValidation.as_view(),
        name='djng_model_form_validation'),
    url(r'^threeway_databinding/$', Ng3WayDataBindingView.as_view(),
        name='djng_3way_databinding'),
    url(r'^form_data_valid', NgFormDataValidView.as_view(), name='form_data_valid'),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('djng_form_validation'))),
)
