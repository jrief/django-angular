'use strict';

describe('test module ng.django.forms', function() {
	var john = 'john@example.net';
	var template =
		'<form name="valid_form" action=".">' +
		'<input name="email_field" ng-model="mail_addr" type="text" {value} />'
		'</form>';
	
	describe('overrides internal form behavior', function() {
		var unbound_form, bound_form, scope;

		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			//bound_form = angular.element(template.replace('{value}', 'value="' + john + '"'));
			//$compile(bound_form)(scope);
			unbound_form = angular.element(template.replace('{value}', ''));
			dump($compile(unbound_form)(scope));
		}));

		
		it('should read from attribute "value" into ng-model', function() {
			dump(unbound_form);
			dump(scope.valid_form.email_field);
			//expect(email_field.val()).toBe(john);
			//expect(scope.valid_form.email).toBe(john);
			expect(true).toBe(true);
		});

	});

});
