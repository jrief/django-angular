
angular
	.module('djangular-demo')
	.config(toastrConfiguration)
	.controller('MyFormCtrl', MyFormCtrl);
	
	
/*
 * change styling to bootstrap
 */
function toastrConfiguration(toastrConfig) {

	angular.extend(toastrConfig, {
	    toastClass: 'alert',
	    iconClasses: {
	        error: 'alert-danger',
	        info: 'alert-info',
	        success: 'alert-success',
	        warning: 'alert-warning'
	    }
	});
}


function MyFormCtrl($scope, $http, djangoForm, djngMessagesModel, toastr) {
	
	$scope.submit = function(data, form) {
		$http.post(".", data)
			.success(function(response) {
				djangoForm.setErrors(form, response.errors)
			});
	};
	
	$scope.$watch(function(){
		return djngMessagesModel.count;
	},_handleCountChange);
	
	function _handleCountChange(newValue, oldValue) {
		if(newValue != oldValue && newValue > 0) {
			var messages = djngMessagesModel.getMessages(),
				i = 0,
				len = messages.length,
				message;
			
			for(; i < len; i++) {
				message = messages[i];
				console.log(message);
				toastr[message.type](message.message, message.type.charAt(0).toUpperCase() + message.type.slice(1));
			}
		}
	}
}