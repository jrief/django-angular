(function(angular, undefined) {
'use strict';

// module: djng.uploadfiles
// Connect the third party module `ng-file-upload` to django-angular
var fileuploadModule = angular.module('djng.fileupload', ['ngFileUpload']);


fileuploadModule.directive('djngFileuploadUrl', ['Upload', function(Upload) {
	return {
		restrict: 'A',
		require: 'ngModel',
		link: function(scope, element, attrs, ngModelController) {
			if (!attrs.currentFile) {
				element.addClass('empty');
			}
			ngModelController.$setViewValue({
				current_file: attrs.currentFile
			});

			scope.uploadFile = function(file, id, model) {
				var data = {'file:0': file},
				    element = angular.element(document.querySelector('#' + id));
				Upload.upload({
					data: data,
					url: attrs.djngFileuploadUrl
				}).then(function(response) {
					var field = response.data['file:0'],
					    current = angular.isString(attrs.currentFile) ? {current_file: attrs.currentFile} : {};
					element.removeClass('uploading');
					element.css('background-image', field.url);
					element.removeClass('empty')
					delete field.url;  // we don't want to send back the whole image
					angular.extend(scope.$eval(model), field, current);
				}, function(respose) {
					element.removeClass('uploading');
					console.error(respose.statusText);
				});
			};
		}
	};
}]);

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
