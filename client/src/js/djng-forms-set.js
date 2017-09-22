(function(angular, undefined) {
'use strict';

var djngModule = angular.module('djng.forms-set', ['djng.forms']);


// Directive ``<ANY djng-forms-set endpoint="/rest/endpoint" ...>``, the REST endpoint.
// Use this as a wrapper around self validating <form ...> or <ANY ng-form ...> elements (see
// directive below), so that we can use a proceed/submit button outside of the ``<form ...>`` elements.
// Whenever one of those forms does not validate, that button can be rendered as:
// ``<button ng-click="update(some_action)" ng-disabled="setIsInvalid">Submit</button>``
djngModule.directive('djngFormsSet', function() {
	return {
		require: 'djngFormsSet',
		controller: 'FormUploadController',
		link: function(scope, element, attrs, formsSetController) {
			if (!attrs.endpoint)
				throw new Error("Attribute 'endpoint' is not set!");

			formsSetController.endpointURL = attrs.endpoint;
		}
	};
});


// This directive enriches AngularJS's internal form-controllers if they are wrapped inside a <ANY djng-forms-set ...>
// directive. One purpose is to summarize the validity of the given forms, so that buttons rendered outside of the
// <form ...> elements but inside the <djng-forms-set ...> element can check the validity of all forms using.
// For this check, the scope provides the attributes ``setIsValid`` and ``setIsInvalid`` which shall be used
// inside the submission button:
// ``<button type="button" ng-disabled="setIsInvalid" ng-click="update()">Submit</button>``
// Another purpose of this directive is to summarize the scope-models of the given forms, so that the scope can
// be uploaded to the endpoint URL using one submission.
djngModule.directive('form', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?djngFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var formsSetController = controllers[0], formController = controllers[1];

			if (!formsSetController)
				return;  // not for forms outside <ANY djng-forms-set></ANY djng-forms-set>

			if (!attrs.name)
				throw new Error("Each <form> embedded inside a <djng-forms-set> must identify itself by name.")

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

			element.on('$destroy', function() {
				element.find('input').off('keyup change');
				element.find('select').off('keyup change');
				element.find('textarea').off('blur');
			});

			// delay first evaluation until form is fully validated
			$timeout(reduceValidation);

			// check each child form's $valid state and reduce it to one single state scope.setIsValid
			function reduceValidation() {
				formsSetController.digestValidatedForms[formController.$name] = formController.$valid;
				scope.setIsValid = true;
				angular.forEach(formsSetController.digestValidatedForms, function(validatedForm) {
					scope.setIsValid = scope.setIsValid && validatedForm;
				});
				scope.setIsInvalid = !scope.setIsValid;
			}

		}
	};
}]);


})(window.angular);
