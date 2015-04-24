==============
django-angular
==============

Let Django play well with AngularJS
===================================

0.7.13 (latest)
---------------
* Change for ``Form``s inheriting from ``NgFormBaseMixin`` using ``field_css_classes`` as dict:
  CSS classes specified as default now must explicitly be added to the fields defining their own
  CSS classes. Before this was implicit.
* Added AngularJS directive ``djng-bind-if``. See docs for details.
* Reverted fix for FireFox checkbox change sync issue (#135) since it manipulated the DOM. Instead
  added ``scope.$apply()`` which fixes the issue on FF.
* In BS3 styling, added ``CheckboxFieldRenderer`` to ``CheckboxInlineFieldRenderer`` (the default),
  so that forms with multiple checkbox input fields can be rendered as block items instead of
  inlines.
* In BS3 styling, added ``RadioFieldRenderer`` to ``RadioInlineFieldRenderer`` (the default), so
  that forms with multiple radio input fields can be rendered as block items instead of inlines.
* Fixed 'classic form' issue whereby ``ngModel`` was not being added to ``select`` of ``textarea``
  elements, so returned errors where not displayed.

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
