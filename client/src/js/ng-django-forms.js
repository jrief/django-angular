(function(angular, undefined) {
'use strict';

// module: ng.django.forms
// Correct Angular's form.FormController behavior after rendering bound forms.
// Additional validators for form elements.
var djng_forms_module = angular.module('ng.django.forms', []);

// create a simple hash code for the given string
function hashCode(s) {
	return s.split("").reduce(function(a, b) {
		a = (a << 5) - a + b.charCodeAt(0);
		return a & a;
	}, 0);
}

// This directive adds a dummy binding to input fields without attribute ng-model, so that AngularJS
// form validation gets notified whenever the fields content changes.
djng_forms_module.directive('input', ['$compile', function($compile) {
	return {
		restrict: 'E',
		require: '?^form',
		link: function(scope, element, attr, formCtrl) {
			var modelName;
			if (!formCtrl || angular.isUndefined(formCtrl.$name) || element.prop('type') === 'hidden' || angular.isUndefined(attr.name) || angular.isDefined(attr.ngModel))
				return;
			modelName = 'dmy' + Math.abs(hashCode(formCtrl.$name)) +'.' + attr.name;
			attr.$set('ngModel', modelName);
			$compile(element, null, 9999)(scope);
		}
	};
}]);

// Bound fields with invalid input data, shall be marked as ng-invalid-bound, so that
// the input field visibly contains invalid data, even if pristine
djng_forms_module.directive('djngError', function() {
	return {
		restrict: 'A',
		require: '?^form',
		link: function(scope, element, attrs, formCtrl) {
			var boundField;
			if (!formCtrl || angular.isUndefined(attrs.name) || attrs.djngError !== 'bound-field')
				return;
			boundField = formCtrl[attrs.name];
			boundField.$setValidity('bound', false);
			boundField.$parsers.push(function(value) {
				// set bound field into valid state after changing value
				boundField.$setValidity('bound', true);
				element.removeAttr('djng-error');
			});
		}
	};
});

// This directive overrides some of the internal behavior on forms if used together with AngularJS.
// Otherwise, the content of bound forms is not displayed, because AngularJS does not know about
// the concept of bound forms and thus hides values preset by Django while rendering HTML.
djng_forms_module.directive('ngModel', function($parse) {
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
		var multivalues = [];
		angular.forEach(field.options, function(option) {
			if (option.defaultSelected) {
				// restore the select option to selected
				angular.element(option).prop('selected', 'selected');
				if (field.multiple) {
					multivalues.push(option.value);
				} else {
					return option.value;
				}
			}
		});
		if (field.multiple) {
			return multivalues;
		}
	}

	function restoreTextArea(field) {
		// restore the field's content from the rendered content of bound fields
		if(field.defaultValue) {
			return field.defaultValue;
		}
	}
	
	function processDefaultValue(scope, ngModelName, value) {
		
		if(!angular.isDefined(value)) {
			return;
		}
		
		var parts = ngModelName.split('.'),
			prop = parts.pop(),
			modelName = parts.join('.'),
			fn = $parse(model !== '' ? model : prop),
			model;
								
		if(modelName !== '') {
				
			fn = $parse(modelName);
			model = fn(scope) || {};
			model[prop] = value;
			fn.assign(scope, model);
				
		}else{
				
			fn = $parse(prop);
			fn.assign(scope, value);
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
			if (!field || !formCtrl)
				return;

			var defaultValue;
				
			switch (field.tagName) {
			case 'INPUT':
				defaultValue = restoreInputField(field);
				break;
			case 'SELECT':
				defaultValue = restoreSelectOptions(field);
				break;
			case 'TEXTAREA':
				defaultValue = restoreTextArea(field);
				break;
			default:
				console.log('Unknown field type');
				break;
			}
			
			processDefaultValue(scope, attrs.ngModel, defaultValue);
		}
	};
});



djng_forms_module.directive('validateMultipleFields', function() {
	return {
		restrict: 'A',
		require: '^?form',
		// create child scope for changed method
		scope: true,
		compile: function(element, attrs) {
			angular.forEach(element.find('input'), function(elem) {
				elem = angular.element(elem)
				elem.attr('ng-change', 'changed()');
			});
			
			return {
				
				post: function(scope, element, attrs, controller) {
					var formCtrl, subFields, checkboxCtrls = [];

					scope.changed = function() {
						validate(true)
					}

					function validate(trigger) {
						var valid = false;
						angular.forEach(checkboxCtrls, function(checkbox) {
							valid = valid || checkbox.$modelValue;
							if(checkbox.clearRejected) {
								checkbox.clearRejected();
							}
						});
						
						formCtrl.$setValidity('required', valid);
						formCtrl.$setValidity('rejected', true);
						formCtrl.$message = ''
						
						if (trigger && angular.isString(subFields)) {
							formCtrl[subFields].$dirty = true;
							formCtrl[subFields].$pristine = false;
						}
					}

					if (!controller)
						return;
					formCtrl = controller;
					try {
						subFields = angular.fromJson(attrs.validateMultipleFields);
					} catch (SyntaxError) {
						subFields = attrs.validateMultipleFields;
					}
					angular.forEach(element.find('input'), function(elem) {
						if (subFields.indexOf(elem.name) >= 0) {
							checkboxCtrls.push(formCtrl[elem.name]);
						}
					});

					validate();
				}
			}
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
				var validity = controller.$isEmpty(value) || validateDate(value);
				controller.$setValidity('date', validity);
				return validity ? value : undefined;
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

	function resetFieldValidity(field) {
		var pos = field.$viewChangeListeners.push(field.clearRejected = function() {
			field.$message = '';
			field.$setValidity('rejected', true);
			field.$viewChangeListeners.splice(pos - 1, 1);
			delete field.clearRejected;
		})
	}
	
	function isField(field) {
		return angular.isArray(field.$viewChangeListeners)
	}

	return {
		// setErrors takes care of updating prepared placeholder fields for displaying form errors
		// deteced by an AJAX submission. Returns true if errors have been added to the form.
		setErrors: function(form, errors) {
			// remove errors from this form, which may have been rejected by an earlier validation
			form.$message = '';
			if (form.$error.hasOwnProperty('rejected') &&
				angular.isArray(form.$error.rejected)) {
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


})(window.angular);
