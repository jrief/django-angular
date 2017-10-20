.. _angular-form-validation:

=====================================
Validate Django forms using AngularJS
=====================================

Django's forms.Form_ class offers many possibilities to validate a given form. This, for obvious
reasons is done on the server. However, customers may not always accept to submit a form, just to
find out that they missed to input some correct data into a field. Therefore, adding client side
form validation is a good idea and very common. But since client side validation easily can be
bypassed, the same validation has to occur a second time, when the server accepts the forms data
for final processing.

*This leads to code duplication and generally violates the DRY principle!*


NgFormValidationMixin
=====================

A workaround to this problem is to use Django's form declaration to automatically generate client
side validation code, suitable for AngularJS. By adding a special mixin class to the form class,
this can be achieved automatically and on the fly

.. code-block:: python

	from django import forms
	from django.utils import six
	from djng.forms import fields, NgDeclarativeFieldsMetaclass, NgFormValidationMixin

	class MyValidatedForm(six.with_metaclass(NgDeclarativeFieldsMetaclass, NgFormValidationMixin, forms.Form)):
	    form_name = 'my_valid_form'
	    surname = fields.CharField(label='Surname', min_length=3, max_length=20)
	    age = fields.DecimalField(min_value=18, max_value=99)

.. note:: Since **django-angular**-1.1, you must use the adopted field classes, instead of Django's own ``fields``.

In the majority of cases, the Form is derived from Django's ``forms.Form``, so the above example
can be rewritten in a simpler way, by using the convenience class ``NgForm`` as a replacement:

.. code-block:: python

	from djng.forms import NgFormValidationMixin, NgForm
	
	class MyValidatedForm(NgFormValidationMixin, NgForm):
	    # members as above

If the Form shall inherit from Django's ``forms.ModelForm``, use the convenience class
``NgModelForm``:

.. code-block:: python

	from djng.forms import NgFormValidationMixin, NgModelForm
	
	class MyValidatedForm(NgFormValidationMixin, NgModelForm):
	    class Meta:
	         model = Article
	
	    # fields as usual

Each page under control of AngularJS requires a unique form name, otherwise the AngularJS's form
validation engine shows undefined behavior. Therefore you must name each form inheriting from
``NgFormValidationMixin``. If a form is used only once per page, the form's name can be added to
the class declaration, as shown above. If no form name is specified, it defaults to ``form``,
limiting the number of validated forms per page to one.

If a form inheriting from ``NgFormValidationMixin`` shall be instantiated more than once per page,
each instance of that form must be instantiated with a different name. This then must be done in
the constructor of the form, by passing in the argument ``form_name='my_form'``.

In the view class, add the created form to the rendering context:

.. code-block:: python

	def get_context_data(self, **kwargs):
	    context = super(MyRenderingView, self).get_context_data(**kwargs)
	    context.update(form=MyValidatedForm())
	    return context

or if the same form declaration shall be used more than once:

.. code-block:: python

	def get_context_data(self, **kwargs):
	    context = super(MyRenderingView, self).get_context_data(**kwargs)
	    context.update(form1=MyValidatedForm(form_name='my_valid_form1'),
	                   form2=MyValidatedForm(form_name='my_valid_form2'))
	    return context

.. note:: Do not use an empty ``label`` when declaring a form field, otherwise the class
          ``NgFormValidationMixin`` won't be able to render AngularJS's validation error elements.
          This also applies to ``auto_id``, which if False, will not include ``<label>`` tags while
          rendering the form.


Render this form in a template
------------------------------

.. code-block:: html

	<form name="{{ form.form_name }}" novalidate>
	  {{ form }}
	  <input type="submit" value="Submit" />
	</form>

Remember to add the entry ``name="{{ form.form_name }}"`` to the ``form`` element, otherwise AngularJS's
validation engine won't work. Use the directive ``novalidate`` to disable the browser’s native form
validation. If you just need AngularJS's built in form validation mechanisms without customized
checks on the forms data, there is no need to add an ``ng-controller`` onto a wrapping HTML element.
The only measure to take, is to give each form on a unique name, otherwise the AngularJS form
validation engine shows undefined behavior.

Forms which do not validate on the client, probably shall not be posted. This can simply be disabled
by replacing the submit button with the following HTML code:

.. code-block:: html

	<input type="submit" class="btn" ng-disabled="{{ form.form_name }}.$invalid" value="Submit">


More granular output
....................

If the form fields shall be explicitly rendered, the potential field validation errors can be
rendered in templates using a special field tag. Say, the form contains

.. code-block:: python

	from django import forms
	from djng.forms import fields, NgFormValidationMixin
	
	class MyValidatedForm(NgFormValidationMixin, forms.Form):
		email = fields.EmailField(label='Email')

then access the potential validation errors in templates using ``{{ form.email.errors }}``. This
renders the form with an unsorted list of potential errors, which may occur during client side
validation.

.. code-block:: html

	<ul class="djng-form-errors" ng-hide="subscribe_form.email.$pristine">
	  <li ng-show="subscribe_form.email.$error.required" class="ng-hide">This field is required.</li>
	  <li ng-show="subscribe_form.email.$error.email" class="">Enter a valid email address.</li>
	</ul>

The AngularJS form validation engine, normally hides these potential errors. They only become
visible, if the user enters an invalid email address.


