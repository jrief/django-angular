django-angular
==============

Let Django play well with AngularJS
------------------------------------
Slides from the Django Conference 2014 are available [here](http://djangoconf.aws.awesto.com/slides).

Please test version 0.7.3 beta
------------------------------
* Added support to render Django Forms using a plugable style. Bootstrap3 styling has been
  implemented.
* Lots of bugfixes. Please check the ChangeLog for details.


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
