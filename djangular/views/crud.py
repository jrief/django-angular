# -*- coding: utf-8 -*-
import json

from django.core.exceptions import ValidationError
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.views.generic import FormView


class NgCRUDView(FormView):
    """
    Basic view to support default angular $resource CRUD actions on server side
    Subclass and override model_class with your model

    Optional 'pk' GET parameter must be passed when object identification is required (save to update and delete)

    If fields != None the serialized data will only contain field names from fields array
    """
    model_class = None
    fields = None
    content_type = 'application/json'
    slug_field = 'slug'

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to call appropriate methods:
        * $query - ng_query
        * $get - ng_get
        * $save - ng_save
        * $delete and $remove - ng_delete
        """
        if request.method == 'GET':
            if 'pk' in request.GET or self.slug_field in request.GET:
                return self.ng_get(request, *args, **kwargs)
            return self.ng_query(request, *args, **kwargs)
        elif request.method == 'POST':
            return self.ng_save(request, *args, **kwargs)
        elif request.method == 'DELETE':
            return self.ng_delete(request, *args, **kwargs)
        return self.error_json_response('This view can not handle method {0}'.format(request.method), 405)

    def get_form_class(self):
        """
        Build ModelForm from model_class
        """
        return modelform_factory(self.model_class)

    def build_json_response(self, data):
        response = HttpResponse(self.serialize_to_json(data), self.content_type)
        response['Cache-Control'] = 'no-cache'
        return response

    def error_json_response(self, message, status_code=400, detail=None):
        response_data = {
            "message": message,
            "detail": detail,
        }
        response = HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder, separators=(',', ':')), self.content_type, status=status_code)
        response['Cache-Control'] = 'no-cache'
        return response

    def serialize_to_json(self, queryset):
        """
        Return JSON serialized data
        serialize() only works on iterables, so to serialize a single object we put it in a list
        """
        object_data = []
        query_fields = self.get_fields()
        try:
            iter(queryset)
            raw_data = serializers.serialize('python', queryset, fields=query_fields)
        except TypeError:  # Not iterable
            raw_data = serializers.serialize('python', [queryset, ], fields=query_fields)

        for obj in raw_data:  # Add pk to fields
            obj['fields']['pk'] = obj['pk']
            object_data.append(obj['fields'])

        if len(raw_data) > 1:  # If a queryset has more than one object
            return json.dumps(object_data, cls=DjangoJSONEncoder, separators=(',', ':'))
        return json.dumps(object_data[0], cls=DjangoJSONEncoder, separators=(',', ':'))  # If there's only one object

    def get_form_kwargs(self):
        kwargs = super(NgCRUDView, self).get_form_kwargs()
        # Since angular sends data in JSON rather than as POST parameters, the default data (request.POST)
        # is replaced with request.body that contains JSON encoded data
        kwargs['data'] = json.loads(self.request.body)
        if 'pk' in self.request.GET or self.slug_field in self.request.GET:
            kwargs['instance'] = self.get_object()
        return kwargs

    def get_object(self):
        if 'pk' in self.request.GET:
            return self.model_class.objects.get(pk=self.request.GET['pk'])
        elif self.slug_field in self.request.GET:
            return self.model_class.objects.get(**{self.slug_field: self.request.GET[self.slug_field]})
        raise ValueError("Attempted to get an object by 'pk' or slug field, but no identifier is present. Missing GET parameter?")

    def get_fields(self):
        """
        Get fields to return from a query.
        Can be overridden (e.g. to use a query parameter).
        """
        return self.fields

    def get_query(self):
        """
        Get query to use in ng_query
        Allows for easier overriding
        """
        return self.model_class.objects.all()

    def ng_query(self, request, *args, **kwargs):
        """
        Used when angular's query() method is called
        Build an array of all objects, return json response
        """
        return self.build_json_response(self.get_query())

    def ng_get(self, request, *args, **kwargs):
        """
        Used when angular's get() method is called
        Returns a JSON response of a single object dictionary
        """
        try:
            return self.build_json_response(self.get_object())
        except self.model_class.DoesNotExist as e:
            return self.error_json_response(str(e), 404)
        except ValidationError as e:
            return self.error_json_response(e.message)
        except ValueError as e:
            return self.error_json_response(str(e))

    def ng_save(self, request, *args, **kwargs):
        """
        Called on $save()
        Use modelform to save new object or modify an existing one
        """
        try:
            form = self.get_form(self.get_form_class())
        except ValidationError as e:
            # Validation errors may already occur during instantiation.
            return self.error_json_response(e.message)

        if form.is_valid():
            obj = form.save()
            return self.build_json_response(obj)
        return self.error_json_response('Form not valid', detail=form.errors)

    def ng_delete(self, request, *args, **kwargs):
        """
        Delete object and return it's data in JSON encoding
        """
        try:
            obj = self.get_object()
            obj.delete()
        except ValueError as e:
            self.error_json_response(str(e))
        return self.build_json_response(obj)
