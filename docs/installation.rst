.. _installation_and_configuration:

============
Installation
============

Install **django-angular**. The latest stable release can be found on PyPI

.. code-block:: bash

	pip install django-angular


Change to the root directory of your projects and install Node dependencies:

.. code-block:: bash

	npm init
	npm install angular@~1.5 --save


Configuration
=============

Add ``'djng'`` to the list of ``INSTALLED_APPS`` in your project's ``settings.py`` file

.. code-block:: python

	INSTALLED_APPS = [
	    ...
	    'djng',
	    ...
	]


Don't forget to define your ``STATIC_ROOT`` and ``STATIC_URL`` properly. Since we load JavaScript and CSS files
directly from our Node dependencies, add that directory to the static files search path:

.. code-block:: python

	STATICFILES_DIRS = [
	    ('node_modules', os.path.join(PROJECT_DIR, 'node_modules')),
	]


.. note:: **django-angular** does not define any database models. It can therefore easily be
        installed without any database synchronization.

.. _Django: http://djangoproject.com/
.. _AngularJS: http://angularjs.org/
.. _pip: http://pypi.python.org/pypi/pip
