(function(angular, undefined) {
'use strict';

// module: djng.rmi
var djng_rmi_module = angular.module('djng.rmi', []);

// A simple wrapper to extend the $httpProvider for executing remote methods on the server side
// for Django Views derived from JSONResponseMixin.
// It can be used to invoke GET and POST requests. The return value is the same promise as returned
// by $http.get() and $http.post().
// Usage:
// djangoRMI.name.method(data).success(...).error(...)
// @param data (optional): If set and @allowd_action was auto, then the call is performed as method
//     POST. If data is unset, method GET is used. data must be a valid JavaScript object or undefined.
djng_rmi_module.provider('djangoRMI', function() {
	var remote_methods, http;

	this.configure = function(conf) {
		remote_methods = conf;
		convert_configuration(remote_methods);
	};

	function convert_configuration(obj) {
		angular.forEach(obj, function(val, key) {
			if (!angular.isObject(val))
				throw new Error('djangoRMI.configure got invalid data');
			if (val.hasOwnProperty('url')) {
				// convert config object into function
				val.headers['X-Requested-With'] = 'XMLHttpRequest';
				obj[key] = function(data) {
					var config = angular.copy(val);
					if (config.method === 'POST') {
						if (data === undefined)
							throw new Error('Calling remote method '+ key +' without data object');
						config.data = data;
					} else if (config.method === 'auto') {
						if (data === undefined) {
							config.method = 'GET';
						} else {
							// TODO: distinguish between POST and PUT
							config.method = 'POST';
							config.data = data;
						}
					}
					return http(config);
				};
			} else {
				// continue to examine the values recursively
				convert_configuration(val);
			}
		});
	}

	this.$get = ['$http', function($http) {
		http = $http;
		return remote_methods;
	}];
});

})(window.angular);
