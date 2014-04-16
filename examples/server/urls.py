# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from server.views import (SubscribeViewWithFormValidation, SubscribeViewWithModelForm,
        SubscribeViewWithModelFormAndValidation, ThreeWayDataBindingView, NgFormDataValidView,
        PartialsView)


urlpatterns = patterns('',
    url(r'^form_validation$', SubscribeViewWithFormValidation.as_view(),
        name='djng_form_validation'),
    url(r'^model_form$', SubscribeViewWithModelForm.as_view(),
        name='djng_model_form'),
    url(r'^model_form_validation$', SubscribeViewWithModelFormAndValidation.as_view(),
        name='djng_model_form_validation'),
    url(r'^threeway_databinding$', ThreeWayDataBindingView.as_view(),
        name='djng_3way_databinding'),
    url(r'^form_data_valid', NgFormDataValidView.as_view(),
        name='form_data_valid'),
    url(r'^partials/', PartialsView.as_view(),
        name='djng_partials_demo'),
     url(r'^$', RedirectView.as_view(url=reverse_lazy('djng_form_validation')),  # RedirectView.as_view(url=reverse('djng_form_validation')),
         name='djng_home'),
)
