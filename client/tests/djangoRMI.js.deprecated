'use strict';

describe('unit tests for module djng.rmi', function() {
	var $httpBackend, djangoRMI;

	beforeEach(function() {
		module('djng.rmi');
	});

	describe('emulating get_current_remote_methods', function() {
		beforeEach(function() {
			angular.module('testApp', function() {}).config(function(djangoRMIProvider) {
				djangoRMIProvider.configure({"foo": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "foo"}, "method": "auto"}, "bar": {"url": "/straight_methods/", "headers": {"DjNg-Remote-Method": "bar"}, "method": "auto"}});
			});
			module('djng.forms', 'testApp');
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
			module('djng.forms', 'testApp');
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
