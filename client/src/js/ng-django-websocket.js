(function(angular, undefined) {
'use strict';

function noop() {}

// Add three-way data-binding for AngularJS with Django using websockets.
angular.module('ng.django.websocket', []).provider('djangoWebsocket', function() {
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

	this.$get = ['$q', '$timeout', '$interval', function($q, $timeout, $interval) {
		var ws, deferred, timer_promise = null, wait_for = null, scope, collection;
		var is_subscriber = false, is_publisher = false;
		var heartbeat_promise = null, missed_heartbeats = 0;

		function connect(uri) {
			try {
				_console.log("Connecting to "+uri);
				deferred = $q.defer();
				ws = new WebSocket(uri);
				ws.onopen = onOpen;
				ws.onmessage = onMessage;
				ws.onerror = onError;
				ws.onclose = onClose;
				timer_promise = null;
			} catch (err) {
				deferred.reject(new Error(err));
			}
		}

		function onOpen(evt) {
			_console.log('Connected');
			wait_for = 500;
			deferred.resolve();
			if (heartbeat_msg && heartbeat_promise === null) {
				missed_heartbeats = 0;
				heartbeat_promise = $interval(sendHeartbeat, 5000);
			}
		}

		function onClose(evt) {
			_console.log("Connection closed");
			if (!timer_promise && wait_for) {
				timer_promise = $timeout(function() {
					connect(ws.url);
				}, wait_for);
				wait_for = Math.min(wait_for + 500, 5000);
			}
		}

		function onError(evt) {
			_console.error("Websocket connection is broken!");
			deferred.reject(new Error(evt));
		}

		function onMessage(evt) {
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
		}

		function sendHeartbeat() {
			try {
				missed_heartbeats++;
				if (missed_heartbeats > 3)
					throw new Error("Too many missed heartbeats.");
				ws.send(heartbeat_msg);
			} catch(e) {
				$interval.cancel(heartbeat_promise);
				heartbeat_promise = null;
				_console.warn("Closing connection. Reason: " + e.message);
				ws.close();
			}
		}

		function listener(newValue, oldValue) {
			if (newValue !== undefined) {
				ws.send(JSON.stringify(newValue));
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
			connect: function($scope, facility, channels, scope_obj) {
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
