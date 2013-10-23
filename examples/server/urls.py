# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from server.views import NgFormValidationView


urlpatterns = patterns('',
    url(r'^angular_form/$', NgFormValidationView.as_view(), name='ng_form_validation'),
)
