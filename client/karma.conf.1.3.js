'use strict';

// Karma configuration
module.exports = function(config) {
	function getFiles() {
		var fs = require('fs'); 
		var files = [];
		['angular.js', 'angular-mocks.js', 'angular-messages.js'].forEach(function(item) {
			var cachename = 'cdncache/' + item;
			files.push(fs.existsSync(cachename) ? cachename : 'http://code.angularjs.org/1.3.0/' + item);
		});
		return files.concat(['src/js/*.js', 'tests/*.js', 'mocks/*.js']);
	}

	config.set({
		// frameworks to use
		frameworks: ['jasmine'],

		// list of files / patterns to load in the browser
		files: getFiles(),

		// list of files to exclude
		exclude: [],

		// test results reporter to use
		// possible values: 'dots', 'progress', 'junit', 'growl', 'coverage'
		reporters: ['progress'],

		// web server port
		port: 9090,

		// enable / disable colors in the output (reporters and logs)
		colors: true,

		// level of logging
		// possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
		logLevel: config.LOG_INFO,

		// enable / disable watching file and executing tests whenever any file changes
		autoWatch: false,

		// Start these browsers, currently available:
		// - Chrome
		// - ChromeCanary
		// - Firefox
		// - Opera (has to be installed with `npm install karma-opera-launcher`)
		// - Safari (only Mac; has to be installed with `npm install karma-safari-launcher`)
		// - PhantomJS
		// - IE (only Windows; has to be installed with `npm install karma-ie-launcher`)
		browsers: ['ChromeCanary'],

		// If browser does not capture in given timeout [ms], kill it
		captureTimeout: 60000,

		// Continuous Integration mode
		// if true, it capture browsers, run tests and exit
		singleRun: false
	});
};
