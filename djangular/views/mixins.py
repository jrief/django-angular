# -*- coding: utf-8 -*-
import json
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
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


class DjngPartialViewMixin(object):
    hashPrefix = None
    html5mode = True
    allowed_route_attrs = ['controller', 'template', 'templateUrl', 'redirectTo']

    def location_provider_config(self, attr):
        items = []
        if self.hashPrefix is not None:
            items.append("hashPrefix('{0}')".format(str(self.hashPrefix)))
        if isinstance(self.html5mode, bool):
            items.append("html5Mode({0})".format(str(self.html5mode).lower()))
        return items and [('$locationProvider', attr, format_html('.'.join([attr] + items)))] or []

    def route_provider_config(self, attr):
        items = []
        for key, elems in self.ng_routes.items():
            attrs = format_html_join(',', "'{0}':'{1}'",
                        ((k, v) for k, v in elems.items() if k in self.allowed_route_attrs))
            if key == None:
                # this special key is used to handle the default route
                items.append(format_html("otherwise({{{0}}})", attrs))
            else:
                items.append(format_html("when('/{0}',{{{1}}})", key, attrs))
        return items and [('$routeProvider', attr, mark_safe('.'.join([attr] + items)))] or []

    def state_provider_config(self, attr):
        items = []
        for key, elems in self.ng_routes.items():
            attrs = format_html_join(',', "'{0}':'{1}'",
                        ((k, v) for k, v in elems.items() if k in self.allowed_route_attrs))
            if key == None:
                # this special key is used to handle the default route
                items.append(format_html("otherwise({{{0}}})", attrs))
            else:
                items.append(format_html("when('/{0}',{{{1}}})", key, attrs))
        return items and [('$stateProvider', attr, mark_safe('.'.join([attr] + items)))] or []

    @staticmethod
    def join_configs(configs):
        return format_html("[{0},function({1}){{{2}}}]",
                format_html_join(',', "'{0}'", configs),  # named AngularJS providers
                format_html_join(',', '{1}', configs),  # providers as minimized arguments
                format_html_join('', '{2};', configs))  # function statements

    def render_state_config(self):
        """
        Renders a Javascript function embedded into a dependency injection array, which shall be be
        used to configure the Angular application, when used with partial routing.
        """
        pass

    def render_routes_config(self):
        """
        Renders a Javascript function embedded into a dependency injection array, which shall be be
        used to configure the Angular application, when used with partial routing.
        """
        provider_configs = []
        provider_configs.extend(self.location_provider_config('l'))
        provider_configs.extend(self.route_provider_config('r'))
        return self.join_config(provider_configs)

    def get_context_data(self, **kwargs):
        context = super(djngPartialViewMixin, self).get_context_data(**kwargs)
        context.update(config_djng_routes=self.render_routes_config)
        return context
