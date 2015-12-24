.. _reverse-urls:

================================
Manage Django URLs for AngularJS
================================

AngularJS controllers communicating with the Django application through Ajax, often require URLs,
pointing to some of the views of your application. Don't fall into temptation to hard code such a
URL into the client side controller code. Even worse would be to create Javascript dynamically using
a template engine. There is a clean and simple solution to solve this problem.

.. note:: Until version 0.7 **django-angular** reversed all existing URLs of a project and created
	an object exposing them to Javascript. Documentation for now deprecated approach is available
	:ref:`here <manage-urls>`.
	
	Starting with version 0.8, **django-angular** provides a new way to handle URLs, which offers
	the reversing functionality directly to AngularJS modules.

This service is provided by ``djangoUrl.reverse(name, args_or_kwargs)`` method. It behaves
exactly like Django's `URL template tag`_.


Basic operation principle
=========================

**django-angular** encodes the parameters passed to ``djangoUrl.reverse()`` into a special URL
starting with ``/angular/reverse/...``. This URL is used as a new entry point for the real HTTP
invocation.


Installation
============

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

The ``djangoUrl`` service is now available through `dependency injection`_ to all directives and
controllers.


Setting via Django Middleware
-----------------------------

* Add ``'djangular.middleware.DjangularUrlMiddleware'`` to ``MIDDLEWARE_CLASSES`` in your Django
``settings.py`` file:

.. code-block:: python

	MIDDLEWARE_CLASSES = (
	    'djangular.middleware.DjangularUrlMiddleware',
	    # Other middlewares
	)

.. warning:: This must be the **first** middleware included in ``MIDDLEWARE_CLASSES``

Using this approach adds some magicness to your URL routing, because the ``DjangularUrlMiddleware``
class bypasses the HTTP request from normal URL resolving and calls the corresponding view function
directly.


Usage
=====

The reversing functionality is provided by:

.. code-block:: javascript

	djangoUrl.reverse(name, args_or_kwargs)
	
This method behaves exactly like Django's `URL template tag`_ ``{% url 'named:resource' %}``.


Parameters
----------

* ``name``: The URL name you wish to reverse, exactly the same as what you would use in
  ``{% url %}`` template tag.
* ``args_or_kwargs`` (optional): An array of arguments, e.g. ``['article', 4]`` or an object of
  keyword arguments, such as ``{'type': 'article', 'id': 4}``.


Examples
--------

A typical Angular Controller would use the service ``djangoUrl`` such as:

.. code-block:: javascript

	var myApp = angular.module('MyApp', ['ng.django.urls']);
	
	myApp.controller('RemoteItemCtrl', ['$scope', '$http', '$log', 'djangoUrl', function($scope, $http, $log, djangoUrl) {
	
	    $scope.loadItem = function() {
	        var fetchItemURL = djangoUrl.reverse('namespace:fetch-item');
	        $http.get(fetchItemURL).success(function(item) {
	            $log.info('Fetched item: ' + item);
	        }).error(function(msg) {
	            console.error('Unable to fetch item. Reason: ' + msg);
	        });
	    }
	
	}]);

and with args:

.. code-block:: javascript

	$http.get(djangoUrl.reverse('api:articles', [1]))

or with kwargs:

.. code-block:: javascript

	$http.get(djangoUrl.reverse('api:articles', {'id': 1}))


Additional notes
----------------

If you want to override reverse url, e.g. if django app isn't on top level or you want to call another server
it can be set in ``.config()`` stage:

.. code-block:: javascript

	myApp.config(function(djangoUrlProvider) {
	  djangoUrlProvider.setReverseUrl('custom.com/angular/reverse/');
	});

.. warning:: The path of request you want to reverse must still remain ``/angular/reverse/`` on django server,
			 so that middleware knows it should be reversed.

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _dependency injection: http://docs.angularjs.org/guide/di
.. _URL template tag : https://docs.djangoproject.com/en/dev/ref/templates/builtins/#url
