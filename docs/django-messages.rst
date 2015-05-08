.. _angular-django-messages:

=========================================
The Django Messages framework and Angular
=========================================

Some introduction text that i'm yet to think of...


Enabling views to return Django Messages
========================================

You must first enable_ the Django Messages framework for your project.

.. _enable: https://docs.djangoproject.com/en/1.7/ref/contrib/messages/#enabling-messages

.. note:: Context processors

    You only need to add these if you're also intending on rendering messages in server side templates.


Adding messages to a Views response
===================================

There are two ways to enable this functionality.

AjaxDjangoMessagesMiddleware
----------------------------

The first is middleware, which can be added in ``settings.py`` and adds blanket coverage to
the entire site: 

.. code-block:: python

     MIDDLEWARE_CLASSES = (
	    ...
	    'django.contrib.sessions.middleware.SessionMiddleware',
	    'django.contrib.messages.middleware.MessageMiddleware',
	
	    'djangular.middleware.AjaxDjangoMessagesMiddleware'
	)
	
Using this method, it's also possible to exclude specific URLS (by ``app_name``, ``namespace``, 
``namespace:name`` or ``name``) using the ``DJANGULAR_MESSAGES_EXCLUDE_URLS`` setting.

.. code-block:: python

    DJANGULAR_MESSAGES_EXCLUDE_URLS = (
        "(myapp)",  # anything in the myapp URLConf
        "[blogs]",  # Anything in the blogs namespace
         "accounts:detail",  # An AccountDetail view you wish to exclude
        "home",  # Site homepage
    )
	
.. warning:: Adding app_names to applications.

    To make the (myapp) work, you may need to define an app_name in the include() function in the URLConf. For example:
    
    .. code-block:: python

        # in urls.py
	    url(r'^something/', include('myapp.urls',  app_name="myapp"))



Using the Decorator
-------------------

If you only wish to affect a specific view, you can use the ``djangular.core.decorators.add_messages_to_response``
decorator.

**Class Based View example**:

.. code-block:: python
    
    from django.views.generic import View
    from django.utils.decorators import method_decorator

    from djangular.core.decorators import add_messages_to_response

    class MyClassBasedView(View):
        
        @method_decorator(add_messages_to_response)
        def post(self, request, *args, **kwargs):
            return HttpResponse(json.dumps({'data': 'my response data'}),
			                    status=200,
			                    content_type='application/json')
			
For more information on this technique, please see here_.

.. _here: https://docs.djangoproject.com/en/1.5/topics/class-based-views/intro/#decorating-the-class 


**Function Based View example**:

.. code-block:: python

    from django.http import HttpResponse

    from djangular.core.decorators import add_messages_to_response
    
    @add_messages_to_response
    def my_function_based_view(request):
        return HttpResponse(json.dumps({'data': 'my response data'}),
		                    status=200,
		                    content_type='application/json')

The Result
----------		
		
Using either of these methods, there are two criteria that must be meet in order for 
a view to add Django Messages to its response:

1. The request must be ajax
2. The response ``content-type`` must be ``application/json``

If both these criteria are meet and messages exist, they'll be added to the response 
content in the following format:

Original response content:

.. code-block:: javascript

    {'data': 'my response data'}

Converted response content with messages added:

.. code-block:: javascript

    {
        'data': {'data': 'my response data'},
        'django_messages': [ 
            {
                message: "this is a message",
                tags: "info",
                type: "info",
                level: 20
            },
            ...
        ]
    }


Handling Django Messages in Angular
===================================

First include the messages module.

.. code-block:: javascript

    var app = angular.module('myApp', ['ng.django.messages']);


Handling messages
-----------------

The easiest way to handle messages in your Angular client, is through the ``djngMessagesInterceptor``.

.. code-block:: javascript

    app.config(function($httpProvider){
        $httpProvider.interceptors.push('djngMessagesInterceptor');
    });

This intercepts the response, checking its data for the existence of the ``django_messages`` 
property. If it exists, it's stripped and the response data is reverted back to it's original 
form.


Responding to intercepted messages
----------------------------------

There are two ways to respond to intercepted messages. You can either add a handler to
the ``djngMessagesSignal`` to be notified when messages are intercepted:

.. code-block:: javascript
    
    app.controller('MyCtrl', function($scope, djngMessagesSignal) {
        
        vm.messages = [];

        djngMessagesSignal.onMessagesUpdated($scope, _messagesUpdated);

        function _messagesUpdated(messages) {
            vm.messages = messages;
        }
    });

or you can add a responder to the ``djngMessagesInterceptor`` to handle new messages:

.. code-block:: javascript

    app.factory('messagesModel', function() {

        var _messages = [];

        return {
            addMessages: function(messages) {
                _messages = messages;
            },
            get messages() {
                return _messages;
            }
        };
    });
    
    app.controller('MyCtrl', function(messagesModel) {
        
        var vm = this;
        
        vm.model = messagesModel;
    });

    app.run(function(djngMessagesInterceptor, messagesModel) {

        djngMessagesInterceptor.setResponders(messagesModel);
    });


.. code-block:: html

    <div controller="MyCtrl as ctrl">
        <div ng-repeat="message in ctrl.model.messages">
            <div>{{message.type}}</div>
            <div>{{message.message}}</div>
        </div>
    </div>
    
