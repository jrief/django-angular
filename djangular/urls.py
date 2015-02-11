# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from djangular.views.resolvers import UrlResolverView


urlpatterns = patterns('',
    url(r'^url/$', UrlResolverView.as_view(), name='djng_url_resolver'),
)
