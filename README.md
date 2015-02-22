==============
django-angular
==============

Let Django play well with AngularJS
===================================

0.7.10 (latest)
---------------
* Fixed inheritance problem (#122) caused by a metaclass conflicting with Django's
  ``DeclarativeFieldsMetaclass``. This now should fix some issues when using ``forms.ModelForm``.
  Please refer to the documentation, since the API changed slightly.
* Fixed expansion for templatetag ``{% angularjs %}`` (#117) when using lists in Python / arrays
  in JavaScript.

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
