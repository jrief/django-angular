(function(angular, undefined) {
'use strict';

// module: djng.uploadfiles
// Connect the third party module `ng-file-upload` to django-angular
var fileuploadModule = angular.module('djng.fileupload', ['ngFileUpload']);


fileuploadModule.directive('djngFileuploadUrl', ['Upload', function(Upload) {
	return {
		restrict: 'A',
		require: 'ngModel',
		link: function(scope, element, attrs, ngModelController) {
			ngModelController.$setViewValue({});
			element.data('area_label', element.val());
			if (attrs.currentFile) {
				angular.extend(scope.$eval(attrs.ngModel), {current_file: attrs.currentFile});
				element.data('current_file', attrs.currentFile);
				element.val(attrs.currentFile.substring(0, attrs.currentFile.indexOf(':')));
				element.addClass('djng-preset');
			} else {
				element.addClass('djng-empty');
			}

			scope.uploadFile = function(file, filetype, id, model) {
				var data = {'file:0': file, filetype: filetype},
				    element = angular.element(document.querySelector('#' + id));
				element.addClass('uploading');
				Upload.upload({
					data: data,
					url: attrs.djngFileuploadUrl
				}).then(function(response) {
					var field = response.data['file:0'], current = element.data('current_file');
					element.removeClass('uploading');
					element.css('background-image', field.url);
					element.removeClass('djng-empty')
					element.removeClass('djng-preset')
					element.val(field.file_name);
					delete field.url;  // we don't want to send back the whole image
					angular.extend(scope.$eval(model), field, current ? {current_file: current} : {});
				}, function(respose) {
					element.removeClass('uploading');
					console.error(respose.statusText);
				});
			};
		}
	};
}]);


fileuploadModule.directive('djngFileuploadButton', function() {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			scope.deleteImage = function(id, model) {
				var model = scope.$eval(model),
				    element = angular.element(document.querySelector('#' + id));
				element.css('background-image', 'none');
				element.addClass('djng-empty');
				element.removeClass('djng-preset');
				element.val(element.data('area_label'));
				if (model) {
					model.temp_name = 'delete';  // tags previous image for deletion
				}
			};
		}
	};
});

})(window.angular);

