# -*- coding: utf-8 -*-
import json

from django.test import TestCase
from django.test.client import RequestFactory

from djangular.views.crud import NgCRUDView
from djangular.views.mixins import JSONResponseMixin
from server.models import DummyModel, DummyModel2, SimpleModel


class CRUDTestViewWithFK(JSONResponseMixin, NgCRUDView):
    """
    Include JSONResponseMixin to make sure there aren't any problems when using both together
    """
    model = DummyModel


class CRUDTestView(JSONResponseMixin, NgCRUDView):
    """
    Include JSONResponseMixin to make sure there aren't any problems when using both together
    """
    model = DummyModel2


class CRUDTestViewWithSlug(NgCRUDView):
    """
    Differs from CRUDTestViewWithFK in slug field 'email', which has a 'unique' constraint and
    can be used as an alternative key (for GET operations only).
    """
    model = SimpleModel
    slug_field = 'email'


class CRUDViewTest(TestCase):
    names = ['John', 'Anne', 'Chris', 'Beatrice', 'Matt']
    emails = ["@".join((name, "example.com")) for name in names]

    def setUp(self):
        self.factory = RequestFactory()

        # DummyModel2 and DummyModel / CRUDTestViewWithFK
        model2 = DummyModel2(name="Model2 name")
        model2.save()
        for name in self.names:
            DummyModel(name=name, model2=model2).save()

        # SimpleModel / CRUDTestViewWithSlug
        for name, email in zip(self.names, self.emails):
            SimpleModel(name=name, email=email).save()

    def test_ng_query(self):
        # CRUDTestViewWithFK
        request = self.factory.get('/crud/')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        for obj in data:
            db_obj = DummyModel.objects.get(pk=obj['pk'])
            self.assertEqual(obj['name'], db_obj.name)

        # CRUDTestViewWithSlug
        request2 = self.factory.get('/crud/')
        response2 = CRUDTestViewWithSlug.as_view()(request2)
        data2 = json.loads(response2.content.decode('utf-8'))
        for obj in data2:
            db_obj = SimpleModel.objects.get(email=obj['email'])
            self.assertEqual(obj['name'], db_obj.name)

    def test_ng_get(self):
        # CRUDTestViewWithFK
        request = self.factory.get('/crud/?pk=1')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.names[0], data['name'])

        # CRUDTestViewWithSlug
        request2 = self.factory.get('/crud/?email={0}'.format(self.emails[0]))
        response2 = CRUDTestViewWithSlug.as_view()(request2)
        data2 = json.loads(response2.content.decode('utf-8'))
        self.assertEqual(self.names[0], data2['name'])

    def test_ng_save_create(self):
        # CRUDTestViewWithFK
        request = self.factory.post('/crud/',
                                    data=json.dumps({'name': 'Leonard'}),
                                    content_type='application/json')
        response = CRUDTestView.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        pk = data['pk']

        request2 = self.factory.get('/crud/?pk={0}'.format(pk))
        response2 = CRUDTestView.as_view()(request2)
        data2 = json.loads(response2.content.decode('utf-8'))
        self.assertEqual(data2['name'], 'Leonard')

        # CRUDTestViewWithSlug
        request3 = self.factory.post('/crud/',
                                    data=json.dumps({'name': 'Leonard', 'email': 'Leonard@example.com'}),
                                    content_type='application/json')
        CRUDTestViewWithSlug.as_view()(request3)

        request4 = self.factory.get('/crud/?email={0}'.format('Leonard@example.com'))
        response4 = CRUDTestViewWithSlug.as_view()(request4)
        data4 = json.loads(response4.content.decode('utf-8'))
        self.assertEqual(data4['name'], 'Leonard')

        request5 = self.factory.post('/crud/',
                                    data=json.dumps({'name': 'Leonard2', 'email': 'Leonard@example.com'}),
                                    content_type='application/json')
        response5 = CRUDTestViewWithSlug.as_view()(request5)
        self.assertGreaterEqual(response5.status_code, 400)
        data5 = json.loads(response5.content.decode('utf-8'))
        self.assertTrue('detail' in data5 and 'email' in data5['detail'] and len(data5['detail']['email']) > 0)

    def test_ng_save_update(self):
        # CRUDTestViewWithFK
        request = self.factory.post('/crud/?pk=1',
                                    data=json.dumps({'pk': 1, 'name': 'John2'}),
                                    content_type='application/json')
        response = CRUDTestView.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['name'], 'John2')

        request2 = self.factory.get('/crud/?pk=1')
        response2 = CRUDTestView.as_view()(request2)
        data2 = json.loads(response2.content.decode('utf-8'))
        self.assertEqual(data2['name'], 'John2')

        # CRUDTestViewWithSlug
        request3 = self.factory.post('/crud/?pk=1',
                                    data=json.dumps({'name': 'John', 'email': 'John2@example.com'}),
                                    content_type='application/json')
        response3 = CRUDTestViewWithSlug.as_view()(request3)
        data3 = json.loads(response3.content.decode('utf-8'))
        self.assertEqual(data3['name'], 'John')
        self.assertEqual(data3['email'], 'John2@example.com')

        request4 = self.factory.get('/crud/?email=John2@example.com')
        response4 = CRUDTestViewWithSlug.as_view()(request4)
        data4 = json.loads(response4.content.decode('utf-8'))
        self.assertEqual(data4['name'], 'John')

        request5 = self.factory.post('/crud/?pk=3',  # Modifying "Chris"
                                    data=json.dumps({'pk': 4, 'name': 'John2', 'email': 'John2@example.com'}),
                                    content_type='application/json')
        response5 = CRUDTestViewWithSlug.as_view()(request5)
        self.assertGreaterEqual(response5.status_code, 400)
        data5 = json.loads(response5.content.decode('utf-8'))
        self.assertTrue('detail' in data5 and 'email' in data5['detail'] and len(data5['detail']['email']) > 0)

    def test_ng_delete(self):
        # CRUDTestViewWithFK
        request = self.factory.delete('/crud/?pk=1')
        response = CRUDTestViewWithFK.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        deleted_name = data['name']

        request2 = self.factory.get('/crud/')
        response2 = CRUDTestViewWithFK.as_view()(request2)
        data2 = json.loads(response2.content.decode('utf-8'))
        for obj in data2:
            self.assertTrue(deleted_name != obj['name'])

        # CRUDTestViewWithSlug delete is not different from CRUDTestViewWithFK only testing error status codes
        request5 = self.factory.delete('/crud/?email=Anne@example.com')  # Missing pk
        response5 = CRUDTestViewWithSlug.as_view()(request5)
        self.assertEqual(response5.status_code, 400)

        request6 = self.factory.delete('/crud/?pk=100')  # Invalid pk
        response6 = CRUDTestViewWithSlug.as_view()(request6)
        self.assertEqual(response6.status_code, 404)
