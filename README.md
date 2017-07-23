# django-angular

Let Django play well with AngularJS

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![PyPI version](https://img.shields.io/pypi/v/django-angular.svg)](https://https://pypi.python.org/pypi/django-angular)
[![Python versions](https://img.shields.io/pypi/pyversions/djangocms-cascade.svg)](https://pypi.python.org/pypi/djangocms-cascade)
[![Software license](https://img.shields.io/pypi/l/djangocms-cascade.svg)](https://github.com/jrief/djangocms-cascade/blob/master/LICENSE-MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/shields_io.svg?style=social&label=jacobrief&maxAge=2592000)](https://twitter.com/jacobrief)

## Breaking News

In Django version 1.11, template-based widget rendering has been introduced.
This gives us a lot more flexibility when rendering form widgets. However,
**django-angular** had to be refactored and be adopted to this new API. I'd like
to ask everybody to test the new branch https://github.com/jrief/django-angular/tree/features/django-1.11-support
before releasing a next major version.


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

### 1.0.0 (2017-07-23)

* Adopted for Django's template-based widget rendering, introduced in version 1.11.
* Drop support for Django 1.7, 1.8 and 1.9.
* Fixed #270: Exception while rendering form using ``as_ul``.
* Removed templatetag ``{% csrf_value %}``, since Django offers ab equivalent tag.
* Fix file input css (remove the border) and add some documentation about common reported errors.
* Remove support for bower in favor of npm.


## License

Copyright &copy; 2017

MIT licensed
