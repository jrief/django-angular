.. _forms_set:

=========
Forms Set
=========

In component based web development, it is quite common to arrange more than one form on the same
page. As opposed to form submissions via ``application/x-www-form-urlencoded`` or
``multipart/form-data``, we can, thanks to Ajax, submit the content of more than one form using a
single HTTP-request. This requires to dispatch the submitted data on the server to each form class,
but if we prefix them with unique identifiers, that's a no-brainer.


Directive ``djng-forms-set``
============================

To achieve this, we can reuse the same Form mixin classes as we have used in the previous examples.
The main difference is that we must wrap the set of forms into the AngularJS directive,
``<djng-forms-set upload-url="/some/endpoint">...</djng-forms-set>``. Inside this directive, we
render the forms as usual using ``{⁠{ some_form.as_div }⁠}``.


Forms Submission
----------------

The submit button(s) can now be placed outside of the ``<form>...</form>`` element. This allows us
to submit the content from multiple forms altogether. We now however must specify the common
endpoint to accept our form submissions; this is, as you might have expected, the attribute
``upload-url="/some/endpoint" in our forms wrapping directive ``djng-forms-set``. To send the forms
content to the server, add ``ng-click="update()"`` to the submission button. By itself however,
this invocation of ``update()`` does not execute any further action on the client. We therefore
must tell our directive, what we want to do next. For this, **django-angular**'s ``button``
directive offers a few prepared targets, such as ``reloadPage()`` or ``redirectTo()``. They
typically shall be executed asynchronouosly, *after* the server replied to the update request.


Chaining Targets
................

Since form submission is asynchronous, here we extensively use the promises functions provided by
AngularJS.

If we change the button element to ``<button ng-click="update().then(reloadPage())">``, *then*
after our successful Ajax submission, the current page is reloaded.

Another useful target is ``redirectTo('/path/to/view')``, which, after a successful submission,
redirects the user to another page. If the response contains
``{data: {success_url: "/path/to/other/view"}}``, then the URL provided to the ``redirectTo(...)``
function is overridden by ``success_url``.

If we override the ``button`` directive in our own application, we can add as many alternative
targets as we want. This can be used to create execution chains as just demonstrated.


Forms Validation
----------------

All Forms wrapped inside our ``djng-forms-set`` directive, are validated. This can and shall be
used to prevent submitting data, if at least one of the forms does not validate. For this, just
add ``ng-disabled="setIsInvalid"`` to the submission button.


Form Submission Methods
-----------------------

By using the ``update()`` function, **django-angular** submits the forms data with an HTTP-request
using method *PUT*. To submit the same data using HTTP method *POST*, use the provided function
``create()``. To submit via HTTP method *DELETE*, use the provided function ``delete()``.


Form Processing Delays
----------------------

Sometimes processing form data can take additional time. To improve the user experience, we shall
add some feedback to the submission button. By changing the submit action to
``ng-click="disableButton().then(update().then(redirectTo()).finally(reenableButton()))"`` the
submit button is deactivated (``disableButton``) during the form submission and will be reactivated
(``reenableButton``) as soon as the server responded. Here we use ``finally``, since we want to
reactivate the button, regardless of the servers's success status. Remember,
``...then(redirectTo())`` is only invoked on success.

If the <button> element contains an <i> element, during the timeout period, the CSS classes are
replaced by ``glyphicon glyphicon-refresh djng-rotate-animate``. This adds a rotating spinner wheel
to the button until ``reenableButton()`` is executed.


Passing Extra Data
------------------

Sometimes we might want to use more than one submit button. In order to distinguish which of those
buttons has been pressed, add for instance ``extra-data="{foo: 'bar'}"`` to the corresponding
``<button>`` element. That dictionary then is added to the payload and can be extracted by the
server's view for further analysis.
