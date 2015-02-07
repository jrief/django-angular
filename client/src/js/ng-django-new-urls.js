(function (angular, undefined) {
    'use strict';
    // module: ng.django.urls
    // Provide url reverse resolution functionality for django urls in angular
    var djngUrls = angular.module('ng.django.urls', []);

    // Reverse returns a object with properties for url resolution
    // Using a http interceptor the configuration object is replaced with correct url
    // and request params are filled with data for url resolution
    djngUrls.service('djangoUrlNew', function () {
        this.reverse = function (url_name, args_or_kwargs) {
            if (Array.isArray(args_or_kwargs)) {
                return {name: url_name, args: args_or_kwargs}
            }
            return {name: url_name, kwargs: args_or_kwargs}
        };
    });

    // If config.url is not a string, but a django-url config object replace url with UrlResolverView url
    // and fill arguments/keyword arguments appropriately
    djngUrls.factory('urlResolverInterceptor', function () {
        return {
            'request': function (config) {
                var djngUrlConfig = config.url;
                if (typeof djngUrlConfig === 'string') {
                    return config;
                }
                config.url = '/url/';
                config.params = config.params || {};
                config.params['djng_url_name'] = djngUrlConfig.name;
                config.params['djng_url_args'] = djngUrlConfig.args || [];
                if (typeof djngUrlConfig.kwargs !== 'undefined') {
                    for (var key in djngUrlConfig.kwargs) {
                        if (djngUrlConfig.kwargs.hasOwnProperty(key)) {
                            config.params['djng_url_kwarg_' + key] = djngUrlConfig.kwargs[key];
                        }
                    }
                }
                return config;
            }
        }
    });

    // Add interceptor
    djngUrls.config(function ($httpProvider) {
        $httpProvider.interceptors.push('urlResolverInterceptor');
    });

}(window.angular));

