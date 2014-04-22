# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns, include
from django.views.generic import View
from djangular.views.mixins import JSONResponseMixin, allow_remote_invocation


class RemoteMethodsView(JSONResponseMixin, View):
    @allow_remote_invocation
    def foo(self, in_data):
        return {'foo': 'abc'}

    @allow_remote_invocation
    def bar(self, in_data):
        return {'bar': 'abc'}


subsub_patterns = patterns('',
    url(r'^app/$', RemoteMethodsView.as_view(), name='app'),
)

sub_patterns = patterns('',
    url(r'^sub/', include(subsub_patterns, namespace='sub')),
)

urlpatterns = patterns('',
    url(r'^sub_methods/', include(sub_patterns, namespace='submethods')),
    url(r'^straight_methods/$', RemoteMethodsView.as_view(), name='straightmethods'),
)
