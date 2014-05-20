(function(angular, undefined) {
'use strict';

angular.module('djangular.router', ['ui.router']).provider('$state', ['$provide', '$stateProvider', function($provide, $stateProvider) {
	var super_state = $stateProvider.state, state_config;

	// function to be called from Django's initialization code
	$stateProvider.initialize = function(config) {
		state_config = config;
	};

	// override function `$stateProvider.state`
	$stateProvider.state = function(name, params) {
		if (state_config === undefined)
			throw new Error("$stateProvider has not been initialized");
		console.log($stateProvider);
		super_state(name, params);
		return $stateProvider;
	};

/*
	$provide.decorator('$state', function($delegate) {
		$delegate.foo = function() {
			alert('Foo');
		};
		return $delegate;
	});
*/
	return $stateProvider;
}]);

})(window.angular);
