(function(angular, undefined) {
'use strict';

function noop() {}

// Add three-way data-binding for AngularJS with Django using websockets.
var djng_ws_module = angular.module('ng.django.websocket', []);

// Wraps the built-in WebSocket into a replaceable provider suitable for dependency injection.
djng_ws_module.service('$websocket', function() {
	var ws;
	this.connect = function(url) {
		ws = new WebSocket(url);
		ws.onopen = this.onopen;
		ws.onmessage = this.onmessage;
		ws.onerror = this.onerror;
		ws.onclose = this.onclose;
	};
	this.reconnect = function() {
		ws = new WebSocket(ws.url);
	};
	this.send = function(msg) {
		ws.send(msg);
	};
	this.close = function() {
		ws.close();
	};
});

djng_ws_module.provider('djangoWebsocket', function() {
	var _console = { log: noop, warn: noop, error: noop };
	var websocket_uri, heartbeat_msg = null;

	// Set prefix for the Websocket's URI.
	// This URI must be set during initialization using
	// djangoWebsocketProvider.setURI('{{ WEBSOCKET_URI }}');
	this.setURI = function(uri) {
		websocket_uri = uri;
		return this;
	};

	// Set the heartbeat message and activate the heartbeat interval to 5 seconds.
	// The heartbeat message shall be configured using
	// djangoWebsocketProvider.setHeartbeat({{ WS4REDIS_HEARTBEAT }});  // unquoted!
	// The default behavior is to not listen on heartbeats.
	this.setHeartbeat = function(msg) {
		heartbeat_msg = msg;
		return this;
	};

	this.setLogLevel = function(logLevel) {
		switch (logLevel) {
		case 'debug':
			_console = console;
			break;
		case 'log':
			_console.log = console.log;
			/* falls through */
		case 'warn':
			_console.warn = console.warn;
			/* falls through */
		case 'error':
			_console.error = console.error;
			/* falls through */
		default:
			break;
		}
		return this;
	};

	this.$get = ['$websocket', '$q', '$timeout', '$interval', function($websocket, $q, $timeout, $interval) {
		var ws, deferred, timer_promise = null, wait_for = null, scope, collection;
		var is_subscriber = false, is_publisher = false;
		var heartbeat_promise = null, missed_heartbeats = 0;

		function connect(uri) {
			try {
				_console.log("Connecting to "+uri);
				deferred = $q.defer();
				$websocket.connect(uri);
				timer_promise = null;
			} catch (err) {
				deferred.reject(new Error(err));
			}
		}

		$websocket.onopen = function(evt) {
			_console.log('Connected');
			wait_for = 500;
			deferred.resolve();
			if (heartbeat_msg && heartbeat_promise === null) {
				missed_heartbeats = 0;
				heartbeat_promise = $interval(sendHeartbeat, 5000);
			}
		};

		$websocket.onclose = function(evt) {
			_console.log("Connection closed");
			if (!timer_promise && wait_for) {
				timer_promise = $timeout(function() {
					$websocket.reconnect();
				}, wait_for);
				wait_for = Math.min(wait_for + 500, 5000);
			}
		};

		$websocket.onerror = function(evt) {
			_console.error("Websocket connection is broken!");
			deferred.reject(new Error(evt));
		};

		$websocket.onmessage = function(evt) {
			if (evt.data === heartbeat_msg) {
				// reset the counter for missed heartbeats
				missed_heartbeats = 0;
				return;
			}
			try {
				var server_data = angular.fromJson(evt.data);
				if (is_subscriber) {
					scope.$apply(function() {
						angular.extend(scope[collection], server_data);
					});
				}
			} catch(e) {
				_console.warn('Data received by server is invalid JSON: ' + evt.data);
			}
		};

		function sendHeartbeat() {
			try {
				missed_heartbeats++;
				if (missed_heartbeats > 3)
					throw new Error("Too many missed heartbeats.");
				$websocket.send(heartbeat_msg);
			} catch(e) {
				$interval.cancel(heartbeat_promise);
				heartbeat_promise = null;
				_console.warn("Closing connection. Reason: " + e.message);
				$websocket.close();
			}
		}

		function listener(newValue, oldValue) {
			if (newValue !== undefined) {
				$websocket.send(angular.toJson(newValue));
			}
		}

		function setChannels(channels) {
			angular.forEach(channels, function(channel) {
				if (channel.substring(0, 9) === 'subscribe') {
					is_subscriber = true;
				} else if (channel.substring(0, 7) === 'publish') {
					is_publisher = true;
				}
			});
		}

		function watchCollection() {
			scope.$watchCollection(collection, listener);
		}

		function getWebsocketURL(facility, channels) {
			var parts = [websocket_uri, facility, '?'];
			parts.push(channels.join('&'));
			return parts.join('');
		}

		return {
			connect: function($scope, scope_obj, facility, channels) {
				scope = $scope;
				setChannels(channels);
				collection = scope_obj;
				scope[collection] = scope[collection] || {};
				connect(getWebsocketURL(facility, channels));
				if (is_publisher) {
					deferred.promise.then(watchCollection);
				}
				return deferred.promise;
			}
		};
	}];
});

})(window.angular);
