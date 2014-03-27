
// this directive can be added to an input field which shall validate inserted dates, for example:
// <input ng-model="a_date" type="text" validate-date="^(\d{4})\/(\d{1,2})\/(\d{1,2})$" />
// Now, this field is considered valid only if the date is valid and matches the given regular
// expression.
my_app.directive('validateDate', function() {
	var validDatePattern = null;

	function validateDate(date) {
		var matched, dateobj;
		if (!date) // empty field are validated by the required validator
			return true;
		dateobj = new Date(date);
		matched = validDatePattern ? Boolean(date.match(validDatePattern)) : true;
		return matched && !isNaN(dateobj);
	}

	return {
		require: 'ngModel',
		restrict: 'A',
		link: function(scope, elem, attrs, controller) {
			if (attrs.validateDate) {
				// if a pattern is set, only valid dates with that pattern are accepted
				validDatePattern = new RegExp(attrs.validateDate, 'g');
			}

			// watch for modifications on input fields containing attribute 'validate-date="/pattern/"'
			scope.$watch(attrs.ngModel, function(date) {
				if (controller.$pristine)
					return;
				controller.$setValidity('date', validateDate(date));
			});
		}
	}
});
