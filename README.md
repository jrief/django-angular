# django-angular

Let Django play well with AngularJS

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![PyPI version](https://img.shields.io/pypi/v/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Python versions](https://img.shields.io/pypi/pyversions/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Software license](https://img.shields.io/pypi/l/django-angular.svg)](https://github.com/jrief/django-angular/blob/master/LICENSE-MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/jacobrief.svg?style=social&label=Jacob+Rief)](https://twitter.com/jacobrief)

## Breaking News

On 2017-10-19 **django-angular** version 2.0 has been released.

### Backward Incompatibility

To be compliant with other libraries such as **djangorestframework**,  server-side responses on
rejected forms use error code 422, rather than 200. If you use your own form controllers, adopt
them accordingly. The JSON format used to communicate errors downstream has changed slightly.

### New Features

For a smoother transition path, **django-angular** added two directives in version 2.0:

``<form djng-endpoint="/path/to/endpoint">...</form>``, which can be used to upload form
data to the server. It also populates the error fields, in case the server rejected some data.

``<djng-forms-set endpoint="/path/to/endpoint"><form ...>...</form>...</djng-forms-set>``
Similar to the above directive, but rather than validating one single form, it validates a
set of forms using one shared endpoint.

A promise chain has been introduced. Buttons used to submit form data and then proceed with
something else, now can be written as:

``<button ng-click="do(update()).then(redirectTo('/path/to/other/page'))">Label</button>``


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

## Future Plans
A next big change to **django-angular** is to add support for Angular2 and/or 4. This will
require additional development time from my side, so please
[consider to fund this and other upcoming features using Gratipay](https://gratipay.com/django-angular/).


## Latest Changes

### 1.1 (2017-08-17)

* Instead of adding extra functionality to Django's form fields via inheritance magic, now one must
  use the corresponding field classes from ``djng.forms.fields`` if its own form class inheritis
  from ``NgForm`` or ``NgModelForm``.
* Added support to upload files and images via Ajax.


## License

Copyright &copy; 2017

MIT licensed
