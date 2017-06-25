(function(angular, undefined) {
'use strict';

var djngModule = angular.module('djng.forms-set', ['djng.forms']);


// Directive <ANY djng-forms-set upload-url="/rest/endpoint" ...>, optionally with a REST endpoint.
// Use this as a wrapper around self validating <form ...> or <ANY ng-form ...> elements (see directive below),
// so that we can disable the proceed button whenever one of those forms does not validate.
// For our form-set, such a submit button can be rendered as:
// <button ng-click="update(some_action)" ng-disabled="setIsValid===false">Submit</button>
djngModule.directive('djngFormsSet', function() {
	return {
		require: 'djngFormsSet',
		scope: true,
		controller: ['$scope', '$http', '$window', 'djangoForm', function($scope, $http, $window, djangoForm) {
			var self = this;

			// a map of booleans keeping the validation state for each of the child forms
			this.digestValidatedForms = {};

			// dictionary of form names mapping their model scopes
			this.digestUploadScope = {};

			// check each child form's $valid state and reduce it to one single state scope.setIsValid
			this.reduceValidation = function(formId, formIsValid) {
				self.digestValidatedForms[formId] = formIsValid;
				$scope.setIsValid = true;
				angular.forEach(self.digestValidatedForms, function(validatedForm) {
					$scope.setIsValid = $scope.setIsValid && validatedForm;
				});
			};

			this.uploadScope = function(method, action, extraData) {
				if (!self.uploadURL)
					throw new Error("Can not upload form data: Missing attribute 'upload-url'");

				// merge the data from various scope entities into one data object
				var data = {};
				if (extraData) {
					angular.merge(data, extraData);
				}
				angular.forEach(self.digestUploadScope, function(scopeModel) {
					var modelScope = {}, value = $scope.$eval(scopeModel);
					if (value) {
						modelScope[scopeModel] = value;
						angular.merge(data, modelScope);
					}
				});

				// submit data from all forms below this endpoint to the server
				$http({
					url: self.uploadURL,
					method: method,
					data: data
				}).then(function(response) {
					angular.forEach(self.digestUploadScope, function(scopeModel, formName) {
						if (!djangoForm.setErrors($scope[formName], response.errors)) {
							if (action === 'RELOAD_PAGE') {
								$window.location.reload();
							} else if (action !== 'DO_NOTHING') {
								if (response.data.success_url) {
									$window.location.assign(response.data.success_url);
								} else {
									$window.location.assign(action);
								}
							}
						}
					});
				}, function(response) {
					console.error(response);
				});
			};
		}],
		link: function(scope, element, attrs, formsSetController) {
			if (attrs.uploadUrl) {
				formsSetController.uploadURL = attrs.uploadUrl;
			}
		}
	};
});


// This directive enriches AngularJS's internal form-controllers if they are wrapped inside a <ANY djng-forms-set ...>
// directive. One purpose is to summarize the validity of the given forms, so that buttons rendered outside of the
// <form ...> elements but inside the <ANY djng-forms-set ...> element can check the validity of all forms using
// the scope attribute ``setIsValid``.
// Another purpose of this directive is to summarize the scope-models of the given forms, so that the scope can
// be uploaded to the endpoint URL using one submission.
// Usage: <form name="my_name" scope-model="my_data" novalidate> where `my_data` is used to access the form's
// data inside the scope.
djngModule.directive('form', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?djngFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var formsSetController = controllers[0], formController = controllers[1];

			if (!formsSetController)
				return;  // not for forms outside <ANY djng-forms-set></ANY djng-forms-set>

			if (attrs.name && attrs.scopeModel) {
				formsSetController.digestUploadScope[attrs.name] = attrs.scopeModel;
			}

			// create new isolated scope for this form
			scope = scope.$new(true);

			element.find('input').on('keyup change', function() {
				// delay until validation is ready
				$timeout(reduceValidation);
			});
			element.find('select').on('change', function() {
				$timeout(reduceValidation);
			});
			element.find('textarea').on('blur', function() {
				$timeout(reduceValidation);
			});

			// delay first evaluation until form is fully validated
			$timeout(reduceValidation);

			function reduceValidation() {
				formsSetController.reduceValidation(scope.$id, formController.$valid);
			}
		}
	};
}]);



// This directive enriches the button element if it is wrapped inside a <ANY djng-forms-set ...> directive.
// It adds three functions to its scope ``create``, ``update`` and ``delete`` which shall be used to invoke a POST,
// PUT or DELETE request on the forms-set endpoint URL.
// Optionally one can add ``extra-data="..."`` to this button element, in order to pass further information
// to the given endpoint.
djngModule.directive('button', function() {
	return {
		restrict: 'E',
		require: '^?djngFormsSet',
		scope: true,
		link: function(scope, element, attrs, formsSetController) {
			if (!formsSetController)
				return;  // not for buttons outside <ANY djng-forms-set></ANY djng-forms-set>

			scope.create = function(action) {
				formsSetController.uploadScope('POST', action, scope.djngExtraData);
			};

			scope.update = function(action) {
				formsSetController.uploadScope('PUT', action, scope.djngExtraData);
			};

			scope.delete = function(action) {
				formsSetController.uploadScope('DELETE', action, scope.djngExtraData);
			};

			if (attrs.extraData) {
				scope.djngExtraData = scope.$eval(attrs.extraData) || attrs.extraData;
			}
		}
	};
});


})(window.angular);
