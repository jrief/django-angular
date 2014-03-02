
(function(angular, undefined) {
'use strict';

angular.module('djangular-demo', ['ngResource', 'ng.django.websocket'])
.config(function($httpProvider, djangoWebsocketProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	djangoWebsocketProvider.prefix('/ws');
	djangoWebsocketProvider.debug(false);
})
.factory('SimpleModel', function ($resource) {
    return $resource('/crud/simplemodel', {'pk': '@pk'}, {});
})
.directive('serverValidated', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ctrl) {
            ctrl.$viewChangeListeners.push(function() {
                if (ctrl.$error.serverResponse) {
                    ctrl.$setValidity('serverResponse', true);
                }
            });
        }
    }
})
.controller('MyFormController', function($scope, djangoWebsocket) {
	djangoWebsocket.connect($scope, ['subscribe-broadcast', 'publish-broadcast'], 'subscribe_data');
})
.controller('SimpleFormController', function($scope, SimpleModel) {
    $scope.subscribe_data = new SimpleModel();
    $scope.serverResponse = {};
    $scope.submit = function() {
        $scope.subscribe_data.$save(
            function(out_data) {
                // Success.
                $scope.submit_result = "Submit succeeded!";
            },
            function(out_data) {
                // Failure.
                $scope.submit_result = "Submit failed - server responded: " + out_data.data.message;
                $scope.serverResponse = {};
                angular.forEach(out_data.data.detail, function(messages, field) {
                    $scope.simple_form[field].$setValidity('serverResponse', false);
                    $scope.serverResponse[field] = messages.join('\n');
                });
            }
        );
    }
});

})(window.angular);
