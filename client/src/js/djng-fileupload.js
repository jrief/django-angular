(function(angular, undefined) {
'use strict';

// module: djng.uploadfiles
// Connect the third party module `ng-file-upload` to django-angular
var fileuploadModule = angular.module('djng.fileupload', ['ngFileUpload']);

fileuploadModule.controller('FileUploadController', ['$scope', 'Upload', function($scope, Upload) {
	this.uploadFiles = function(element, attrs, files) {
		angular.forEach(files, function(file, index) {
			var data = {}, identifier = 'file:' + index;
			if (file.$error)
				return;
			data[identifier] = file;
			Upload.upload({
				data: data,
				url: attrs.fileuploadUrl
			}).then(function(response) {
				var field = response.data[identifier];
				element.css('background-image', field.url);
				delete field.url;  // we don't want to send back the whole image
				angular.extend($scope.$eval(attrs.ngModel), field);
			}, function(respose) {
				console.error(respose.statusText);
			});
		});
	};

}]);


fileuploadModule.directive('ngfDrop', function() {
	return {
		restrict: 'AEC',
		controller: 'FileUploadController',
		link: function(scope, element, attrs, fileUploadController) {
			scope.uploadFiles = function(files) {
				fileUploadController.uploadFiles(element, attrs, files);
			};

			scope.getClass = function() {
				return scope.$eval(attrs.ngModel)['temp_name'] ? '' : 'empty'
			};
		}
	};
});


fileuploadModule.directive('ngfSelect', function() {
	return {
		restrict: 'AEC',
		controller: 'FileUploadController',
		link: function(scope, element, attrs, fileUploadController) {
			scope.uploadFiles = function(files) {
				fileUploadController.uploadFiles(element, attrs, files);
			};
			scope.getClass = function() {
				return scope.$eval(attrs.ngModel)['temp_name'] ? '' : 'empty'
			};
		}
	};
});

fileuploadModule.directive('djngFileuploadButton', function() {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			var ngModel = attrs['djngFileuploadButton'];

			scope.deleteImage = function() {
				console.log(scope.$eval(ngModel));
				scope.$eval(ngModel)['temp_name'] = null;
			};

			scope.isEmpty = function() {
				return !scope.$eval(ngModel)['temp_name'];
			};
		}
	};
});

})(window.angular);
