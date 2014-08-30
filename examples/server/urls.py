# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
#from server.views import (SubscribeViewWithModelFormAndValidation,  Ng3WayDataBindingView, NgFormDataValidView)
from server.views.classic_subscribe import SubscribeView as ClassicSubscribeView
from server.views.subscribe_client_validation import SubscribeView as SubscribeClientValidationView
from server.views.model_scope_view import SubscribeView as SubscribeViewWithModelScope
from server.views import NgFormDataValidView


urlpatterns = patterns('',
    url(r'^classic_form/$', ClassicSubscribeView.as_view(),
        name='djng_classic_subscription'),
    url(r'^form_validation/$', SubscribeClientValidationView.as_view(),
        name='djng_form_validation'),
    url(r'^model_scope/$', SubscribeViewWithModelScope.as_view(),
        name='djng_model_scope'),
#    url(r'^model_form_validation/$', SubscribeViewWithModelFormAndValidation.as_view(),
#        name='djng_model_form_validation'),
#    url(r'^threeway_databinding/$', Ng3WayDataBindingView.as_view(),
#        name='djng_3way_databinding'),
    url(r'^form_data_valid', NgFormDataValidView.as_view(), name='form_data_valid'),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('djng_form_validation'))),
)
