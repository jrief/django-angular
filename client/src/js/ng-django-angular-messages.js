(function(angular, undefined) {
'use strict';


if(angular.version.minor < 3 ) {
	// throw new Error('The ng.django.angular.messages module requires AngularJS 1.3+');
}


angular.module('ng.django.angular.messages', ['ng.django.forms'])
	.directive('form', formDirectiveFactory())
	.directive('ngForm', formDirectiveFactory(true))
	.directive('djngError', djngError)
	.directive('djngRejected', djngRejected)
	.factory('djngAngularMessagesForm', djngAngularMessagesForm);


/**
 * An extension to form
 * 
 * Adds the following methods and functionality:
 * 
 * - djngSetValidFieldsPristine()
 */

function formDirectiveFactory(isNgForm) {
	return function() {
		return {
			restrict: isNgForm ? 'EAC' : 'E',
			require: 'form',
			link: {
				pre: function(scope, element, attrs, formCtrl) {
					var controls, modelName;
					var _superAdd = formCtrl.$addControl;

					formCtrl.$addControl = function(control) {
						_superAdd(control)
						controls = controls || [];

						if(controls.indexOf(control) === -1) {
							controls.push(control);
						}
					}

					var _superRemove = formCtrl.$removeControl;

					formCtrl.$removeControl = function(control) {
						_superRemove(control)

						if(controls && controls.indexOf(control) !== -1) {
							controls.splice(controls.indexOf(control), 1);
						}
					}

					formCtrl.djngSetValidFieldsPristine = function() {
						var i = 0, len = controls.length, control;

						for (; i < len; i++) {
							control = controls[i];
							if(control.$valid) {
								control.$setPristine();
							}
						}
					}
				}
		 	}
		}
	}
}


function djngError($timeout) {
	return {
		restrict: 'A',
		require: [
			'?^form',
			'?ngModel'
		],
		link: function(scope, element, attrs, ctrls) {
			
			var formCtrl = ctrls[0],
				ngModel = ctrls[1];
			
			if (attrs.djngError !== 'bound-msgs-field' || !formCtrl || !ngModel)
				return;

			element.removeAttr('djng-error');
			element.removeAttr('djng-error-msg');

			$timeout(function() {
				// TODO: use ngModel.djngAddRejected to set message

				ngModel.$message = attrs.djngErrorMsg;
				ngModel.$validate();
				formCtrl.$setSubmitted();
			});
		}
	}
}


function djngRejected() {
	return {
		restrict: 'A',
		require: '?ngModel',
		link: function(scope, element, attrs, ngModel) {
			if (!ngModel || attrs.djngRejected !== 'validator')
				return;

			var _hasMessage = false, _value = null;
			
			ngModel.$validators.rejected = function(value) {
				if (_hasMessage && (_value !== value)) {
					_hasMessage = false;
					_value = null;
					ngModel.$message = undefined;
				} else {
					_hasMessage = !!ngModel.$message;

					if (_hasMessage)
						_value = value;	
				}
				return !_hasMessage;
			}

		}
	}
}


function djngAngularMessagesForm() {
	var NON_FIELD_ERRORS = '__all__';

	return {
		setErrors: setErrors
	}

	function setErrors(form, errors) {
		_clearFormMessage(form);
		_displayErrors(form, errors);
		return _isNotEmpty(errors);
	};

	function _clearFormMessage(form) {
		form.$message = undefined;
	};

	function _displayErrors(form, errors) {
		form.$setSubmitted();
		
		angular.forEach(errors, function(error, key) {
			var field, message = error[0];

			if (key == NON_FIELD_ERRORS) {
				form.$message = message;
				/*
				 * Only set current valid fields to pristine
				 *
				 * Any field that's been submitted with an error should
				 * still display its error
				 *
				 * Any field that was valid when the form was submitted,
				 * may have caused the NON_FIELD_ERRORS, so should be set
				 * to pristine to prevent it's valid state being displayed
				 */
				form.djngSetValidFieldsPristine();
			} else if (form.hasOwnProperty(key)) {
				field = form[key];
				field.$message = message;
				if (isField(field)) {
					field.$validate();
				} else {
					// this field is a composite of input elements
					field.$setSubmitted();

					angular.forEach(field, function(subField, subKey) {
						if (isField(subField)) {
							subField.$validate();
						}
					});
				}
			}
		});
	}
	
	function isField(field) {
		return !!field && angular.isArray(field.$viewChangeListeners);
	}

	function _isNotEmpty(obj) {
		for (var p in obj) { 
			if (obj.hasOwnProperty(p))
				return true;
		}
		return false;
	}
};


})(window.angular);
