(function (angular, undefined) {
    'use strict';
    // module: ng.django.urls
    // Provide url reverse resolution functionality for django urls in angular
    var djngUrls = angular.module('ng.django.urls', []);

    djngUrls.service('djangoUrl', ['patterns', function (patterns) {

        // Fill a url template with arguments
        // Find everything that matches the argument pattern and replace it
        // with the first argument from args array (and remove it from the array)
        function fill_args(url_regex, args) {
            return url_regex.replace(/\([^\)]+\)/g, function (match) {
                if (args.length === 0) {
                    // Like django's url templatetag raise an error when there aren't enough arguments
                    throw 'Djangular URL error: Not enough arguments';
                }
                return args.shift();
            });
        }

        // Fill a url template with keyword arguments
        // For everything that matches the argument pattern try finding it's name in kwargs object
        // If one is found, replace argument with that, otherwise replace it with ':' prefixed argument name
        // The ':' prefixing gives a parametrized url template, ':some_name' can later be filled by angular services
        function fill_kwargs(url_regex, kwargs) {
            kwargs = kwargs || {};
            // The behaviour differs from django's url templatetag here
            // If there are missing kwargs, do the ':' prefixing rather than raising an error
            return url_regex.replace(/\([^\)]+\)/g, function (match) {
                var name = match.match(/<([^>]+)>/)[1];
                if (typeof kwargs[name] === 'undefined') {
                    return ':' + name;
                }
                return kwargs[name];
            });
        }

        // Public interface
        this.reverse = function (url_name, args_or_kwargs) {
            // Find the suitable url regex patteren by name, raise an error if none is found
            var re = patterns[url_name];
            if (typeof re === 'undefined') {
                throw 'Djangular URL error: No matching URL found';
            }
            // Depending on type of args_or_kwargs call suitable method
            // Array (of arguments) -> fill_args()
            // Object (of keyword arguments) -> fill_kwargs()
            if (Array.isArray(args_or_kwargs)) {
                return fill_args(re, args_or_kwargs);
            }
            return fill_kwargs(re, args_or_kwargs);
        };
    }
    ]);
}(window.angular));

