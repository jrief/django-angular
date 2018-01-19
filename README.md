# django-angular

Let Django play well with AngularJS

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![PyPI version](https://img.shields.io/pypi/v/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Python versions](https://img.shields.io/pypi/pyversions/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Software license](https://img.shields.io/pypi/l/django-angular.svg)](https://github.com/jrief/django-angular/blob/master/LICENSE-MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/jacobrief.svg?style=social&label=Jacob+Rief)](https://twitter.com/jacobrief)

## Breaking News

On 2017-11-17 **django-angular** version 2.0 has been released.

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
A next big change to **django-angular** should be to add support for Angular2/4/5.
However, I'm still unsure about the future roadmap of the Angular, and I currently
don't have the resources to do so.

## Latest Changes

### 2.0 (2017-11-17)

2.0
---
* To be compliant with other frameworks, Ajax responses from invalid form submissions, now respond
  with a ``HttpResponseBadRequest`` (status code 422) rather than with a ``HttpResponse`` (status
  200). This requires to adopt the form response views and the response handlers in JavaScript
  files, submitting the form data.
* No more need to add a customized controller for uploading form data to the server. Instead add the
  directive ``djng-endpoint="/path/to/endpoint"`` to a form and submit the form's content using an
  action event.
* New AngularJS directive ``djng-forms-set``, usable to validate and submit more than one form.
* AngularJS directive for the ``button``-element, usable to create a chain of action promises for
  form submissions.
* Add support for AngularJS version 1.6 by replacing deprecated occurrences of ``$http(...).success(...)``
  against ``$http(...).then(...)``.
* Sekizai's postprocessor ``module_list`` and ``module_config`` are deprecated and will be removed,
  since it is easier to fulfill the same result using Sekizai's templatetag ``with_data``.
* Radio input fields do not require the DjNg directive ``validate-multiple-fields`` anymore.


## License

Copyright &copy; 2017

MIT licensed
