# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django.core.exceptions import FieldError
from django.forms.forms import get_declared_fields
from django.forms.models import BaseModelForm, ModelFormOptions, ALL_FIELDS, fields_for_model
from django.forms.widgets import media_property
from django.utils import six


class PatchedModelFormMetaclass(type):
    """Stolen from django.forms.models and fixed for Django-1.6"""
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, BaseModelForm)]
            # for Django<=1.6, fix bug in forms.models:  ^^^^^^^^^^^^^
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(PatchedModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = ModelFormOptions(getattr(new_class, 'Meta', None))

        # We check if a string was passed to `fields` or `exclude`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        for opt in ['fields', 'exclude', 'localized_fields']:
            value = getattr(opts, opt)
            if isinstance(value, six.string_types) and value != ALL_FIELDS:
                msg = ("%(model)s.Meta.%(opt)s cannot be a string. "
                       "Did you mean to type: ('%(value)s',)?" % {
                           'model': new_class.__name__,
                           'opt': opt,
                           'value': value,
                       })
                raise TypeError(msg)

        if opts.model:
            # If a model is defined, extract form fields from it.

            if opts.fields is None and opts.exclude is None:
                # This should be some kind of assertion error once deprecation
                # cycle is complete.
                warnings.warn("Creating a ModelForm without either the 'fields' attribute "
                              "or the 'exclude' attribute is deprecated - form %s "
                              "needs updating" % name,
                              PendingDeprecationWarning, stacklevel=2)

            if opts.fields == ALL_FIELDS:
                # sentinel for fields_for_model to indicate "get the list of
                # fields from the model"
                opts.fields = None

            fields = fields_for_model(opts.model, opts.fields, opts.exclude,
                                      opts.widgets, formfield_callback,
                                      opts.localized_fields, opts.labels,
                                      opts.help_texts, opts.error_messages)

            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in six.iteritems(fields) if not v]
            missing_fields = set(none_model_fields) - \
                             set(declared_fields.keys())
            if missing_fields:
                message = 'Unknown field(s) (%s) specified for %s'
                message = message % (', '.join(missing_fields),
                                     opts.model.__name__)
                raise FieldError(message)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class
