# -*- coding: utf-8 -*-
from django.forms import fields
from django.forms import widgets
from djng.forms import field_mixins
from . import widgets as bs3widgets


class BooleanFieldMixin(field_mixins.BooleanFieldMixin):
    def get_converted_widget(self):
        assert(isinstance(self, fields.BooleanField))
        if isinstance(self.widget, widgets.CheckboxInput):
            self.widget_css_classes = None
            if not isinstance(self.widget, bs3widgets.CheckboxInput):
                new_widget = bs3widgets.CheckboxInput(self.label)
                new_widget.__dict__, new_widget.choice_label = self.widget.__dict__, new_widget.choice_label
                self.label = ''  # label is rendered by the widget and not by BoundField.label_tag()
                return new_widget


class ChoiceFieldMixin(field_mixins.ChoiceFieldMixin):
    def get_converted_widget(self):
        assert(isinstance(self, fields.ChoiceField))
        if isinstance(self.widget, widgets.RadioSelect):
            self.widget_css_classes = None
            if not isinstance(self.widget, bs3widgets.RadioSelect):
                new_widget = bs3widgets.RadioSelect()
                new_widget.__dict__ = self.widget.__dict__
                return new_widget


class MultipleChoiceFieldMixin(field_mixins.MultipleChoiceFieldMixin):
    def get_converted_widget(self):
        assert(isinstance(self, fields.MultipleChoiceField))
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            self.widget_css_classes = None
            if not isinstance(self.widget, bs3widgets.CheckboxSelectMultiple):
                new_widget = bs3widgets.CheckboxSelectMultiple()
                new_widget.__dict__ = self.widget.__dict__
                return new_widget
