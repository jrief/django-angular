# django-angular

Let Django play well with AngularJS


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


## Build status

[![Build Status](https://travis-ci.org/jrief/django-angular.svg?branch=master)](https://travis-ci.org/jrief/django-angular)


## Latest Changes

### 0.8.4 (2016-08-20)

* Added two optional Sekiazai's postprocessors for better dependency resolution of AngularJS
  imports and module initialization.


## License

Copyright &copy; 2017

MIT licensed
