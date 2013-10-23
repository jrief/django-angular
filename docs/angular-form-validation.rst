.. _angular-form-validation:

=====================================
Validate Django forms using AngularJS
=====================================

Django's ``forms.Form`` class offers many possibilities to validate a given form. This for obvious
reasons is done on the server. However, customers may not always accept to submit a form, just to
find out that they missed to input some correct data into a field. Therefore client side form
validation is a good idea and very common. But since client side validation easily can by bypassed,
the same validation has to occur a second time, when the server accepts the forms data for final
processing.

.. note:: This leads to code duplication is generally violates the DRY principle!

A workaround to this problem is to use Django's form declaration to automatically generate client
side validation code, suitable for AngularJS. By adding a special mixin class to your form
declaration, this can be achieved automatically and on the fly::

  from django import forms
  from djangular.forms import NgModelFormMixin, NgFormValidationMixin

  class MyValidatedForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
      surname = forms.CharField(label='Surname', min_length=3, max_length=20)
      age = forms.DecimalField(min_value=18, max_value=99)

When you initialize this form, give it a name, otherwise the form's name defaults to "form". This is
required, since the AngularJS validation code expects a named form.

In the view class, add the created form to the rendering context::

  def get_context_data(self, **kwargs):
      context = super(MyRenderingView, self).get_context_data(**kwargs)
      context.update(form=MyValidatedForm())
      return context

Render this form in a template::

  <div ng-controller="MyFormController">
      <form name="{{ form.name }}" method="post" novalidate>
          {{ form }}
          <input type="submit" value="Submit" />
      </form>
  </div>

Remember to add the entry ``name="{{ form.name }}"``. Use the directive ``novalidate``, to disable
the browser’s native form validation. Since AngularJS now is responsible for validation wrap the
form declaration into a controller ``ng-controller="MyFormController"``. The most simplest
controller will do the job, if no customized validation has to be performed::

  function MyFormController($scope) {
  }

If this form is rendered, each input field is prefixed with a list of errors, one for each
constraint, which may not be satisfied. If a client now enters some invalid data, these error
messages become visible. The message text is exactly the same as would be shown if the server
complains about invalid data.
