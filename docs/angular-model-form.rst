.. _angular-model-form:

===============================================
Integrate a Django form with an AngularJS model
===============================================

When deriving from Django's ``forms.Form`` class in an AngularJS environment, it can be useful to
enrich the rendered form output with an AngularJS HTML tag, such as::

	ng-model="model_name"

where *model_name* corresponds to the named field from the declared form class.

Sample code
===========

Assume to have a simple Django form class with a single input field. Enrich its functionality
by mixing in the **djng** class ``NgModelFormMixin``

.. note:: Here the names **NgModelForm...** do not interrelate with Django's ``forms.ModelForm``.
		Instead that name reflects the HTML attribute ``ng-model`` as used in ``<form>``-elements
		under control of AngularJS.

.. code-block:: python

	from django import forms
	from django.utils import six
	from djng.forms import NgDeclarativeFieldsMetaclass, NgModelFormMixin

	class ContactForm(six.with_metaclass(NgDeclarativeFieldsMetaclass, NgModelFormMixin, forms.Form)):
	    subject = forms.CharField()
	    # more fields ...

In the majority of cases, the Form is derived from Django's ``forms.Form``, so the above example
can be rewritten in a simpler way, by using the convenience class ``NgForm`` as a replacement:

.. code-block:: python

	from djng.forms import NgModelFormMixin, NgForm

	class MyValidatedForm(NgModelFormMixin, NgForm):
	    # members as above

If the Form shall inherit from Django's ``forms.ModelForm``, use the convenience class
``NgModelForm``:

.. code-block:: python

	from djng.forms import NgModelFormMixin, NgModelForm

	class MyValidatedForm(NgModelFormMixin, NgModelForm):
	    class Meta:
	         model = Article

	    # fields as usual

Now, each rendered form field gets an additional attribute ``ng-model`` containing the field's name.
For example, the input field named ``subject`` now will be rendered as:

.. code-block:: html

	<input id="id_subject" type="text" name="subject" ng-model="subject" />

This means, that to a surrounding Angular controller, the field's value is immediately added to its
``$scope``.

Full working example
====================

This demonstrates how to submit form data using an AngularJS controller. The Django view handling
this unbound contact form class may look like

.. code-block:: python

	from django.views.generic import TemplateView

	class ContactFormView(TemplateView):
	    template = 'contact.html'

	    def get_context_data(self, **kwargs):
	        context = super(ContactFormView, self).get_context_data(**kwargs)
	        context.update(contact_form=ContactForm())
	        return context

with a template named ``contact.html``:

.. code-block:: html

	<form ng-controller="MyFormCtrl" name="contact_form">
	    {{contact_form}}
	    <button ng-click="submit()">Submit</button>
	</form>

.. _angular-model-form-example:

and using some Javascript code to define the AngularJS controller:

.. code-block:: javascript

	my_app.controller('MyFormCtrl', function($scope, $http) {
	    $scope.submit = function() {
	        var in_data = { subject: $scope.subject };
	        $http.post('/url/of/your/contact_form_view', in_data)
	            .success(function(out_data) {
	                // do something
	            });
	    }
	});

Note that the ``<form>`` tag does not require any ``method`` or ``action`` attribute, since the
promise_ ``success`` in the controller's submit function will handle any further action.
The success handler, for instance could load a new page or complain about missing fields. It now
it is even possible to build forms without using the ``<form>`` tag anymore. All what's needed
from now on, is a working AngularJS controller.

As usual, the form view must handle the post data received through the POST (aka Ajax) request.
However, AngularJS does not send post data using ``multipart/form-data`` or
``application/x-www-form-urlencoded`` encoding – rather, it uses plain JSON, which avoids an
additional decoding step.

.. note:: In real code, do not hard code the URL into an AngularJS controller as shown in this
		example. Instead inject an object containing the URL into the form controller as explained
		in :ref:`manage Django URL's for AngularJS <manage-urls>`

Add these methods to view class handling the contact form

.. code-block:: python

	import json
	from django.views.decorators.csrf import csrf_exempt
	from django.http import HttpResponseBadRequest

	class ContactFormView(TemplateView):
	    # use ‘get_context_data()’ from above

	    @csrf_exempt
	    def dispatch(self, *args, **kwargs):
	        return super(ContactFormView, self).dispatch(*args, **kwargs)

	    def post(self, request, *args, **kwargs):
	        if not request.is_ajax():
	            return HttpResponseBadRequest('Expected an XMLHttpRequest')
	        in_data = json.loads(request.body)
	        bound_contact_form = CheckoutForm(data={'subject': in_data.get('subject')})
	        # now validate ‘bound_contact_form’ and use it as in normal Django

.. warning:: In real code, **do not** use the ``@csrf_exempt`` decorator, as shown here for
		simplicity. Please read on how
		to :ref:`protect your views from Cross Site Request Forgeries<csrf-protection>`.

Prefixing the form fields
-------------------------
The problem with this implementation, is that one must remember to access each form field three
times. Once in the declaration of the form, once in the Ajax handler of the AngularJS controller,
and once in the post handler of the view. This make maintenance hard and is a violation of the DRY
principle. Therefore it makes sense to add a prefix to the model names. One possibility would be to
add the argument ``scope_prefix`` on each form's instantiation, ie.::

	contact_form = ContactForm(scope_prefix='my_prefix')

This, however, has to be done across all instantiations of your form class. The better way is to
hard code this prefix into the constructor of the form class

.. code-block:: python

	class ContactForm(NgModelFormMixin, forms.Form):
	    # declare form fields

	    def __init__(self, *args, **kwargs):
	        kwargs.update(scope_prefix='my_prefix')
	        super(ContactForm, self).__init__(*args, **kwargs)

Now, in the AngularJS controller, the scope for this form starts with an object named ``my_prefix``
containing an entry for each form field. This means that an input field, the is rendered
as:

.. code-block:: html

	<input id="id_subject" type="text" name="subject" ng-model="my_prefix.subject" />

This also simplifies the Ajax submit function, because now all input fields are available as a
single Javascript object, which can be posted as ``$scope.my_prefix`` to your Django view:

.. code-block:: javascript

	$http.post('/url/of/contact_form_view', $scope.my_prefix)

Working with nested forms
-------------------------
**NgModelFormMixin** is able to handle nested forms as well. Just remember to add the attribute
``prefix='subform_name'`` with the name of the sub-form, during the instantiation of your main form.
Now your associated AngularJS controller adds this additional model to the object
``$scope.my_prefix``, keeping the whole form self-contained and accessible through one Javascript
object, aka ``$scope.my_prefix``.

The Django view responsible for handling the post request of this form, automatically handles the
parsing of all bound form fields, even from the nested forms.

.. note:: Django, internally, handles the field names of nested forms by concatenating the prefix
		with the field name using a dash ‘``-``’. This behavior has been overridden in order to
		use a dot ‘``.``’, since this is the natural separator between Javascript objects.

.. _promise: https://en.wikipedia.org/wiki/Promise_(programming)


Form with FileField or ImageField
---------------------------------

If you have a `FileField` within your form, you need to add in your `<form>` definition:

`enctype="multipart/form-data`

For fancier rendering and behaviour, consider using a custom directive.
Handling file upload is a bit out of scope for this library.

Only basic behaviour is supported with django-angular.
