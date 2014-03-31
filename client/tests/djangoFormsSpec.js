'use strict';

describe('unit tests for module ng.django.forms', function() {
	var john = 'john@example.net';
	var template =
		'<form name="valid_form" action=".">' +
		'<input name="email_field" ng-model="model.email" type="text" {value} />' +
		'</form>';

	function compileUnboundForm($compile, scope) {
		var doc = template.replace('{value}', '').replace('{date}', '');
		var unbound_form = angular.element(doc);
		$compile(unbound_form)(scope);
		scope.$digest();
	}

	function compileBoundForm($compile, scope) {
		var doc = template.replace('{value}', 'value="' + john + '"').replace('{date}', '');
		var bound_form = angular.element(doc);
		$compile(bound_form)(scope);
		scope.$digest();
	}

	describe('test default form behavior', function() {
		var scope;

		beforeEach(inject(function($rootScope) {
			scope = $rootScope.$new();
		}));

		describe('on unbound forms', function() {
			it('the view value of empty input fields should remain undefined', inject(function($compile) {
				compileUnboundForm($compile, scope);
				expect(scope.valid_form.email_field.$viewValue).toBe(undefined);
			}));
		});

		describe('on bound forms', function() {
			it('the view value of filled input fields should remain undefined', inject(function($compile) {
				compileBoundForm($compile, scope);
				expect(scope.valid_form.email_field.$viewValue).toBe(undefined);
			}));
		});
	});

	describe('test overridden form behavior', function() {
		var scope;
	
		beforeEach(function() {
			// djangular's 'form' directive, overrides the behavior of the view value.
			module('ng.django.forms');
		});

		beforeEach(inject(function($rootScope) {
			scope = $rootScope.$new();
		}));

		describe('on unbound forms', function() {
			it('the view value of empty input fields should be empty', inject(function($compile) {
				compileUnboundForm($compile, scope);
				expect(scope.valid_form.email_field.$viewValue).toBe('');
			}));
		});

		describe('on bound forms', function() {
			it('the view value of filled input fields should remain as is', inject(function($compile) {
				compileBoundForm($compile, scope);
				expect(scope.valid_form.email_field.$viewValue).toBe(john);
			}));
		});

	});

	describe('test directive validateDate', function() {
		var scope, form;
	
		beforeEach(function() {
			// djangular's 'form' directive, overrides the behavior of the view value.
			module('ng.django.forms');
		});

		beforeEach(inject(function($rootScope) {
			scope = $rootScope.$new();
		}));

		beforeEach(inject(function($compile) {
			var doc =
				'<form name="form">' +
				'<input name="date_field" ng-model="model.date" type="text" validate-date="^(\\d{4})-(\\d{1,2})-(\\d{1,2})$" />' +
				'</form>';
			var element = angular.element(doc);
			scope.model = { date: null };
			$compile(element)(scope);
			form = scope.form;
		}));

		it('to reject 2014/04/01', function() {
			form.date_field.$setViewValue('2014/04/01');
			scope.$digest();
			expect(form.date_field.$valid).toBe(false);
		});

		it('to accept 2014-04-01', function() {
			form.date_field.$setViewValue('2014-03-01');
			scope.$digest();
			expect(form.date_field.$valid).toBe(true);
		});

		it('to reject 2014-04-31', function() {
			form.date_field.$setViewValue('2014-02-29');
			scope.$digest();
			expect(form.date_field.$valid).toBe(false);
		});
	});
});
