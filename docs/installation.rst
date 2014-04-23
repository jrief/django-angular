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

* `Django`_ >=1.5
* `AngularJS`_ >=1.2

Configuration
=============

Add ``'djangular'`` to the list of ``INSTALLED_APPS`` in your project's ``settings.py`` file

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'djangular',
	    ...
	)

.. note:: **django-angular** does not define any database models. It can therefore easily be
          installed without any database synchronization.

.. note:: don't forget to define your ``STATIC_ROOT`` and ``STATIC_URL`` properly, then
          launch the ``python manage.py collectstatic`` command to update your
          static content with the javascript files provided by django-angular

.. _Django: http://djangoproject.com/
.. _AngularJS: http://angularjs.org/
.. _pip: http://pypi.python.org/pypi/pip
