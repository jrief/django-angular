'use strict';

describe('unit tests for module ng.django.messages', function() {
	
	function compileForm($compile, scope, replace_value) {
		var template =
			'<form name="valid_form" action=".">' +
			'<input name="email_field" ng-model="model.email" type="email" djng-validate-rejected {value} />' +
			'</form>';
		var form = angular.element(template.replace('{value}', replace_value));
		$compile(form)(scope);
		scope.$digest();
	}
	
	function compileFormWithBoundError($compile, scope, replace_value) {
		var template =
			'<form name="valid_form" action=".">' +
			'<input name="email_field" ng-model="model.email" type="email" djng-error="valid email required" djng-validate-rejected  {value} />' +
			'</form>';
		var form = angular.element(template.replace('{value}', replace_value));
		$compile(form)(scope);
		scope.$digest();
	}
	
	beforeEach(function() {
		module('ng.django.messages');
	});
	
	
	describe('form extension behaviour', function() {
		
		var scope, form, field;

		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			compileForm($compile, scope, '');
			form = scope.valid_form;
			field = scope.valid_form.email_field;
		}));
		
		it('should set valid fields back to pristine', function() {
			field.$setViewValue('example@example.com');
			expect(field.$valid).toBe(true);
			expect(field.$pristine).toBe(false);
			form.setValidFieldsPristine();
			expect(field.$valid).toBe(true);
			expect(field.$pristine).toBe(true);
		});
		
		it('should leave invalid fields dirty', function() {
			field.$setViewValue('example');
			expect(field.$valid).toBe(false);
			expect(field.$pristine).toBe(false);
			form.setValidFieldsPristine();
			expect(field.$valid).toBe(false);
			expect(field.$pristine).toBe(false);
		});
		
	});
	
	
	describe('bound form error handling', function() {
		
		var scope, form, field, $timeout;

		beforeEach(inject(function($rootScope, $compile, _$timeout_) {
			scope = $rootScope.$new();
			compileFormWithBoundError($compile, scope, 'value="barry"');
			form = scope.valid_form;
			field = scope.valid_form.email_field;
			$timeout = _$timeout_;
		}));
		
		it('should invalidate field when djng-error exists', function() {
			$timeout.flush();
			expect(field.$valid).toBe(false);
			expect(field.$error.rejected).toBe(true);
			expect(field.$message.rejected).toBe('valid email required');
		});
		
		it('should set form to $submitted', function() {
			$timeout.flush();
			expect(form.$submitted).toBe(true);
		});
	});
	
	
	describe('rejected validation directive', function() {
		
		var scope, form, field;

		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			compileForm($compile, scope, '');
			form = scope.valid_form;
			field = scope.valid_form.email_field;
		}));
		
		it('should invalidate field when rejected message exists', function() {
			field.$setViewValue('example@example.com');
			field.$message = {rejected: 'email already in use'};
			field.$validate();
			expect(field.$valid).toBe(false);
			expect(field.$error.rejected).toBe(true);
		});
		
		it('should clear message and return true when new value is set on field and rejected message exists from previous failed rejected validation', function() {
			field.$setViewValue('example@example.com');
			field.$message = {rejected: 'email already in use'};
			field.$validate();
			expect(field.$valid).toBe(false);
			expect(field.$error.rejected).toBe(true);
			field.$setViewValue('example@example2.com');
			expect(field.$valid).toBe(true);
			expect(field.$error.rejected).toBe(undefined);
		});
		
		it('should not remove message if field value is the same as previous failed rejected validation', function() {
			field.$setViewValue('example@example.com');
			field.$message = {rejected: 'email already in use'};
			field.$validate();
			expect(field.$valid).toBe(false);
			expect(field.$error.rejected).toBe(true);
			field.$setViewValue('example@example.com');
			field.$validate();
			expect(field.$valid).toBe(false);
			expect(field.$error.rejected).toBe(true);
		});
	});
	
	
	describe('form rejected error handling', function() {
		
		var scope, form, field, djngMessagesForm,
			formError = {errors: {__all__: ["The email is rejected by the server."]}},
			fieldError = {errors: {email_field: ["This field is required."]}};
		
		beforeEach(inject(function($rootScope, $compile, _djngMessagesForm_){
			scope = $rootScope.$new();
			compileForm($compile, scope, '');
			form = scope.valid_form;
			field = scope.valid_form.email_field;
			djngMessagesForm = _djngMessagesForm_;
		}));
		
		it('should return false if no errors listed', function() {
			expect(djngMessagesForm.setErrors(form, undefined)).toBe(false);
		});
		
		it('should return true if non field errors listed', function() {
			expect(djngMessagesForm.setErrors(form, formError.errors)).toBe(true);
		});
		
		it('should return true if field errors listed', function() {
			expect(djngMessagesForm.setErrors(form, fieldError.errors)).toBe(true);
		});
		
		it('should add rejected non field errors to form.$message and set valid fields pristine', function() {
			field.$setViewValue('example@example.com');
			expect(field.$pristine).toBe(false);
			djngMessagesForm.setErrors(form, formError.errors);
			expect(form.$message).toBe('The email is rejected by the server.');
			expect(field.$pristine).toBe(true);
		});
		
		it('should add rejected error message to field.$message.rejected and validate', function() {
			djngMessagesForm.setErrors(form, fieldError.errors);
			expect(field.$message.rejected).toBe('This field is required.');
			expect(field.$valid).toBe(false);
		});
	});
	
});
