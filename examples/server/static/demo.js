
(function(angular, undefined) {
'use strict';

angular.module('djangular-demo', ['ng.django.websocket'])
.config(function(djangoWebsocketProvider) {
	djangoWebsocketProvider.prefix('/ws');
})
.controller('MyFormController', function($scope, djangoWebsocket) {
	console.log(djangoWebsocket); console.log($scope); console.log($scope.subscribe_form);
	djangoWebsocket.connect($scope, ['subscribe-broadcast']).then(function() {
		$scope.$watchCollection('subscribe_data', djangoWebsocket.watcher);
	});
});

})(window.angular);
