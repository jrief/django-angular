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
      'delete': {method:'DELETE'} };

Of course this need support on the server side. This can easily be done with **djangular** ``NgCRUDView``.

.. note:: ``remove()`` and ``delete()`` do exactly the same thing. Usage of ``remove()`` is encouraged, since
          ``delete`` is a reserved word in IE.

Configuration
-------------
Subclass ``NgCRUDView`` and override model_class attribute::

  from djangular.views.crud import NgCRUDView

  class MyCRUDView(NgCRUDView):
      model_class = MyModel

Add urlconf entry pointing to the view::

   ...
   url(r'crud/mymodel$', MyCRUDView.as_view(), name='my_crud_view'),
   ...

Set up Angular service using ``$resource``:

.. code-block:: javascript

    var myServices = angular.module('myServices', ['ngResource']);

    myServices.factory('MyModel', ['$resource', function ($resource) {
        return $resource('crud/mymodel', {'pk': '@pk'}, {
        })
    }]);
Another quick change is required to Angular app config, without this ``DELETE`` requests fail ``CSRF`` test:

.. code-block:: javascript

    var my_app = angular.module('myApp', [/* other dependencies */, 'ngCookies']).run(function($http, $cookies) {
	    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
	    //Add the following two lines
	    $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
	    });

That's it. Now you can use CRUD methods.

Usage example
-------------

.. code-block:: javascript

    myControllers.controller('myCtrl', ['$scope', 'MyModel', function ($scope, MyModel) {
        //Query returns an array of objects, MyModel.objects.all() by default
        $scope.models = MyModel.query();

        //Getting a single object
        var model = MyModel.get({pk: 1});


        //We can crete new objects
        var new_model = new MyModel({name: 'New name'});
        new_model.$save(function(){
           $scope.models.push(new_model);
        });
        //In callback we push our new object to the models array

        //Updating objects
        new_model.name = 'Test name';
        new_model.$save();

        //Deleting objects
        new_model.$remove();
        //This deletes the object on server, but it still exists in the models array
        //To delete it in frontend we have to remove it from the models array

    }]);

.. note:: In real world applications you might want to restrict access to certain methods.
          This can be done using decorators, such as ``@login_required``.
          For additional functionality :ref:`JSONResponseMixin <dispatch-ajax-requests>` and NgCRUDView can be used together.

.. _$resource: http://docs.angularjs.org/api/ngResource.$resource
.. _JSONResponseMixin: dispatch-ajax-requests