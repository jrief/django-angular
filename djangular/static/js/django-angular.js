/*
 * django-angular-websocket
 * https://github.com/jrief/django-angular
 *
 * Add three-way data-binding for AngularJS with Django using websockets.
 *
 * Copyright (c) 2014 Jacob Rief
 * Licensed under the MIT license.
 */

(function(angular, undefined) {
'use strict';

angular.module('ng.django.websocket', []).provider('djangoWebsocket', function() {
	var _prefix;
	var _console = { log: noop, warn: noop, error: noop };

	function noop() {}

	this.prefix = function(prefix) {
		_prefix = prefix;
		return this;
	};

	this.debug = function(debug) {
		if (debug) {
			_console = console;
		}
		return this;
	};

	this.$get = ['$window', '$q', '$timeout', function($window, $q, $timeout) {
		var ws, deferred, timer = null, interval = null, scope, channels, collection;

		function connect(uri) {
			try {
				_console.log("Connecting to "+uri);
				deferred = $q.defer();
				ws = new WebSocket(uri);
				ws.onopen = on_open;
				ws.onmessage = on_message;
				ws.onerror = on_error;
				ws.onclose = on_close;
				timer = null;
			} catch (err) {
				deferred.reject(new Error(err));
			}
		}

		function on_open(evt) {
			_console.log('Connected');
			interval = 3000;
			deferred.resolve();
		}

		function on_close(evt) {
			_console.log("Connection closed");
			if (!timer && interval) {
				timer = $timeout(function() {
					connect(ws.url);
				}, interval);
				interval = Math.min(interval + 1000, 90000);
			}
		}

		function on_error(evt) {
			_console.error("Websocket connection is broken!");
			deferred.reject(new Error(evt));
		}

		function on_message(evt) {
			try {
				var server_data = JSON.parse(evt.data);
				scope.$apply(function() {
					angular.extend(scope[collection], server_data);
				});
			} catch(e) {
				_console.warn('Data received by server is invalid JSON: ' + evt.data);
			}
		}

		function listener(newValue, oldValue) {
			if (newValue !== undefined) {
				ws.send(JSON.stringify(newValue));
			}
		}

		return {
			connect: function(scope_, channels_, collection_) {
				var parts = [], location = $window.location;
				scope = scope_;
				channels = channels_;
				collection = collection_;
				parts.push(location.protocol === 'https' ? 'wss:' : 'ws:');
				parts.push('//');
				parts.push(location.host);
				parts.push(_prefix);
				parts.push(location.pathname);
				parts.push('?');
				parts.push(channels.join('&'));
				connect(parts.join(''));
				scope[collection] = scope[collection] || {};
				deferred.promise.then(function() {
					scope.$watchCollection(collection, listener);
				});
				return deferred.promise;
			}
		};
	}];
});

})(window.angular);
