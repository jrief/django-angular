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
    Subclass and override ``model`` with your model

    Optional 'pk' GET parameter must be passed when object identification is required (save to update and delete)

    If fields != None the serialized data will only contain field names from fields array
    """
    model = None
    fields = None
    content_type = 'application/json'
    slug_field = 'slug'
    serialize_natural_keys = False

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to call appropriate methods:
        * $query - ng_query
        * $get - ng_get
        * $save - ng_save
        * $delete and $remove - ng_delete
        """
        try:
            if request.method == 'GET':
                if 'pk' in request.GET or self.slug_field in request.GET:
                    return self.ng_get(request, *args, **kwargs)
                return self.ng_query(request, *args, **kwargs)
            elif request.method == 'POST':
                return self.ng_save(request, *args, **kwargs)
            elif request.method == 'DELETE':
                return self.ng_delete(request, *args, **kwargs)
        except self.model.DoesNotExist as e:
            return self.error_json_response(str(e), 404)
        except ValueError as e:
            return self.error_json_response(str(e))
        except ValidationError as e:
            return self.error_json_response(e.message)

        return self.error_json_response('This view can not handle method {0}'.format(request.method), 405)

    def get_form_class(self):
        """
        Build ModelForm from model
        """
        return modelform_factory(self.model)

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
        is_queryset = False
        query_fields = self.get_fields()
        try:
            iter(queryset)
            is_queryset = True
            raw_data = serializers.serialize('python', queryset, fields=query_fields, use_natural_keys=self.serialize_natural_keys)
        except TypeError:  # Not iterable
            raw_data = serializers.serialize('python', [queryset, ], fields=query_fields, use_natural_keys=self.serialize_natural_keys)

        for obj in raw_data:  # Add pk to fields
            obj['fields']['pk'] = obj['pk']
            object_data.append(obj['fields'])

        if is_queryset:
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
            return self.model.objects.get(pk=self.request.GET['pk'])
        elif self.slug_field in self.request.GET:
            return self.model.objects.get(**{self.slug_field: self.request.GET[self.slug_field]})
        raise ValueError("Attempted to get an object by 'pk' or slug field, but no identifier is present. Missing GET parameter?")

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

        # Do not fall back to dispatch error handling, instead provide field details.
        error_detail = {"non_field_errors": form.non_field_errors()}
        error_detail.update(form.errors)
        return self.error_json_response("Form not valid", detail=error_detail)

    def ng_delete(self, request, *args, **kwargs):
        """
        Delete object and return it's data in JSON encoding
        """
        if 'pk' not in request.GET:
            raise ValueError("Object id is required to delete.")

        obj = self.get_object()
        obj.delete()
        return self.build_json_response(obj)
