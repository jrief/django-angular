angular.module('djangular-demo').controller('MyFormCtrl', ['$scope', '$http', '$window', 'djangoForm',
                                            function($scope, $http, $window, djangoForm) {
	$scope.submit = function() {
		if ($scope.subscribe_data) {
			$http.post(".", $scope.subscribe_data).then(function(response) {
				// on successful post, redirect onto success page
				$window.location.href = response.data.success_url;
			}).catch(function(response) {
				// on form validation error, populate the fields with their messages
				djangoForm.clearErrors($scope.my_form);
				djangoForm.setErrors($scope.my_form, response.data.my_form.errors);
			}).finally(function(response) {
				djangoForm.setModels($scope.my_form, response.data.my_form.models);
			});
		}
		return false;
	};
}]);
