# -*- coding: utf-8 -*-
import json
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest


def allowed_action(func):
    """
    All methods which shall be callable through a given Ajax 'action' must be
    decorated with @allowed_action. This is required for safety reasons. It
    inhibits the caller to invoke all available methods of a class.
    """
    setattr(func, 'is_allowed_action', None)
    return func


class JSONResponseMixin(object):
    """
    A mixin that dispatches POST requests containing the keyword 'action' onto
    the method with that name. It renders the returned context as JSON response.
    """

    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        action = kwargs.get('action')
        action = action and getattr(self, action, None)
        if not callable(action):
            return self._dispatch_super(request, *args, **kwargs)
        out_data = json.dumps(action(), cls=DjangoJSONEncoder)
        response = HttpResponse(out_data)
        response['Content-Type'] = 'application/json;charset=UTF-8'
        response['Cache-Control'] = 'no-cache'
        return response

    def post(self, request, *args, **kwargs):
        try:
            if not request.is_ajax():
                return self._dispatch_super(request, *args, **kwargs)
            in_data = json.loads(str(request.body))
            action = in_data.pop('action', kwargs.get('action'))
            handler = action and getattr(self, action, None)
            if not callable(handler):
                return self._dispatch_super(request, *args, **kwargs)
            if not hasattr(handler, 'is_allowed_action'):
                raise ValueError('Method "%s" is not decorated with @allowed_action' % action)
            out_data = json.dumps(handler(in_data), cls=DjangoJSONEncoder)
            return HttpResponse(out_data, content_type='application/json;charset=UTF-8')
        except ValueError as err:
            return HttpResponseBadRequest(err)

    def _dispatch_super(self, request, *args, **kwargs):
        base = super(JSONResponseMixin, self)
        handler = getattr(base, request.method.lower(), None)
        if callable(handler):
            return handler(request, *args, **kwargs)
        raise ValueError('This view can not handle method %s' % request.method)


class NgPartialViewMixin(object):
    html5mode = True
    allowed_route_attrs = ['controller', 'template', 'templateUrl', 'redirectTo']

    def render_config_routes(self):
        if hasattr(self, 'get_ng_routes'):
            routes = self.get_ng_routes()
        elif hasattr(self, 'ng_routes'):
            routes = self.ng_routes
        else:
            raise AttributeError("Class %s has neither an member 'ng_routes' nor a method 'get_ng_routes'" % self.__class__)
        base_href = reverse(self.request.resolver_match.view_name)
        items = []
        for key, elems in routes.items():
            attrs = format_html_join(',', "'{0}':'{1}'",
                        ((k, v) for k, v in elems.items() if k in self.allowed_route_attrs))
            if key == None:
                # this special key is used to handle the default route
                items.append(format_html("otherwise({{{0}}})", attrs))
            else:
                items.append(format_html("when('/{0}',{{{1}}})", key, attrs))
        html5mode = str(self.html5mode).lower()
        return format_html("['$locationProvider','$routeProvider',function(l,r){{l.html5Mode({0});r.{1};}}]",
                           html5mode, mark_safe('.'.join(items)))

    def get_context_data(self, **kwargs):
        context = super(NgPartialViewMixin, self).get_context_data(**kwargs)
        context.update(config_ng_routes=self.render_config_routes)
        return context
