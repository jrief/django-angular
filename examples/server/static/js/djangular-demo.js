'use strict';

angular.module('djangular-demo', ['ui.bootstrap']);

function AdultSubscriptionController($scope) {
	console.log('AdultSubscriptionController');

	$scope.subscribe_data = { first_name: '' };
}
