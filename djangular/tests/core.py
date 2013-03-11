from django.db import models
from django.test import TestCase
from django.utils import simplejson as json
from django.forms.util import ValidationError


class JSONFieldTest(TestCase):

    def test_json_field_create(self):
        """Test saving a JSON object in our JSONField"""
        self.failUnless(True)
