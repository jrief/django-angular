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
		require: 'ngModel',
		link: function(scope, elem, attrs, ctrl) {
			var orig_type = attrs.type;

			// load initial value from element
			if (!elem.val()) {
				elem.addClass('empty');
				elem.val(attrs.autoLabel);
				if (orig_type === 'password') {
					elem.attr('type', 'text');
				}
				ctrl.$setViewValue('');
			} else {
				ctrl.$setViewValue(elem.val());
			}

			// on focus, replace auto-label with empty field
			elem.bind('focus', function() {
				if (elem.hasClass('empty')) {
					elem.val('');
					elem.removeClass('empty error');
					elem.attr('type', orig_type);
				}
			});

			// view -> model
			elem.bind('blur', function() {
				console.log('view -> model: '+elem.val());
				var orig_val = elem.val();
				autoAddLabel(orig_val);
				scope.$apply(function() {
					ctrl.$setViewValue(orig_val);
				});
			});

			// model -> view
			ctrl.$render = function() {
				console.log('model -> view: '+ctrl.$viewValue);
				autoAddLabel(ctrl.$viewValue);
			};

			function autoAddLabel(val) {
				if (!val) {
					elem.addClass('empty');
					elem.val(attrs.autoLabel);
					if (orig_type === 'password') {
						elem.attr('type', 'text');
					}
				} else {
					elem.val(val);
				}
			}

		}
	};
});

})(window.angular);
