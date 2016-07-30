# django-angular

Let Django play well with AngularJS


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


## Latest Changes

### 0.8.3

* Refactored client side test runner to use npm instead of Grunt.
* Use tox to create the testing matrix.
* Fix #261: ModelMultipleChoiceField and CheckboxSelectMultiple.
* Deprecate ``{% csrf_value %}`` in favour of ``{{ csrf_token }}``.


## License

Copyright &copy; 2016

MIT licensed
