django-angular
==============

Let Django play well with AngularJS
------------------------------------
Slides from the Django Conference 2014 are available [here](http://djangoconf.aws.awesto.com/slides).

NEW in 0.7.1
------------
* For remote method invocation, replace keyword ``action`` against a private HTTP-header
  ``DjNg-Remote-Method``. Added template tags ``djng_all_rmi`` and ``djng_current_rmi`` which
  return a list of methods to be used for remote invocation.
* Experimental support for Python-3.3.

Project home: https://github.com/jrief/django-angular

[Demo](http://djangular.aws.awesto.com/form_validation/) on how to combine Django with Angular's form validation.

Detailed documentation on [ReadTheDocs](http://django-angular.readthedocs.org/).

Please participate at this [survey on naming conventions](https://github.com/jrief/django-angular/issues/35)!

Please drop me a line, if and where you use this project.

Features
--------
* Seamless integration of Django forms with AngularJS controllers.
* Client side form validation for Django forms using AngularJS.
* Let an AngularJS controller call methods in a Django view - kind of Javascript RPCs.
* Manage Django URLs for static controller files.
* Three way data binding to connect AngularJS models with a server side message queue.
* Perform basic CRUD operations.

Build status
------------
[![Build Status](https://travis-ci.org/jrief/django-angular.png?branch=master)](https://travis-ci.org/jrief/django-angular)

License
-------
Copyright &copy; 2014 Jacob Rief. Licensed under the MIT license.
