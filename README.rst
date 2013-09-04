django-angular
==============

Utilities to let Django play nice together with AngularJS
---------------------------------------------------------

You can find detailed documentation on `ReadTheDocs <http://django-angular.readthedocs.org/>`_

Features
--------
* Seamless integration of Django forms with AngularJS controllers
* Let an AngularJS controller call methods in a Django view - kind of Javascript RPCs
* Add labels to form fields when they are empty
* Manage Django URLs for static controller files
and more to come ...

Build status
------------
.. image:: https://travis-ci.org/jrief/django-angular.png
   :target: https://travis-ci.org/jrief/django-angular

Installation
------------
From pypi::

  pip install django-angular

From github::

  https://github.com/jrief/django-angular

License
-------
Copyright (c) 2013 Jacob Rief  
Licensed under the MIT license.

Release History
---------------
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

