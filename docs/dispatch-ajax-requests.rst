.. _dispatch-ajax-requests:

======================================================
Dispatching Ajax requests from an AngularJS controller
======================================================

Wouldn't it be nice to call a Django view method, directly from your AngularJS controller, like
a `Remote Procedure Call`_ or say **remote method invocation**?

This can be achieved by adding a **djangular** mixin class to that desired view

.. code-block:: python

  from django.views.generic import View
  from djangular.views.mixins import JSONResponseMixin, allowed_action
  
  class MyJSONView(JSONResponseMixin, View):
      # other view methods
  
      @allowed_action
      def process_something(self, in_data):
          # process in_data
          out_data = {
              'foo': 'bar',
              'success': True,
          }
          return out_data

.. _dispatch-ajax-request-example:

Let's assume that the URL used for posting this request is attached to this view. Now in your
AngularJS controller, calling the view's method ``process_something`` is as simple as:

.. code-block:: javascript

	my_app.controller('MyFormCtrl', function($scope, $http) {
	    $scope.submit = function() {
	        // merge $scope.my_prefix into object containing the action keyword
	        var in_data = {action: 'process_something'};
	        angular.copy($scope.my_prefix, in_data);
	        $http.post('/url/of/my_json_view', in_data)
	            .success(function(out_data) {
	                if (out_data.success) {
	                    // update the controllers scope
	                } else {
	                    alert('Something went wrong!');
	                }
	            });
	    }
	});

.. note:: In real code do not hard code the URL into an AngularJS controller as shown in this
       example. Instead, inject an object containing the URL into the controller function as
       explained in :ref:`manage Django URL's for AngularJS <manage-urls>`.

The Javascript object ``in_data`` contains the special keyword ``action``, which contains the
method to be called in the attached Django view. Here the view's method
``MyJSONView.process_something(self, in_data)`` receives a Python dictionary containing an exact
copy of the Javascript object ``$scope.my_prefix``, where the value pair with the key ``action``
has already been popped off.

.. warning:: To eschew the possibility for an attacker to call any method of your view by setting the
       keyword ``action`` to an arbitrary method name, the author of the view must explicitly give
       permission to call this method. This is done by adding the decorator ``@allowed_action`` in
       front of the methods to be exposed. Otherwise the remote caller receives an
       HttpResponseBadRequest_ error.


Dispatching Ajax requests using method GET
==========================================

Sometimes you only have to fetch some data from the server. If you prefer to fetch this data using
the GET method, you have no way to pass in the ``action`` keyword with the remote method you want
to execute. But **django-angular** lets you hard-code that action inside your URL dispatcher

.. code-block:: python

	urlpatterns = patterns('',
	    ...
	    url(r'^fetch-some-data.json$', MyResponseView.as_view(), {'action': 'get_data'}),
	    ...
	)

By calling the URL ``fetch-some-data.json``, the responding view dispatches incoming requests
directly onto the method ``get_data``. This works with GET requests as well as with POST requests

.. code-block:: python

	class MyResponseView(JSONResponseMixin, View):
	    def get_data(self):
	        return { 'foo': 'bar' }

.. note:: For GET requests, the method ``get_data`` does not require the decorator
       ``@allowed_action``, since this method invocation has been determined by programmer, rather
       than the client. Therefore this is not a security issue.

.. _Remote Procedure Call: http://en.wikipedia.org/wiki/Remote_procedure_calls
.. _HttpResponseBadRequest: https://docs.djangoproject.com/en/1.5/ref/request-response/#httpresponse-subclasses
.. _manage Django URL's for AngularJS: manage-urls
