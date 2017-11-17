.. _tutorial-forms:

=====================================
Tutorial: Django Forms with AngularJS
=====================================

Django offers an excellent Form framework which is responsible for rendering and validating HTML
forms. Since Django's design philosophy is to be independent of the styling and JavaScript, this
Form framework requires some adoption in order to play well with AngularJS and optionally Bootstrap.

A common technique to adopt the styling of a Django Form, is to extend the template so that each
Form field is rendered by hand written HTML. This of course leads to code duplication and is a
violation of the DRY principle.

An alternative technique is to add crispy-forms_ to your project and enrich the Django Forms with a
helper class. Unfortunately, **crispy-form** does not work very well with **django-angular**. In
order to add the same functionality in a “DRY” manner, a special Mixin class can be added to your
forms, rather than having to work with helper-classes.

This tutorial attempts to explain how to combine the Django Form framework in combination with
AngularJS and Bootstrap.

.. _crispy-forms: http://django-crispy-forms.readthedocs.org/


Basic Form Submission
=====================

Lets start with a very basic example, a functioning demo is available here: http://django-angular.awesto.com/classic_form/

Say, we have a simple but rather long Form definition, to subscribe a person wanting to visit us:

.. literalinclude:: ../examples/server/forms/subscribe_form.py
    :linenos:
    :language: python
    :lines: 2, 6, 16-50

Since we want to render this form in a DRY manner, our favorite template syntax is something such
as:

.. code-block:: html

	<form name="{{ form.form_name }}" method="post" action=".">
		{% csrf_token %}
		{{ form }}
		<input type="submit" value="Subscribe">
	</form>

In this example, the whole form is rendered in one pass including all HTML elements, such as
``<label>``, ``<select>``, ``<option>`` and ``<input>``. Additionally, bound forms are rendered with
their preset values and a list of errors, if the previous Form validation did not succeed.

The Django Form framework comes with three different rendering methods: ``as_p()``, ``as_ul()`` and
``as_table()`` (the default). Unfortunately, these three rendering methods are not suitable for
nowadays needs, such as Bootstrap styling and Ajax based Form validation.

In order to be more flexible without having to abandon the “DRY” principle, the above
``SubscriptionForm`` has been enriched by the Mixin class ``Bootstrap3FormMixin``. This class adds
an additional method ``as_div()``, which is responsible for rendering the Form suitable for Bootstrap
styling.

Additionally, this Mixin class wraps the list of validation errors occurred during the last Form
validation into the AngularJS directive ``ng-show``, so that error messages disappear after the
user starts typing, and thus puts the Form into a “dirty”, or in other words “non-pristine”, state.

You can test this yourself, by leaving out some fields or entering invalid values and submitting
the Form.


Bound Form in AngularJS
-----------------------

AngularJS does not take into account the concept of bound Forms. Therefore, input fields rendered
with preset values, are displayed as empty fields. To circumvent this, the **django-angular**
Form directive re-enables the rendering of the bound field values.


Dynamically Hiding Form Fields for Bootstrap
--------------------------------------------

A common use case is to hide a form field based on the value of another. For example, to hide the
``phone`` field if the user selects *Female* within ``SubscriptionForm``, overwrite
``field_css_classes`` on ``SubscriptionForm``:

.. code-block:: python

	field_css_classes = {
	    '*': 'form-group has-feedback',
	    'phone': "ng-class:{'ng-hide':sex==='f'}",
	}

``field_css_classes`` adds css classes to the wrapper div surrounding individual fields in bootstrap.
In the above example, ``'*'`` adds the classes ``form-group has-feedback`` to all fields within the
form and ``'ng-class:{"ng-hide":sex==="f"}'`` is added only to the ``phone`` field. Only Angular
directives that can be used as CSS classes are allowed within ``field_css_classes``.  Additionally,
if specified as a string, the string may not contain any spaces or double quotes. However, if
specified as a list, spaces can be used, and the above example can be rewritten as:

.. code-block:: python

	field_css_classes = {
	    '*': 'form-group has-feedback',
	    'phone': ["ng-class: {'ng-hide': sex==='f'};"],
	}

By adding the keyword ``'__default__'`` to this list, the CSS classes for the default entry,
ie. ``'*'``, are merged with the CSS classes for the current field.


Adding an asterisk for required fields
--------------------------------------

An asterisk is often added after labels on required fields (like with django-crispy-forms for
example). This can be accomplished by using native Django and CSS. To do this, set the
``required_css_class attribute`` on ``SubscriptionForm`` (see `Django documentation`_).

.. _Django documentation: https://docs.djangoproject.com/en/stable/ref/forms/api/#django.forms.Form.required_css_class

.. code-block:: python

	required_css_class = 'djng-field-required'

Next, add the *CSS*:

.. code-block:: css

	label.djng-field-required::after {
	    content: "\00a0*";
	}


Client-side Form validation
===========================

To enable client-side Form validation, simply add the mixin class ``NgFormValidationMixin`` to
the ``SubscriptionForm`` class:

.. code-block:: python

	class SubscriptionForm(NgFormValidationMixin, Bootstrap3FormMixin, forms.Form):
	    # form fields as usual

Here the rendered Form contains all the AngularJS directives as required for client side Form
validation. If an entered value does not match the criteria as defined by the definition of
``SubscriptionForm``, AngularJS will notify the user immediately