(function(angular, undefined) {
'use strict';

// module: djng.forms
// Correct Angular's form.FormController behavior after rendering bound forms.
// Additional validators for form elements.
var djng_forms_module = angular.module('djng.forms', []);

// create a simple hash code for the given string
function hashCode(s) {
	return s.split("").reduce(function(a, b) {
		a = (a << 5) - a + b.charCodeAt(0);
		return a & a;
	}, 0);
}

// This directive adds a dummy binding to form elements without ng-model attribute,
// so that AngularJS form validation gets notified whenever the fields content changes
// http://www.w3schools.com/html/html_form_elements.asp
var form_elements = ['input', 'select', 'textarea', 'datalist'];

angular.forEach(form_elements, function(element) {
	djng_forms_module.directive(element, addNgModelDirective());
});

function addNgModelDirective() {
	return ['$compile', function($compile) {
		return {
			restrict: 'E',
			require: '?^form',
			link: function(scope, element, attr, formCtrl) {
				var modelName;
				if (!formCtrl || angular.isUndefined(formCtrl.$name) || element.prop('type') === 'hidden' || angular.isUndefined(attr.name) || angular.isDefined(attr.ngModel))
					return;
				modelName = 'dmy' + Math.abs(hashCode(formCtrl.$name)) +'.' + attr.name.replace(/-/g, "_");
				attr.$set('ngModel', modelName);
				$compile(element, null, 9999)(scope);
			}
		};
	}];
}

// Bound fields with invalid input data, shall be marked as ng-invalid-bound, so that
// the input field visibly contains invalid data, even if pristine
djng_forms_module.directive('djngError', function() {
	return {
		restrict: 'A',
		require: '?^form',
		link: function(scope, element, attrs, formCtrl) {
			var boundField;
			var field = angular.isElement(element) ? element[0] : null;
			if (!field || !formCtrl || angular.isUndefined(attrs.name) || attrs.djngError !== 'bound-field')
				return;
			boundField = formCtrl[attrs.name];
			boundField.$setValidity('bound', false);
			boundField.$parsers.push(function(value) {
				if (value !== field.defaultValue) {
					// set bound field into valid state after changing value
					boundField.$setValidity('bound', true);
					element.removeAttr('djng-error');
				}
				return value;
			});
		}
	};
});

// This directive overrides some of the internal behavior on forms if used together with AngularJS.
// Otherwise, the content of bound forms is not displayed, because AngularJS does not know about
// the concept of bound forms and thus hides values preset by Django while rendering HTML.
djng_forms_module.directive('ngModel', ['$log', function($log) {
	function restoreInputField(field) {
		// restore the field's content from the rendered content of bound fields
		switch (field.type) {
		case 'radio':
			if (field.defaultChecked) {
				return field.defaultValue;
			}
			break;
		case 'checkbox':
			if (field.defaultChecked) {
				return true;
			}
			break;
		case 'password':
			// after an (un)successful submission, reset the password field
			return null;
			break;
		default:
			if(field.defaultValue) {
				return field.defaultValue;
			}
			break;
		}
	}

	function restoreSelectOptions(field) {
		var result = [];
		angular.forEach(field.options, function(option) {
			if (option.defaultSelected) {
				// restore the select option to selected
				angular.element(option).prop('selected', 'selected');
				if (field.multiple) {
					result.push(option.value);
				} else {
					result = option.value;
					return;
				}
			}
		});
		return result;
	}

	function restoreTextArea(field) {
		// restore the field's content from the rendered content of bound fields
		if(field.defaultValue) {
			return field.defaultValue;
		}
	}

	function setDefaultValue(modelCtrl, value) {
		if(angular.isDefined(value)) {
			modelCtrl.$setViewValue(value);
			if(angular.isObject(modelCtrl.$options)) {
				modelCtrl.$commitViewValue();
			}
		}
	}

	return {
		restrict: 'A',
		// make sure this directive is applied after angular built-in one
		priority: 1,
		require: ['ngModel', '^?form'],
		link: function(scope, element, attrs, ctrls) {
			var field = angular.isElement(element) ? element[0] : null;
			var modelCtrl = ctrls[0], formCtrl = ctrls[1] || null;
			var curModelValue = scope.$eval(attrs.ngModel);
  
			// if model already has a value defined, don't set the default
			if (!field || !formCtrl || angular.isDefined(curModelValue)) {
				return;
			}

			switch (field.tagName) {
			case 'INPUT':
				setDefaultValue(modelCtrl, restoreInputField(field));
				break;
			case 'SELECT':
				setDefaultValue(modelCtrl, restoreSelectOptions(field));
				break;
			case 'TEXTAREA':
				setDefaultValue(modelCtrl, restoreTextArea(field));
				break;
			default:
				$log.log('Unknown field type: ' + field.tagName);
				break;
			}

			// restore the form's pristine state
			formCtrl.$setPristine();
		}
	};
}]);


// This directive is added automatically by django-angular for widgets of type RadioSelect and
// CheckboxSelectMultiple. This is necessary to adjust the behavior of a collection of input fields,
// which forms a group for one `django.forms.Field`.
djng_forms_module.directive('validateMultipleFields', function() {
	return {
		restrict: 'A',
		require: '^?form',
		link: function(scope, element, attrs, formCtrl) {
			var subFields, checkboxElems = [];

			function validate(event) {
				var valid = false;
				angular.forEach(checkboxElems, function(checkbox) {
					valid = valid || checkbox.checked;
				});
				formCtrl.$setValidity('required', valid);
				if (event) {
					formCtrl.$dirty = true;
					formCtrl.$pristine = false;
					// element.on('change', validate) is jQuery and runs outside of Angular's digest cycle.
					// Therefore Angular does not get the end-of-digest signal and $apply() must be invoked manually.
					scope.$apply();
				}
			}

			if (!formCtrl)
				return;
			try {
				subFields = angular.fromJson(attrs.validateMultipleFields);
			} catch (SyntaxError) {
				if (!angular.isString(attrs.validateMultipleFields))
					return;
				subFields = [attrs.validateMultipleFields];
				formCtrl = formCtrl[subFields];
			}
			angular.forEach(element.find('input'), function(elem) {
				if (subFields.indexOf(elem.name) >= 0) {
					checkboxElems.push(elem);
					angular.element(elem).on('change', validate);
				}
			});

			// remove "change" event handlers from each input field
			element.on('$destroy', function() {
				angular.forEach(element.find('input'), function(elem) {
					angular.element(elem).off('change');
				});
			});
			validate();
		}
	};
});


// This directive can be added to an input field which shall validate inserted dates, for example:
// <input ng-model="a_date" type="text" validate-date="^(\d{4})-(\d{1,2})-(\d{1,2})$" />
// Now, such an input field is only considered valid, if the date is a valid date and if it matches
// against the given regular expression.
djng_forms_module.directive('validateDate', function() {
	var validDatePattern = null;

	function validateDate(date) {
		var matched, dateobj;
		if (!date) // empty field are validated by the "required" validator
			return true;
		dateobj = new Date(date);
		if (isNaN(dateobj))
			return false;
		if (validDatePattern) {
			matched = validDatePattern.exec(date);
			return matched && parseInt(matched[2], 10) === dateobj.getMonth() + 1;
		}
		return true;
	}

	return {
		require: '?ngModel',
		restrict: 'A',
		link: function(scope, elem, attrs, controller) {
			if (!controller)
				return;

			if (attrs.validateDate) {
				// if a pattern is set, only valid dates with that pattern are accepted
				validDatePattern = new RegExp(attrs.validateDate, 'i');
			}

			var validator = function(value) {
				var validity = controller.$isEmpty(value) || validateDate(value);
				controller.$setValidity('date', validity);
				return validity ? value : undefined;
			};

			controller.$parsers.push(validator);
		}
	};
});


// This directive can be added to an input field to validate emails using a similar regex to django
djng_forms_module.directive('validateEmail', function() {
	return {
		require: '?ngModel',
		restrict: 'A',
		link: function(scope, elem, attrs, controller) {
			if (controller && controller.$validators.email && attrs.emailPattern) {
				var emailPattern = new RegExp(attrs.emailPattern, 'i');

				// Overwrite the default Angular email validator
				controller.$validators.email = function(value) {
					return controller.$isEmpty(value) || emailPattern.test(value);
				};
			}
		}
	};
});


// If forms are validated using Ajax, the server shall return a dictionary of detected errors to the
// client code. The success-handler of this Ajax call, now can set those error messages on their
// prepared list-items. The simplest way, is to add this code snippet into the controllers function
// which is responsible for submitting form data using Ajax:
//  $http.post("/path/to/url", $scope.data).success(function(data) {
//      djangoForm.setErrors($scope.form, data.errors);
//  });
// djangoForm.setErrors returns false, if no errors have been transferred.
djng_forms_module.factory('djangoForm', function() {
	var NON_FIELD_ERRORS = '__all__';

	function isNotEmpty(obj) {
		for (var p in obj) {
			if (obj.hasOwnProperty(p))
				return true;
		}
		return false;
	}

	function resetFieldValidity(field) {
		var pos = field.$viewChangeListeners.push(field.clearRejected = function() {
			field.$message = '';
			field.$setValidity('rejected', true);
			field.$viewChangeListeners.splice(pos - 1, 1);
			delete field.clearRejected;
		});
	}

	function isField(field) {
		return angular.isArray(field.$viewChangeListeners);
	}

	return {
		// setErrors takes care of updating prepared placeholder fields for displaying form errors
		// detected by an AJAX submission. Returns true if errors have been added to the form.
		setErrors: function(form, errors) {
			// remove errors from this form, which may have been rejected by an earlier validation
			form.$message = '';
			if (form.hasOwnProperty('$error') && angular.isArray(form.$error.rejected)) {
				/*
				 * make copy of rejected before we loop as calling
				 * field.$setValidity('rejected', true) modifies the error array
				 * so only every other one was being removed
				 */
				var rejected = form.$error.rejected.concat();
				angular.forEach(rejected, function(rejected) {
					var field, key = rejected.$name;
					if (form.hasOwnProperty(key)) {
						field = form[key];
						if (isField(field) && field.clearRejected) {
							field.clearRejected();
						} else {
							field.$message = '';
							// this field is a composite of input elements
							angular.forEach(field, function(subField, subKey) {
								if (subField && isField(subField) && subField.clearRejected) {
									subField.clearRejected();
								}
							});
						}
					}
				});
			}
			// add the new upstream errors
			angular.forEach(errors, function(errors, key) {
				var field;
				if (errors.length > 0) {
					if (key === NON_FIELD_ERRORS) {
						form.$message = errors[0];
						form.$setPristine();
					} else if (form.hasOwnProperty(key)) {
						field = form[key];
						field.$message = errors[0];
						field.$setValidity('rejected', false);
						field.$setPristine();
						if (isField(field)) {
							resetFieldValidity(field);
						} else {
							// this field is a composite of input elements
							angular.forEach(field, function(subField, subKey) {
								if (subField && isField(subField)) {
									resetFieldValidity(subField);
								}
							});
						}
					}
				}
			});
			return isNotEmpty(errors);
		}
	};
});


// Directive <ANY djng-bind-if="any_variable"> behaves similar to `ng-bind` but leaves the elements
// content as is, if the value to bind is undefined. This allows to set a default value in case the
// scope variables are not ready yet.
djng_forms_module.directive('djngBindIf', function() {
	return {
		restrict: 'A',
		compile: function(templateElement) {
			templateElement.addClass('ng-binding');
			return function(scope, element, attr) {
				element.data('$binding', attr.ngBind);
				scope.$watch(attr.djngBindIf, function ngBindWatchAction(value) {
					if (value === undefined || value === null)
						return;
					element.text(value);
				});
			};
		}
	};
});


})(window.angular);

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

