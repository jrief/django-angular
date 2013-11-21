.. _csrf-protection:

=====================================
Cross Site Request Forgery protection
=====================================

Ajax requests submitted using method POST are put to a similar risk for
`Cross Site Request Forgeries`_ as HTTP forms. This type of attack occurs when a malicious Web site
is able to invoke an Ajax request onto your Web site. In Django, one should always add the template
tag csrf_token_ to render a hidden input containing the token, inside each form submitted by method
POST.

When it comes to making an Ajax request, it normally is not possible to pass that token using a
Javascript object, because scripts usually are static and no secret can be added dynamically. To
effectively solve that problem in a DRY manner, there are two similar possibilities.

When initialising the Angular application, add to following snippet to the ``run`` method::

	angular.module('myApp', [/* other dependencies */, 'ngCookies']).run(function($http, $cookies) {
	    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
	});

The problem with this approach is, that one must ensure that the ``CSRF`` cookie is *not* configured
as HTTP_ONLY_, otherwise that value can't be accessed from Javascript. Therefore **djangular**
offers a templatetag to hard code that value into a template::

	{% load djangular_tags %}
	
	angular.module('myApp', [/* other dependencies */]).run(function($http) {
	    $http.defaults.headers.post['X-CSRFToken'] = "{% csrf_value %}";
	});

The latter is my preferred method.

Optionally, if the above methods do not work, add the following method to the view handling the
Ajax request::

	from django.views.decorators.csrf import csrf_exempt
	
	@csrf_exempt
	def dispatch(self, *args, **kwargs):
	    return super(MyView, self).dispatch(*args, **kwargs)

This disables Cross Site Request Forgery protection for Ajax request. Use it at your own risk!


.. _Cross Site Request Forgeries: http://www.squarefree.com/securitytips/web-developers.html#CSRF
.. _csrf_token: https://docs.djangoproject.com/en/1.6/ref/templates/builtins/#csrf-token
.. _HTTP_ONLY: http://www.codinghorror.com/blog/2008/08/protecting-your-cookies-httponly.html
