
angular
    .module('djangular-demo')
    .controller('MyFormCtrl', MyFormCtrl);


function MyFormCtrl($scope, $http, djangoForm, djngMessagesSignal, toastr) {
	
    $scope.submit = function(data, form) {
        $http.post(".", data)
            .success(function(response) {
                djangoForm.setErrors(form, response.errors)
            });
    };

    djngMessagesSignal.onMessagesUpdated($scope, _messagesUpdated);

    function _messagesUpdated(messages) {
	
        var i = 0,
            len = messages.length,
            message;
		
        for(; i < len; i++) {
            message = messages[i];
            toastr[message.type](message.message, message.type.charAt(0).toUpperCase() + message.type.slice(1));
        }
    }
}