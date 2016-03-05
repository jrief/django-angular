# django-angular

## Let Django play well with AngularJS

### 0.8.1 (latest)

From a functional point of view, very litte changed from version 0.7.16 to 0.8.0 with one *big*
exception:

**djangular has been renamed to djng** and **ng.django-...** has been renamed to **djng-...**.
This was requested by many users since it:

* caused a naming conflict with another Django app named the same and 
* the identifier "djangular" by many users was seen as a bad choice for this Django app.
* violated the AngularJS principle that only their modules shall be prefixed with ``ng``.

Please read https://github.com/jrief/django-angular/issues/35 for the preceded discussion
on this topic.

## Documentation

Detailed documentation on [ReadTheDocs](http://django-angular.readthedocs.org/en/latest/).

[Demo](http://django-angular.awesto.com/form_validation/) on how to combine Django with Angular's form validation.

Please drop me a line, if and where you use this project.

## Features

* Seamless integration of Django forms with AngularJS controllers.
* Client side form validation for Django forms using AngularJS.
* Let an AngularJS controller call methods in a Django view - kind of Javascript RPCs.
* Manage Django URLs for static controller files.
* Three way data binding to connect AngularJS models with a server side message queue.
* Perform basic CRUD operations.

## Build status

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![Downloads](http://img.shields.io/pypi/dm/django-angular.svg?style=flat-square)](https://pypi.python.org/pypi/django-angular/)

## License

Copyright &copy; 2016

MIT licensed
