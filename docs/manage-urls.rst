.. _manage-urls:

=================================
Manage Django URL's for AngularJS
=================================

You may have noticed, that AngularJS controllers sometimes need a URL pointing to a Django view of
your application. Do not enter into temptation to hard code such a URL into the client side
controller code. Nor enter into temptation to create Javascript dynamically using a template
engine. There is a clean and simple solution to solve this problem.

It is good practice to add configuration directives to applications as constants to the `AngularJS
module definition`_. This can safely be done in the template code rendered by Django, where it
belongs!

It is assumed that your AngularJS application has already been initialized with something
similar to:

.. code-block:: html

	<script>
	    var my_app = angular.module('MyApp', [/* application dependencies */]);
	</script>

Now, add configuration constants to the template code rendered by Django:

.. code-block:: javascript

	my_app.constant('urls', {
	    this_view_url: "{% url 'this_view' %}",
	    that_view_url: "{% url 'that_view' %}",
	    ...
	});

This newly generated Javascript object named ``urls`` is available through `dependency injection`_
to all directives and controllers which are part of your AngularJS module ``my_app``.
It separates the concern of configuring different settings, depending in which environment the
Javascript code is executed. This becomes really beneficial when writing pure client side unit
tests, using tools such as Jasmine_.

The remaining task which has to be performed, is to inject this Javascript object into AngularJS
controllers, which require URL's to, for instance, invoke Ajax requests on the server side.
Now, the controller examples from :ref:`JSONResponseMixin <dispatch-ajax-request-example>` and
:ref:`NgModelFormMixin <angular-model-form-example>` then can be rewritten as:

.. code-block:: javascript

	my_app.controller('MyFormCtrl', function($scope, $http, urls) {
	    $scope.submit = function() {
	        $http.post(urls.this_view_url, $scope.my_prefix)
	            .success(function(out_data) {
	                // do something
	            });
	    }
	});

The constant ``urls.that_view_url`` now can also be used in an `AngularJS html partial`_, provided
that the controller function adds this to its scope.

.. code-block:: javascript

	my_app.controller('MyUploadCtrl', function($scope, $http, urls) {
	    $scope.urls = urls;
	});

Now, partials can be delivered by Django's static file handler, rather than having to be rendered
by the template engine:

.. code-block:: html
 
   <!-- partial, delivered as static html, therefore {{ }} is expanded by AngualarJS, not by Django! -->
   <a href="{{ urls.that_view_url }}" class="button" role="button">Upload File</a>


List all URLs which belong to a namespace
------------------------------------------
To avoid the repetitive work of adding all the URL's to this constant Javascript object, a utility
function named ``urls_by_namespace`` is available, which returns a Python dictionary with all URL's
belonging to a certain namespace

.. code-block:: python

	import json
	from django.views.generic import View
	from django.utils.safestring import mark_safe
	from djangular.core.urlresolvers import urls_by_namespace

	class MyView(View):
	    def get_context_data(self, **kwargs):
	        context = super(MyView, self).get_context_data(**kwargs)
	        my_urls = json.dumps(urls_by_namespace('my_url_namespace'))
	        context.update(my_urls=mark_safe(my_urls))
	        return context

This dictionary then can be used to fill the constant Javascript object to be injected into
AngularJS directives and controllers:

.. code-block:: html

  <script>
  my_app.constant('urls', {{ my_urls }});
  </script>

.. warning:: This function is still experimental, so be prepared for API changes.

.. _AngularJS module definition: http://docs.angularjs.org/api/angular.module
.. _AngularJS html partial: http://docs.angularjs.org/tutorial/step_07#template
.. _dependency injection: http://docs.angularjs.org/guide/di
.. _Jasmine: http://pivotal.github.io/jasmine/
