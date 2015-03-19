.. _angular-messages:

==================================================
Render Form field error lists in ngMessages format
==================================================

.. note:: This requires Angular 1.3+ and the ``angular-messages`` module - https://docs.angularjs.org/api/ngMessages


NgMessagesMixin
===============

The ``NgMessagesMixin`` mixin can be used in conjunction with other django-angular form mixins (``NgFormValidationMixin``
and ``NgModelFormMixin``) or on its own, to facilitate the rendering of form field error lists, in the
correct format for the ngMessages directive.

.. code-block:: python

	from django import forms
	from djangular.forms import NgForm, NgFormValidationMixin, NgMessagesMixin

	class MyNgMessagesForm(NgMessagesMixin, NgFormValidationMixin, NgForm):
		form_name = 'my_form'
		email = forms.EmailField(label='Email')
		
Then using ``{{ form.email.errors }}`` would output the following markup:

.. code-block:: html

	<ul class="djng-field-errors" ng-messages="my_form.email.$error" ng-show="my_form.$submitted || my_form.email.$dirty">
		<li ng-message="required" class="invalid">This field is required.</li>
		<li ng-message="email" class="invalid">Enter a valid email address.</li>
		<li ng-message="rejected" class="invalid">
			<span ng-bind="my_form.email.$message.rejected"></span>
		</li>
	</ul>
	
	
Handling Ajax form errors
.........................
	
The ``NgMessagesMixin`` also adds the ``djng-validate-rejected`` directive attribute to each form ``input``.
This directive handles the display of server side errors, by adding a ``rejected`` validator to the ``input``'s
``ngModel.$validators`` array.

.. code-block:: html

	<input id="id_email" name="email" ng-model="email" type="email" required="required" djng-validate-rejected>
	
The ``djngMessagesForm.setErrors`` method is then used to parse the errors from the server response, apply them
to the relevant fields ``field.$message.rejected`` property and call the fields ``$validate`` method to trigger
the rejected validator and display the error message.

.. code-block:: javascript

	.factory('myFormService', function($http, djngMessagesForm) {
		
		return {
			submit: function(data, form) {
				return $http.post('my/form/url', data)
							.success(function(response) {
								if(!djngMessagesForm.setErrors(form, response.errors)) {
									// we have no errors
								}
							})
			}
		}
	});

The markup below is a snippet of the ``{{ form.email.errors }}`` shown earlier. It shows the specific part that deals
with the display of the rejected error message. The ``<span>`` to bind to the value of ``my_form.email.$message.rejected``
and display the message is necessary due to the following bug/issue - https://github.com/angular/angular.js/issues/8089

.. code-block:: html

	<li ng-message="rejected" class="invalid">
		<span ng-bind="my_form.email.$message.rejected"> /* rejected error message will be displayed here */ </span>
	</li>


Use with other django-angular form mixins
...........................................

When using the ``NgMessagesMixin``, the form class must always inherit from ``NgMessagesMixin`` first.
Valid examples:

.. code-block:: python

	from django import forms
	from djangular.forms import NgForm, NgFormValidationMixin, NgMessagesMixin

	class MyNgMessagesForm(NgMessagesMixin, NgFormValidationMixin, NgForm):
		# custom form logic
		
Or

.. code-block:: python

	from django import forms
	from djangular.forms import NgForm, NgModelFormMixin, NgFormValidationMixin, NgMessagesMixin

	class MyNgMessagesForm(NgMessagesMixin, NgModelFormMixin, NgFormValidationMixin, NgForm):
		# custom form logic
		
But not

.. code-block:: python

	from django import forms
	from djangular.forms import NgForm, NgFormValidationMixin, NgMessagesMixin

	class MyNgMessagesForm(NgFormValidationMixin, NgMessagesMixin, NgForm):
		# custom form logic

.. note:: Depending on the combination of form mixins used, up to a 30% decrease in watchers can be achieved
	when using the ``NgMessagesMixin``

