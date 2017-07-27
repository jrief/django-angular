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
			element.addClass('uploading');
			Upload.upload({
				data: data,
				url: attrs.fileuploadUrl
			}).then(function(response) {
				var field = response.data[identifier],
				    current = angular.isString(attrs.currentFile) ? {current_file: attrs.currentFile} : {};
				element.removeClass('uploading');
				element.css('background-image', field.url);
				delete field.url;  // we don't want to send back the whole image
				angular.extend($scope.$eval(attrs.ngModel), field, current);
			}, function(respose) {
				element.removeClass('uploading');
				console.error(respose.statusText);
			});
		});
	};
}]);


fileuploadModule.directive('ngfDrop', function() {
	return {
		restrict: 'AEC',
		controller: 'FileUploadController',
		require: ['ngfDrop', 'ngModel'],
		link: function(scope, element, attrs, ctrls) {
			var fileUploadController = ctrls[0], ngModelController = ctrls[1];

			ngModelController.$setViewValue({
				current_file: attrs.currentFile,
				temp_name: Boolean(attrs.currentFile)
			});

			scope.uploadFiles = function(files) {
				fileUploadController.uploadFiles(element, attrs, files);
			};

			scope.getClass = function() {
				var model = ngModelController.$viewValue;
				if (!model || !model.temp_name)
					return 'empty';
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
		}
	};
});

fileuploadModule.directive('djngFileuploadButton', function() {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			scope.deleteImage = function() {
				var model = scope.$eval(attrs.djngFileuploadButton);
				if (model) {
					model.temp_name = false;  // tags previous image for deletion
				}
			};

			scope.isEmpty = function() {
				var model = scope.$eval(attrs.djngFileuploadButton);
				return !(model && model.temp_name);
			};
		}
	};
});

})(window.angular);
