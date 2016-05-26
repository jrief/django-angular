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
djng_forms_module.directive('ngModel', ['$log', function ($log) {
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
				$log.log('Unknown field type');
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
