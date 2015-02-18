# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from djangular.views.resolvers import DjangularUrlResolverView


urlpatterns = patterns('',
    url(r'^url/$', DjangularUrlResolverView.as_view(), name='djng_url_resolver'),
)
