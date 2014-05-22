'use strict';

describe('unit tests for module ng.django.forms', function() {
	function compileForm($compile, scope, replace_value) {
		var template =
			'<form name="valid_form" action=".">' +
			'<input name="email_field" ng-model="model.email" type="text" {value} />' +
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
				expect(scope.valid_form.email_field.$viewValue).toBe('');
			}));
		});

		describe('on bound forms', function() {
			it('the view value of filled input fields should remain as is', inject(function($compile) {
				compileForm($compile, scope, 'value="john@example.net"');
				expect(scope.valid_form.email_field.$viewValue).toBe('john@example.net');
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
					'<input name="email_field" ng-model="model.email" type="text" />' +
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

	describe('test provider djangoRMI', function() {
		var $httpBackend, djangoRMI;

		beforeEach(function() {
			module('ng.django.forms');
		});

		describe('emulating get_current_remote_methods', function() {
			beforeEach(function() {
				angular.module('testApp', function() {}).config(function(djangoRMIProvider) {
					djangoRMIProvider.configure({"foo": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "foo"}, "method": "auto"}, "bar": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "bar"}, "method": "auto"}});
				});
				module('ng.django.forms', 'testApp');
			});

			beforeEach(inject(function($injector) {
				$httpBackend = $injector.get('$httpBackend');
			}));

			it('should call View method foo using GET', inject(function(djangoRMI) {
				$httpBackend.when('GET', '/straight_methods/').respond(200, {success: true});
				djangoRMI.foo().success(function(data) {
					expect(data.success).toBe(true);
				});
				$httpBackend.flush();
			}));

			it('should call View method foo using POST', inject(function(djangoRMI) {
				$httpBackend.when('POST', '/straight_methods/').respond(200, {yeah: 'success'});
				djangoRMI.foo({some: 'data'}).success(function(data) {
					expect(data.yeah).toBe('success');
				});
				$httpBackend.flush();
			}));
		});

		describe('emulating get_all_remote_methods', function() {
			beforeEach(function() {
				angular.module('testApp', function() {}).config(function(djangoRMIProvider) {
					djangoRMIProvider.configure({"submethods": {"sub": {"app": {"foo": {"url": "/sub_methods/sub/app/", "headers": {"DjNg-Remote-Method": "foo"}, "method": "auto"}, "bar": {"url": "/sub_methods/sub/app/", "headers": {"DjNg-Remote-Method": "bar"}, "method": "auto"}}}}, "straightmethods": {"foo": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "foo"}, "method": "auto"}, "bar": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "bar"}, "method": "auto"}}});
				});
				module('ng.django.forms', 'testApp');
			});

			beforeEach(inject(function($injector) {
				$httpBackend = $injector.get('$httpBackend');
			}));

			it('should call View method foo using GET', inject(function(djangoRMI) {
				$httpBackend.when('GET', '/sub_methods/sub/app/').respond(200, {foo: null});
				djangoRMI.submethods.sub.app.foo().success(function(data) {
					expect(data.foo).toBe(null);
				});
				$httpBackend.flush();
			}));

			it('should call View method bar using GET', inject(function(djangoRMI) {
				$httpBackend.when('GET', '/sub_methods/sub/app/').respond(200, {bar: 'nothing'});
				djangoRMI.submethods.sub.app.bar().success(function(data) {
					expect(data.bar).toBe('nothing');
				});
				$httpBackend.flush();
			}));

			it('should call View method foo using POST', inject(function(djangoRMI) {
				$httpBackend.when('POST', '/sub_methods/sub/app/').respond(200, {foo: 'some data'});
				djangoRMI.submethods.sub.app.foo({some: 'data'}).success(function(data) {
					expect(data.foo).toBe('some data');
				});
				$httpBackend.flush();
			}));

			it('should call View method bar using POST', inject(function(djangoRMI) {
				$httpBackend.when('POST', '/sub_methods/sub/app/').respond(200, {bar: 'other data'});
				djangoRMI.submethods.sub.app.bar({other: 'data'}).success(function(data) {
					expect(data.bar).toBe('other data');
				});
				$httpBackend.flush();
			}));
		});
	});
});