(function (angular, undefined) {
    'use strict';
    /*
     module: djng.urls
     Provide url reverse resolution functionality for django urls in angular
     Usage: djangoUrl.reverse(url_name, args_or_kwargs)

     Examples:
     - djangoUrl.reverse('home', [user_id: 2]);
     - djangoUrl.reverse('home', [2]);
     */
    var djngUrls = angular.module('djng.urls', []);

    djngUrls.provider('djangoUrl', function djangoUrlProvider() {
            var reverseUrl = '/angular/reverse/';

            this.setReverseUrl = function (url) {
                reverseUrl = url;
            };

            this.$get = function () {
                return new djangoUrl(reverseUrl);
            };
        }
    );

    var djangoUrl = function (reverseUrl) {
        /*
         Url-reversing service
         */

        //Functions from angular.js source, not public available
        //See: https://github.com/angular/angular.js/issues/7429
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
                if (value === null || value === undefined) return;
                if (angular.isObject(value)) {
                    value = angular.toJson(value);
                }
                /*
                 If value is a string and starts with ':' we don't encode the value to enable parametrized urls
                 E.g. with .reverse('article',{id: ':id'} we build a url
                 /angular/reverse/?djng_url_name=article?id=:id, which angular resource can use
                 https://docs.angularjs.org/api/ngResource/service/$resource
                 */
                if ((typeof value === 'string' || value instanceof String) && value.lastIndexOf(':', 0) === 0) {
                    parts.push(encodeURIComponent(key) + '=' + value)
                } else {
                    parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
                }

            });
            return url + ((url.indexOf('?') === -1) ? '?' : '&') + parts.join('&');
        }

        // Service public interface
        this.reverse = function (url_name, args_or_kwargs) {
            var url = buildUrl(reverseUrl, {djng_url_name: url_name});
            /*
             Django wants arrays in query params encoded the following way: a = [1,2,3] -> ?a=1&a=2$a=3
             buildUrl function doesn't natively understand lists in params, so in case of a argument array
             it's called iteratively, adding a single parameter with each call

             url = buildUrl(url, {a:1}) -> returns /url?a=1
             url = buildUrl(url, {a:2}) -> returns /url?a=1&a=2
             ...
             */
            if (Array.isArray(args_or_kwargs)) {
                forEachSorted(args_or_kwargs, function (value) {
                    url = buildUrl(url, {'djng_url_args': value});
                });
                return url;
            }
            /*
             If there's a object of keyword arguments, a 'djng_url_kwarg_' prefix is prepended to each member
             Then we can directly call the buildUrl function
             */
            var params = {};
            forEachSorted(args_or_kwargs, function (value, key) {
                params['djng_url_kwarg_' + key] = value;
            });
            /*
             If params is empty (no kwargs passed) return url immediately
             Calling buildUrl with empty params object adds & or ? at the end of query string
             E.g. buldUrl('/url/djng_url_name=home', {}) -> /url/djng_url_name=home&
             */
            if (angular.equals(params, {})) { // If params is empty, no kwargs passed.
                return url;
            }
            return buildUrl(url, params);
        };
    };

}(window.angular));


