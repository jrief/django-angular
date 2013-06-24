.. _installation_and_configuration:

Installation and Configuration
==============================

Getting the latest release
--------------------------

The easiest way to get ``django-angular`` is simply to install it with `pip`_::

    $ pip install django-angular

Please also check the latest sourcecode from `github`_.

Dependencies
------------

* `Django`_ >=1.3.1
* `AngularJS`_ >=1.0.4

Configuration
-------------

Add ``"djangular"`` to your project's ``INSTALLED_APPS`` setting, and make sure that static files
are found in external Django apps::

  INSTALLED_APPS = (
      ...
      'djangular',
      ...
  )
  
  STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ...
  )

.. note:: **django-angular** does not define any database models. It can therefore easily be
          installed without any database synchronization.

.. _github: https://github.com/jrief/django-angular
.. _Django: http://djangoproject.com/
.. _AngularJS: http://angularjs.org/
.. _pip: http://pypi.python.org/pypi/pip
