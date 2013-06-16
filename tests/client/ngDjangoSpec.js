'use strict';

describe('test module django-angular', function() {
	beforeEach(function() {
		module('ngDjango');
	});

	describe('for an empty input field of type text using directive auto-label', function() {
		var email_field, scope;

		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			email_field = angular.element('<input type="text" name="useremail" auto-label="E-Mail" ng-model="form.email" value="" />');
			$compile(email_field)(scope);
		}));

		it('should display the auto-label as input value', function() {
			expect(email_field.val()).toBe('E-Mail');
			expect(email_field.hasClass('empty')).toBe(true);
			expect(scope.form.email).toBe('');
		});

		describe('when input field gains focus', function() {
			beforeEach(function() {
				email_field.triggerHandler('focus');
			});

			afterEach(function() {
				email_field.triggerHandler('blur');
			});

			it('should hide the auto-label and remove class "empty"', function() {
				expect(email_field.val()).toBe('');
				expect(email_field.hasClass('empty')).toBe(false);
				expect(scope.form.email).toBe('');
			});

			it('should restore the auto-label and class "empty" when leaving field unchanged', function() {
				email_field.triggerHandler('blur');
				expect(email_field.val()).toBe('E-Mail');
				expect(email_field.hasClass('empty')).toBe(true);
				expect(scope.form.email).toBe('');
			});

			describe('when text is entered into the input field', function() {
				beforeEach(function() {
					email_field.val('me@example.com');
					email_field.triggerHandler('blur');
				});

				it('should remember the entered text in scope.form and remove class "empty"', function() {
					expect(email_field.val()).toBe('me@example.com');
					expect(email_field.hasClass('empty')).toBe(false);
					expect(scope.form.email).toBe('me@example.com');
				});

				it('should reset the field as "empty"', function() {
					email_field.triggerHandler('focus');
					email_field.val('');
					email_field.triggerHandler('blur');
					expect(email_field.val()).toBe('E-Mail');
					expect(email_field.hasClass('empty')).toBe(true);
					expect(scope.form.email).toBe('');
				});
			});
		});

		describe('when the value is set through the model controller', function() {
			beforeEach(function() {
				expect(email_field.val()).toBe('E-Mail');
				scope.form.email = 'john@doe.com';
				scope.$digest();
			});

			it('should display the value in the input field', function() {
				expect(email_field.val()).toBe('john@doe.com');
				expect(email_field.hasClass('empty')).toBe(false);
			});

			it('should replace an empty value in the input field by auto-label', function() {
				scope.form.email = '';
				scope.$digest();
				expect(email_field.val()).toBe('E-Mail');
				expect(email_field.hasClass('empty')).toBe(true);
			});

		});

	});

	describe('for input field of type password using directive auto-label', function() {
		var pwd_field, scope;

		beforeEach(inject(function($rootScope, $compile) {
			scope = $rootScope.$new();
			pwd_field = angular.element('<input type="password" name="userpwd" auto-label="Password" ng-model="form.passwd" value="" />');
			$compile(pwd_field)(scope);
		}));

		it('should display the auto-label as input value for a text field', function() {
			expect(pwd_field.val()).toBe('Password');
			expect(pwd_field.attr('type')).toBe('text');
			expect(pwd_field.hasClass('empty')).toBe(true);
			expect(scope.form.passwd).toBe('');
		});

		describe('when password field gains focus', function() {
			beforeEach(function() {
				pwd_field.triggerHandler('focus');
			});

			afterEach(function() {
				pwd_field.triggerHandler('blur');
			});

			it('should hide the auto-label, remove class "empty" and obfuscate text input', function() {
				expect(pwd_field.val()).toBe('');
				expect(pwd_field.hasClass('empty')).toBe(false);
				expect(scope.form.passwd).toBe('');
				expect(pwd_field.attr('type')).toBe('password');
			});
		});
	});
});
