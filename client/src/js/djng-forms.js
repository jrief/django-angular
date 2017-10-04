(function(angular, undefined) {
'use strict';

// module: djng.forms
// Correct Angular's form.FormController behavior after rendering bound forms.
// Additional validators for form elements.
var djngModule = angular.module('djng.forms', []);


// create a simple hash code for the given string
function hashCode(s) {
	return s.split("").reduce(function(a, b) {
		a = (a << 5) - a + b.charCodeAt(0);
		return a & a;
	}, 0);
}

// These directives adds a dummy binding to form elements without ng-model attribute,
// so that AngularJS form validation gets notified whenever the fields content changes
// http://www.w3schools.com/html/html_form_elements.asp
angular.forEach(['input', 'select', 'textarea', 'datalist'], function(element) {
	djngModule.directive(element, (function() {
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
	})());
});


// Bound fields with invalid input data, shall be marked as ng-invalid-bound, so that
// the input field visibly contains invalid data, even if pristine
djngModule.directive('djngError', function() {
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
djngModule.directive('ngModel', ['$log', function($log) {
	function restoreInputField(field) {
		// restore the field's content from the rendered content of bound fields
		switch (field.type) {
		case 'radio':
			if (field.defaultChecked)
				return field.defaultValue;
			break;
		case 'checkbox':
			if (field.defaultChecked)
				return true;
			break;
		case 'password':
			// after an (un)successful submission, reset the password field
			return null;
		default:
			if (field.defaultValue)
				return field.defaultValue;
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
		if (angular.isDefined(value)) {
			modelCtrl.$setViewValue(value);
			if (angular.isObject(modelCtrl.$options)) {
				modelCtrl.$commitViewValue();
			}
		}
	}

	return {
		restrict: 'A',
		// make sure this directive is applied after angular built-in one
		priority: 2,
		require: ['ngModel', '^?form', '^?djngMultifieldsRequired'],
		link: function(scope, element, attrs, controllers) {
			var field = angular.isElement(element) ? element[0] : null;
			var modelCtrl = controllers[0], formCtrl = controllers[1], multifieldsCtrl = controllers[2];
			var curModelValue = scope.$eval(attrs.ngModel);

			// if model already has a value defined, don't set the default
			if (!field || !formCtrl || angular.isDefined(curModelValue))
				return;

			switch (field.tagName) {
			case 'INPUT':
				setDefaultValue(modelCtrl, restoreInputField(field));
				if (multifieldsCtrl) {
					// if field is wrapped inside a sub-form, add custom validation
					multifieldsCtrl.subFields.push(modelCtrl);
					modelCtrl.$validators.multifield = multifieldsCtrl.validate;
				}
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


// Directive <ANY djng-multifields-required="true|false"> is added automatically by django-angular for widgets
// of type CheckboxSelectMultiple. This is necessary to adjust the behavior of a collection of input fields,
// which forms a group for one `django.forms.Field`.
djngModule.directive('djngMultifieldsRequired', function() {
	return {
		restrict: 'A',
		require: 'djngMultifieldsRequired',
		controller: ['$scope', function($scope) {
			var self = this;
			this.subFields = [];

			this.validate = function() {
				var validated = !self.anyFieldRequired;
				angular.forEach(self.subFields, function(subField) {
					validated = validated || subField.$viewValue;
				});
				if (validated) {
					// if at least one checkbox was selected, validate all of them
					angular.forEach(self.subFields, function(subField) {
						subField.$setValidity('multifield', true);
					});
				}
				return validated;
			};
		}],
		link: function(scope, element, attrs, controller) {
			controller.anyFieldRequired = scope.$eval(attrs.djngMultifieldsRequired);
		}
	};
});


// This directive can be added to an input field which shall validate inserted dates, for example:
// <input ng-model="a_date" type="text" validate-date="^(\d{4})-(\d{1,2})-(\d{1,2})$" />
// Now, such an input field is only considered valid, if the date is a valid date and if it matches
// against the given regular expression.
djngModule.directive('validateDate', function() {
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
djngModule.directive('validateEmail', function() {
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


djngModule.controller('FormUploadController', ['$scope', '$http', '$q', function($scope, $http, $q) {
	var self = this;

	// a map of booleans keeping the validation state for each of the child forms
	this.digestValidatedForms = {};

	// dictionary of form names mapping their model scopes
	this.digestUploadScope = {};

	this.uploadScope = function(method, extraData) {
		var deferred = $q.defer(), data = {}, promise;
		if (!self.endpointURL)
			throw new Error("Can not upload form data: Missing endpoint.");

		if (method === 'GET') {
			// send data from all forms below this endpoint to the server
			promise = $http({
				url: self.endpointURL,
				method: method,
				params: extraData
			});
		} else {
			// merge the data from various scope entities into one data object
			if (angular.isObject(extraData)) {
				angular.merge(data, extraData);
			}
			angular.forEach(self.digestUploadScope, function(scopeModels) {
				var modelScopeData = {};
				angular.forEach(scopeModels, function(scopeModel) {
					var values = $scope.$eval(scopeModel);
					if (values) {
						modelScopeData[scopeModel] = values;
						angular.merge(data, modelScopeData);
					}
				});
			});

			// submit data from all forms below this endpoint to the server
			promise = $http({
				url: self.endpointURL,
				method: method,
				data: data
			});
		}
		promise.then(function(response) {
			angular.forEach(self.digestUploadScope, function(scopeModels, formName) {
				self.clearErrors($scope[formName]);
				if (angular.isObject(response.data[formName])) {
					self.setModels($scope[formName], response.data[formName]);
				}
			});
			deferred.resolve(response);
		}).catch(function(response) {
			if (response.status >= 400 && response.status <= 499) {
				angular.forEach(self.digestUploadScope, function(scopeModels, formName) {
					self.clearErrors($scope[formName]);
				});
				angular.forEach(self.digestUploadScope, function(scopeModels, formName) {
					if (angular.isObject(response.data[formName])) {
						self.setErrors($scope[formName], response.data[formName]);
					}
					$scope[formName].$setSubmitted();
				});
			}
			deferred.reject(response);
		});

		return deferred.promise;
	};

	// clearErrors removes errors from this form, which may have been rejected by an earlier validation
	this.clearErrors = function(form) {
		form.$message = '';
		if (form.hasOwnProperty('$error') && angular.isArray(form.$error.rejected)) {
			// make copy of form.$error.rejected before we loop as calling
			// field.$setValidity('rejected', true) modifies the error array so only every
			// other one was being removed
			angular.forEach(form.$error.rejected.concat(), function(rejected) {
				var field, key = rejected ? rejected.$name : null;
				if (form.hasOwnProperty(key)) {
					field = form[key];
					if (isField(field) && angular.isFunction(field.clearRejected)) {
						field.clearRejected();
					} else if (isForm(field)) {
						// this field acts as form and is a composite of input elements
						field.$setValidity('rejected', true);
						angular.forEach(field, function(subField, subKey) {
							if (isField(subField) && subField.clearRejected) {
								subField.clearRejected();
							}
						});
					}
				}
			});
		}
	};

	// setErrors takes care of updating prepared placeholder fields for displaying form errors
	// detected by an AJAX submission. Returns true if errors have been added to the form.
	this.setErrors = function(form, errors) {
		var NON_FIELD_ERRORS = '__all__';

		function resetFieldValidity(field) {
			var pos = field.$viewChangeListeners.push(field.clearRejected = function() {
				field.$message = "";
				field.$setValidity('rejected', true);
				field.$viewChangeListeners.splice(pos - 1, 1);
				delete field.clearRejected;
			});
		}

		// add the new upstream errors
		angular.forEach(errors, function(errors, key) {
			var field;
			if (errors.length > 0) {
				if (key === NON_FIELD_ERRORS || key === 'non_field_errors') {
					form.$message = errors[0];
					form.$setPristine();
					form.$setValidity('rejected', false);
				} else if (form.hasOwnProperty(key)) {
					field = form[key];
					field.$message = errors[0];
					field.$setValidity('rejected', false);
					field.$setPristine();
					if (isField(field)) {
						resetFieldValidity(field);
					} else /* TODO: if isForm(field) */ {
						// this field is a composite of input elements
						angular.forEach(field, function(subField, subKey) {
							if (isField(subField)) {
								resetFieldValidity(subField);
							}
						});
					}
				}
			}
		});
	};

	// setModels takes care of updating the models of the given form. This can be used to update the forms
	// content with data send by the server.
	this.setModels = function(formCtrl, models) {
		if (models.success_message) {
			formCtrl.$message = models.success_message;
		}
		angular.forEach(models, function(value, key) {
			var fieldCtrl = formCtrl[key];
			if (isField(fieldCtrl)) {
				fieldCtrl.$setViewValue(value, 'updateOn');
				if (angular.isObject(fieldCtrl.$options)) {
					fieldCtrl.$commitViewValue();
				}
				fieldCtrl.$render();
				fieldCtrl.$validate();
				fieldCtrl.$setUntouched();
				fieldCtrl.$setPristine();
			} else if (isForm(fieldCtrl)) {
				// this field is a composite of checkbox input elements
				angular.forEach(fieldCtrl, function(subField, subKey) {
					var leaf;
					if (isField(subField)) {
						leaf = subField.$name.replace(fieldCtrl.$name + '.', '');
						if (value.indexOf(leaf) === -1) {
							leaf = null;
						}
						subField.$setViewValue(leaf, 'updateOn');
						if (angular.isObject(subField.$options)) {
							subField.$commitViewValue();
						}
						subField.$render();
						subField.$validate();
						subField.$setUntouched();
					}
				});
				fieldCtrl.$setPristine();
			}
		});
	};

	// use duck-typing to determine if field is a FieldController
	function isField(field) {
		return field && angular.isArray(field.$viewChangeListeners);
	}

	function isForm(form) {
		return form && form.constructor.name === 'FormController';
	}

}]);


djngModule.directive('djngEndpoint', function() {
	return {
		require: ['form', 'djngEndpoint'],
		restrict: 'A',
		controller: 'FormUploadController',
		link: function(scope, element, attrs, controllers) {
			var formController = controllers[0];
			if (!attrs.name)
				throw new Error("Attribute 'name' is not set for this form!");
			if (!attrs.djngEndpoint)
				throw new Error("Attribute 'djng-endpoint' is not set for this form!");
			controllers[1].endpointURL = attrs.djngEndpoint;

			scope.hasError = function(field) {
				if (angular.isObject(formController[field])) {
					if (formController[field].$pristine && formController[field].$error.rejected)
						return 'has-error';
					if (formController[field].$touched && formController[field].$invalid)
						return 'has-error';
				}
			};

			scope.successMessageVisible = function() {
				return !formController.$error.rejected && formController.$submitted;
			};

			scope.rejectMessageVisible = function() {
				return formController.$error.rejected && formController.$submitted;
			};

			scope.getSubmitMessage = function() {
				return formController.$message;
			};

			scope.dismissSubmitMessage = function() {
				if (formController.$error.rejected) {
					formController.$setValidity('rejected', true);
					formController.$setPristine();
					return true;
				}
			};

			// resets the form into pristine state, after a successful submission
			element.on('focusin', function() {
				if (scope.dismissSubmitMessage()) {
					scope.$apply();
				}
			});
		}
	};
});


// All directives `ng-model` which are used inside  `<ANY djng-forms-set>...</ANY djng-forms-set>`,
// must keep track on the scope parts, which later shall be uploaded to the server.
djngModule.directive('ngModel', ['djangoForm', function(djangoForm) {
	return {
		restrict: 'A',
		require: ['^?djngFormsSet', '^?form', '^?djngEndpoint'],
		link: function(scope, element, attrs, controllers) {
			var formController = controllers[1], digestUploadScope, scopePrefix;

			if (!formController)
				return;  // outside of neither <djng-forms-set /> nor <form djng-endpoint="..." />

			scopePrefix = djangoForm.getScopePrefix(attrs.ngModel);
			if (controllers[0]) {
				// inside  <djng-forms-set>...</djng-forms-set>
				digestUploadScope(controllers[0]);
			}
			if (controllers[2]) {
				// inside  <form djng-endpoint="...">...</form>
				digestUploadScope(controllers[2]);
			}

			function digestUploadScope(controller) {
				if (!angular.isArray(controller.digestUploadScope[formController.$name])) {
					controller.digestUploadScope[formController.$name] = [];
				}
				if (scopePrefix && controller.digestUploadScope[formController.$name].indexOf(scopePrefix) === -1) {
					controller.digestUploadScope[formController.$name].push(scopePrefix);
				}
			}
		}
	};
}]);


// If forms are validated using Ajax, the server shall return a dictionary of detected errors to the
// client code. The success-handler of this Ajax call, now can set those error messages on their
// prepared list-items. The simplest way, is to add this code snippet into the controllers function
// which is responsible for submitting form data using Ajax:
djngModule.factory('djangoForm', ['$parse', function($parse) {
	return {
		getScopePrefix: function(modelName) {
			var context = {}, result;
			$parse(modelName).assign(context, true);
			angular.forEach(context, function(val, key) {
				result = key;
			});
			return result;
		}
	};
}]);


// This directive enriches the button element with a set of actions chainable through promises.
// It adds three functions to its scope ``create``, ``update`` and ``delete`` which shall be used to invoke a POST,
// PUT or DELETE request on the forms-set endpoint URL.
// Optionally one can pass an object to create, update or delete, in order to pass further information
// to the given endpoint.
djngModule.directive('button', ['$q', '$timeout', '$window', function($q, $timeout, $window) {
	return {
		restrict: 'E',
		require: ['^?djngFormsSet', '^?form', '^?djngEndpoint'],
		scope: true,
		link: function(scope, element, attrs, controllers) {
			var uploadController = controllers[2] || controllers[0];

			if (!uploadController)
				return;  // button neither inside <form djng-endpoint="...">...</form> nor inside <djng-forms-set>...</djng-forms-set>

			// prefix function create/update/delete with: do(...).then(...)
			// to create the initial promise
			scope.do = function(resolve, reject) {
				return $q.resolve().then(resolve, reject);
			};

			scope.fetch = function(extraData) {
				return function() {
					return uploadController.uploadScope('GET', extraData);
				};
			};

			scope.create = function(extraData) {
				return function() {
					return uploadController.uploadScope('POST', extraData);
				};
			};

			scope.update = function(extraData) {
				return function() {
					return uploadController.uploadScope('PUT', extraData);
				};
			};

			scope.delete = function(extraData) {
				return function() {
					return uploadController.uploadScope('DELETE', extraData);
				};
			};

			// Disable the button for further submission. Reenable it using the
			// restore() function. Usage:
			// <button ng-click="do(disable()).then(update()).then(...).finally(restore())">
			scope.disable = function() {
				return function(response) {
					scope.disabled = true;
					return $q.resolve(response);
				};
			};

			scope.isDisabled = function() {
				if (controllers[1])
					return controllers[1].$invalid || scope.disabled;
				if (controllers[0])
					return !controllers[0].setIsValid || scope.disabled;
			};

			// Some actions require a lot of time. This function disables the button and
			// replaces existing icons against a spinning wheel. Remove the spinner and
			// reenable it using the restore() function. Usage:
			// <button ng-click="do(spinner()).then(update()).then(...).finally(restore())">
			scope.spinner = function() {
				return function(response) {
					scope.disabled = true;
					angular.forEach(element.find('i'), function(icon) {
						icon = angular.element(icon);
						if (!icon.data('remember-class')) {
							icon.data('remember-class', icon.attr('class'));
						}
						icon.attr('class', 'glyphicon glyphicon-refresh djng-rotate-animate');
					});
					return $q.resolve(response);
				};
			};

			// Replace the existing icon symbol against an OK tick. Restore the previous
			// symbol using the restore() function.
			scope.showOk = function() {
				return function(response) {
					angular.forEach(element.find('i'), function(icon) {
						icon = angular.element(icon);
						if (!icon.data('remember-class')) {
							icon.data('remember-class', icon.attr('class'));
						}
						icon.attr('class', 'glyphicon glyphicon-ok');
					});
					return $q.resolve(response);
				};
			};

			// Replace the existing icon symbol against an fail symbol. Restore the previous
			// symbol using the restore() function.
			scope.showFail = function() {
				return function(response) {
					angular.forEach(element.find('i'), function(icon) {
						icon = angular.element(icon);
						if (!icon.data('remember-class')) {
							icon.data('remember-class', icon.attr('class'));
						}
						icon.attr('class', 'glyphicon glyphicon-remove');
					});
					return $q.resolve(response);
				};
			};

			// Remove any classes previously previously added to the buttons's icon.
			scope.restore = function() {
				return function(response) {
					scope.disabled = false;
					angular.forEach(element.find('i'), function(icon) {
						icon = angular.element(icon);
						if (icon.data('remember-class')) {
							icon.attr('class', icon.data('remember-class'));
							icon.removeData('remember-class');
						}
					});
					return $q.resolve(response);
				};
			};

			scope.emit = function(name, args) {
				return function(response) {
					scope.$emit(name, args);
					return $q.resolve(response);
				};
			};

			scope.reloadPage = function() {
				return function(response) {
					$window.location.reload();
				};
			};

			scope.redirectTo = function(url) {
				return function(response) {
					if (angular.isDefined(response.data.success_url)) {
						$window.location.assign(response.data.success_url);
					} else {
						$window.location.assign(url);
					}
				};
			};

			// add an artificial delay in milliseconds before proceeding
			scope.delay = function(ms) {
				return function(response) {
					return $q(function(resolve) {
						scope.timer = $timeout(function() {
							scope.timer = null;
							resolve(response);
						}, ms);
					});
				};
			};

			scope.$on('$destroy', function() {
				if (scope.timer) {
					$timeout.cancel(scope.timer);
				}
			});

		}
	};
}]);


// Directive <ANY djng-bind-if="any_variable"> behaves similar to `ng-bind` but leaves the elements
// content as is, if the value to bind is undefined. This allows to set a default value in case the
// scope variables are not ready yet.
djngModule.directive('djngBindIf', function() {
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
