# -*- coding: utf-8 -*-
import json

from django.core.exceptions import ValidationError
from django.core import serializers
from django.forms.models import modelform_factory
from django.views.generic import FormView

from djng.views.mixins import JSONBaseMixin, JSONResponseException


class NgMissingParameterError(ValueError):
    pass


class NgCRUDView(JSONBaseMixin, FormView):
    """
    Basic view to support default angular $resource CRUD actions on server side
    Subclass and override ``model`` with your model

    Optional 'pk' GET parameter must be passed when object identification is required (save to update and delete)

    If fields != None the serialized data will only contain field names from fields array
    """
    model = None
    fields = None
    form_class = None
    slug_field = 'slug'
    serializer_name = 'python'
    serialize_natural_keys = False

    allowed_methods = ['GET', 'POST', 'DELETE']
    exclude_methods = []

    def get_allowed_methods(self):
        return [method for method in self.allowed_methods if method not in self.exclude_methods]

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to call appropriate methods:
        * $query - ng_query
        * $get - ng_get
        * $save - ng_save
        * $delete and $remove - ng_delete
        """
        allowed_methods = self.get_allowed_methods()
        try:
            if request.method == 'GET' and 'GET' in allowed_methods:
                if 'pk' in request.GET or self.slug_field in request.GET:
                    return self.ng_get(request, *args, **kwargs)
                return self.ng_query(request, *args, **kwargs)
            elif request.method == 'POST' and 'POST' in allowed_methods:
                return self.ng_save(request, *args, **kwargs)
            elif request.method == 'DELETE' and 'DELETE' in allowed_methods:
                return self.ng_delete(request, *args, **kwargs)
        except self.model.DoesNotExist as e:
            return self.error_json_response(e.args[0], 404)
        except NgMissingParameterError as e:
            return self.error_json_response(e.args[0])
        except JSONResponseException as e:
            return self.error_json_response(e.args[0], e.status_code)
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                return self.error_json_response('Form not valid', detail=e.message_dict)
            else:
                return self.error_json_response(e.message)

        return self.error_json_response('This view can not handle method {0}'.format(request.method), 405)

    def get_form_class(self):
        """
        Build ModelForm from model
        """
        return self.form_class or modelform_factory(self.model, exclude=[])

    def build_json_response(self, data, **kwargs):
        return self.json_response(self.serialize_queryset(data), separators=(',', ':'), **kwargs)

    def error_json_response(self, message, status_code=400, detail=None):
        response_data = {
            "message": message,
            "detail": detail,
        }
        return self.json_response(response_data, status=status_code, separators=(',', ':'))

    def serialize_queryset(self, queryset):
        """
        Return serialized queryset or single object as python dictionary
        serialize() only works on iterables, so to serialize a single object we put it in a list
        """
        object_data = []
        is_queryset = False
        query_fields = self.get_fields()
        try:
            iter(queryset)
            is_queryset = True
            raw_data = serializers.serialize(self.serializer_name, queryset, fields=query_fields,
                                             use_natural_keys=self.serialize_natural_keys)
        except TypeError:  # Not iterable
            raw_data = serializers.serialize(self.serializer_name, [queryset, ], fields=query_fields,
                                             use_natural_keys=self.serialize_natural_keys)

        for obj in raw_data:  # Add pk to fields
            obj['fields']['pk'] = obj['pk']
            object_data.append(obj['fields'])

        if is_queryset:
            return object_data
        return object_data[0]  # If there's only one object

    def get_form_kwargs(self):
        kwargs = super(NgCRUDView, self).get_form_kwargs()
        # Since angular sends data in JSON rather than as POST parameters, the default data (request.POST)
        # is replaced with request.body that contains JSON encoded data
        kwargs['data'] = json.loads(self.request.body.decode('utf-8'))

        # Add instance if object identifier present
        if 'pk' in self.request.GET or self.slug_field in self.request.GET:
            kwargs['instance'] = self.get_object()
        return kwargs

    def get_object(self):
        if 'pk' in self.request.GET:
            return self.model.objects.get(pk=self.request.GET['pk'])
        elif self.slug_field in self.request.GET:
            return self.model.objects.get(**{self.slug_field: self.request.GET[self.slug_field]})
        raise NgMissingParameterError(
            "Attempted to get an object by 'pk' or slug field, but no identifier is present. Missing GET parameter?")

    def get_fields(self):
        """
        Get fields to return from a query.
        Can be overridden (e.g. to use a query parameter).
        """
        return self.fields

    def get_queryset(self):
        """
        Get query to use in ng_query
        Allows for easier overriding
        """
        return self.model.objects.all()

    def ng_query(self, request, *args, **kwargs):
        """
        Used when angular's query() method is called
        Build an array of all objects, return json response
        """
        return self.build_json_response(self.get_queryset())

    def ng_get(self, request, *args, **kwargs):
        """
        Used when angular's get() method is called
        Returns a JSON response of a single object dictionary
        """
        return self.build_json_response(self.get_object())

    def ng_save(self, request, *args, **kwargs):
        """
        Called on $save()
        Use modelform to save new object or modify an existing one
        """
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            obj = form.save()
            return self.build_json_response(obj)

        raise ValidationError(form.errors)

    def ng_delete(self, request, *args, **kwargs):
        """
        Delete object and return it's data in JSON encoding
        The response is build before the object is actually deleted
        so that we can still retrieve a serialization in the response
        even with a m2m relationship
        """
        if 'pk' not in request.GET:
            raise NgMissingParameterError("Object id is required to delete.")

        obj = self.get_object()
        response = self.build_json_response(obj)
        obj.delete()
        return response
