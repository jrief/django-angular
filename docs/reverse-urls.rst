.. _reverse-urls:

=================================
Manage Django URL's for AngularJS
=================================

You may have noticed, that AngularJS controllers sometimes need a URL pointing to a Django view of
your application. Do not enter into temptation to hard code such a URL into the client side
controller code. Nor enter into temptation to create Javascript dynamically using a template
engine. There is a clean and simple solution to solve this problem.

.. note:: With version 0.8 **django-angular** introduced a new way to handler urls. Documentation for now deprecated
          approach is available here: :ref:`here <manage-urls>`.

Installation
============

First there is some configuration required on server side.

1. Add ``'djangular.middlewares.DjangularUrlMiddleware'`` to ``MIDDLEWARE_CLASSES`` in django settings

.. warning:: This must be the first middleware included in ``MIDDLEWARE_CLASSES``

2. Include ``django-angular`` urls into the root url configuration

.. code-block:: python

    urlpatterns = patterns('',
    url(r'^djangular/', include('djangular.urls', namespace='djangular')),
    # Other urls
    )

To use the ``djangoUrl`` service you first have to include ``django-angular.js``:

.. code-block:: html

    <script src="{% static 'djangular/js/django-angular.js' %}"></script>

And add ``ng.django.urls`` as a dependency for you app:

.. code-block:: html

    <script>
        var my_app = angular.module('MyApp', ['ng.django.urls', /* other dependencies */]);
    </script>

The ``djangoUrl`` service is then available through `dependency injection`_
to all directives and controllers.

Usage
=====
The reversing functionality is provided by ``djangoUrl.reverse(name, args_or_kwargs)`` method. It behaves exactly like the
django's url template tag.

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
	    $http.post(djangoUrl.reverse('api:articles', [1])));
	    // or with kwargs
        $http.post(djangoUrl.reverse('api:articles', {'id': 1})
	});

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _dependency injection: http://docs.angularjs.org/guide/di
