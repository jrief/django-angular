.. _upload-files:

==============================
Upload Files and images Images
==============================

**Django-Angular** emphasizes the use of Ajax request-response cycles while handling form data. One
disadvantage of this approach is, that you can't use it to upload files to the server, because
browsers can not serialize file payload into JSON. Instead, in order to upload files one must
**POST** a ``<form>`` using ``enctype="multipart/form-data"``.

This approach nowadays is outdated. Moreover, it requires the use of an ``<input type="file">``
field, which doesn't provide a good user experience either. A disfunctional example:

.. raw:: html

    <label>Upload File:</label> <input type="file">

Instead, we nowadays are used to drag files directly into the browser window and drop them onto an
input field, which immediately displays the uploaded image. By adding two third party packages,
**django-angular** provides such a solution.

By replacing Django's form fields ``FileField`` against :class:`djng.forms.fields.FileField` and
``ImageField`` against :class:`djng.forms.fields.ImageField`, the corresponding form field is
rendered as a rectangular area, where one can drag a file or image onto, and drop it. It then is
uploaded immediately to the server, which keeps it in a temporary folder and returns a thumbail
of that file/image together with a reference onto a temporary representation.

In the next step, when the user submits the form, only the reference to that temporary file is
added to the post data. Therefore the payload of such a form can be posted using JSON via Ajax.
This gives a much smoother user experience, rather than uploading the form together with the image
payload using a full request-response cycle.


Installation
============

.. code-block:: shell

	pip install easy-thumbnails

and add it to the project's ``settings.py``:

.. code-block:: python

	INSTALLED_APPS = [
	    ...
	    'djng',
	    'easy_thumnails',
	    ...
	]

Check that your ``MEDIA_ROOT`` points onto a writable directory. Use ``MEDIA_URL = '/media/'`` or
whatever is appropriate for your project.

Install additional Node dependencies:

.. code-block:: shell

	npm install ng-file-upload --save


Usage in Forms
==============

First, we must add an endpoint to our application which receives the uploaded images. To the
``urls.py`` of the project add:

.. code-block:: python

	from djng.views.upload import FileUploadView

	urlpatterns = [
	    ...
	    url(r'^upload/$', FileUploadView.as_view(), name='fileupload'),
	    ...
	]

By default files are uploaded into the directory ``<MEDIA_ROOT>/upload_temp``. This location can be
changed using the settings variable ``DJNG_UPLOAD_TEMP``.

In our form declaration, we replace Django's ``ImageField`` by an alternative implementation
provided by **django-angular**. This class accepts two optional additional attributes:

* ``fileupload_url``: The URL pointing onto the view accepting the uploaded image. If omitted, it
  defaults to the URL named ``fileupload``.
* ``area_label``: This is the text rendered inside the draggable area. Don't confuse this with the
  label, which is rendered before that area.

An example:

.. code-block:: python

	from django.urls import reverse_lazy
	from djng.forms import NgModelFormMixin
	from djng.forms.fields import ImageField
	from . import subscribe_form

	class SubscribeForm(NgModelFormMixin, subscribe_form.SubscribeForm):
	    scope_prefix = 'my_data'
	    form_name = 'my_form'

	    photo = ImageField(
	        label='Photo of yourself',
	        fileupload_url=reverse_lazy('fileupload'),
	        area_label='Drop image here or click to upload',
	        required=True)

The Django View responsible for accepting submissions from that form, works just as if Django's
internal :class:`django.forms.fields.ImageField` would have been used. The attribute
``cleaned_data['photo']`` then contains an object of type FieldFile_ after a form submission.

.. _FieldFile: https://docs.djangoproject.com/en/stable/ref/models/fields/#django.db.models.fields.files.FieldFile


Usage in Models
===============

Often you might use a model and rely on Django's automatic form generation. **django-angular** does
this out-of-the-box, whenever the form implementing the model inherits form ``NgModelForm``.


Usage in Templates
==================

When using this file uploader, the Angular App requires an additional stylesheet and an external
JavaScript module:

.. code-block:: django

	{% load static %}

	<head>
	    ...
	    <link href="{% static 'djng/css/fileupload.css' %}" rel="stylesheet" />
	</head>

	<body>
	    ...
	    <script src="{% static 'node_modules/ng-file-upload/dist/ng-file-upload.js' %}" type="text/javascript"></script>
	    <script src="{% static 'djng/js/django-angular.min.js' %}" type="text/javascript"></script>
	</body>

additionally, the Angular App must be initialized such as:

.. code-block:: html

	<script>
	angular.module('myApp', [..., 'djng.fileupload', 'djng.forms', ...])
	.config(['$httpProvider', function($httpProvider) {
	    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	    $httpProvider.defaults.headers.common['X-CSRFToken'] = '{{ csrf_token }}';
	}]);
	</script>


Caveats
=======

When users upload images, but never submit the corresponding form, the folder holding these
temporary images gets filled up. Therefore you should add some kind of (cron)job which cleans up
that folder from time to time.

Depending on your setup, also provide some security measure, so that for example, only logged in
users have access onto the view for uploading images. Otherwise the temporary folder might get
filled with crap.


Security Measures
=================

Altought the relative location of the uploaded files is returned to the client and visible in its
browser, it almost is impossible to access images which have not been uploaded by the provided class
:class:`djng.views.FileUploadView`, or rendered by the provided widget
:class:`djng.forms.widgets.DropFileInput`. This is because all file names are cryptographically
signed, so to harden them against tampering. Otherwise someone else could pilfer or delete images
uploaded to the temporary folder, provided that he's able to guess the image name.
