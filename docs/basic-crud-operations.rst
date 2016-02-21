.. _basic-crud-operations:

=============================
Perform basic CRUD operations
=============================

When using Angular's `$resource`_ to build services, each service comes with free CRUD
(create, read, update, delete) methods:

.. code-block:: javascript

	{ 'get':    {method:'GET'},
	  'save':   {method:'POST'},
	  'query':  {method:'GET', isArray:true},
	  'remove': {method:'DELETE'},
	  'delete': {method:'DELETE'}
	};

Of course this need support on the server side. This can easily be done with **django-angular**'s
``NgCRUDView``.

.. note:: ``remove()`` and ``delete()`` do exactly the same thing. Usage of ``remove()`` is
          encouraged, since ``delete`` is a reserved word in IE.


Configuration
-------------
Subclass ``NgCRUDView`` and override model attribute:

.. code-block:: python

	from djng.views.crud import NgCRUDView
	
	class MyCRUDView(NgCRUDView):
	    model = MyModel

Add urlconf entry pointing to the view:

.. code-block:: python

   ...
   url(r'^crud/mymodel/?$', MyCRUDView.as_view(), name='my_crud_view'),
   ...

Set up Angular service using ``$resource``:

.. code-block:: javascript

	var myServices = angular.module('myServices', ['ngResource']);
	
	myServices.factory('MyModel', ['$resource', function($resource) {
	    return $resource('/crud/mymodel/', {'pk': '@pk'}, {
	    });
	}]);

.. note:: Since there is a known bug with $resource not respecting trailing slash, the urls in Django urlconf used by $resource
          must either not have trailing slash or it should be optional (preferred) - e.g. ``url/?``. Adding the trailing slash
          to the $resource configuration regardless (``/crud/mymodel/``) ensures future compatibility in case the bug gets fixed and
          will then follow Django's trailing slash convention. This has been fixed in AngularJS 1.3. More information here `trailingSlashBugFix`_

Another quick change is required to Angular app config, without this ``DELETE`` requests fail ``CSRF`` test:

.. code-block:: javascript

    var my_app = angular.module('myApp', [/* other dependencies */, 'ngCookies']).run(
        function($http, $cookies) {
            $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
            // Add the following two lines
            $http.defaults.xsrfCookieName = 'csrftoken';
            $http.defaults.xsrfHeaderName = 'X-CSRFToken';
	});

That's it. Now you can use CRUD methods.


Optional attributes
-------------------
The following options are currently available to subclasses of ``NgCRUDView``:

``fields``
^^^^^^^^^^

Set this to a tuple or list of field names for only retrieving a subset of model fields during a
`get` or `query` operation. Alternatively, if this may vary (e.g. based on query parameters or
between `get` and `query`) override the ``get_fields()`` method instead.

With ``None`` (default), all model fields are returned. The object identifier (``pk``) is always
provided, regardless of the selection.


``form_class``
^^^^^^^^^^^^^^

Set this to a specific form for your model to perform custom validation with it.
Alternatively, if it may vary you can override the ``get_form_class()`` method instead.

With ``None`` (default), a modelForm including all fields will be generated and used.


``slug_field``
^^^^^^^^^^^^^^

Similar to Django's SingleObjectMixin, objects can be selected using an alternative key such as a
title or a user name. Especially when using the `ngRoute module`_ of AngularJS, this makes
construction of descriptive URLs easier. Query parameters can be extracted directly from `$route`_
or `$routeParams`_ and passed to the query.

This attribute (default is ``'slug'``) describes the field name in the model as well as the query
parameter from the client. For example, if it is set to ``'name'``, perform a query using

.. code:: js

    var model = MyModel.get({name: "My name"});

.. note:: Although the view will not enforce it, it is strongly recommended that you only use unique
        fields  for this purpose. Otherwise this can lead to a ``MultipleObjectsReturned``
        exception, which is not handled by this implementation.

        Also note that you still need to pass the object identifier ``pk`` on update and delete
        operations. Whereas for save operations, the check on ``pk`` makes the distinction between
        an update and a create operation, this restriction on deletes is only for safety purposes.


``allowed_methods``
^^^^^^^^^^^^^^^^^^^

By default, ``NgCRUDView`` maps the request to the corresponding django-angular method, e.g. a ``DELETE`` request would call
the ``ng_delete`` method.

``allowed_methods`` is set by default to ``['GET', 'POST', 'DELETE']``.
If you need to prevent any method, you can overrride the ``allowed_methods`` attributes. Alternatively, you can use the ``exclude_methods`` attributes.


``exclude_methods``
^^^^^^^^^^^^^^^^^^^

To allow all methods by default, ``exclude_methods`` is set as an empty list.
To exclude any method, you can override this attribute to exclude the ``'GET'``, ``'POST'`` or  ``'DELETE'``.
See ``allowed_methods`` for more informations.


Usage example
-------------

.. code-block:: javascript

	myControllers.controller('myCtrl', ['$scope', 'MyModel', function ($scope, MyModel) {
	    // Query returns an array of objects, MyModel.objects.all() by default
	    $scope.models = MyModel.query();
	
	    // Getting a single object
	    var model = MyModel.get({pk: 1});
	
	
	    // We can crete new objects
	    var new_model = new MyModel({name: 'New name'});
	    new_model.$save(function(){
	       $scope.models.push(new_model);
	    });
	    // In callback we push our new object to the models array
	
	    // Updating objects
	    new_model.name = 'Test name';
	    new_model.$save();
	
	    // Deleting objects
	    new_model.$remove();
	    // This deletes the object on server, but it still exists in the models array
	    // To delete it in frontend we have to remove it from the models array
	
	}]);

.. note:: In real world applications you might want to restrict access to certain methods.
          This can be done using decorators, such as ``@login_required``.
          For additional functionality :ref:`JSONResponseMixin <remote-method-invocation>` and
          ``NgCRUDView`` can be used together.

.. _$resource: http://docs.angularjs.org/api/ngResource.$resource
.. _ngRoute module: http://docs.angularjs.org/api/ngRoute
.. _$route: http://docs.angularjs.org/api/ngRoute/service/$route
.. _$routeParams: http://docs.angularjs.org/api/ngRoute/service/$routeParams
.. _trailingSlashBugFix: https://github.com/kwk/docker-registry-frontend/commit/d2b34b79c669d68bb1c587aab819b48157a790e7
