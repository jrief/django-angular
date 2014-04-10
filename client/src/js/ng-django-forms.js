(function(angular, undefined) {
'use strict';

// module: ng.django.forms
// Correct Angular's form.FormController behavior after rendering bound forms.
// Additional validators for form elements.
var djng_forms = angular.module('ng.django.forms', []);

// This directive overrides some of the internal behavior on forms if used together with AngularJS.
// If not used, the content of bound forms is not displayed, because AngularJS does not know about
// the concept of bound forms.
djng_forms.directive('form', function() {
	return {
		restrict: 'E',
		scope: 'isolate',
		priority: -1,
		link: function(scope, element, attrs) {
			var form = scope[attrs.name];
			var fields = angular.element(element).find('input');
			angular.forEach(fields, function(field) {
				if (form[field.name] !== undefined) {
					// restore the field's content from the rendered content of bound fields
					form[field.name].$setViewValue(field.defaultValue);
				}
			});
			// restore the form's pristine state
			form.$setPristine();
		}
	};
});

// This directive can be added to an input field which shall validate inserted dates, for example:
// <input ng-model="a_date" type="text" validate-date="^(\d{4})-(\d{1,2})-(\d{1,2})$" />
// Now, such an input field is only considered valid, if the date is a valid date and if it matches
// against the given regular expression.
djng_forms.directive('validateDate', function() {
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
		require: 'ngModel',
		restrict: 'A',
		link: function(scope, elem, attrs, controller) {
			if (attrs.validateDate) {
				// if a pattern is set, only valid dates with that pattern are accepted
				validDatePattern = new RegExp(attrs.validateDate, 'g');
			}

			// watch for modifications on input fields containing attribute 'validate-date="/pattern/"'
			scope.$watch(attrs.ngModel, function(date) {
				if (controller.$pristine)
					return;
				controller.$setValidity('date', validateDate(date));
			});
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
djng_forms.factory('djangoForm', function() {
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

})(window.angular);
