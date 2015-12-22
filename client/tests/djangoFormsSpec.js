'use strict';

describe('unit tests for module ng.django.forms', function() {
	function compileForm($compile, scope, replace_value) {
		var template =
			'<form name="valid_form" action=".">' +
			'<input name="email_field" ng-model="model.email" djng-rejected type="text" {value} />' +
			'</form>';
		var form = angular.element(template.replace('{value}', replace_value));
		$compile(form)(scope);
		scope.$digest();
	}

	describe('test default form behavior', function() {
		var scope;

		beforeEach(inject(function($rootScope) {
			scope = $rootScope.$new();
		}));

		describe('on unbound forms', function() {
			it('the view value of empty input fields should remain undefined', inject(function($compile) {
				compileForm($compile, scope, '');
				expect(scope.valid_form.email_field.$viewValue).toBe(undefined);
			}));
		});

		describe('on bound forms', function() {
			it('the view value of filled input fields should remain undefined', inject(function($compile) {
				compileForm($compile, scope, 'value="john@example.net"');
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
				compileForm($compile, scope, '');
				expect(scope.valid_form.email_field.$viewValue).toBe(undefined);
			}));
		});

		describe('on bound forms', function() {
			it('the view value of filled input fields should remain as is', inject(function($compile) {
				compileForm($compile, scope, 'value="john@example.net"');
				expect(scope.valid_form.email_field.$viewValue).toBe('john@example.net');
			}));
		});

	});
	
	describe('test directive djngRejected', function() {
		
		var scope, form, field;
	
		beforeEach(function() {
			module('ng.django.forms');
		});
		
		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			compileForm($compile, scope, '');
			form = scope.valid_form;
			field = scope.valid_form.email_field;
		}));
		
		it('should add djngAddRejected method to ngModel', function() {
			expect(typeof field.djngAddRejected).toBe('function');
		});
		
		it('should add djngClearRejected method to ngModel', function() {
			expect(typeof field.djngClearRejected).toBe('function');
		});
		
		it('should set rejected state on control', function() {
			field.djngAddRejected('i am rejected');
			expect(field.$error.rejected).toBe(true);
			expect(field.$message).toBe('i am rejected');
			expect(field.$pristine).toBe(true);
		});
		
		it('should remove rejected state from control', function() {
			field.djngAddRejected('i am rejected');
			expect(field.$error.rejected).toBe(true);
			expect(field.$message).toBe('i am rejected');
			expect(field.$pristine).toBe(true);
			field.djngClearRejected();
			expect(field.$error.rejected).toBe(false);
			expect(field.$message).toBe(undefined);
		});
		
		it('should remove rejected state when model changes', function() {
			field.djngAddRejected('i am rejected');
			expect(field.$error.rejected).toBe(true);
			expect(field.$message).toBe('i am rejected');
			expect(field.$pristine).toBe(true);
			scope.model = {email: 'barry@barry.com'};
			scope.$digest();
			expect(field.$error.rejected).toBe(false);
			expect(field.$message).toBe(undefined);
		});
		
		it('should remove rejected state when $viewValue changes', function() {
			field.djngAddRejected('i am rejected');
			expect(field.$error.rejected).toBe(true);
			expect(field.$message).toBe('i am rejected');
			expect(field.$pristine).toBe(true);
			field.$setViewValue('barry@barry.com');
			expect(field.$error.rejected).toBe(false);
			expect(field.$message).toBe(undefined);
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

	describe('test provider djangoForm', function() {
		var scope, djangoForm;

		beforeEach(function() {
			module('ng.django.forms');
		});

		describe('using manual instantiation', function() {
			beforeEach(function() {
				angular.module('testApp', function() {}).config(function(djangoFormProvider) {
					djangoForm = djangoFormProvider.$get();
				});
				module('ng.django.forms', 'testApp');
			});

			beforeEach(inject(function($rootScope) {
				scope = $rootScope.$new();
			}));

			beforeEach(inject(function($compile) {
				var form = angular.element(
					'<form name="form" action=".">' +
					'<input name="email_field" ng-model="model.email" djng-rejected type="text" />' +
					'</form>'
				);
				$compile(form)(scope);
				scope.$digest();
			}));

			it('should give a valid form', function() {
				expect(djangoForm.setErrors(scope.form, {})).toBe(false);
				expect(scope.form.email_field.$valid).toBe(true);
			});

			it('should give an invalid form', function() {
				var errors = { email_field: ['A server side error occurred'] };
				expect(djangoForm.setErrors(scope.form, errors)).toBe(true);
				expect(scope.form.email_field.$valid).toBe(false);
			});

		});
	});

});
