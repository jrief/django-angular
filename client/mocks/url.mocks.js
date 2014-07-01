angular.module('ng.django.urls.mocks', []).constant('patterns', {
    'home': '/',
    'api:overview': '/api/(?P<website_id>\\d)/overview/',
    'app': '/app/(?P<website_id>\\d)/',
    'api:visitors': '/api/(?P<website_id>\\d)/visitors/(?P<visitor_id>\\d)/'}
);