Bound forms
...........

If the `form is bound`_ and rendered, then errors detected by the server side's validation code are
rendered as unsorted list in addition to the list of potential errors. Both of these error lists are
rendered using their own ``<ul>`` elements. The behavior for potential errors remains the same, but
detected errors are hidden the moment, the user sets the form into a dirty state.

.. note:: AngularJS normally hides the content of bound forms, which means that ``<input>`` fields
          seem empty, even if their ``value`` attribute is set. In order to restore the content of
          those input fields to their default value, initialize your AngularJS application with
          ``angular.module('MyApp', ['djng.forms']);``.


Combine NgFormValidationMixin with NgModelFormMixin
---------------------------------------------------

While it is possible to use ``NgFormValidationMixin`` on itself, it is perfectly legal to mix
``NgModelFormMixin`` with ``NgFormValidationMixin``. However, a few precautions have to be taken.

On class declaration inherit first from ``NgModelFormMixin`` and *afterward* from
``NgFormValidationMixin``. Valid example:

.. code-block:: python

	from django import forms
	from djng.forms import NgFormValidationMixin, NgModelFormMixin
	
	class MyValidatedForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
	    # custom form fields

but don't do this

.. code-block:: python

	class MyValidatedForm(NgFormValidationMixin, NgModelFormMixin, forms.Form):
	    # custom form fields

Another precaution to take, is to use different names for the forms name and the ``scope_prefix``.
So, this is legal

.. code-block:: python

	form = MyValidatedForm(form_name='my_form', scope_prefix='my_model')

but this is not

.. code-block:: python

	form = MyValidatedForm(form_name='my_form', scope_prefix='my_form')


An implementation note
......................

AngularJS names each input field to validate, by concatenating its forms name with its fields name.
This object member then contains an error object, named ``my_form.field_name.$error`` filled by
the AngularJS validation mechanism. The placeholder for the error object would clash with
``ng-model``, if the form name is identical to the scope prefix. Therefore, just remember to use
different names.


Customize detected and potential validation errors
==================================================

If a form with AngularJS validation is rendered, each input field is prefixed with an unsorted list
``<ul>`` of potential validation errors. For each possible constraint violation, a list item
``<li>`` containing a descriptive message is added to that list.

If a client enters invalid data into that form, AngularJS unhides one of these prepared error
messages, using ng-show_. The displayed message text is exactly the same as would be shown if
the server side code complains about invalid data during form validation. These prepared error
messages can be customized during `form field definition`_.

The default error list is rendered as ``<ul class="djng-form-errors">...</ul>``. To each ``<li>``
of this error list, the attribute ``class="invalid"`` is added. The last list-item
``<li class="valid"></li>`` is somehow special, as it is only visible if the corresponding input
field contains valid data. By using special style sheets, one can for instance add a green
tick after a validated input field, to signal that everything is OK.

The styling of these validation elements must be done through CSS, for example with:

.. code-block:: css

	ul.djng-form-errors {
		margin-left: 0;
		display: inline-block;
		list-style-type: none;
	}
	ul.djng-form-errors li.invalid {
		color: #e9322d;
	}
	ul.djng-form-errors li.invalid:before {
		content: "\2716\20";  /* adds a red cross before the error message */
	}
	ul.djng-form-errors li.valid:before {
		color: #00c900;
		content: "\2714";  /* adds a green tick */
	}

If you desire an alternative CSS class or an alternative way of rendering the list of errors, then
initialize the form instance with

.. code-block:: python

	class MyErrorList(list):
	    # rendering methods go here
	
	# during form instantiation
	my_form = MyForm(error_class=MyErrorList)

Refer to ``TupleErrorList`` on how to implement an alternative error list renderer. Currently this
error list renderer, renders two ``<ul>``-elements for each input field, one to be shown for
*pristine* forms and one to be shown for *dirty* forms.


Adding an AngularJS directive for validating form fields
--------------------------------------------------------

Sometimes it can be useful to add a generic field validator on the client side, which can be
controlled by the form's definition on the server. One such example is Django's DateField:

.. code-block:: python

	from django import forms
	
	class MyForm(forms.Form):
	    # other fields
	    date = forms.DateField(label='Date',
	        widget=forms.widgets.DateInput(attrs={'validate-date': '^(\d{4})-(\d{1,2})-(\d{1,2})$'}))

Since AngularJS can not validate dates, such a field requires a customized directive, which with
the above definition, will be added as new attribute to the input element for date:

.. code-block:: html

	<input name="date" ng-model="my_form_data.birth_date" type="text" validate-date="^(\d{4})-(\d{1,2})-(\d{1,2})$" />

If your AngularJS application has been initialized with

.. code-block:: javascript

	angular.module('MyApp', ['djng.forms']);

then this new attribute is detected by the AngularJS directive ``validateDate``, which in turn
checks the date for valid input and shows the content of the errors fields, if not.

If you need to write a reusable component for customized form fields, refer to that directive as a
starting point.

.. _forms.Form: https://docs.djangoproject.com/en/dev/topics/forms/#form-objects
.. _form field definition: https://docs.djangoproject.com/en/dev/ref/forms/fields/#error-messages
.. _ng-show: http://docs.angularjs.org/api/ng.directive:ngShow
.. _form is bound: https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.BoundField.errors
