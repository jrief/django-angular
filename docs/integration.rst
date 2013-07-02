.. _integration:

Integrating AngularJS with Django
=================================

XMLHttpRequest
--------------
As a convention in web applications, Ajax requests shall send the HTTP-Header::

  X-Requested-With: XMLHttpRequest

while invoking POST-requests. In AngularJS versions 1.0.x this was the default behavior, but in
versions 1.1.x this support has been dropped. Strictly speaking, Django applications do not require
this header, but if it is missing, all invocations to::

  request.is_ajax()

would return ``False``, even for perfectly valid Ajax requests. Thus, if you use AngularJS version
1.1.x, add the following statement during module instantiation:

.. code-block:: javascript

  angular.module('MyNgModule').config(function($httpProvider) {
      $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
  });


Template tags
-------------
Django and AngularJS share the same token for variable substitution in templates, ie.
``{{ variable_name }}``. This should not be a big problem, since you are strongly discouraged to mix
Django template code with AngularJS template code. However this recommendation is often not 
practical in all situations, and there might be a need to mix both template languages, one which is
expanded by Django on the server, and one which is expanded by AngularJS in the browser.

The cleanest solution to circumvent this, is by using the verbatim_ tag, which became available in
Django 1.5.

A less clean solution, is to change the syntax of the AngularJS template tags. Just
add the following statement during module instantiation:

.. code-block:: javascript

  angular.module('MyNgModule').config(function($interpolateProvider) {
      $interpolateProvider.startSymbol('{$');
      $interpolateProvider.endSymbol('$}');
  });

Now, you can easily distinguish a server side variable substitution ``{{ varname }}`` from a client
side variable substitution ``{$ varname $}``.

This approach is even less verbose than using the *verbatim* tag. The problem, however, is that you
have to remember this alternative tag syntax for all of your AngularJS templates. This also makes
it difficult to integrate third party AngularJS directives, which are shipped with their own
templates.

Partials
........
In AngularJS, when used together with external templates, static HTML code often is loaded by a
routeProvider_. These so named partials can be placed in their own sub-directory below
``STATIC_ROOT``.

If for some reason you need mixed template code, ie. one which first is expanded by Django and later
is parsed by AngularJS, then add to your ``urls.py``::

  partial_patterns = patterns('',
      url(r'^partial-template1.html$', PartialView.as_view(template_name='partial-template1.html'), name='partial_template1'),
      ... more partials ...,
  )
  
  urlpatterns = patterns('',
      ...
      url(r'^partials/', include(partial_patterns, namespace='partials')),
      ...
  )

By using the utility function::

  from djangular.core.urlsresolvers import urls_by_namespace
  
  my_partials = urls_by_namespace('partials')

the caller obtains a list of all partials defined for the given namespace. This list can be used
when creating a Javascript array of URL's to be injected into controllers.

Dynamically generated Javascript code
.....................................

There might be good reasons to mix Django template with AngularJS template code. Consider a
multilingual application, where text shall be translated, using the superb Django translation_
engine.

Also, sometimes your application must pass configuration settings, which are created by Django
during runtime, such as reversing a URL. These are the use cases when to mix Django template with
AngularJS template code. Remember, when adding dynamically generated Javascript code, to keep these
sections small and mainly for the purpose of configuring your AngularJS module. **All other Javascript
code shall go into separate static files!**

.. warning:: Never use Django template code to dynamically generate AngularJS controllers or
       directives. This will make it very hard to debug and impossible to add Jasmine_ unit tests to
       your code. Always do a clear separation between the configuration of your AngularJS
       module, which is part of your application, and the client side logic, which shall be testable
       without the need of a running Django server.

.. _verbatim: https://docs.djangoproject.com/en/1.5/ref/templates/builtins/#verbatim
.. _routeProvider: _http://docs.angularjs.org/api/ng.$routeProvider
.. _translation: https://docs.djangoproject.com/en/1.5/topics/i18n/translation/
.. _Jasmine: http://pivotal.github.io/jasmine/
