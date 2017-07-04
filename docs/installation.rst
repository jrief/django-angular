.. _installation_and_configuration:

============
Installation
============
Install **Django-Angular**. The latest stable release can be found on PyPI

.. code-block:: bash

	pip install django-angular

or the newest development version from GitHub

.. code-block:: bash

	pip install -e git+https://github.com/jrief/django-angular#egg=django-angular


Dependencies
------------

**django-angular** has no dependencies to any other Django app. It however requires
that AngularJS is installed through other means than pip. The best solution is to
run:

.. code-block:: shell

	npm install angularjs@1.5 --save

in your project's root folder and add it to the Django's static files search path:

.. code-block:: shell

	npm install angularjs@1.5 --save

	STATICFILES_DIRS = [
	    ...
	    ('node_modules', /path/to/my-project-root/node_modules'),
	]

From the project's templates, you may refer the AngularJS files as:

.. code-block:: django

	<script src="{% static 'node_modules/angular/angular.js' %}" type="text/javascript">


Configuration
=============

Add ``'djng'`` to the list of ``INSTALLED_APPS`` in your project's ``settings.py`` file

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'djng',
	    ...
	)

Please don't forget to define your ``STATIC_ROOT`` and ``STATIC_URL`` properly, then
launch the ``python manage.py collectstatic`` command to update your static content
with the JavaScript files provided by **django-angular**.


Django-1.11
-----------

**Django**, since version 1.11, is shipped with an exchangeable widget rendering engine. This is a
great improvement for **django-angular**, since it doensn't have to override the widgets and its
renderers. Instead, your projects ``settings.py``, please use this configuration directive:

.. code-block:: python

	FORM_RENDERER = 'djng.forms.renderers.DjangoAngularBootstrap3Templates'

if templates shall be rendered with a Bootstrap3 grid, otherwise use:

.. code-block:: python

	FORM_RENDERER = 'djng.forms.renderers.DjangoAngularTemplates'


.. note:: **django-angular** does not define any database models. It can therefore easily be
          installed without any database synchronization.

.. _Django: http://djangoproject.com/
.. _AngularJS: http://angularjs.org/
.. _pip: http://pypi.python.org/pypi/pip
