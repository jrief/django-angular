.. _reverse-urls:

================================
Manage Django URLs for AngularJS
================================

AngularJS controllers communicating with the Django application through Ajax, often require URLs, pointing
to some of the views of your application. Do not enter into temptation to hard code such a URL into the
client side controller code. Even worse would be to create Javascript dynamically using a template
engine. There is a clean and simple solution to solve this problem.

.. note:: With version 0.8 **django-angular** introduced a new way to handle urls. Documentation for now
          deprecated approach is available :ref:`here <manage-urls>`.


Installation
============

Django settings
---------------

* Add ``'djangular.middlewares.DjangularUrlMiddleware'`` to ``MIDDLEWARE_CLASSES`` in django settings

.. code-block:: python

    MIDDLEWARE_CLASSES = (
        'djangular.middlewares.DjangularUrlMiddleware',
        # Other middlewares
    )

.. warning:: This must be the first middleware included in ``MIDDLEWARE_CLASSES``


Angular
-------

* Include ``django-angular.js``:

.. code-block:: html

    <script src="{% static 'djangular/js/django-angular.js' %}"></script>

* Add ``ng.django.urls`` as a dependency for you app:

.. code-block:: html

    <script>
        var my_app = angular.module('MyApp', ['ng.django.urls', /* other dependencies */]);
    </script>

The ``djangoUrl`` service is now available through `dependency injection`_
to all directives and controllers.

Usage
=====
The reversing functionality is provided by ``djangoUrl.reverse(name, args_or_kwargs)`` method. It behaves
exactly like Django's `URL template tag`_.


Parameters
----------
name
    The url name you wish to reverse, exactly the same as what you would use in ``{% url %}`` template tag.
args_or_kwargs (optional)
    An array of arguments, e.g. ``['article', 4]`` or an object of keyword arguments,
    such as ``{'type': 'article', 'id': 4}``.

Example
-------
.. code-block:: javascript

    my_app.controller('MyCtrl', function($http, djangoUrl) {
        $http.get(djangoUrl.reverse('api:articles', [1])));
        // or with kwargs
        $http.get(djangoUrl.reverse('api:articles', {'id': 1});
    });

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _dependency injection: http://docs.angularjs.org/guide/di
.. _URL template tag : https://docs.djangoproject.com/en/dev/ref/templates/builtins/#url
