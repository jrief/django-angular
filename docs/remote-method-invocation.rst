.. _dispatch-ajax-requests:

========================
Remote Method Invocation
========================

Wouldn't it be nice to call a Django view method, directly from your AngularJS controller, like
a `Remote Procedure Call`_ or say **Remote Method Invocation**?

Single Page Applications
========================
By nature, Single Page Web Applications implemented in Django, require one single View. These kind
of applications can however not always be build around the four possible request methods ``GET``,
``PUT``, ``POST`` and ``DELETE``. They rather require many different entry points to fulfill the
communication between the client and the server.

Normally, this is done by adding a key to the request data, which upon evaluation calls the
appropriate method. However, such an approach is cumbersome and error-prone.

*Django-Angular* offers some helper functions, which allow a client to call a View's method just as
if they would be normal asynchronous functions. To achieve this, let your View's class additionally
inherit from JSONResponseMixin:

.. code-block:: python

	from django.views.generic import View
	from djangular.views.mixins import JSONResponseMixin, allow_remote_invocation
	
	class MyJSONView(JSONResponseMixin, View):
	    # other view methods
	
	    @allow_remote_invocation
	    def process_something(self, in_data):
	        # process in_data
	        out_data = {
	            'foo': 'bar',
	            'success': True,
	      }
	      return out_data

In this View, methods decorated with ``@allow_remote_invocation`` can now be invoked remotely, for
instance in an AngularJS controller. To handle this in an ubiquitous manner, *Django-Angular*
implements two special template_tag, which exports all the methods allowed for remote invocation
to an AngularJS Provider.

Template Tag ``djng_all_rmi``
-----------------------------
The AngularJS Provider ``djangoRMIProvider`` shall be configured during the initialization of the
client side, such as:

.. code-block:: javascript

	{­% load djangular_tags %­}
	…
	<script type="text/javascript">
	my_app.config(function(djangoRMIProvider) {
	    djangoRMIProvider.configure({­% djng_all_rmi %­});
	});
	</script>

This makes available all methods allowed for remote invocation, from all View classes of your Django
project.

Template Tag ``djng_current_rmi``
---------------------------------
Alternatively, the AngularJS Provider ``djangoRMIProvider`` can be configured during the
initialization of the client side, such as:

.. code-block:: javascript

	my_app.config(function(djangoRMIProvider) {
	    djangoRMIProvider.configure({­% djng_current_rmi %­});
	});

This makes available all methods allowed for remote invocation, from the current View classes of
your Django project.


Have the client calling an allowed method from a Django View
------------------------------------------------------------
By injecting ``djangoRMI``, allowed methods from your Django Views can be called directly from any
AngularJS Controller. This example shows how to call methods configured with the template tag
``djng_current_rmi``:

.. code-block:: javascript

	my_app.controller("SinglePageCtlr", function($scope, djangoRMI) {
	    $scope.invoke = function() {
	        var in_data = { some: data };
	        djangoRMI.process_something(in_data)
	           .success(function(out_data) {
	               // do something with out_data
	           });
	    };
	});

If ``djangoRMIProvider`` is configured using the template tag ``djng_all_rmi``, the allowed
methods are grouped into objects named by their url_name_. If these `URL patterns`_ are part of a
namespace_, the above objects furthermore are grouped into objects named by their namespace.

.. _url_name: https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.ResolverMatch.url_name
.. _URL patterns: https://docs.djangoproject.com/en/dev/ref/urls/#patterns
.. _namespace: https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.ResolverMatch.namespace

.. note:: djangoRMI is a simple wrapper around AngularJS's built in $httpProvider. However, it
          automatically determines the correct URL and embeds the method name into the special
          HTTP-header ``DjNg-Remote-Method``. In all other aspects, it behaves like $httpProvider.


Dispatching Ajax requests using method GET
==========================================
Sometimes you only have to retrieve some data from the server. If you prefer to fetch this data
using an ordinary GET request, ie. one without the special AngularJS provider ``djangoRMI``, then
it is possible to hard-code the method for invocation in the urlpatterns_ inside the URL dispatcher.

.. _urlpatterns: https://docs.djangoproject.com/en/dev/ref/urls/#django.conf.urls.patterns

.. code-block:: python

	class MyResponseView(JSONResponseMixin, View):
	    def get_some_data(self):
	        return {'foo': 'bar'}
	
	    def get_other_data(self):
	        return ['baz', 'cap']
	
	urlpatterns = patterns('',
	    …
	    url(r'^fetch-some-data.json$', MyResponseView.as_view(), {'invoke_method': 'get_some_data'}),
	    url(r'^fetch-other-data.json$', MyResponseView.as_view(), {'invoke_method': 'get_other_data'}),
	    …
	)

If a client calls the URL ``/fetch-some-data.json``, the responding view dispatches incoming
requests directly onto the method ``get_some_data``. This kind of invocation only works for GET
requests. Here the fetching methods do not require the decorator ``@allow_remote_invocation``,
since the programmer determines all possible invocations.

.. _Remote Procedure Call: http://en.wikipedia.org/wiki/Remote_procedure_calls
