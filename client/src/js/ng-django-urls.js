(function (angular, undefined) {
    'use strict';

    // module: ng.django.urls
    // Provide url reverse resolution functionality for django urls in angular
    var djngUrls = angular.module('ng.django.urls', []);

    djngUrls.service('djangoUrl', function () {
        function fill_args(url_regex, args){
            return url_regex.replace(/\([^/]+\)/g, function(match){
                if (args.length == 0){
                    throw "Djangular URL error: Not enough arguments";
                }
                return args.shift();
            });
        }
        function fill_kwargs(url_regex, kwargs){
            return url_regex.replace(/\([^/]+\)/g, function(match){
                var name = match.match(/<([^>]+)>/)[1];
                if (typeof kwargs[name] === 'undefined'){
                    return ":" + name;
                }
                return kwargs[name];
            });
        }
        this.resolve = function(url_name, args_or_kwargs) {
            // TODO urlname -> regex pattern
            if (Array.isArray(args_or_kwargs)){
                return fill_args(url_name, args_or_kwargs);
            }
            return fill_kwargs(url_name, args_or_kwargs);
        }
    })


})(window.angular);