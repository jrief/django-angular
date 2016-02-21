.. _template-sharing:

=============================================
Share a template between Django and AngularJS
=============================================

Templates syntax for Django and AngularJS is very similar, and with some caveats it is possible to
reuse a Django template for rendering in AngularJS. The classical approach to embed AngularJS
template code inside Django's template code, is to use the ``{% verbatim %}`` template tag.
This tag however deactivates all Django's template parsing, so every block tag must be placed
outside a ``{% verbatim %}`` ... ``{% endverbatim %}`` section. This makes mixed template coding
quite messy.

For this purpose use the template tag ``{% angularjs %}``
=========================================================

The template tag ``{% angularjs %}`` ... ``{% endangularjs %}`` delegates Django's variable
expansion to AngularJS, but continues to process the Django block tags, such as ``{% if ... %}``,
``{% for ... %}``, ``{% load ... %}``, etc.

Conditionally activate variable expansion
-----------------------------------------

The template tag ``{% angularjs <arg> %}`` takes one optional argument, which when it evaluates to
true, it turns on AngularJS's variable expansion. Otherwise, if it evaluates to false, it turns on
Django's variable expansion. This becomes handy when using include snippets which then can be used
by both, the client and the server side template rendering engines.

Example
=======

A Django ListView produces a list of items and this list is serializable as JSON. For browsers
without JavaScript and for crawlers from search engines, these items shall be rendered through the
Django's template engine. Otherwise, AngularJS shall iterate over this list and render these items.

Template used by the list view:

.. code-block:: html

	<div ng-if="!items">
	{% for item in items %}
	    {% include "path/to/includes/item-detail.html" with ng=0 %}
	{% endfor %}
	</div>
	<div ng-if="items">
	{% include "path/to/includes/item-detail.html" with ng=1 %}
	</div>

Here the scope variable ``items`` is set by a surrounding ``ng-controller``. As we can see, the
template ``path/to/includes/item-detail.html`` is included twice, once defining an additional
context variable ``ng`` as true and later, the same include with that variable as false.

Assume, this list view shall render a model, which contains the following fields:

.. code-block:: python

	class Item(models.Model):
	    title = CharField(max_length=50)
	    image = ImageField()  # built-in or from a third party library
	    description = HTMLField()  # from a third party library
	    
	    def get_absolute_url(self):
	        return reverse(...)

Now, the included template can be written as:

.. code-block:: html

	{% load djng_tags %}
	{% angularjs ng %}
	<div{% if ng %} ng-repeat="item in items"{% endif %}>
	    <h4><a ng-href="{{ item.absolute_url }}"{% if not ng %} href="{{ item.absolute_url }}"{% endif %}>{{ item.name }}</a></h4>
	    <img ng-src="{{ item.image.url }}"{% if not ng %} src="{{ item.image.url }}"{% endif %} width="{{ item.image.width }}" height="{{ item.image.height }}" />
	    <div{% if ng %} ng-bind-html="item.description"{% endif %}>{% if not ng %}{{ item.description }}{% endif %}</div>
	</div>
	{% endangularjs %}

A few things to note here:

The content between the template tags ``{% angularjs ng %}`` and ``{% endangularjs %}`` is rendered
through the Django template engine as usual, if the context variable ``ng`` evaluates to false.
Otherwise all variable expansions, ie. ``{{ varname }}`` or ``{{ varname|filter }}`` are kept as-is
in HTML, while block tags are expanded by the Django template engine.

The context data, as created by the list view, must be processed into a list serializable as
JSON. This list then can be used directly by the Django template renderer or transferred to the
AngularJS engine, using a XMLHttpRequest or other means.

This means that the default method ``get_context_data()`` must resolve all object fields into basic
values, since invocations to models methods, such as ``get_absolute_url()``, now can not be done
by the template engine, during the iteration step, ie. ``{% for item in items %}``. The same applies
for image thumbnailing, etc.

In AngularJS `references onto URLs`_ and `image sources`_ must be done with ``<a ng-href="...">``
and ``<img ng-src="...">``, rather than using ``<a href="...">`` or ``<img src="...">``
respectively. Therefore, while rendering the Django template, these fields are added twice.

In AngularJS, text data containing HTML tags, must be rendered using ng-bind-html_ rather than
using the mustache syntax. This is to ensure, that unverified content from upstream sources is
sanitized. We can assert this, since this text content is coming from the database field
``description`` and thus is marked as `safe string`_ by Django.


Python List / Javascript Arrays
-------------------------------

The Django template engine accesses members of Python dictionaries using the *dot* notation. This is
the same notation as used by JavaScript to access members of objects. When accessing lists in Django
templates or arrays in JavaScript, this notation is not compatible any more. Therefore as
convenience, always use the Django template notation, even for JavaScript arrays. Say, in Python
you have a list of objects:

.. code-block:: python

	somelist = [{'member': 'first'}, {'member': 'second'}, {'member': 'third'},]

To access the third member, Django's template code shall be written as:

.. code-block:: html

	{{ somelist.2.member }}

when this block is resolved for AngularJS template rendering, the above code is expanded to:

.. code-block:: html

	{{ somelist[2].member }}

otherwise it would be impossible to reuse Python lists converted to JavaScript arrays inside the
same template code.


Conditionally bind scope variables to an element with ``djng-bind-if``
----------------------------------------------------------------------

Sometimes it makes sense to bind the scope variable to an element if it exists. Otherwise render
the same variable from Django's context. Example:

.. code-block:: html

	<span djng-bind-if="some_prefix.value">{{ some_prefix.value }}</span>

functionally, this is equivalent to:

	<span ng-if="some_prefix.value">{% verbatim %}{{ some_prefix.value }}{% endverbatim %}</span>
	<span ng-if="!some_prefix.value">{{ some_prefix.value }}</span>

but less verbose and easier to read.


.. _references onto URLs: https://docs.angularjs.org/api/ng/directive/ngHref
.. _image sources: https://docs.angularjs.org/api/ng/directive/ngSrc
.. _ng-bind-html: https://docs.angularjs.org/api/ng/directive/ngBindHtml
.. _safe string: https://docs.djangoproject.com/en/dev/ref/utils/#module-django.utils.safestring
