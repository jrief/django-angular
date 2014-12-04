(function(angular, undefined) {
'use strict';

angular
    .module('ng.django.messages',[
        'ngMessages'
    ])

    .directive('form', formExtension)
    .directive('validateRejected', validateRejected)
    .factory('djangoMessagesForm', djangoMessagesForm);




/**
 * An extension to form
 * 
 * Adds the following methods and functionality:
 * 
 * - setValidFieldsPristine()
 */
function formExtension() {

	return {
		restrict: 'E',
		require: [
		    '^?form'
		],
		link: {
			pre: function($scope, $element, $attrs, ctrls) {

	  		    var ctrl = ctrls[0],
	  		    	controls,
	  		    	modelName;

	  		    var _superAdd = ctrl.$addControl;

	  		    ctrl.$addControl = function(control) {

	  		    	_superAdd(control)

	  		    	controls = controls || [];

	  		    	if(controls.indexOf(control) === -1) {
	  		    		controls.push(control);
	  		    	}
	  		    }

		  		var _superRemove = ctrl.$removeControl;

		  	    ctrl.$removeControl = function(control) {

		  	    	_superRemove(control)

			    	if(controls && controls.indexOf(control) !== -1) {
	  		    		controls.splice(controls.indexOf(control), 1);
	  		    	}
	  		    }

	  		    ctrl.setValidFieldsPristine = function() {

	    			var i = 0,
		    		  	len = controls.length,
		  				control;

		  			for(; i < len; i++) {
		  				control = controls[i];
		  				if(control.$valid) {
		  					control.$setPristine();
		  				}
		  			}
		  		}
		   	}
	 	}
	}
};


function validateRejected() {

	return {
		require: 'ngModel',
		link: function($scope, $element, $attrs, ngModel) {

			var _hasMessage = false,
				_value = null;

			ngModel.$validators.rejected = function(value) {
                
				if(_hasMessage && (_value !== value)) {
					
					_hasMessage = false;
					_value = null;
					ngModel.$message.rejected = undefined;
					
				}else{
					
					_hasMessage = ngModel.$message.rejected !== undefined;
					
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
		
		form.$setSubmitted();
		
		angular.forEach(errors,
			function(error, key) {
				var field,
					message = error[0];
				
				if(form.hasOwnProperty(key)) {
					
					field = form[key];
					
					if(!angular.isObject(field.$message)) {
						field.$message = {};
					}
					
					field.$message.rejected = message;
					
					if (angular.isFunction(field.$validate)) {

						field.$validate();
						
					} else {
						// this field is a composite of input elements
						field.$setSubmitted();
						
						angular.forEach(field, function(subField, subKey) {
							if(angular.isDefined(subField) &&
							   angular.isFunction(subField.$validate)) {	
								subField.$validate();
							}
						});
					}
			
				}else{
					
					form.$message = message;
					form.setValidFieldsPristine();
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
