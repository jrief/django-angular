# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from server.views.classic_subscribe import SubscribeView as ClassicSubscribeView
from server.views.client_validation import SubscribeView as ClientValidationView
from server.views.model_scope import SubscribeView as ModelScopeView
from server.views.combined_validation import SubscribeView as CombinedValidationView
from server.views.threeway_databinding import SubscribeView as ThreeWayDataBindingView
from server.views import NgFormDataValidView


urlpatterns = [
    url(r'^classic_form/$', ClassicSubscribeView.as_view(),
        name='djng_classic_subscription'),
    url(r'^form_validation/$', ClientValidationView.as_view(),
        name='djng_form_validation'),
    url(r'^model_scope/$', ModelScopeView.as_view(),
        name='djng_model_scope'),
    url(r'^combined_validation/$', CombinedValidationView.as_view(),
        name='djng_combined_validation'),
    url(r'^threeway_databinding/$', ThreeWayDataBindingView.as_view(),
        name='djng_3way_databinding'),
    url(r'^form_data_valid', NgFormDataValidView.as_view(), name='form_data_valid'),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('djng_form_validation'))),
]
