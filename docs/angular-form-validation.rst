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
	from djangular.forms import NgFormValidationMixin
	
	class MyValidatedForm(NgFormValidationMixin, forms.Form):
	    surname = forms.CharField(label='Surname', min_length=3, max_length=20)
	    age = forms.DecimalField(min_value=18, max_value=99)

When initializing this form, give it a name, otherwise it's name defaults to ``form``. Such a form
name is required by the AngularJS's validation engine.

.. note:: Do not use an empty ``label`` when declaring a form field, otherwise the class
          ``NgFormValidationMixin`` won't be able to render AngularJS's validation error elements.
          This also applies to ``auto_id``, which if False, will not include ``<label>`` tags while
          rendering the form.

In the view class, add the created form to the rendering context

.. code-block:: python

	def get_context_data(self, **kwargs):
	    context = super(MyRenderingView, self).get_context_data(**kwargs)
	    context.update(form=MyValidatedForm())
	    return context

Render this form in a template
------------------------------

.. code-block:: html

	<form name="{{ form.name }}" novalidate>
	  {{ form }}
	  <input type="submit" value="Submit" />
	</form>

Remember to add the entry ``name="{{ form.name }}"`` to the ``form`` element. Use the directive
``novalidate`` to disable the browser’s native form validation. If you just need AngularJS's built
in form validation mechanisms without customized checks on the forms data, there is no need to add
an ``ng-controller`` onto a wrapping HTML element. The only measure to take, is to give each
form on a unique name, otherwise the AngularJS form validation code might get confused.

.. note:: On Django-1.5, some field constraints, such as the attributes ``min_length`` and
		``max_length``, are ignored when used with this Mixin. In Django-1.6 this has been fixed.

More granular output
....................
If the form fields shall be explicitly rendered, the potential field validation errors can be
rendered in templates using a special field tag. Say, the form contains

.. code-block:: python

	from django import forms
	from djangular.forms import NgFormValidationMixin
	
	class MyValidatedForm(NgFormValidationMixin, forms.Form):
	    email = forms.EmailField(label='Email')

then access the potential validation errors in templates using ``{{ form.email.ng_errors }}``. This
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
          ``angular.module('MyApp', ['ng.django.forms']);``.


Combine NgFormValidationMixin with NgModelFormMixin
---------------------------------------------------
While it is possible to use ``NgFormValidationMixin`` on itself, it is perfectly legal to mix
``NgModelFormMixin`` with ``NgFormValidationMixin``. However, a few precautions have to be taken.

On class declaration inherit first from ``NgModelFormMixin`` and *afterward* from
``NgFormValidationMixin``. Valid example:

.. code-block:: python

	from django import forms
	from djangular.forms import NgFormValidationMixin, NgModelFormMixin
	
	class MyValidatedForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
	    pass

but don't do this

.. code-block:: python

	class MyValidatedForm(NgFormValidationMixin, NgModelFormMixin, forms.Form):
	    pass

Another precaution to take, is to use different names for the forms name and the ``scope_prefix``.
So, this is legal

.. code-block:: python

	form = MyValidatedForm(name='my_form', scope_prefix='my_model')

but this is not

.. code-block:: python

	form = MyValidatedForm(name='my_form', scope_prefix='my_form')

AngularJS names each input field to validate, by concatenating its forms name with its fields name.
This object member then contains an error object, named ``formname.fieldname.$error`` filled by the
AngularJS validation mechanism. The placeholder for the error object would clash with ``ng-model``,
if the forms name is identical to the model prefix. Therefore, remember to use different names.


Customize detected and potential validation errors
==================================================
If a form with AngularJS validation is rendered, each input field is prefixed with an unsorted list
``<ul>`` of potential validation errors. For each possible constraint violation, a list item
``<li>`` containing a descriptive message is added to that list.

If a client enters invalid data into that form, AngularJS unhides one of these prepared error
messages, using ng-show_. The displayed message text is exactly the same as would be shown if
the server side code complains about invalid data during form validation. These prepared error
messages can be customized during `form field definition`_.

The default error list is rendered as ``<ul class="djng-form-errors">...</ul>``. If you desire an
alternative CSS class or an alternative way of rendering the list of errors, then initialize the
form instance with

.. code-block:: python

	class MyErrorList(list):
	    # rendering methods go here
	
	# during form instantiation
	my_form = MyForm(ng_validation_error_class=MyErrorList)

Refer to ``TupleErrorList`` on how to implement an error list renderer.


Adding form validation to customized fields
-------------------------------------------
Django's form validation is not 100% compatible with AngularJS's validation. Therefore **djangular**
is shipped with a mapping module to translate Django's form validation to AngularJS. This module
is located in ``djangular.forms.patched_fields``.

If you need to add or to replace any of these mappings, create a Python module which implements an
alternative mapping to the module shipped with **djangular**. Refer to an alternative module in your
``settings.py`` with the configuration directive ``DJANGULAR_VALIDATION_MAPPING_MODULE``.


Demos
=====
There are three forms using the AngularJS validation mechanisms.

*Simple Form* shows how to implement a Django form with augmented functionality to add AngularJS's
form validation in a DRY manner using the class ``NgFormValidationMixin``. This application does
not require an AngularJS controller.

*Model Form* show how to mix ``NgModelFormMixin`` with ``NgFormValidationMixin``. This demo shows
how to add an AngularJS controller to a managed form.

*Three-Way Data-Binding* shows a full working example of a form synchronized by the server with all
browsers accessing the same URL.

To test this code, a small demo is supplied with this package. With Django >= 1.5 installed, it
should run out of the box.

* Change into the directory ``examples``
* run ``./manage.py runserver``
* point your browser onto one of

  * http://localhost:8000/simple_form/
  * http://localhost:8000/model_form/
  * http://localhost:8000/threeway_databinding/

Start to fill out the fields. 

* *First name* requires at least 3 characters.
* *Last name* must start with a capital letter.
* *E-Mail* must be a valid address.
* *Phone number* can start with ``+`` and may contain only digits, spaces and dashes.

Incorrect input is handled by AngularJS's form validation engine. For simulation purpose, a server
side validation has been added, which disallows the use of email addresses containing
``recipient@example.tld`` and the combination of *“John Doe”* for the first- and last name. A
violation of the latter results in non-field errors, displayed independently of any field.

.. _forms.Form: https://docs.djangoproject.com/en/dev/topics/forms/#form-objects
.. _form field definition: https://docs.djangoproject.com/en/dev/ref/forms/fields/#error-messages
.. _ng-show: http://docs.angularjs.org/api/ng.directive:ngShow
.. _form is bound: https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.BoundField.errors
