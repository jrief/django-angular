# -*- coding: utf-8 -*-
import json

from django.test import TestCase
from django.test.client import RequestFactory

from djangular.views.crud import NgCRUDView
from djangular.views.mixins import JSONResponseMixin
from server.models import DummyModel, DummyModel2


class CRUDTestViewWithFK(JSONResponseMixin, NgCRUDView):
    """
    Include JSONResponseMixin to make sure there aren't any problems when using both together
    """
    model_class = DummyModel

class CRUDTestView(JSONResponseMixin, NgCRUDView):
    """
    Include JSONResponseMixin to make sure there aren't any problems when using both together
    """
    model_class = DummyModel2


class CRUDViewTest(TestCase):
    names = ['John', 'Anne', 'Chris', 'Beatrice', 'Matt']

    def setUp(self):
        self.factory = RequestFactory()
        model2 = DummyModel2(name="Model2 name")
        model2.save()
        for name in self.names:
            DummyModel(name=name, model2=model2).save()

    def test_ng_query(self):
        request = self.factory.get('/crud/')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content)
        for obj in data:
            db_obj = DummyModel.objects.get(pk=obj['pk'])
            self.assertEqual(obj['name'], db_obj.name)

    def test_ng_get(self):
        request = self.factory.get('/crud/?pk=1')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content)
        self.assertEqual(self.names[0], data['name'])

    def test_ng_save_create(self):
        request = self.factory.post('/crud/',
                                    data=json.dumps({'name': 'Leonard'}),
                                    content_type='application/json')
        response = CRUDTestView.as_view()(request)
        data = json.loads(response.content)
        pk = data['pk']

        request2 = self.factory.get('/crud/?pk=%d' % pk)
        response2 = CRUDTestView.as_view()(request2)
        data2 = json.loads(response2.content)
        self.assertEqual(data2['name'], 'Leonard')

    def test_ng_save_update(self):
        request = self.factory.post('/crud/?pk=1',
                                    data=json.dumps({'pk': 1, 'name': 'John2'}),
                                    content_type='application/json')
        response = CRUDTestView.as_view()(request)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'John2')

        request2 = self.factory.get('/crud/?pk=1')
        response2 = CRUDTestView.as_view()(request2)
        data2 = json.loads(response2.content)
        self.assertEqual(data2['name'], 'John2')

    def test_ng_delete(self):
        request = self.factory.delete('/crud/?pk=1')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content)
        deleted_name = data['name']

        request2 = self.factory.get('/crud/')
        response2 = CRUDTestViewWithFK.as_view()(request2)
        data2 = json.loads(response2.content)
        for obj in data2:
            self.assertTrue(deleted_name != obj['name'])