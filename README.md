==============
django-angular
==============

Let Django play well with AngularJS
===================================

New in 0.7.8
------------
* Fixed: ng-minlength and ng-maxlength are not set to ``None`` if unset.
* Fixed: Concatenated latest version of django-angular.js.

0.7.7
-----
* Tested with Django-1.7, Django-1.6 and Django-1.5
* Tested on Python 2.7 and Python 3.3
* Huge refactoring of the code base. It now is much easier to understand the code and to add custom
  Fields and Widgets.
* Fixed the behaviour of all Widgets offered by Django. They now all validate independently of the
  method (Post or Ajax) used to submit data to the server.


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
Copyright &copy; 2014 Jacob Rief.

MIT licensed.
