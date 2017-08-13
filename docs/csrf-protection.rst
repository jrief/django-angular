.. _csrf-protection:

=====================================
Cross Site Request Forgery protection
=====================================

Ajax requests submitted using method POST are put to a similar risk for
`Cross Site Request Forgeries`_ as HTTP forms. This type of attack occurs when a malicious Web site
is able to invoke an Ajax request onto your Web site. In Django, one should always add the template
tag csrf_token_ to render a hidden input field containing the token, inside each form submitted by
method POST.

When it comes to making an Ajax request, it normally is not possible to pass that token using a
Javascript object, because scripts usually are static and no secret can be added dynamically.
AngularJS natively supports CSRF protection, only some minor configuration is required to work with
Django.


Configure Angular for Django's CSRF protection
==============================================

Angular looks for ``XSRF-TOKEN`` cookie and submits it in ``X-XSRF-TOKEN`` http header, while Django
sets ``csrftoken`` cookie and expects ``X-CSRFToken`` http header. All we have to do is change the
name of cookie and header Angular uses. This is best done in ``config`` block:


.. code-block:: javascript

	var my_app = angular.module('myApp', [/* dependencies */]).config(function($httpProvider) {
	    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	});

When using this approach, ensure that the ``CSRF`` cookie is *not* configured as HTTP_ONLY_,
otherwise for security reasons that value can't be accessed from JavaScript.

Alternatively, if the block used to configure the AngularJS application is rendered using a Django
template, one can add the value of the token directly to the request headers:

.. code-block:: javascript

	var my_app = angular.module('myApp', [/* dependencies */]).config(function($httpProvider) {
	    $httpProvider.defaults.headers.common['X-CSRFToken'] = '{{ csrf_token }}';
	    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	}

.. _Cross Site Request Forgeries: http://www.squarefree.com/securitytips/web-developers.html#CSRF
.. _csrf_token: https://docs.djangoproject.com/en/1.6/ref/templates/builtins/#csrf-token
.. _HTTP_ONLY: http://www.codinghorror.com/blog/2008/08/protecting-your-cookies-httponly.html
.. _method run: http://docs.angularjs.org/api/angular.Module#methods_run
