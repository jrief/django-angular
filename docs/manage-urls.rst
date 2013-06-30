.. _manage-urls:

=================================
Manage Django URL's for AngularJS
=================================

You may have noticed, that AngularJS controllers sometimes need an URL pointing to a Django view of
your application. Don't fall into the temptation to hard code such an URL into your Javascript
controller code. Nor fall into the temptation to dynamically create Javascript by using a template
engine. There is a clean and simple solution to this problem.

It is good practice to add configuration directives to applications as constants to the `AngularJS
module definition`_. This can safely be done in your template code and belongs in there!

.. code-block:: html

  <script>
  angular.module('MyNgModule').constant('urls', {
      this_view_url: "{% url this_view %}",
      that_view_url: "{% url that_view %}",
      ...
  });
  </script>

This newly generated constant object is available through `dependency injection`_ to all directives
and controllers which are part of your AngularJS module. Now the remaining task which has to be
performed, is to inject this constant object into the controllers which require a Django URL.
The controller examples from :ref:`JSONResponseMixin <dispatch-ajax-request-example>` and
:ref:`NgModelFormMixin <angular-model-form-example>` then can be rewritten as:

.. code-block:: javascript

  function MyFormCtrl($scope, $http, url) {
      $scope.submit = function() {
          $http.post(url.this_view_url, $scope.my_prefix)
              .success(function(out_data) {
                  // do something
              });
      }
  }

List all URL's which belong to a namespace
------------------------------------------

To avoid the repetitive work of adding all the URL's to this constant, a utility function is
available, which returns a Python dictionary with all URL's which belong to a certain namespace.
This function is available as::

  from djangular.core.urlresolvers import urls_by_namespace

The returned dictionary can be used directly to fill the constant with the URLs to be passed into
your AngularJS controller:

.. code-block:: html

  <script>
  angular.module('MyNgModule').constant('urls', dict_goes_here);
  </script>

.. warning:: This function is still experimental. Use it at your own risk.

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _dependency injection: http://docs.angularjs.org/guide/di
