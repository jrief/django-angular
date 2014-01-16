.. _angular-form-validation:

=====================================
Validate Django forms using AngularJS
=====================================

Django's ``forms.Form`` class offers many possibilities to validate a given form. This, for obvious
reasons is done on the server. However, customers may not always accept to submit a form, just to
find out that they missed to input some correct data into a field. Therefore, adding client side
form validation is a good idea and very common. But since client side validation easily can be
bypassed, the same validation has to occur a second time, when the server accepts the forms data
for final processing.

*This leads to code duplication and generally violates the DRY principle!*

NgFormValidationMixin
---------------------
A workaround to this problem is to use Django's form declaration to automatically generate client
side validation code, suitable for AngularJS. By adding a special mixin class to the form class,
this can be achieved automatically and on the fly::

	from django import forms
	from djangular.forms import NgFormValidationMixin
	
	class MyValidatedForm(NgFormValidationMixin, forms.Form):
	    surname = forms.CharField(label='Surname', min_length=3, max_length=20)
	    age = forms.DecimalField(min_value=18, max_value=99)

When initializing this form, give it a name, otherwise the form's name defaults to "form". This is
required, since the AngularJS validation code expects a named form.

In the view class, add the created form to the rendering context::

	def get_context_data(self, **kwargs):
	    context = super(MyRenderingView, self).get_context_data(**kwargs)
	    context.update(form=MyValidatedForm())
	    return context

Render this form in a template:

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

Combining NgFormValidationMixin with NgModelFormMixin
-----------------------------------------------------
While it is possible to use ``NgFormValidationMixin`` on itself, it is perfectly legal to mix
``NgModelFormMixin`` with ``NgFormValidationMixin``. However, a few precautions have to be taken.

On class declaration inherit first from ``NgModelFormMixin`` and *afterward* from
``NgFormValidationMixin``. Valid example::

	from django import forms
	from djangular.forms import NgFormValidationMixin, NgModelFormMixin
	
	class MyValidatedForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
	    pass

but don't do this::

	class MyValidatedForm(NgFormValidationMixin, NgModelFormMixin, forms.Form):
	    pass

Another precaution to take, is to use different names for the forms name and the ``scope_prefix``.
So, this is legal::

	form = MyValidatedForm(name='my_form', scope_prefix='my_model')

but this is not::

	form = MyValidatedForm(name='my_form', scope_prefix='my_form')

AngularJS names each input field to validate, by concatenating its forms name with its fields name.
This object member then contains an error object, named ``formname.fieldname.$error`` filled by the
AngularJS validation mechanism. The placeholder for the error object would clash with ``ng-model``,
if the forms name is identical to the model prefix. Therefore, remember to use different names.

Customizing validation errors
-----------------------------
If a validated Django form is rendered, each input field is prefixed with an unsorted list ``<ul>``
of errors, one list item ``<li>`` for each constraint, which might not be satisfied during
validation. Now, if a client enters invalid data, these prepared error messages are made visible
using ng-show_. The message text is exactly the same as would be shown if the server side, ie.
Django itself, complains about invalid data. These error messages can be customized during the field
initialization.

The default error list is rendered as ``<ul class="djng-form-errors">...</ul>``. If an alternative
CSS class is desired, initialize the form using the optional argument
``form_error_class='my-error-class'``.

Demo
----
There are two forms using the AngularJS validation mechanisms, one with and one without using the
additional ``NgModelFormMixin``. The former displays the entered model data as a simple code object.

To test this code, a small demo is supplied with this package. With Django >= 1.5 installed, it
should run out of the box. Just change into the directory ``examples``, run ``./manage.py runserver``
and point your browser onto http://localhost:8000/simple_form/ or http://localhost:8000/model_form/

Start to fill out the fields. *First name* requires at least 3 characters; *Last name* must start
with a capital letter; *E-Mail* must be a valid address; *Phone number* can start with ``+`` and
may contain only digits, spaces and dashes.

.. _ng-show: http://docs.angularjs.org/api/ng.directive:ngShow