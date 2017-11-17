.. _demos:

=================
Running the demos
=================

Shipped with this project, there are four demo pages, showing how to use the AngularJS validation
and data-binding mechanisms in combination with Django forms. Use them as a starting point for your
own application using **django-angular**.

To run the demos, change into the directory ``examples`` and start the development server:

.. code-block:: bash

	pip install -r requirements.txt
	./manage.py runserver

You can also run unit tests:

.. code-block:: bash

	py.test

or, even better

.. code-block:: bash

	tox

Now, point a browser onto one of

* http://localhost:8000/classic_form/
* http://localhost:8000/form_validation/
* http://localhost:8000/model_scope/
* http://localhost:8000/combined_validation/
* http://localhost:8000/threeway_databinding/


Classic Form
============
Classic Subscribe Form with no data validation.


Form Validation
===============

The *Form Validation* demo shows how to implement a Django form with enriched functionality to
add AngularJS's form validation in a DRY manner. This demo combines the classes
``NgFormValidationMixin`` with Django's ``forms.Form`` . This demo works without an AngularJS
controller.


Model Form
==========

The *Model Form* demo shows how to combine a Django form with ``NgFormValidationMixin``, which
creates an AngularJS model on the client in a DRY manner. This model, a Plain Old Javascript Object,
then can be used inside an AngularJS controller for all kind of purposes. Using an XMLHttpRequest,
this object can also be sent back to the server and bound to the same form is was created from.


Model Form Validation
=====================

The *Model Form Validation* shows how to combined both techniques from above, to create an AngularJS
model which additionally is validated on the client.


Three-Way Data-Binding
======================

*Three-Way Data-Binding* shows how to combine a Django form with ``NgFormValidationMixin``, so that
the form is synchronized by the server on all browsers accessing the same URL.

This demo is only available, if the external dependency `Websocket for Redis`_ has been installed.

.. _Websocket for Redis: https://pypi.python.org/pypi/django-websocket-redis


Artificial form constraints
===========================

These demos are all based on the same form containing seven different input fields: CharField,
RegexField (twice), EmailField, DateField, IntegerField and FloadField. Each of those fields has
a different constraint:

* *First name* requires at least 3 characters.
* *Last name* must start with a capital letter.
* *E-Mail* must be a valid address.
* *Phone number* can start with ``+`` and may contain only digits, spaces and dashes.
* *Birth date* must be a vaild date.
* *Weight* must be an integer between 42 and 95.
* *Height* must be a float value between 1.48 and 1.95.

Additionally there are two artificial constraints defined by the server side validation, which for
obvious reasons require a HTTP round trip in order to fail. These are:

* The full name may not be “John Doe”
* The email address may not end in “@example.com”, “@example.net” or similar.

If the client bypasses client-side validation by deactivating JavaScript, the server validation
still rejects these error. Using form validation this way, incorrect form values always are rejected
by the server.
