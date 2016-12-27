# -*- coding: utf-8 -*-
# flake8: noqa

# We import all widgets from our bootstrap module
# but customize only the needed ones
from ..bootstrap.widgets import (
    ChoiceFieldRenderer as OriginalChoiceFieldRenderer,
    CheckboxInput as OriginalCheckboxInput,
    CheckboxChoiceInput as OriginalCheckboxChoiceInput,
    CheckboxInlineChoiceInput as OriginalCheckboxInlineChoiceInput,
    CheckboxFieldRenderer as OriginalCheckboxFieldRenderer,
    CheckboxInlineFieldRenderer as OriginalCheckboxInlineFieldRenderer,
    CheckboxSelectMultiple as OriginalCheckboxSelectMultiple,
    RadioChoiceInput as OriginalRadioChoiceInput,
    RadioInlineChoiceInput as OriginalRadioInlineChoiceInput,
    RadioFieldRenderer as OriginalRadioFieldRenderer,
    RadioInlineFieldRenderer as OriginalRadioInlineFieldRenderer,
    RadioSelect as OriginalRadioSelect,
)


class ChoiceFieldRenderer(OriginalChoiceFieldRenderer):
    pass


class CheckboxInput(OriginalCheckboxInput):
    _label_attrs = ['class="form-check-label"']


class CheckboxChoiceInput(OriginalCheckboxChoiceInput):
    _checkbox_class = "form-check-input"


class CheckboxInlineChoiceInput(OriginalCheckboxInlineChoiceInput):
    _label_attrs = ['class="form-check-label"']


class CheckboxFieldRenderer(OriginalCheckboxFieldRenderer):
    choice_input_class = CheckboxChoiceInput


class CheckboxInlineFieldRenderer(OriginalCheckboxInlineFieldRenderer):
    choice_input_class = CheckboxInlineChoiceInput


class CheckboxSelectMultiple(OriginalCheckboxSelectMultiple):
    renderer = CheckboxInlineFieldRenderer


class RadioChoiceInput(OriginalRadioChoiceInput):
    _radio_class = "radio"


class RadioInlineChoiceInput(OriginalRadioInlineChoiceInput):
    _label_attrs = ['class="radio-inline"']


class RadioFieldRenderer(OriginalRadioFieldRenderer):
    choice_input_class = RadioChoiceInput


class RadioInlineFieldRenderer(OriginalRadioInlineFieldRenderer):
    choice_input_class = RadioInlineChoiceInput


class RadioSelect(OriginalRadioSelect):
    renderer = RadioFieldRenderer
