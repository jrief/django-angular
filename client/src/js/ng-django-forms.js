(function(angular, undefined) {
'use strict';

// module: ng.django.forms
// Correct Angular's form.FormController behavior after rendering bound forms.
// Additional validators for form elements.
var djng_forms_module = angular.module('ng.django.forms', []);

// This directive overrides some of the internal behavior on forms if used together with AngularJS.
// If not used, the content of bound forms is not displayed, because AngularJS does not know about
// the concept of bound forms.
// TODO: Find out, if the form was bound or unbound. This can be done looking at the fields values
// or by adding a special value to each field. If forms are unbound, use that information to send
// data via PUT rather than POST, since this is how new objects shall be created. An alternative
// would be to create a directive djng-bound-form, which shall be added to a form, whenever it is
// bound. This can easily be done from django.
djng_forms_module.directive('form', function() {
	function restoreInputFields(form, fields) {
		angular.forEach(fields, function(field) {
			var model_field = form[field.name];
			if (model_field !== undefined) {
				// restore the field's content from the rendered content of bound fields
				switch (field.type) {
				case 'text': case 'email': case 'number': case 'url':
					model_field.$setViewValue(field.defaultValue);
					break;
				case 'radio':
					if (field.defaultChecked) {
						model_field.$setViewValue(field.defaultValue);
					}
					break;
				case 'checkbox':
					if (field.defaultChecked) {
						model_field.$setViewValue(true);
					}
					break;
				case 'password':
					// after an (un)successful submission, reset the password field
					model_field.$setViewValue(null);
					break;
				}
			}
		});
	}

	function restoreSelectOptions(form, selects) {
		angular.forEach(selects, function(field) {
			var multivalues = [];
			if (form[field.name] !== undefined) {
				angular.forEach(field.options, function(option) {
					if (option.defaultSelected) {
						// restore the select option to selected
						angular.element(option).prop('selected', 'selected');
						if (field.multiple) {
							multivalues.push(option.value);
						} else {
							form[field.name].$setViewValue(option.value);
						}
					}
				});
				if (field.multiple) {
					form[field.name].$setViewValue(multivalues);
				}
			}
		});
	}

	function restoreTextAreas(form, textareas) {
		angular.forEach(textareas, function(field) {
			if (form[field.name] !== undefined && field.defaultValue) {
				// restore the field's content from the rendered content of bound fields
				form[field.name].$setViewValue(field.defaultValue);
			}
		});
	}

	return {
		restrict: 'E',
		scope: 'isolate',
		priority: -1,
		link: function(scope, element, attrs) {
			var form = scope[attrs.name], ngelem = angular.element(element);
			restoreInputFields(form, ngelem.find('input'));
			restoreSelectOptions(form, ngelem.find('select'));
			restoreTextAreas(form, ngelem.find('textarea'));
			// restore the form's pristine state
			form.$setPristine();
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
			return matched && parseInt(matched[2]) === dateobj.getMonth() + 1;
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
				if (controller.$isEmpty(value)) {
					controller.$setValidity('date', true);
				} else {
					controller.$setValidity('date', validateDate(value));
				}
			};

			controller.$parsers.push(validator);
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

	return {
		// setErrors takes care of updating prepared placeholder fields for displaying form errors
		// deteced by an AJAX submission. Returns true if errors have been added to the form.
		setErrors: function(form, errors) {
			// remove errors from this form, which may have been rejected by an earlier validation
			form.$message = '';
			if (form.$error.hasOwnProperty('rejected')) {
				angular.forEach(form.$error.rejected, function(rejected) {
					var field, key = rejected.$name;
					if (form.hasOwnProperty(key)) {
						field = form[key];
						field.$message = '';
						field.$setValidity('rejected', true);
						if (field.rejectedListenerPos !== undefined) {
							field.$viewChangeListeners.splice(field.rejectedListenerPos, 1);
							delete field.rejectedListenerPos;
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
						field.rejectedListenerPos = field.$viewChangeListeners.push(function() {
							// changing the field the server complained about, resets the form into valid state
							field.$setValidity('rejected', true);
							field.$viewChangeListeners.splice(field.rejectedListenerPos, 1);
							delete field.rejectedListenerPos;
						}) - 1;
					}
				}
			});
			return isNotEmpty(errors);
		}
	};
});


// A simple wrapper to extend the $httpProvider for executing remote methods on the server side
// for Django Views derived from JSONResponseMixin.
// It can be used to invoke GET and POST request. The return value is the same promise as returned
// by $http.get() and $http.post().
// Usage:
// djangoRMI.name.method(data).success(...).error(...)
// @param data (optional): If set and @allowd_action was auto, then the call is performed as method
//     POST. If data is unset, method GET is used. data must be a valid JavaScript object or undefined.
djng_forms_module.provider('djangoRMI', function() {
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
