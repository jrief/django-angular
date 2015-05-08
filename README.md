==============
django-angular
==============

Let Django play well with AngularJS
===================================

0.7.14 (latest)
---------------
* Support for Django-1.8. Many Thanks to AntonOfTheWoods!
* The widget ``bootstrap3.widgets.CheckboxInput`` got a keyword to set the choice label of a field.
  This allows to style this kind of field individually in a Django ``Form``.

[Demo](http://djangular.aws.awesto.com/form_validation/) on how to combine Django with Angular's form validation.

Detailed documentation on [ReadTheDocs](http://django-angular.readthedocs.org/en/latest/).

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
[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![Downloads](http://img.shields.io/pypi/dm/django-angular.svg?style=flat-square)](https://pypi.python.org/pypi/django-angular/)

License
-------
Copyright &copy; 2015 Jacob Rief.

MIT licensed.
