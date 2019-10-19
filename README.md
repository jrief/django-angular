# django-angular

Let Django play well with AngularJS

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)
[![PyPI version](https://img.shields.io/pypi/v/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Python versions](https://img.shields.io/pypi/pyversions/django-angular.svg)](https://pypi.python.org/pypi/django-angular)
[![Software license](https://img.shields.io/pypi/l/django-angular.svg)](https://github.com/jrief/django-angular/blob/master/LICENSE-MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/jacobrief.svg?style=social&label=Jacob+Rief)](https://twitter.com/jacobrief)

## What does it offer?

Add AngularJS directives to Django Forms. This allows to handle client side form validation using
the constraints provided by the server side Form declaration.

For more information, please visit the [demo site](https://django-angular.awesto.com/form_validation/).


### How to run

```
git clone https://github.com/jrief/django-angular.git django-angular.git
cd django-angular.git
docker build -t django-angular.git .
docker run -d -it -p 9002:9002 django-angular.git
```

Open the application at `http://{docker-host's-ip}:9002/`

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


## License

Copyright &copy; 2019

MIT licensed
