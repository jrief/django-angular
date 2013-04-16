/*
 * django-angular
 * https://github.com/jrief/django-angular
 *
 * Add Angular directives which play together with special mixin classes adopted
 * for the Django framework.
 *
 * Copyright (c) 2013 Jacob Rief
 * Licensed under the MIT license.
 */

(function(angular, undefined) {
'use strict';

angular.module('ngDjango', []).directive('autoLabel', function() {
	return {
		restrict: 'A',
		scope: 'isolate',
		link: function(scope, elem, attrs) {
			var $element = angular.element(elem);
			var watchers = null;
			var orig_type = attrs.type;

			scope.$evalAsync(function() {
				if ($element.val() === '') {
					removeWatchers();
					$element.addClass('empty');
					$element.val(attrs.autoLabel);
					if (orig_type === 'password') {
						$element.attr('type', 'text');
					}
				}
			});

			elem.bind('focus', function() {
				if (!$element.hasClass('empty'))
					return;
				removeWatchers();
				$element.val('');
				$element.removeClass('empty error');
				$element.attr('type', orig_type);
			});

			elem.bind('focusout', function() {
				if ($element.val() === '') {
					$element.addClass('empty');
					$element.val(attrs.autoLabel);
					if (orig_type === 'password') {
						$element.attr('type', 'text');
					}
					// restore watchers
					if (watchers) {
						scope.$$watchers = watchers;
						watchers = null;
					}
				}
			});

			function removeWatchers() {
				watchers = scope.$$watchers;
				scope.$$watchers = [];
			}

		}
	};
});

})(window.angular);
