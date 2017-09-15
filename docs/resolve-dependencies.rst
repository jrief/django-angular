.. _resolve-dependencies:

============================
Resolve Angular Dependencies
============================

As with any application, we also must manage the client side files. They normally are not available
from **PyPI** and must be installed by other means than ``pip``. This typically is the
`Node Packet Manager`_ also known as ``npm``. When managing a Django project, I strongly recommend
to keep external dependencies outside of any asset's folder, such as ``static``. They *never
must* be checked into your version control system! Instead change into to the root directory of
your project and run:

.. code-block:: bash

	npm install npm install <pkg>@<version> --save

This command installs third party packages into the folder ``node_modules`` storing all dependencies
inside the file ``package.json``. This file shall be added to revision control, whereas we
explicitly ignore the folder ``node_modules`` by adding it to ``.gitignore``.

We then can restore our external dependencies at any time by running the command ``npm install``.
This step has to be integrated into your project's deployment scripts. It is the equivalent to
``pip install -r requirements.txt``.


Accessing External Dependencies
===============================

Our external dependencies now are located outside of any static folder. We then have to tell Django
where to find them. By using these configuration variables in ``settings.py``

.. code-block:: python

	BASE_DIR = os.path.join(os.path.dirname(__file__)

	# Root directory for this Django project (may vary)
	PROJECT_ROOT = os.path.abspath(BASE_DIR, os.path.pardir)

	STATICFILES_DIRS = (
	    os.path.join(BASE_DIR, 'static'),
	    ('node_modules', os.path.join(PROJECT_ROOT, 'node_modules')),
	)

with this additional static files directory, we now can access external assets, such as

.. code-block:: html

	{% load static %}

	<script src="{% static 'node_modules/angular/angular.min.js' %}" type="text/javascript"></script>


Sekizai
=======

django-sekizai_ is an asset manager for any Django project. It helps the authors of projects to
declare their assets in the files where they are required. During the rendering phase, these
declared assets are grouped together in central places.

**django-sekizai** is an optional dependency, only required if you want to use the postprocessor.

This helps us to separate concern. We include Stylesheets and JavaScript files only when and where
we need them, instead of add every dependency we ever might encounter.

Additionally, in AngularJS we must initialize and optionally configure the loaded modules. Since we
do not want to load and initialize every possible AngularJS module we ever might need in any
sub-pages of our project, we need a way to initialize and configure them where we need them. This
can be achieved with two special Sekizai postprocessors.


Example
-------

In the base template of our project we initialize AngularJS

.. code-block:: django
	:caption: my_project/base.html

	{% load static sekizai_tags %}

	<html ng-app="myProject">
	    <head>
	        ...
	        {% render_block "css" postprocessor "compressor.contrib.sekizai.compress" %}
	        ...
	    </head>
	    <body>
	        ...

somewhere in this file, include the minimum set of Stylesheets and JavaScript files required by
AngularJS

.. code-block:: django

	{% addtoblock "js" %}<script src="{% static 'node_modules/angular/angular.min.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'node_modules/angular-sanitize/angular-sanitize.min.js' %}"></script>{% endaddtoblock %}

Before the closing ``</body>``-tag, we then combine those includes and initialize the client side
application

.. code-block:: django
	:emphasize-lines: 5,11

	...
	{% render_block "js" postprocessor "compressor.contrib.sekizai.compress" %}
	<script type="text/javascript">
	angular.module('myProject', ['ngSanitize', {% with_data "ng-requires" as ng_requires %}
	    {% for module in ng_requires %}'{{ module }}'{% if not forloop.last %}, {% endif %}{% endfor %}
	{% end_with_data %}])
	{% with_data "ng-config" as ng_configs %}
	    {% for config in ng_configs %}.config({{ config }}){% endfor %};
	{% end_with_data %}
	</script>

	</body>

Say, in one of the templates which extends our base template, we need the AngularJS animation
functionality. Instead of adding this dependency to the base template, and thus to every page of
our project, we only add it to the template which requires this functionality.

.. code-block:: django
	:caption: my_project/specialized.html

	{% extends "my_project/base.html" %}
	{% load static sekizai_tags %}

	{% block any_inhertited_block_will_do %}
	    {% addtoblock "js" %}<script src="{% static 'node_modules/angular-animate/angular-animate.min.js' %}"></script>{% endaddtoblock %}
	    {% add_data "ng-requires" "ngAnimate" %}
	    {% addtoblock "ng-config" %}['$animateProvider', function($animateProvider) {
	        // restrict animation to elements with the bi-animate css class with a regexp.
	        $animateProvider.classNameFilter(/bi-animate/); }]{% endaddtoblock %}
	{% endblock %}

Here ``addtoblock "js"`` adds the inclusion of the additional requirement to our list of external
files to load.

The second line, ``add_data "ng-requires" "ngAnimate"`` adds ``ngAnimate`` to the list of Angular
requirements. In our base template we use ``{% with_data "ng-requires" as ng_requires %}`` to iterate
over the list ``ng_requires``, which itself creates the list of AngularJS dependencies.

The third line, ``addtoblock "ng-config"`` adds a configuration statement. In our base template this
is executed after our AngularJS application configured their dependencies.

By using this simple trick, we can delegate the dependency resolution and the configuration of our
AngularJS application to our extended templates. This also applies for HTML snippets included by
an extended template.

This approach is a great way to separate concern to the realm it belongs to.

.. _Node Packet Manager: https://www.npmjs.com/
.. _django-sekizai: https://django-sekizai.readthedocs.io/
