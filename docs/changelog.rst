.. _changelog:

===============
Release History
===============

0.7.16
------
* Ready for Django-1.9.
* Fixed: Non-ascii characters were not being processed correctly by ``django.http.request.QueryDict.init``.
* In JavaScript, replaced ``console.log`` by ``$log.log``.
* Use decimal base on invocation of ``parseInt``.
* Use square brackets to access scope members, which otherwise won't support fields containing ``-``.
* templatetag ``load_djng_urls`` has been removed.
* For CRUD, check if request method is allowed.
* Fixed djngError directive, when using AngularJS-1.3.
* Added support for ``ngMessages``, as available with AngularJS-1.3.

0.7.15
------
* Simplified middleware for reversing the URL.
* Reversing url in ``djangoUrl`` service can now be overriden.

0.7.14
------
* Supporting Django-1.8.
* The widget ``bootstrap3.widgets.CheckboxInput`` got a keyword to set the choice label of a field.
  This allows to style this kind of field individually in a Django ``Form``.

0.7.13
------
* Change for Forms inheriting from ``NgFormBaseMixin`` using ``field_css_classes`` as dict:
  CSS classes specified as default now must explicitly be added the fields defining their own
  CSS classes. Before this was implicit.
* Added AngularJS directive ``djng-bind-if``. See docs for details.
* Reverted fix for FireFox checkbox change sync issue (135) since it manipulated the DOM. Instead
  added ``scope.$apply()`` which fixes the issue on FF.
* In BS3 styling, added ``CheckboxFieldRenderer`` to ``CheckboxInlineFieldRenderer`` (the default),
  so that forms with multiple checkbox input fields can be rendered as block items instead of
  inlines.
* In BS3 styling, added ``RadioFieldRenderer`` to ``RadioInlineFieldRenderer`` (the default), so
  that forms with multiple radio input fields can be rendered as block items instead of inlines.
* Fixed 'classic form' issue whereby ``ngModel`` was not being added to ``select`` of ``textarea``
  elements, so returned errors where not displayed.

0.7.12
------
* No functional changes.

0.7.11
------
* Using ``field.html_name`` instead of ``field.name``. Otherwise ``add_prefix()`` function on
  form objects doesn't work properly.
* Fixed Firefox checkbox change sync issue caused by ``click`` and ``change`` firing in
  opposite order to other browsers. Switched to ``ng-change`` to normalise behaviour.
* Moved rejected error cleanup logic into ``field.clearRejected`` method, so that it can be
  removed from anywhere that has access to the field.
* Fixed issue in rejected error clean up loop.
* Added missing subfield cleanup to rejected error cleanup loop.
* Added AngularJS service ``djangoUrl`` to resolve URLs on the client in the same way as on
  the server.

