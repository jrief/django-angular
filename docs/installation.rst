.. _installation_and_configuration:

============
Installation
============

Install **django-angular**. The latest stable release can be found on PyPI

.. code-block:: bash

	pip install django-angular


Change to the root directory of your project and install Node dependencies:

.. code-block:: bash

	npm init
	npm install angular@~1.5 --save


Dependencies
------------

**django-angular** has no dependencies to any other Django app, except ``easy-thumbnails`` and
``Pillow`` if using the image upload feature.

Projects using **django-angular** however require that AngularJS is installed through other means
than pip. The best solution is to run:

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

	INSTALLED_APPS = [
	    ...
	    'djng',
	    'easy_thumbnails',  # optional, if ImageField is used
	    ...
	]


Don't forget to define your ``STATIC_ROOT`` and ``STATIC_URL`` properly. Since we load JavaScript
and CSS files directly from our Node dependencies, add that directory to the static files search
path:

.. code-block:: python

	STATICFILES_DIRS = [
	    ('node_modules', os.path.join(PROJECT_DIR, 'node_modules')),
	]



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
