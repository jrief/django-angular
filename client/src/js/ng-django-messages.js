(function(angular, undefined) {
'use strict';

angular
    .module('ng.django.messages',[
        'ngMessages'
    ])

    .directive('validateRejected', validateRejected)
    .factory('djangoMessagesForm', djangoMessagesForm);




function validateRejected() {

	return {
		require: 'ngModel',
		link: function($scope, $element, $attrs, ngModel) {

			var _hasMessage = false,
				_value;

			ngModel.$validators.rejected = function(value) {

				if(_hasMessage && (_value && _value !== value)) {
					
					_hasMessage = false;
					_value = undefined;
					ngModel.$message = undefined;
					
				}else{
					
					_hasMessage = ngModel.$message !== undefined;
					if(_hasMessage) {
					    _value = value;	
					}
				}

				return !_hasMessage;
			}
		}
	}
}


function djangoMessagesForm() {
	
	return {
		setErrors: setErrors
	}
	
	/* ============================ */
	
	function setErrors(form, errors) {
		_clearFormMessage(form);
		_displayErrors(form, errors);
		return _isNotEmpty(errors);
	};
	
	function _clearFormMessage(form) {
		form.$message = '';
	};
	
	function _displayErrors(form, errors) {
		angular.forEach(errors,
			function(error, key) {
				var field,
					message = error[0];
				
				form.$setDirty();
				
				if(form.hasOwnProperty(key)) {
					
					field = form[key];
					field.$dirty = true;
					field.$message = message;

					if (angular.isFunction(field.$validate)) {
						field.$validate();
					} else {
						// this field is a composite of input elements
						angular.forEach(field, function(subField, subKey) {
							if (angular.isDefined(subField) &&
								angular.isFunction(subField.$validate)) {
								subField.$validate();
							}
						});
					}
			
				}else{
					
					form.$message = message;
					form.$setPristine();
				}
			}
		);
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
