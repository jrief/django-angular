.. _three-way-data-binding:

======================
Three-way data-binding
======================

One of AngularJS biggest selling propositions is its `two-way data-binding`_. Two way data-binding
is an automatic way of updating the view whenever the model changes, as well as updating the model
whenever the view changes.

With **djng** and the additional module django-websocket-redis_, one can extend this feature
to reflect all changes to a model, back and forward with a corresponding object stored on the
server. This means that the server “sees” whenever the model on the client changes and can by
itself, modify values on the client side at any time, without having the client to poll for new
messages. This is very useful, when the server wants to inform the client about asynchronous events
such as sport results, chat messages or multi-player game events.

Installation
============
If you want to use three-way data-binding with Django, the webbrowser must have support for
websockets. Nowadays, most modern browsers do so.

Install **django-websocket-redis** from PyPI::

  pip install django-websocket-redis

and follow the `configuration instructions`_.

Demo
====
In the examples directory there is a demo showing the capabilities. If **ws4redis** can be found in
the Python search path, this special demo should be available together with the other two examples.
Run the demo server::

  cd examples
  ./manage runserver

point a browser onto http://localhost:8000/threeway_databinding/ and fill the input fields.
Point a second browser onto the same URL. The fields content should be the same in all browsers.
Change some data, the fields content should update concurrently in all attached browsers.

Add three-way data-binding to an AngularJS application
======================================================
Refer to the Javascript file ``django-angular.js`` somewhere on your page:

.. code-block:: html

    {% load static %}
    <script src="{% static 'djng/js/django-angular.min.js' %}" type="text/javascript"></script>

add the module dependency to your application initialization:

.. code-block:: javascript

    var my_app = angular.module('myApp', [/* other dependencies */, 'djng.websocket']);

configure the websocket module with a URL prefix of your choice:

.. code-block:: javascript

    my_app.config(['djangoWebsocketProvider', function(djangoWebsocketProvider) {
        // use WEBSOCKET_URI from django settings as the websocket's prefix
        djangoWebsocketProvider.setURI('{{ WEBSOCKET_URI }}');
        djangoWebsocketProvider.setHeartbeat({{ WS4REDIS_HEARTBEAT }});

        // optionally inform about the connection status in the browser's console
        djangoWebsocketProvider.setLogLevel('debug');
    }]);

If you want to bind the data model in one of your AngularJS controllers, you must inject the
provider **djangoWebsocket** into this controller and then attach the websocket to the server.

.. code-block:: javascript

    my_app.controller('MyController', function($scope, djangoWebsocket) {
        djangoWebsocket.connect($scope, 'my_collection', 'foobar', ['subscribe-broadcast', 'publish-broadcast']);

        // use $scope.my_collection as root object for the data which shall be three-way bound
    });

This creates a websocket attached to the server sides message queue via the module **ws4redis**.
It then shallow watches the properties of the object named ``'my_collection'``, which contains the
model data. It then fires whenever any of the properties change (for arrays, this implies watching
the array items; for object maps, this implies watching the properties). If a change is detected,
it is propagated up to the server. Changes made to the corresponding object on the server side,
are immediately send back to all clients listening on the named facility, referred here as ``foobar``.

.. note:: This feature is new and experimental, but due to its big potential, it will be regarded
          as one of the key features in future versions of **django-angular**.

.. _two-way data-binding: http://docs.angularjs.org/guide/databinding
.. _django-websocket-redis: https://github.com/jrief/django-websocket-redis
.. _configuration instructions: http://django-websocket-redis.readthedocs.org/en/latest/installation.html
