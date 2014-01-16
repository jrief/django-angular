.. _installation_and_configuration:

Project's home
==============
Check for the latest release of this project and report bugs on `Github`_.

Installation
============
Install **Django-Angular**. The latest stable release can be found on PyPI::

	pip install django-angular

or the newest development version from GitHub::

	pip install -e git+https://github.com/jrief/django-angular#egg=django-angular

Dependencies
------------

* `Django`_ >=1.3.1
* `AngularJS`_ >=1.0.4

Configuration
=============

Add ``'djangular'`` to the list of ``INSTALLED_APPS`` in your project's ``settings.py`` file::

  INSTALLED_APPS = (
      ...
      'djangular',
      ...
  )

.. note:: **django-angular** does not define any database models. It can therefore easily be
          installed without any database synchronization.

.. _Github: https://github.com/jrief/django-angular
.. _Django: http://djangoproject.com/
.. _AngularJS: http://angularjs.org/
.. _pip: http://pypi.python.org/pypi/pip
