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
					var field = response.data['file:0'];
					var cf = element.data('current_file');
					element.removeClass('uploading');
					if (!field)
						return;
					element.css('background-image', field.url);
					element.removeClass('djng-empty');
					element.removeClass('djng-preset');
					element.val(field.file_name);
					delete field.url;  // we don't want to send back the whole image
					angular.extend(scope.$eval(model), field, cf ? {current_file: cf} : {});
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
			scope.deleteImage = function(id, _model) {
				var model = scope.$eval(_model),
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
				require: ['?^form', '?^djngMultifieldsRequired'],
				link: function(scope, element, attr, controllers) {
					var modelName, formCtrl = controllers[0];
					if (!formCtrl || angular.isUndefined(formCtrl.$name) || element.prop('type') === 'hidden' || angular.isUndefined(attr.name) || angular.isDefined(attr.ngModel))
						return;
					modelName = 'dmy' + Math.abs(hashCode(formCtrl.$name)) +'.' + attr.name.replace(/-/g, "_");
					if (controllers[1]) {
						modelName = modelName.concat("['" + attr.value + "']");
					}
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
		var result = field.multiple ? [] : undefined;
		angular.forEach(field.options, function(option) {
			if (option.defaultSelected) {
				// restore the select option to selected
				angular.element(option).prop('selected', 'selected');
				if (field.multiple) {
					result.push(option.value);
				} else {
					result = option.value;
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
		priority: 2,  // make sure this directive is applied after angular built-in one
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


djngModule.controller('FormUploadController', ['$scope', '$http', '$interpolate', '$parse', '$q',
                                       function($scope, $http, $interpolate, $parse, $q) {
	var self = this;

	// a map of booleans keeping the validation state for each of the child forms
	this.endpointValidatedForms = {};

	// dictionary of form names mapping their model scopes
	this.endpointFormsMap = {};

	this.setEndpoint = function(endpointURL, endpointScope) {
		self.endpointURL = $interpolate(decodeURIComponent(endpointURL));
		self.endpointScope = endpointScope;
	};

	this.uploadScope = function(method, urlParams, extraData) {
		var deferred = $q.defer(), data = {}, url, promise;
		if (!self.endpointURL)
			throw new Error("Can not upload form data: Missing endpoint.");

		if (angular.isObject(urlParams)) {
			url = self.endpointURL(urlParams);
		} else {
			url = self.endpointURL();
		}

		if (method === 'GET') {
			// send data from all forms below this endpoint to the server
			promise = $http({
				url: url,
				method: method,
				params: extraData
			});
		} else {
			// merge the data from various scope entities into one data object
			if (angular.isObject(extraData)) {
				angular.merge(data, extraData);
			}
			angular.forEach(self.endpointFormsMap, function(scopeModels) {
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
				url: url,
				method: method,
				data: data
			});
		}
		promise.then(function(response) {
			angular.forEach(self.endpointFormsMap, function(scopeModels, formName) {
				var getter = $parse(formName);
				self.clearErrors(getter($scope));
				if (angular.isObject(getter(response.data))) {
					self.setModels(getter($scope), getter(response.data));
				}
				getter($scope).$setSubmitted();
			});
			deferred.resolve(response);
		}).catch(function(response) {
			if (response.status >= 400 && response.status <= 499) {
				angular.forEach(self.endpointFormsMap, function(scopeModels, formName) {
					self.clearErrors($parse(formName)($scope));
				});
				angular.forEach(self.endpointFormsMap, function(scopeModels, formName) {
					var getter = $parse(formName);
					if (angular.isObject(getter(response.data))) {
						self.setErrors(getter($scope), getter(response.data));
					}
					getter($scope).$setSubmitted();
				});
			}
			deferred.reject(response);
		});

		return deferred.promise;
	};

	// clearErrors removes errors from this form, which may have been rejected by an earlier validation
	this.clearErrors = function(form) {
		form.$message = "";
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
		scope: true,
		link: {
			pre: function(scope, element, attrs, controllers) {
				if (!attrs.name)
					throw new Error("Attribute 'name' is not set for this form!");
				if (!attrs.djngEndpoint)
					throw new Error("Attribute 'djng-endpoint' is not set for this form!");
				controllers[1].setEndpoint(attrs.djngEndpoint, scope);
			},
			post: function(scope, element, attrs, controllers) {
				var formController = controllers[0];

				scope.hasError = function(field) {
					if (angular.isObject(formController[field])) {
						if (formController[field].$pristine && formController[field].$error.rejected)
							return 'has-error';
						if (formController[field].$touched && formController[field].$invalid)
							return 'has-error';
					}
				};

				scope.successMessageIsVisible = function() {
					return formController.$message && !formController.$error.rejected && formController.$submitted;
				};

				scope.rejectMessageIsVisible = function() {
					return formController.$message && formController.$error.rejected && formController.$submitted;
				};

				scope.getSubmitMessage = function() {
					return formController.$message;
				};

				scope.dismissSubmitMessage = function() {
					if (formController.$error.rejected) {
						formController.$setValidity('rejected', true);
					}
					formController.$setPristine();
				};
			}
		}
	};
});


// All directives `ng-model` which are used inside a `<ANY djng-forms-set>...</ANY djng-forms-set>`
// or <form djng-endpoint="...">...</form> must keep track on the scope parts, which later shall be
// uploaded to the server.
djngModule.directive('ngModel', ['djangoForm', function(djangoForm) {
	return {
		restrict: 'A',
		require: ['^?djngFormsSet', '^?form', '^?djngEndpoint'],
		link: function(scope, element, attrs, controllers) {
			var formController = controllers[1], scopePrefix;

			if (!formController)
				return;  // outside of neither <djng-forms-set /> nor <form djng-endpoint="..." />

			scopePrefix = djangoForm.getScopePrefix(attrs.ngModel);
			if (controllers[0]) {
				// inside  <djng-forms-set>...</djng-forms-set>
				addToEndpoint(controllers[0]);
			}
			if (controllers[2]) {
				// inside  <form djng-endpoint="...">...</form>
				addToEndpoint(controllers[2]);
			}

			function addToEndpoint(controller) {
				if (scope.$id !== controller.endpointScope.$id) {
					// detach object scope[scopePrefix] and scope[formController.$name] and move them
					// to controller.endpointScope so that it is still available through prototypical inheritance.
					// This is required in case we use a directive with scope=true.
					if (scope.hasOwnProperty(scopePrefix)) {
						controller.endpointScope[scopePrefix] = scope[scopePrefix];
						delete scope[scopePrefix];
						if (!scope[formController.$name])
							throw new Error("Failed to detach model scope and reappend to its parent.");
					}
					if (scope.hasOwnProperty(formController.$name)) {
						controller.endpointScope[formController.$name] = scope[formController.$name];
						delete scope[formController.$name];
						if (!scope[formController.$name])
							throw new Error("Failed to detach form controller and/or to reappend to its parent.");
					}
				}

				if (!angular.isArray(controller.endpointFormsMap[formController.$name])) {
					controller.endpointFormsMap[formController.$name] = [];
				}
				if (scopePrefix && controller.endpointFormsMap[formController.$name].indexOf(scopePrefix) === -1) {
					controller.endpointFormsMap[formController.$name].push(scopePrefix);
				}
			}

			element.on('change', function() {
				if (formController.$error.rejected) {
					formController.$setValidity('rejected', true);
					formController.$submitted = false;
					scope.$apply();
				}
			});
		}
	};
}]);


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
			var uploadController = controllers[2] || controllers[0], urlParams;

			if (!uploadController)
				return;  // button neither inside <form djng-endpoint="...">...</form> nor inside <djng-forms-set>...</djng-forms-set>

			if (attrs.urlParams) {
				urlParams = scope.$eval(attrs.urlParams);
			}

			// prefix function create/update/delete with: do(...).then(...)
			// to create the initial promise
			scope.do = function(resolve, reject) {
				return $q.resolve().then(resolve, reject);
			};

			scope.fetch = function(extraData) {
				return function() {
					return uploadController.uploadScope('GET', urlParams, extraData);
				};
			};

			scope.create = function(extraData) {
				return function() {
					return uploadController.uploadScope('POST', urlParams, extraData);
				};
			};

			scope.update = function(extraData) {
				return function() {
					return uploadController.uploadScope('PUT', urlParams, extraData);
				};
			};

			scope.delete = function(extraData) {
				return function() {
					return uploadController.uploadScope('DELETE', urlParams, extraData);
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
			scope.showOK = function() {
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

			// Only to be used in a catch clause!
			// Looking at the response error, look for the input field with
			// the rejected content and scroll to this element.
			scope.scrollToRejected = function() {
				return function(response) {
					var form_name, field_name, element;
					if (response.status >= 400 && response.status <= 499) {
						for (form_name in response.data) {
							element = null;
							if (response.data[form_name]['__all__']) {
								element = document.getElementsByName(form_name)[0];
								element = element ? element.getElementsByClassName('djng-line-spreader')[0] : null;
							}
							if (!element) {
								for (field_name in response.data[form_name]) {
									element = document.getElementById('id_' + field_name);
									if (element)
										break;
								}
							}
							if (element) {
								element.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});
								break;
							}
						}
					}
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


// Directive ``<ANY djng-forms-set endpoint="/rest/endpoint" ...>``, the REST endpoint.
// Use this as a wrapper around self validating <form ...> or <ANY ng-form ...> elements (see
// directives above), so that we can use a proceed/submit button outside of the ``<form ...>`` elements.
// Whenever one of those forms does not validate, that button can be rendered as:
// ``<button ng-click="update(some_action)" ng-disabled="isDisabled()">Submit</button>``
djngModule.directive('djngFormsSet', function() {
	return {
		require: 'djngFormsSet',
		controller: 'FormUploadController',
		link: {
			pre: function(scope, element, attrs, uploadController) {
				if (!attrs.endpoint)
					throw new Error("Attribute 'endpoint' is not set!");

				uploadController.setEndpoint(attrs.endpoint, scope);
			}
		}
	};
});


// This directive enriches AngularJS's internal form-controllers if they are wrapped inside a <ANY djng-forms-set ...>
// directive. One purpose is to summarize the validity of the given forms, so that buttons rendered outside of the
// <form ...> elements but inside the <djng-forms-set ...> element can check the validity of all forms.
// Another purpose of this directive is to summarize the scope-models of the given forms, so that the scope can
// be uploaded to the endpoint URL using one submission.
djngModule.directive('form', function() {
	return {
		restrict: 'E',
		require: ['^?djngFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var formsSetController = controllers[0], formController = controllers[1];

			if (!formsSetController)
				return;  // not for forms outside <ANY djng-forms-set></ANY djng-forms-set>

			if (!attrs.name)
				throw new Error("Each <form> embedded inside a <djng-forms-set> must identify itself by name.");

			// check each child form's $valid state and reduce it to one single state `formsSetController.setIsValid`
			scope.$watch(attrs.name + '.$valid', function reduceValidation() {
				formsSetController.endpointValidatedForms[formController.$name] = formController.$valid;
				formsSetController.setIsValid = true;
				angular.forEach(formsSetController.endpointValidatedForms, function(validatedForm) {
					formsSetController.setIsValid = formsSetController.setIsValid && validatedForm;
				});
			});

		}
	};
});


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
                    parts.push(encodeURIComponent(key) + '=' + value);
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

})(window.angular);

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

angular.module('djng', [
	'djng.forms',
	// 'djng.rmi',
	'djng.urls'
]);