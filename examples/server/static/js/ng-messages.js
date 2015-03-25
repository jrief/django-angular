angular.module('djangular-demo').controller('MyFormCtrl', function($scope, $http, $window, djngAngularMessagesForm) {
    $scope.submit = function() {
        if ($scope.subscribe_data) {
            $http.post(".", $scope.subscribe_data).success(function(out_data) {
                if (!djngAngularMessagesForm.setErrors($scope.my_form, out_data.errors)) {
                    // on successful post, redirect onto success page
                    $window.location.href = out_data.success_url;
                }
            }).error(function() {
                console.error('An error occured during submission');
            });
        }
        return false;
    };
});
