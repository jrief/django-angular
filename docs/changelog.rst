.. _changelog:

===============
Release History
===============

2.2
---
* If an HTML element ``<a>`` contains an ``<i>``-element, then enriche the link element with a
  function to give feedback using a tick symbol when clicked.
* Add function ``acceptOrReject()`` which is invoked by the optional ``prepare()``-function inside
  a submit button. It will scroll to invalid form fields whenever a user tries to submit a
  non-validated form. This has a better user experience rather than disabling submit buttons in
  non-validated forms.


2.1
---
* Add provider ``djangoForm`` to make the button classes for ``showOK()`` , ``showFail()`` and
  ``showSpinner()`` configurable.

2.0.4
-----
* AngularJS directive ``djng-forms-set`` now creates its own child scope, inheriting prototypically.
* AngularJS directive ``button`` does not create its own child scope anymore, and now uses that of
  parent directives, either ``djng-forms-set`` or ``djng-endpoint``.


2.0.3
-----
* Fix #333: Automatically generated form names broken in Python 3.


2.0.2
-----
* Do not render empty ``$message``` if Django's validation rejected a field or the whole form.
* Follow JavaScript best practices.


2.0.1
-----
* Prepared for Django-2.0 by changing imports for urlresolvers.
* Changed scope function ``scrollToRejected()`` to scroll smoothly and to the center of a rejected
  element.


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


1.1.4
-----
* Fixed: broken <select>-element if used with ng-model.
* Started to deprecate ``djng.sekizai_processors.module_list``.

1.1.3
-----
* Fix #309: When using Meta to create forms, ``djng.fields.ModelChoiceField`` isn't substituted for
  Django's ``ModelChoiceField``.

1.1.2
-----
* Rather than checking if a field in a form that uses the ``NgMixins`` is in ``djng.forms.fields``,
  check if the field inherits from ``DefaultFieldMixin``. Allows the use of custom form fields.

1.1.1
-----
* Added spinner to upload areas. Whenever one uploads a file, the wheel spins to improve the client's
  user experience.

1.1
---
* Instead of adding extra functionality to Django's form fields via inheritance magic, now one must
  use the corresponding field classes from ``djng.forms.fields`` if its own form class inheritis
  from ``NgForm`` or ``NgModelForm``.
* Added support to upload files and images via Ajax.

1.0.2
-----
* Added templatetag ``djng_locale_script`` to include the proper AngularJS locale script.

1.0.1
-----
* Fixed #297 "Method ``get_context()`` on custom Widget is never called": Added class ``NgWidgetMixin``
  which allows to override method ``get_context()`` in custom widgets.
* Fixed #288 Incorrect ``<label for="...">`` in widget ``RadioChoiceInput``.

1.0.0
-----
* Added support for Django 1.10 and 1.11, tests & travis updated.
* Drop support for Django 1.7, 1.8 and 1.9.
* Removed templatetag ``{% csrf_value %}``, since Django offers ab equivalent tag.
* Fix file input css (remove the border) and add some documentation about common reported errors.
* Remove support for bower in favor of npm.
* Fix exception while rendering Angular Form using ``as_ul``.

0.8.4
-----
* Added two optional Sekiazai's postprocessors for better dependency resolution of AngularJS
  imports and module initialization.

0.8.3
-----
* Refactored client side test runner to use npm instead of Grunt.
* Use tox to create the testing matrix.
* Fix #261: ModelMultipleChoiceField and CheckboxSelectMultiple.
* Deprecate ``{% csrf_value %}`` in favour of ``{{ csrf_token }}``.

0.8.2
-----
* On the client side, validation of the email address is done using the same regular expression
  as is used by Django. Until 0.8.1, the less restrictive Angular validation patterns were used.
* Some widgets require more finegrained formatting capabilities.Added a slightly modified method
  method:`django.forms.utils.flatatt` which can use its own context for formatting.

0.8.1
-----
* Fixed a bug in NgModelFormMixin.get_form_data(): Using ``and ... or ...`` as ternary operator
  can have unwanted side effects. Also changed other occurrences.

0.8.0
-----
* ``djangular`` has been renamed to ``djng`` and ``ng.django-...`` has been renamed to ``djng-...``.
  This was required by many users since it:
  - caused a naming conflict with another django app named djangular and 
  - the identifier "djangular" by many users was seen as a bad choice.
  - violated the AngularJS principle that only their modules shall be prefixed with "ng".
  Please read https://github.com/jrief/django-angular/issues/35 for the preceded discussion on this
  topic.
* Support for ``ngMessages`` was removed again because
  - its code base was buggy and unmaintained
  - it does not make much sense to reduce the amount of auto-generated HTML
  - it added an alternative form rendering mixin, without any additional functionality
* In the ``<select>`` element, the default ``<option selected="selected">`` did not work anymore.
  This regression was introduced in 0.7.16.

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
