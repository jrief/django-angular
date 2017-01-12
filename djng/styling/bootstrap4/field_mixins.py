# -*- coding: utf-8 -*-

from ..bootstrap.field_mixins import (
    build_boolean_field_mixin,
    build_choice_field_mixin,
    build_multiple_choice_field_mixin,
)

from . import widgets


BooleanFieldMixin = build_boolean_field_mixin(widgets)
ChoiceFieldMixin = build_choice_field_mixin(widgets)
MultipleChoiceFieldMixin = build_multiple_choice_field_mixin(widgets)
