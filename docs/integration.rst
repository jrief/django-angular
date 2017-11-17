.. _integration:

===============================
Integrate AngularJS with Django
===============================

XMLHttpRequest
==============

As a convention in web applications, Ajax requests shall send the HTTP-Header::

	X-Requested-With: XMLHttpRequest

while invoking POST-requests. In AngularJS versions 1.0.x this was the default behavior, but in
versions 1.1.x this support has been dropped. Strictly speaking, Django applications do not require
this header, but if it is missing, all invocations to::

	request.is_ajax()

would return ``False``, even for perfectly valid Ajax requests. Thus, if you use AngularJS version
1.1.x or later, add the following statement during module instantiation:

.. code-block:: javascript

	var my_app = angular.module('MyApp').config(function($httpProvider) {
	    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	});


Template tags
=============

Django and AngularJS share the same token for variable substitution in templates, ie.
``{{ variable_name }}``. This should not be a big problem, since you are discouraged to mix
Django template code with AngularJS template code. However, this recommendation is not
viable in all situations. Sometime there might be the need to mix both template languages, one
which is expanded by Django on the server, and one which is expanded by AngularJS in the browser.

The cleanest solution to circumvent this, is by using the verbatim_ tag, which became available in
Django-1.5.

Another approach is to use the AngularJS mustaches inside a templatetag, for instance:

.. code-block:: django

	<h2>{% trans "The value you were looking for is: {{ my_data.my_value }}" %}</h2>

It is strongly discouraged to change the syntax of the AngularJS template tags, because it breaks
the compatibility to all third party AngularJS directives, which are shipped with their own
templates.


Partials
--------

In AngularJS, when used together with external templates, static HTML code often is loaded by a
`$templateCache`_. These so named partials can be placed in their own sub-directory below
``STATIC_ROOT``.

If, for some reason you need mixed template code, ie. one which first is expanded by Django and
later is parsed by AngularJS, then add a view such as

.. code-block:: python

	class PartialGroupView(TemplateView):
	    def get_context_data(self, **kwargs):
	        context = super(PartialGroupView, self).get_context_data(**kwargs)
	        # update the context
	        return context

Resolve this view in ``urls.py``

.. code-block:: python

	partial_patterns = [
	    url(r'^partial-template1.html$', PartialGroupView.as_view(template_name='partial-template1.html'), name='partial_template1'),
	    # ... more partials ...,
	]

	urlpatterns = [
	    # ...
	    url(r'^partials/', include(partial_patterns, namespace='partials')),
	    # ...
	]

By using the utility function

.. code-block:: python

	from djng.core.urlresolvers import urls_by_namespace

	my_partials = urls_by_namespace('partials')

the caller obtains a list of all partials defined for the given namespace. This list can be used
when creating a Javascript array of URL's to be injected into controllers or directives.


Inlining Partials
-----------------

An alternative method for handling AngularJS's partial code, is to use the special script type
``text/ng-template`` and mixing it into existing HTML code. Say, an AngularJS directive
refers to a partial using ``templateUrl: 'template/mixed-ng-snipped.html'`` during the link phase,
then that partial may be embedded inside a normal Django template using

.. code-block:: django

	<script id="template/mixed-ng-snipped.html" type="text/ng-template">
	  <div>{{ resolved_by_django }}</div>
	  <div>{% verbatim %}{{ resolved_by_angular }}{% endverbatim %}</div>
	</script>

or if the ``$interpolateProvider`` is used to replace the AngularJS template tags

.. code-block:: django

	<script id="template/mixed-ng-snipped.html" type="text/ng-template">
	  <div>{{ resolved_by_django }}</div>
	  <div>{$ resolved_by_angular $}</div>
	</script>


Dynamically generated Javascript code
-------------------------------------

There might be good reasons to mix Django template with AngularJS template code. Consider a
multilingual application, where text shall be translated, using the Django translation_ engine.

Also, sometimes your application must pass configuration settings, which are created by Django
during runtime, such as reversing a URL. These are the use cases when to mix Django template with
AngularJS template code. Remember, when adding dynamically generated Javascript code, to keep these
sections small and mainly for the purpose of configuring your AngularJS module. **All other
Javascript code must go into separate static files!**

.. warning:: Never use Django template code to dynamically generate AngularJS controllers or
       directives. This will make it very hard to debug and impossible to add Jasmine_ unit tests to
       your code. Always do a clear separation between the configuration of your AngularJS
       module, which is part of *your* application, and the client side logic, which always shall be
       independently testable without the need of a running Django server.


Bound Forms
===========

AngularJS's does not consider `bound forms`_, rather in their mindset data models shall be bound to
the form's input fields by a controller function. This, for Django developers may be unfamiliar with
their way of thinking. Hence, if bound forms shall be rendered by Django, the behavior of AngularJS
on forms must be adopted using a special directive which overrides the `built-in form directive`_.

To override the built-in behavior, refer to the Javascript file ``django-angular.js`` somewhere on
your page

.. code-block:: django

	<script src="{% static 'djng/js/django-angular.min.js' %}" type="text/javascript"></script>

and add the module dependency to your application initialization

.. code-block:: javascript

	var my_app = angular.module('myApp', [/* other dependencies */, 'djng.forms']);

.. _verbatim: https://docs.djangoproject.com/en/stable/ref/templates/builtins/#verbatim
.. _$routeProvider: http://docs.angularjs.org/api/ngRoute.$routeProvider
.. _$templateCache: https://docs.angularjs.org/api/ng/service/$templateCache
.. _translation: https://docs.djangoproject.com/en/stable/topics/i18n/translation/
.. _Jasmine: http://pivotal.github.io/jasmine/
.. _bound forms: https://docs.djangoproject.com/en/dev/ref/forms/api/#bound-and-unbound-forms
.. _built-in form directive: http://code.angularjs.org/1.2.14/docs/api/ng/directive/form
