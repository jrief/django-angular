
(function(angular, undefined) {
'use strict';

angular.module('djangular-demo', ['ng.django.websocket'])
.config(function(djangoWebsocketProvider) {
	djangoWebsocketProvider.prefix('/ws');
	djangoWebsocketProvider.debug(false);
})
.controller('MyFormController', function($scope, djangoWebsocket) {
	djangoWebsocket.connect($scope, ['subscribe-broadcast', 'publish-broadcast'], 'subscribe_data');
});

})(window.angular);
