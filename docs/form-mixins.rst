.. _form_mixins: AddPlaceholderFormMixin

==========================================
Using attribute placeholder in input field
==========================================

If rendering space is sparse, sometimes it makes sense to place the label of an input field inside
itself, such as shown here:

.. image:: _static/unbound-form.png
   :width: 350
   :alt: Screenshot of an unbound form view

these labels are rendered in grey, so that they can easily be distinguished from normal user input.
If the user starts to enter text into such a field, then the placeholder vanishes.

To ease the integration with Django, add ``AddPlaceholderFormMixin`` while declaring your form
class::

  from django import forms
  from djangular.forms.mixins import AddPlaceholderFormMixin
  
  class ContactForm(AddPlaceholderFormMixin, forms.Form):
      # all form fields as usual
      pass

you may of course add other mixins to this form class, such as
:ref:`NgModelFormMixin <angular-model-form>`. 

If you need backward compatibility with older browsers, which do not support the placeholder
attribute, use this AngularJS directive: https://github.com/jrief/angular-shims-placeholder

.. note:: In Django-1.5 the form API changed and adding non standard attributes to fields became
          easier.
