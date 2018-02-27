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
			ngModelController.$setViewValue({});
			element.data('area_label', element.val());
			if (attrs.currentFile) {
				angular.extend(scope.$eval(attrs.ngModel), {current_file: attrs.currentFile});
				element.data('current_file', attrs.currentFile);
				element.val(attrs.currentFile.substring(0, attrs.currentFile.indexOf(':')));
				element.addClass('djng-preset');
			} else {
				element.addClass('djng-empty');
			}

			scope.uploadFile = function(file, filetype, id, model) {
				var data = {'file:0': file, filetype: filetype},
				    element = angular.element(document.querySelector('#' + id));
				element.addClass('uploading');
				Upload.upload({
					data: data,
					url: attrs.djngFileuploadUrl
				}).then(function(response) {
					var field = response.data['file:0'];
					var cf = element.data('current_file');
					element.removeClass('uploading');
					if (!field)
						return;
					element.css('background-image', field.url);
					element.removeClass('djng-empty');
					element.removeClass('djng-preset');
					element.val(field.file_name);
					delete field.url;  // we don't want to send back the whole image
					angular.extend(scope.$eval(model), field, cf ? {current_file: cf} : {});
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
			scope.deleteImage = function(id, _model) {
				var model = scope.$eval(_model),
				    element = angular.element(document.querySelector('#' + id));
				element.css('background-image', 'none');
				element.addClass('djng-empty');
				element.removeClass('djng-preset');
				element.val(element.data('area_label'));
				if (model) {
					model.temp_name = 'delete';  // tags previous image for deletion
				}
			};
		}
	};
});

})(window.angular);
