angular.module('djangular-demo')
.controller('MyWebsocketCtrl', function($scope, djangoWebsocket) {
	djangoWebsocket.connect($scope, 'subscribe_data', 'subscribe_data', ['subscribe-broadcast', 'publish-broadcast']);
});
