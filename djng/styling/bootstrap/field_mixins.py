# -*- coding: utf-8 -*-

from django.forms import fields, widgets

from djng.forms import field_mixins

# from . import widgets as bootstrap_widgets


def build_boolean_field_mixin(bootstrap_widgets):
    class BooleanFieldMixin(field_mixins.BooleanFieldMixin):
        def get_converted_widget(self):
            assert(isinstance(self, fields.BooleanField))
            if isinstance(self.widget, widgets.CheckboxInput):
                self.widget_css_classes = None
                if not isinstance(self.widget, bootstrap_widgets.CheckboxInput):
                    new_widget = bootstrap_widgets.CheckboxInput(self.label)
                    new_widget.__dict__, new_widget.choice_label = self.widget.__dict__, new_widget.choice_label
                    self.label = ''  # label is rendered by the widget and not by BoundField.label_tag()
                    return new_widget
    return BooleanFieldMixin


def build_choice_field_mixin(bootstrap_widgets):
    class ChoiceFieldMixin(field_mixins.ChoiceFieldMixin):
        def get_converted_widget(self):
            assert(isinstance(self, fields.ChoiceField))
            if isinstance(self.widget, widgets.RadioSelect):
                self.widget_css_classes = None
                if not isinstance(self.widget, bootstrap_widgets.RadioSelect):
                    new_widget = bootstrap_widgets.RadioSelect()
                    new_widget.__dict__ = self.widget.__dict__
                    return new_widget
    return ChoiceFieldMixin


def build_multiple_choice_field_mixin(bootstrap_widgets):
    class MultipleChoiceFieldMixin(field_mixins.MultipleChoiceFieldMixin):
        def get_converted_widget(self):
            assert(isinstance(self, fields.MultipleChoiceField))
            if isinstance(self.widget, widgets.CheckboxSelectMultiple):
                self.widget_css_classes = None
                if not isinstance(self.widget, bootstrap_widgets.CheckboxSelectMultiple):
                    new_widget = bootstrap_widgets.CheckboxSelectMultiple()
                    new_widget.__dict__ = self.widget.__dict__
                    return new_widget
    return MultipleChoiceFieldMixin
