# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.test import TestCase
from sekizai.context import SekizaiContext


class PostProcessorTagsTest(TestCase):

    def test_processor_module_list(self):
        tpl = template.Template("""
            {% load sekizai_tags %}
            {% addtoblock "ng-requires" %}ngAnimate{% endaddtoblock %}
            {% render_block "ng-requires" postprocessor "djng.sekizai_processors.module_list" %}
            """)
        context = SekizaiContext()
        output = tpl.render(context)
        self.assertIn('ngAnimate', output.strip())

    def test_processor(self):
        tpl = template.Template("""
            {% load sekizai_tags %}
            {% addtoblock "ng-config" %}[function() { /* foo */ }]{% endaddtoblock %}
            {% render_block "ng-config" postprocessor "djng.sekizai_processors.module_config" %}
            """)
        context = SekizaiContext()
        output = tpl.render(context)
        self.assertIn('.config([function() { /* foo */ }])', output.strip())