0.7.10
------
* Fixed inheritance problem (#122) caused by a metaclass conflicting with Django's
  ``DeclarativeFieldsMetaclass``. This now should fix some issues when using ``forms.ModelForm``.
  This fix changed the API slightly.
* Fixed expansion for templatetag ``{% angularjs %}`` (#117) when using lists in Python / arrays
  in JavaScript.

0.7.9
-----
* ``TupleErrorList`` has been adopted to fully support Django-1.7.

0.7.8
-----
* Fixed: ``ng-minlength`` and ``ng-maxlength`` are not set to ``None`` if unset.
* Fixed: Concatenated latest version of django-angular.js.

0.7.7
-----
* Refactored the code base. It now is much easier to understand the code and to add custom
  Fields and Widgets.
* Fixed the behaviour of all Widgets offered by Django. They now all validate independently of the
  method (Post or Ajax) used to submit data to the server.

0.7.6
-----
* Fixed regression when using ``Bootstrap3FormMixin`` in combination with ``widgets.CheckboxSelectMultiple``.

0.7.5
-----
* Added: Template tag {% angularjs %} which allows to share templates between Django and AngularJS.
* Fixed: Using {{ field.error }} returned unsafe text.
* Fixed: Adjust the regular expression and run grunt build.

0.7.4
-----
* Fixed: Error rendering while for hidden input fields.
* Fixed: Bootstrap3 styling: label for field was rendered as lazy object instead of string.
* Added: Url resolvers for angular controllers.

0.7.3
-----
* Added support to render a Django Form using a plugable style. Bootstrap3 styling has been
  implemented.
* Added AngularJS directive for ``<input>`` fields: They now add a dummy ``ngModel`` to some
  input fields, so that Forms using the ``NgFormBaseMixin`` honor the pristine state and display
  an error list from the bound form.
* Replaced AngularJS directive for ``form`` by a directive for ``ngModel``. This directive
  restores the values in bound forms otherwise not vivible in the browser.
* Fixed: Instead of adding attributes to Form Field Widgets, those additional attributes now are
  added on the fly while rendering. This caused some problems, when Forms were reused in different
  contexts.
* Fixed: Behavior for BooleanField and MultipleChoiceField has been fixed so AngularJS form
  validation.

0.7.2
-----
* Fixed: select fields, multiple select fields, radio and checkbox input fields and text areas are
  handled by the built-in form directive to adopt Django's bound forms for AngularJS.

0.7.1
-----
* For remote method invocation, replace keyword ``action`` against a private HTTP-header
  ``DjNg-Remote-Method``. Added template tags ``djng_all_rmi`` and ``djng_current_rmi`` which
  return a list of methods to be used for remote invocation.
* Experimental support for Python-3.3.

0.7.0
-----
* Refactored errors handling code for form validation.
  It now is much easier and more flexible for mixing in other form based classes.
* Added a date validator using an AngularJS directive.
  * Can be used as a starting point for other customized validators.
* Added another view, which can be used for NgModelMixin without NgValidationMixin.
* Added new directory to handle client code.
  * Separated JS files for easier development.
  * Grunt now builds, verifies and concatenates that code.
  * Karma and Jasmine run unit tests for client code.
  * A minified version of ``django-angular.js`` is build by grunt and npm-uglify.
* Rewritten the demo pages to give a good starting point for your own projects.

0.6.3
-----
* **ADOPT YOUR SOURCES**:
  The Javascript file ``/static/js/djng-websocket.js`` has been moved and renamed to
  ``/static/djangular/js/django-angular.js``
* Internal error messages generated by server side validation, now are mixed with AngularJS's
  validation errors.
* A special list-item is added to the list of errors. It is shown if the input field contains valid
  data.
* Input fields of bound forms, now display the content of the field, as expected. This requires the
  Angular module ``ng.django.forms``.

0.6.2
-----
* Refactored ``NgFormValidationMixin``, so that potential AngularJS errors do not interfere with
  Django's internal error list. This now allows to use the same form definition for bound and
  unbound forms.

0.6.1
-----
* Bug fix for CRUD view.

0.6.0
-----
* Support for basic CRUD view.

0.5.0
-----
* Added three way data binding.

0.4.0
-----
* Removed @csrf_exempt on dispatch method for Ajax requests.

0.3.0
-----
Client side form validation for Django forms using AngularJS

0.2.2
-----
* Removed now useless directive 'auto-label'. For backwards compatibility
  see https://github.com/jrief/angular-shims-placeholder

0.2.1
-----
* Set Cache-Control: no-cache for Ajax GET requests.

0.2.0
-----
* added handler to mixin class for ajax get requests.
* moved unit tests into testing directory.
* changed request.raw_post_data -> request.body.
* added possibility to pass get and post requests through to inherited view class.

0.1.4
-----
* optimized CI process

0.1.3
-----
* added first documents

0.1.2
-----
* better packaging support

0.1.1
-----
* fixed initial data in NgModelFormMixin

0.1.0
-----
* initial revision