(function(angular, undefined) {
'use strict';

function noop() {}

// Add three-way data-binding for AngularJS with Django using websockets.
var djng_ws_module = angular.module('djng.websocket', []);

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
	var $log =  angular.injector(['ng']).get('$log');

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
			_console = $log;
			break;
		case 'log':
			_console.log = $log.log;
			/* falls through */
		case 'warn':
			_console.warn = $log.warn;
			/* falls through */
		case 'error':
			_console.error = $log.error;
			/* falls through */
		default:
			break;
		}
		return this;
	};

	this.$get = ['$websocket', '$q', '$timeout', '$interval', function($websocket, $q, $timeout, $interval) {
		var ws_url, deferred, scope, collection;
		var is_subscriber = false, is_publisher = false, receiving = false;
		var wait_for_reconnect = 0, heartbeat_promise = null, missed_heartbeats = 0;

		function connect() {
			_console.log("Connecting to "+ws_url);
			deferred = $q.defer();
			$websocket.connect(ws_url);
		}

		$websocket.onopen = function(evt) {
			_console.log('Connected');
			deferred.resolve();
			wait_for_reconnect = 0;
			if (heartbeat_msg && heartbeat_promise === null) {
				missed_heartbeats = 0;
				heartbeat_promise = $interval(sendHeartbeat, 5000);
			}
		};

		$websocket.onclose = function(evt) {
			_console.log("Disconnected");
			deferred.reject();
			wait_for_reconnect = Math.min(wait_for_reconnect + 1000, 10000);
			$timeout(function() {
				$websocket.connect(ws_url);
			}, wait_for_reconnect);
		};

		$websocket.onerror = function(evt) {
			_console.error("Websocket connection is broken!");
			$websocket.close();
		};

		$websocket.onmessage = function(evt) {
			var data;
			if (evt.data === heartbeat_msg) {
				// reset the counter for missed heartbeats
				missed_heartbeats = 0;
				return;
			}
			try {
				data = angular.fromJson(evt.data);
			} catch(e) {
				_console.warn('Data received by server is invalid JSON: ' + evt.data);
				return;
			}
			if (is_subscriber) {
				// temporarily disable the function 'listener', so that message received
				// from the websocket, are not propagated back
				receiving = true;
				scope.$apply(function() {
					angular.extend(scope[collection], data);
				});
				receiving = false;
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
			if (!receiving && !angular.equals(oldValue, newValue)) {
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

		function buildWebsocketURL(facility, channels) {
			var parts = [websocket_uri, facility, '?'];
			parts.push(channels.join('&'));
			ws_url = parts.join('');
		}

		return {
			connect: function($scope, scope_obj, facility, channels) {
				scope = $scope;
				setChannels(channels);
				collection = scope_obj;
				scope[collection] = scope[collection] || {};
				buildWebsocketURL(facility, channels);
				connect();
				if (is_publisher) {
					deferred.promise.then(watchCollection);
				}
				return deferred.promise;
			}
		};
	}];
});

})(window.angular);
