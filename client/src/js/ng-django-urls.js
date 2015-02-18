(function (angular, undefined) {
    'use strict';
    // module: ng.django.urls
    // Provide url reverse resolution functionality for django urls in angular
    var djngUrls = angular.module('ng.django.urls', []);

    djngUrls.service('djangoUrl', function () {
        /*
        Functions from angular.js source, not public available
        See: https://github.com/angular/angular.js/issues/7429
         */
        function forEachSorted(obj, iterator, context) {
            var keys = sortedKeys(obj);
            for (var i = 0; i < keys.length; i++) {
                iterator.call(context, obj[keys[i]], keys[i]);
            }
            return keys;
        }
        function sortedKeys(obj) {
            var keys = [];
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    keys.push(key);
                }
            }
            return keys.sort();
        }
        function buildUrl(url, params) {
            if (!params) return url;
            var parts = [];
            forEachSorted(params, function (value, key) {
                if (value == null || value == undefined) return;
                if (angular.isObject(value)) {
                    value = angular.toJson(value);
                }
                parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
            });
            return url + ((url.indexOf('?') == -1) ? '?' : '&') + parts.join('&');
        }
        // Service public interface
        this.reverse = function (url_name, args_or_kwargs) {
            var url = buildUrl('/djangular/url/', {djng_url_name: url_name});
            if (Array.isArray(args_or_kwargs)) {
                forEachSorted(args_or_kwargs, function(value){
                    url = buildUrl(url, {'djng_url_args': value});
                });
                return url;
            }
            forEachSorted(args_or_kwargs, function(value, key){
                var params = {};
                params['djng_url_kwarg_' + key] = value;
                url = buildUrl(url, params);
            });
            return url;
        };
    });

}(window.angular));

