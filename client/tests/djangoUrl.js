'use strict';

describe('unit tests for module ng.django.url', function () {

    describe('test urls', function () {

        beforeEach(function () {
            // ng.django.urls - core module
            // ng.django.urls - pattern mocks for testing, from mocks/urlmocks.js
            module('ng.django.urls', 'ng.django.urls.mocks');
        });

        describe('general url reverser tests', function () {
            it('should raise an error when no matching url is found', inject(function (djangoUrl) {
                expect(function () {
                    djangoUrl.resolve('home12')
                }).toThrow();
            }));
        });

        describe('test url reverser for simple urls without parameters', function () {
            it('should ignore not-needed parameters', inject(function (djangoUrl) {
                expect(djangoUrl.resolve('home')).toBe('/');
                expect(djangoUrl.resolve('home', [2, 3])).toBe('/');
                expect(djangoUrl.resolve('home', {'some_data': 2})).toBe('/');
            }));
        });

        describe("test url reverser for patterns that require arguments", function () {

            it("should fill arguments correctly", inject(function (djangoUrl) {
                expect(djangoUrl.resolve('api:overview', [2])).toBe('/api/2/overview/');
                expect(djangoUrl.resolve('api:visitors', [3, 4])).toBe('/api/3/visitors/4/');
            }));

            it("should ignore extra arguments", inject(function (djangoUrl) {
                expect(djangoUrl.resolve('api:overview', [2, 3])).toBe('/api/2/overview/')
            }));

            it("should raise an error when there are not enough arguments", inject(function (djangoUrl) {
                expect(function () {
                    djangoUrl.resolve('api:overview', [])
                }).toThrow();
            }));

            it("should not raise an exception when not given any arguments if none are required",
                inject(function (djangoUrl) {
                    expect(function () {
                        djangoUrl.resolve('api:overview')
                    }).not.toThrow();
                }));
        });

        describe("test url reverser for resolving urls with kwargs", function () {

            it("should fill kwargs correctly", inject(function (djangoUrl) {
                expect(djangoUrl.resolve('api:overview', {'website_id': 2})).toBe('/api/2/overview/');
                expect(djangoUrl.resolve('api:visitors', {'website_id': 2, 'visitor_id': 3}))
                    .toBe('/api/2/visitors/3/');
            }));

            it("should ignore extra kwargs", inject(function (djangoUrl) {
                expect(djangoUrl.resolve('api:overview', {'website_id': 2, 'visitor_id': 3}))
                    .toBe('/api/2/overview/');
            }));

            it("should return parametrized url template for missing kwargs", inject(function (djangoUrl) {
                expect(djangoUrl.resolve('api:overview', {})).toBe('/api/:website_id/overview/');
                expect(djangoUrl.resolve('api:visitors', {'visitor_id': 3}))
                    .toBe('/api/:website_id/visitors/3/');
                expect(djangoUrl.resolve('api:visitors', {'website_id': 2}))
                    .toBe('/api/2/visitors/:visitor_id/');
            }));

            it("should default to kwargs mode when no args/kwargs are given (parametrized urls)",
                inject(function (djangoUrl) {
                        expect(djangoUrl.resolve('api:overview')).toBe('/api/:website_id/overview/');
                    }
                ));
        });
    });
});
