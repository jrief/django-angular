'use strict';

describe('unit tests for module djng.url', function () {
    var base_url = '/angular/reverse/';
    var arg_prefix = 'djng_url_args';
    var kwarg_prefix = 'djng_url_kwarg_';
    var url_name_arg = 'djng_url_name';

    describe("test djangoUrlProvider", function () {
        beforeEach(function () {
            module('djng.urls');
        });

        describe("Test provider custom url config", function () {
            it('tests the providers internal function', inject(function(djangoUrl) {
                expect(djangoUrl.reverse('myapp:home')).toBe('/angular/reverse/?djng_url_name=myapp%3Ahome');
            }));
        });

    });

    describe('test djangoUrl url resolving', function () {
        beforeEach(function () {
            module('djng.urls');
        });

        describe('general url reverser tests', function () {
            it('should inject the djangoUrl service without errors', inject(function (djangoUrl) {
                expect(djangoUrl.reverse).toBeDefined();
            }));
            it('should match the base url', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('some:url:name')).toContain(base_url);
            }));
        });

        describe('test building urls, url name', function () {
            it('should correctly add django\'s url name as query parameter', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home')).toBe(base_url + '?' + url_name_arg + '=home')
            }));
            it('should urlencode name if it contains :', inject(function (djangoUrl) {
                // : urlencoded becomes %3A
                expect(djangoUrl.reverse('account:profile')).toBe(base_url + '?' + url_name_arg + '=account%3Aprofile')
            }));
            it('should encode funny characters in name correctly', inject(function (djangoUrl) {
                var urlname = '{6;.-$$+/';
                expect(djangoUrl.reverse(urlname)).toBe(base_url + '?' + url_name_arg + '=' + encodeURIComponent(urlname));
            }));
        });

        describe('test building urls with arguments', function () {
            it('should add single argument as query param with arg_prefix', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home', [1])).toBe(base_url + '?' + url_name_arg + '=home&' + arg_prefix + '=1');
            }));
            it('should add multiple arguments in correct order', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home', [1, 2, 3]))
                    .toBe(base_url + '?' + url_name_arg + '=home&' + arg_prefix + '=1&' + arg_prefix + '=2&' + arg_prefix + '=3');
            }));
            it('should not urlencode args starting with :', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('article', [':id'])).toBe(
                    base_url + '?' + url_name_arg + '=article&' + arg_prefix + '=:id');
            }));
        });

        describe('test building urls with keyword arguments', function () {
            it('should add kwarg as kwarg prefix + kwarg name = kwarg value', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home', {id: '7'}))
                    .toBe(base_url + '?' + url_name_arg + '=home&' + kwarg_prefix + 'id=7');
            }));
            it('should add multiple kwargs', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home', {id: '7', name: 'john'}))
                    .toBe(base_url + '?' + url_name_arg + '=home&' + kwarg_prefix + 'id=7&' + kwarg_prefix + 'name=john');
            }));
            it('should not urlencode kwarg values staring with :', inject(function (djangoUrl) {
                expect(djangoUrl.reverse('home', {id: ':id'}))
                    .toBe(base_url + '?' + url_name_arg + '=home&' + kwarg_prefix + 'id=:id');
            }));
        });

    });
});
