
(function(angular, undefined) {
'use strict';

angular.module('djangular-demo', ['ng.django.websocket'])
.config(function(djangoWebsocketProvider) {
	djangoWebsocketProvider.prefix('/ws');
})
.controller('MyFormController', function($scope, djangoWebsocket) {
	console.log(djangoWebsocket); console.log($scope); console.log($scope.subscribe_data);
	djangoWebsocket.connect($scope, ['subscribe-broadcast', 'publish-broadcast'], 'subscribe_data');
});

})(window.angular);
