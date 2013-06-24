.. _dispatch-ajax-requests:

======================================================
Dispatching Ajax requests from an AngularJS controller
======================================================

Wouldn't it be nice to call a Django view method, directly from your AngularJS controller, similar
to `Remote procedure calls`_?

This can simply be achieved by adding a **djangular** mixin class to that view::

  from django.views.generic import View
  from djangular.views.mixins import JSONResponseMixin, allowed_action
  
  class MyJSONView(JSONResponseMixin, View):
      # other view methods
  
      @allowed_action
      def process_something(self, in_data):
          # process input data
          out_data = {
              'foo': 'bar',
              'success': True,
          }
          return out_data

.. _dispatch-ajax-request-example:

Lets assume that the URL used for posting this request is attached to this view. Now in your
AngularJS controller, calling the views method ``process_something`` is as simple as:

.. code-block:: javascript

  function MyFormCtrl($scope, $http) {
      $scope.submit = function() {
          var in_data = {action: 'process_something'};
          angular.copy($scope.my_prefix, in_data);
          $http.post('/url/of/my_json_view', in_data)
              .success(function(out_data) {
                  if (out_data.success) {
                      // update the controllers scope
                  } else {
                      alert('Something went wrong');
                  }
              });
      }
  }

.. note:: In real code you should not hard code the URL into an AngularJS controller as shown in
       this example. Instead inject an object containing the URL into your controller as explained
       in `manage Django URL's for AngularJS`_.

The special keyword ``action``, as declared in the post data to be sent, contains the method name
of the view to be called. In ``MyJSONView.process_something()`` this ``action`` tuple then is
already stripped off from the passed ``in_data`` and the method receives a Python dictionary
containing an exact copy of the Javascript object ``$scope.my_prefix``.

.. warning:: To eschew to possibility for an attacker to call any method of your view by setting the
       keyword ``action`` to an arbitrary method name, the author of the view must explicitly give
       permission to call this method. This is done by adding the decorator ``@allowed_action`` in
       front of the methods to be exposed. Otherwise the remote caller receives an
       HttpResponseBadRequest_ error.

.. _Remote procedure calls: http://en.wikipedia.org/wiki/Remote_procedure_calls
.. _HttpResponseBadRequest: https://docs.djangoproject.com/en/1.5/ref/request-response/#httpresponse-subclasses
.. _manage Django URL's for AngularJS: manage-urls
