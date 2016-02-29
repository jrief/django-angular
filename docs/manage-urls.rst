.. _manage-urls:

=================================
Manage Django URL's for AngularJS
=================================

.. warning::
   This is now a deprecated way of handling Django urls for AngularJS. For current
   approach see :ref:`updated docs <reverse-urls>`.

You may have noticed, that AngularJS controllers sometimes need a URL pointing to a Django view of
your application. Do not enter into temptation to hard code such a URL into the client side
controller code. Nor enter into temptation to create Javascript dynamically using a template
engine. There is a clean and simple solution to solve this problem.

It is good practice to add configuration directives to applications as constants to the `AngularJS
module definition`_. This can safely be done in the template code rendered by Django, where it
belongs!

Installation
============

It is assumed that your AngularJS application has already been initialized and that you have loaded
django-angular tags, ``{% load djng_tags %}``:

.. code-block:: html

    {% load djng_tags %}
    <script>
        var my_app = angular.module('MyApp', ['djng.urls', /* other dependencies */]);
    </script>

Now, you have to include ``django-angular.js`` and add data about your django url configuration:

.. code-block:: html

    <script src="{% static 'djng/js/django-angular.js' %}"></script>
    <script>angular.module('djng.urls').constant('patterns', {% load_djng_urls %});</script>

The ``djangoUrl`` service is then available through `dependency injection`_
to all directives and controllers.

Usage
=====
The reversing functionality is provided by ``djangoUrl.reverse(name, args_or_kwargs)`` method. It behaves much like the
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

    my_app.controller('MyCtrl', ['$scope', '$http', 'djangoUrl',
     function($scope, $http, djangoUrl) {

	    $http.post(djangoUrl.reverse('api:articles', [1]), {action: 'get_data'})
	        .success(function (out_data) {
                $scope.data = out_data;
        });

        // Or $http.post(djangoUrl.reverse('api:articles', {'id': 1}) ...
        // djangoUrl.reverse('api:article', {'id': 1}) returns something like '/api/article/1/'
	}]);

Parametrized URL templates
------------------------------------------
djangoUrl's ``reverse()`` method also provides an option to create parametrized URL templates, which can be used with
Angular's ``$resource``. These templates look something like: ``/api/articles/:id/``, parameters prefixed by ``:`` are
filled by Angular.

You can create parametrized templates by using ``reverse()`` method in keyword arguments mode. Parameters not present
in keyword arguments object will be replaced by ``:`` prefixed name from urlpatterns.

.. code-block:: javascript

	my_app.controller('MyCtrl', ['$scope', '$http', 'djangoUrl',
	 function($scope, $http, djangoUrl) {
        // Urlconf
        // ...
        // url(r'^api/(?P<type>\w+)/(?P<id>\d+)/$', api.models, name='api'),
        // ...

        // djangoUrl.reverse('api', {'id': 1, 'type': 'article'}) -> /api/article/1/
        // djangoUrl.reverse('api', {'id': 1}) -> /api/:type/1/
        // djangoUrl.reverse('api', {'type': 'article'}) -> /api/article/:id/
        // djangoUrl.reverse('api', {}) -> /api/:type/:id/
        // djangoUrl.reverse('api') -> /api/:type/:id/
        // When nothing is passed as args_or_kwargs argument, reverse() defaults
        // to keyword arguments mode
	}]);

So when building a service with ``$resource`` you can use ``djangoUrl.reverse()`` method just to make a parametrized
URL template, or to partially fill it and have Angular add other arguments.

.. code-block:: javascript

    my_app.controller('MyCtrl', ['$resource', 'djangoUrl', function($resource, djangoUrl) {

        var Article = $resource(djangoUrl.reverse('api'), {'id': '@id', 'type': 'article'});
        // or
        var Article = $resource(djangoUrl.reverse('api', {'type': 'article'}), {id: '@id'});

	}]);

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _dependency injection: http://docs.angularjs.org/guide/di
