# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import fields
from django.forms import widgets
from djng.forms import field_mixins


class BooleanFieldMixin(field_mixins.BooleanFieldMixin):
    def get_converted_widget(self):
        from .widgets import CheckboxInput

        assert(isinstance(self, fields.BooleanField))
        if isinstance(self.widget, widgets.CheckboxInput):
            self.widget_css_classes = None
            if not isinstance(self.widget, CheckboxInput):
                new_widget = CheckboxInput(self.label)
                new_widget.__dict__, new_widget.choice_label = self.widget.__dict__, new_widget.choice_label
                return new_widget


class ChoiceFieldMixin(field_mixins.ChoiceFieldMixin):
    def get_converted_widget(self):
        from .widgets import RadioSelect

        assert(isinstance(self, fields.ChoiceField))
        if isinstance(self.widget, widgets.RadioSelect):
            self.widget_css_classes = None
            if not isinstance(self.widget, RadioSelect):
                new_widget = RadioSelect()
                new_widget.__dict__ = self.widget.__dict__
                return new_widget


class MultipleChoiceFieldMixin(field_mixins.MultipleChoiceFieldMixin):
    def get_converted_widget(self):
        from .widgets import CheckboxSelectMultiple

        assert(isinstance(self, fields.MultipleChoiceField))
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            self.widget_css_classes = None
            if not isinstance(self.widget, CheckboxSelectMultiple):
                new_widget = CheckboxSelectMultiple()
                new_widget.__dict__ = self.widget.__dict__
                return new_widget
