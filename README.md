django-angular
==============

Utilities to let Django play nice together with AngularJS
---------------------------------------------------------

**NEW in 0.6.0**: Added basic CRUD view.

Project home: https://github.com/jrief/django-angular

Detailed documentation

[![ReadTheDocs](https://raw.github.com/jrief/django-angular/master/docs/_static/badge-rtd.png)](http://django-angular.readthedocs.org/)

Features
--------
* Seamless integration of Django forms with AngularJS controllers.
* Client side form validation for Django forms using AngularJS.
* Let an AngularJS controller call methods in a Django view - kind of Javascript RPCs.
* Manage Django URLs for static controller files.
* Three way data binding to connect AngularJS models with a server side message queue.

Build status
------------
[![Build Status](https://travis-ci.org/jrief/django-angular.png?branch=master)](https://travis-ci.org/jrief/django-angular)

Installation
------------
The latest stable release from PyPI:

```pip install django-angular```

or the current development release from github:

```$ pip install -e git+https://github.com/jrief/django-angular.git#egg=django-angular```

License
-------
Copyright (c) 2013 Jacob Rief  
Licensed under the MIT license.

Release History
---------------
* 0.6.0 - Support for basic CRUD view.
* 0.5.0 - Added three way data binding.
* 0.4.0 - Removed @csrf_exempt on dispatch method for Ajax requests.
* 0.3.0 - Client side form validation for Django forms using AngularJS
* 0.2.2
 * Removed now useless directive 'auto-label'. For backwards compatibility
   see https://github.com/jrief/angular-shims-placeholder
* 0.2.1
 * Set Cache-Control: no-cache for Ajax GET requests.
* 0.2.0
 * added handler to mixin class for ajax get requests.
 * moved unit tests into testing directory.
 * changed request.raw_post_data -> request.body.
 * added possibility to pass get and post requests through to inherited view class.
* 0.1.4 - optimized CI process
* 0.1.3 - added first documents
* 0.1.2 - better packaging support
* 0.1.1 - fixed initial data in NgModelFormMixin
* 0.1.0 - initial revision

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/jrief/django-angular/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
