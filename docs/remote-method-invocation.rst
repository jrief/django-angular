.. _remote-method-invocation:

========================
Remote Method Invocation
========================

Wouldn't it be nice to call a Django view method, directly from an AngularJS controller, similar
to a `Remote Procedure Call`_ or say better **Remote Method Invocation**?

.. _Remote Procedure Call: http://en.wikipedia.org/wiki/Remote_procedure_calls

Single Page Applications
========================
By nature, Single Page Web Applications implemented in Django, require one single View. These kind
of applications can however not always be build around the four possible request methods ``GET``,
``PUT``, ``POST`` and ``DELETE``. They rather require many different entry points to fulfill the
communication between the client and the server.

Normally, this is done by adding a key to the request data, which upon evaluation calls the
appropriate method. However, such an approach is cumbersome and error-prone.

*Django-Angular* offers some helper functions, which allows the client to call a Django's View
method, just as if it would be a normal asynchronous JavaScript function. To achieve this, let the
View's class additionally inherit from JSONResponseMixin:

.. code-block:: python

	from django.views.generic import View
	from djng.views.mixins import JSONResponseMixin, allow_remote_invocation
	
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

In this Django View, the method ``process_something`` is decorated with ``@allow_remote_invocation``.
It now can be invoked directly from an AngularJS controller or directive. To handle this in an
ubiquitous manner, *Django-Angular* implements two special template tags, which exports *all*
methods allowed for remote invocation to the provided AngularJS service ``djangoRMI``.

Template Tag ``djng_all_rmi``
-----------------------------
The AngularJS Provider ``djangoRMIProvider`` shall be configured during the initialization of the
client side, such as:

.. code-block:: django

	{% load djng_tags %}
	…
	<script type="text/javascript">
	var tags = {% djng_all_rmi %};
	my_app.config(function(djangoRMIProvider) {
	    djangoRMIProvider.configure(tags);
	});
	</script>

This makes available *all* methods allowed for remote invocation, from *all* View classes of your
Django project.

.. note:: In order to have your methods working, the associated urls need to be named.


Template Tag ``djng_current_rmi``
---------------------------------
Alternatively, the AngularJS Provider ``djangoRMIProvider`` can be configured during the
initialization of the client side, such as:

.. code-block:: django

	{% load djng_tags %}
	…
	<script type="text/javascript">
	var tags = {% djng_current_rmi %};
	my_app.config(function(djangoRMIProvider) {
	    djangoRMIProvider.configure(tags);
	});
	</script>

This makes available *all* methods allowed for remote invocation, from the current View class,
ie. the one rendering the current page.

.. note:: In order to have your methods working, the associated urls need to be named.


Let the client invoke an allowed method from a Django View
----------------------------------------------------------
By injecting the service ``djangoRMI`` into an AngularJS controller, allowed methods from the
Django View which renders the current page, can be invoked directly from JavaScript. This example
shows how to call the above Python method ``process_something``, when configured using the template
tag ``djng_current_rmi``:

.. code-block:: javascript

	my_app.controller("SinglePageCtlr", function($scope, djangoRMI) {
	    $scope.invoke = function() {
	        var in_data = { some: 'data' };
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

.. note:: djangoRMI is a simple wrapper around AngularJS's built in `$http service`_. However, it
          automatically determines the correct URL and embeds the method name into the special
          HTTP-header ``DjNg-Remote-Method``. In all other aspects, it behaves like the
          `$http service`_.

.. _$http service: https://code.angularjs.org/1.2.16/docs/api/ng/service/$http

Dispatching Ajax requests using method GET
==========================================
Sometimes you only have to retrieve some data from the server. If you prefer to fetch this data
using an ordinary GET request, ie. one without the special AngularJS provider ``djangoRMI``, then
it is possible to hard-code the method for invocation into the urlpatterns_ inside the URL
dispatcher.

.. _urlpatterns: https://docs.djangoproject.com/en/dev/ref/urls/#django.conf.urls.patterns

.. code-block:: python

	class MyResponseView(JSONResponseMixin, View):
	    def get_some_data(self):
	        return {'foo': 'bar'}
	
	    def get_other_data(self):
	        return ['baz', 'cap']
	
	urlpatterns = [
	    # …
	    url(r'^fetch-some-data.json$', MyResponseView.as_view(), {'invoke_method': 'get_some_data'}),
	    url(r'^fetch-other-data.json$', MyResponseView.as_view(), {'invoke_method': 'get_other_data'}),
	    # …
	]

If a client calls the URL ``/fetch-some-data.json``, the responding view dispatches incoming
requests directly onto the method ``get_some_data``. This kind of invocation only works for GET
requests. Here these methods *do not* require the decorator ``@allow_remote_invocation``,
since now the server-side programmer is responsible for choosing the correct method and thus a
malicious client cannot bypass the intended behavior.
