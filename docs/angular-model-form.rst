.. _angular-model-form:

===============================================
Integrate a Django form with an AngularJS model
===============================================

When deriving from Django's ``forms.Form`` class in an AngularJS environment, it can be useful to
enrich the rendered form input fields with an AngularJS HTML tag, such as ``ng-model="my_field"``,
where *my_field* corresponds to the named field from the declared form class.


Sample code
===========

Assume we have a simple Django form class with a single input field. Enrich its functionality
by mixing in the **djng** class ``NgModelFormMixin``

.. note:: Here the names **NgModelForm...** do not interrelate with Django's ``forms.ModelForm``.
		Instead that name reflects the HTML attribute ``ng-model`` as used in ``<form>``-elements
		under control of AngularJS.

.. code-block:: python

	from django import forms
	from django.utils import six
	from djng.forms import fields, NgDeclarativeFieldsMetaclass, NgModelFormMixin

	class ContactForm(six.with_metaclass(NgDeclarativeFieldsMetaclass, NgModelFormMixin, forms.Form)):
	    subject = fields.CharField()
	    # more fields ...

.. note:: Since **django-angular**-1.1, you must use the adopted field classes provided by **django-angular**,
		instead of Django's own ``fields`` module.

In the majority of cases, the Form inherits from Django's ``forms.Form``, so the above example
can be rewritten in a simpler way, by using the convenience class ``NgForm`` as a replacement:

.. code-block:: python

	from djng.forms import NgModelFormMixin, NgForm

	class ContactForm(NgModelFormMixin, NgForm):
	    # members as above

If the Form shall inherit from Django's ``forms.ModelForm``, use the convenience class
``NgModelForm``:

.. code-block:: python

	from djng.forms import NgModelFormMixin, NgModelForm

	class ContactForm(NgModelFormMixin, NgModelForm):
	    class Meta:
	         model = ContactModel

	    # fields as usual

Now, each form field rendered by Django, gets an additional attribute ``ng-model`` containing the
field's name. For example, the input field named ``subject`` now will be rendered as:

.. code-block:: html

	<input id="id_subject" type="text" name="subject" ng-model="subject" />

This means, that to a surrounding Angular controller, the field's value is immediately added to its
``$scope``. Since we do not want to pollute the AngularJS's scope with various field names, we pack
them into one single JavaScript object, named according to the ``scope_prefix`` attribute in our
Form class. The above field, then would be rendered as:

.. code-block:: html

	<input id="id_subject" type="text" name="subject" ng-model="my_prefix['subject']" />


Full working example
====================

This demonstrates how to submit form data using **django-angular**'s built-in form controller via Ajax.
The Django view handling this unbound contact form class may look like

.. code-block:: python

	import json
	from django.http import JsonResponse
	from django.urls import reverse_lazy
	from django.views.generic import FormView
	from djng.forms import NgModelFormMixin, NgForm

	class ContactForm(NgModelFormMixin, NgForm):
	    form_name = 'contact_form'
	    scope_prefix = 'contact_data'
	    subject = fields.CharField()

	class ContactFormView(FormView):
	    template = 'contact.html'
	    form_class = ContactForm
	    success_url = reverse_lazy('success-page')

	    def post(self, request, **kwargs):
	        assert request.is_ajax()
	        request_data = json.loads(request.body)
	        form = self.form_class(data=request_data[self.form_class.scope_prefix])
	        if form.is_valid():
	            return JsonResponse({'success_url': force_text(self.success_url)})
	        else:
	            response_data = {form.form_name: form.errors}
	            return JsonResponse(response_data, status=422)

with a template named ``contact.html``:

.. code-block:: html

	<form djng-endpoint="/path/to/contact-form-view" name="contact_form">
	    {{ contact_form }}
	    <button ng-click="do(update()).then(redirectTo())">Submit</button>
	</form>

Note that the ``<form>`` tag does not require any ``method`` or ``action`` attribute. This is because
the form submission is not initiated by the form's submit handler, but rather by the button's *click*
event handler. Inside this click handler, we first submit the form data using the ``update()``
function which itself returns a promise_. On success, our click handler invokes the function inside the
following ``.then(...)`` handler. Since it receives the HTTP response object from the previous
submission, we use this inside the ``redirectTo()`` function. Therefore, we can pass our
``success_url`` from the server, down to our submit button, so that this can trigger a page redirection
action.

In case the form was not validated by the server, a response with an error code 422 (Unprocessable
Entity) is returned. In such a case, the error handler of our form submission function uses the
returned data to fill the normally invisible error message placeholders located nearby each of our
form fields.

.. note:: In real code, do not hard code the URL of the endpoint as shown in this example. Instead
		use the templatetag ``{% url ... %}``.


Working with nested forms
-------------------------

**NgModelFormMixin** is able to handle nested forms as well. Just remember to add the attribute
``prefix='subform_name'`` with the name of the sub-form, during the instantiation of your main form.
Now your associated AngularJS controller adds this additional model to the object
``$scope.my_prefix``, keeping the whole form self-contained and accessible through one Javascript
object, aka ``$scope.my_prefix``.

Nested forms must use the AngularJS directive ``<ng-form ...>`` rather than ``<form ...>``.

.. note:: Django, internally, handles the field names of nested forms by concatenating the prefix
		with the field name using a dash ‘``-``’. This behavior has been overridden in order to
		use a dot ‘``.``’, since this is the natural separator between Javascript objects.


Form with FileField or ImageField
---------------------------------

If you have a ``FileField`` or an ``ImageField`` within your form, you need to provide a file
upload handler. Please refer to the section :ref:`upload-files` for details.

.. _promise: https://en.wikipedia.org/wiki/Promise_(programming)
