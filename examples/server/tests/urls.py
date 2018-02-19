# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import View
from django.http import HttpResponse
from django.template import RequestContext, Template
from djng.views.mixins import JSONResponseMixin, allow_remote_invocation


class TestCSRFValueView(View):
    def get(self, request):
        template = Template('{% load djng_tags %}<script>var x="{{ csrf_token }}";</script>')
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))


class TestUrlResolverTagsView(JSONResponseMixin, View):
    @allow_remote_invocation
    def blah(self, in_data):
        return {'blah': 'abc'}

    def get(self, request):
        load = request.GET.get('load')
        if load == 'root_urls':
            template = Template("{% load djng_tags %}{% load_djng_urls None '' %}")
        else:
            template = Template("{% load djng_tags %}{% load_djng_urls %}")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))


class RemoteMethodsView(JSONResponseMixin, View):
    @allow_remote_invocation
    def foo(self, in_data):
        return {'foo': 'abc'}

    @allow_remote_invocation
    def bar(self, in_data):
        return {'bar': 'abc'}

    def get(self, request):
        template = Template("{% load djng_tags %}{% load_djng_urls 'SELF' %}")
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))


subsub_patterns = [
    url(r'^app/$', RemoteMethodsView.as_view(), name='app'),
]

sub_patterns = ([
    url(r'^sub/', include(subsub_patterns)),
], 'sub')


class TestAngularTagView(View):
    def get(self, request):
        tmpl_id = request.GET.get('tmpl_id')
        switch = bool(request.GET.get('switch'))
        if tmpl_id == 'expand_object':
            template = Template('{% load djng_tags %}{% angularjs switch %}{{ expandme.foo }}{% endangularjs %}')
            context = {'switch': switch, 'expandme': {'foo': 'bar'}}
        elif tmpl_id == 'expand_array':
            template = Template('{% load djng_tags %}{% angularjs switch %}{{ expandme.1.foo }}{% endangularjs %}')
            context = {'switch': switch, 'expandme': [{'foo': 'zero'}, {'foo': 'one'}]}
        else:
            template = Template('{% load djng_tags %}{% angularjs switch %}{{ expandme }}{% endangularjs %}')
            context = {'switch': switch, 'expandme': 'Hello World'}
        request_context = RequestContext(request, context)
        return HttpResponse(template.render(request_context))


def locale_script_view(request):
    template = Template('{% load djng_tags %}{% djng_locale_script %}')
    request_context = RequestContext(request, {})
    return HttpResponse(template.render(request_context))


urlpatterns = [
    url(r'^sub_methods/', include(sub_patterns, namespace='submethods')),
    url(r'^straight_methods/$', TestCSRFValueView.as_view(), name='straightmethods'),
    url(r'^url_resolvers/$', TestUrlResolverTagsView.as_view(), name='urlresolvertags'),
    url(r'^angular_tag/$', TestAngularTagView.as_view(), name='angulartags'),
    url(r'^locale_script_tag/$', locale_script_view, name='locale_script'),
]
