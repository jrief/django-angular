# django-angular

Let Django play well with AngularJS

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![PyPI version](https://img.shields.io/pypi/v/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Python versions](https://img.shields.io/pypi/pyversions/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Software license](https://img.shields.io/pypi/l/django-angular.svg)](https://github.com/jrief/django-angular/blob/master/LICENSE-MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/jacobrief.svg?style=social&label=Jacob+Rief)](https://twitter.com/jacobrief)

## Breaking News

On 2017-08-14 **django-angular** version 1.1 has been released.

This version introduces file- and image uploads through Ajax form submissions.

### Backward Incompatibility

If you create Angular forms from Django models, nothing changes.

If you create Angular forms using the provided mixin classes, then you must use the corresponding
fields as provided by **django-angular**. This keeps the API cleaner and prevents dynamic class 
tweaks.

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


## Latest Changes

### 1.1 (2017-08-17)

* Instead of adding extra functionality to Django's form fields via inheritance magic, now one must
  use the corresponding field classes from ``djng.forms.fields`` if its own form class inheritis
  from ``NgForm`` or ``NgModelForm``.
* Added support to upload files and images via Ajax.


## License

Copyright &copy; 2017

MIT licensed
