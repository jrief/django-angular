.. _angular-model-form:

===============================================
Integrate a Django form with an AngularJS model
===============================================

When you derive from Django's ``forms.Form`` class in an AngularJS environment, it can be useful to
augment the rendered form output with the HTML tags::

  ng-model="model_name"

where *model_name* corresponds to the named field from the declared form class.

Sample code
-----------

Assume you have a simple Django form class with a single input field. Augment its functionality
by mixing in the **djangular** class ``NgModelFormMixin``::

  from django import forms
  from djangular.forms.angular_model import NgModelFormMixin
  
  class ContactForm(NgModelFormMixin, forms.Form):
      subject = forms.CharField()

Now, each rendered form field gets an additional attribute ``ng-model`` containing the field's name.
For instance, the input field named **subject** would be rendered as:

.. code-block:: html

  <input id="id_subject" type="text" name="subject" ng-model="subject" />

This means, that to a surrounding Angular controller, the field's value is immediately added to its
``$scope``.

Full working example
====================

This demonstrates how to submit form data using an AngularJS controller. The Django view handling
this unbound contact form class may look like::

  from django.views.generic import TemplateView

  class ContactFormView(TemplateView):
      template = 'contact.html'
  
      def get_context_data(self, **kwargs):
          context = super(ContactFormView, self).get_context_data(**kwargs)
          conext.update(contact_form=ContactForm())
          return context

with a template named ``contact.html``:

.. code-block:: html

  <form ng-controller="MyFormCtrl">
      {{contact_form}}
      <button ng-click="submit()">Submit</button>
  </form>

.. _angular-model-form-example:

and using some Javascript code to define the AngularJS controller:

.. code-block:: javascript

  function MyFormCtrl($scope, $http) {
      $scope.submit = function() {
          $http.post('/url/of/your/contact_form_view', {
              subject: $scope.subject
          }).success(function(out_data) {
              // do something
          });
      }
  }

Note that your ``<form>`` does not require any ``method`` or ``action`` attribute, since the
promise_ ``success`` in your controller's submit function will handle any further action, for
instance to load a new page or to complain about missing fields. In fact, you can build forms
without even using the ``<form>`` tag anymore. All you need from now on, is a working
AngularJS controller.

As usual, your form view must handle the post data received through the POST (aka Ajax) request.
However, AngularJS does not send post data using ``multipart/form-data`` or
``application/x-www-form-urlencoded`` encoding - rather, it uses plain JSON, which avoids an
additional decoding step.

.. note:: In real code you should not hard code the URL into an AngularJS controller as shown in
       this example. Instead inject an object containing the URL into your controller as explained
       in :ref:`manage Django URL's for AngularJS <manage-urls>`

Add these methods to your contact form view::

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
          in_data = json.loads(request.raw_post_data)
          bound_contact_form = CheckoutForm(data={'subject': in_data.get('subject')})
          # now validate ‘bound_contact_form’ and use it as in normal Django

The problem with this implementation, is that one must remember to access each form field three
times. Once in the declaration of the form, once in the Ajax handler of your AngularJS controller,
and once in the post handler of the view. This make maintenance hard and is a violation of the DRY
principle. Therefore it makes sense to add a prefix to the model names. One possibility would be to add
the argument ``scope_prefix`` on each form's instantiation, ie.::

  contact_form = ContactForm(scope_prefix='my_prefix')

This, however, has to be done across all instantiations of your form class. The better way is to hard
code this prefix into the constructor of the form class::

  class ContactForm(NgModelFormMixin, forms.Form):
      # declare form fields
  
      def __init__(self, *args, **kwargs):
          kwargs.update(scope_prefix='my_prefix')
          super(ContactForm, self).__init__(*args, **kwargs)

Now, in your AngularJS controller, the scope for this form starts with an object named ``my_prefix``
containing an entry for each form field. This means that an input field, for instance, is rendered as:

.. code-block:: html

  <input id="id_subject" type="text" name="subject" ng-model="my_prefix.subject" />

This also simplifies your Ajax submit function, because you just have to pass the Javascript object
``$scope.my_prefix`` as

.. code-block:: javascript

   $http.post('/url/of/contact_form_view', $scope.my_prefix)

to your Django view.

Working with nested forms
-------------------------

**NgModelFormMixin** is able to handle nested forms as well. Just remember to add the attribute
``prefix='subform_name'`` with the name of the sub-form, during the instantiation of your main form.
Now your associated AngularJS controller adds this additional model to the object
``$scope.my_prefix``, keeping the whole form self-contained and accessible through one Javascript
object, aka ``$scope.my_prefix``.

The Django view responsible for handling the post request of this form automatically handles the
parsing of all bound form fields, even from the nested forms.

.. note:: Django, internally, handles the field names of nested forms by concatenating the prefix
          with the field name using a dash ‘``-``’. This behavior has been overridden in order to
          use a dot ‘``.``’, since this is the natural separator between Javascript objects.

.. _promise: https://en.wikipedia.org/wiki/Promise_(programming)
.. _manage Django URL's for AngularJS: manage-urls
