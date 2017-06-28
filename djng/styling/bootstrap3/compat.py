from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.forms import widgets

from djng.forms.compat import (flatatt,
    CheckboxSelectMultiple as DjngCheckboxSelectMultiple, RadioSelect as DjngRadioSelect,
    ChoiceFieldRenderer as DjngChoiceFieldRenderer, CheckboxChoiceInput as DjngCheckboxChoiceInput,
    CheckboxFieldRendererMixin, RadioFieldRendererMixin,
)

class ChoiceFieldRenderer(DjngChoiceFieldRenderer):
    def render(self):
        """
        Outputs a <div ng-form="name"> for this set of choice fields to nest an ngForm.
        """
        start_tag = format_html('<div {}>', mark_safe(' '.join(self.field_attrs)))
        output = [start_tag]
        for widget in self:
            output.append(force_text(widget))
        output.append('</div>')
        return mark_safe('\n'.join(output))


class CheckboxInput(widgets.CheckboxInput):
    def __init__(self, label, attrs=None, check_test=None):
        # the label is rendered by the Widget class rather than by BoundField.label_tag()
        self.choice_label = label
        super(CheckboxInput, self).__init__(attrs, check_test)

    def render(self, name, value, attrs=None):
        attrs = attrs or self.attrs
        label_attrs = ['class="checkbox-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{}"', self.attrs['id']))
        label_for = mark_safe(' '.join(label_attrs))
        tag = super(CheckboxInput, self).render(name, value, attrs)
        return format_html('<label {0}>{1} {2}</label>', label_for, tag, self.choice_label)


class CheckboxChoiceInput(DjngCheckboxChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        label_tag = super(CheckboxChoiceInput, self).render(name, value, attrs, choices)
        return format_html('<div class="checkbox">{}</div>', label_tag)


class CheckboxInlineChoiceInput(CheckboxChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        label_attrs = ['class="checkbox-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{0}_{1}"', self.attrs['id'], self.index))
        label_for = mark_safe(' '.join(label_attrs))
        return format_html('<label {0}>{1} {2}</label>', label_for, self.tag(), self.choice_label)


class CheckboxFieldRenderer(CheckboxFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput


class CheckboxInlineFieldRenderer(CheckboxFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = CheckboxInlineChoiceInput


class CheckboxSelectMultiple(DjngCheckboxSelectMultiple):
    renderer = CheckboxInlineFieldRenderer


class RadioChoiceInput(widgets.RadioChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        label_tag = super(RadioChoiceInput, self).render(name, value, choices)
        return format_html('<div class="radio">{}</div>', label_tag)

    def tag(self, attrs=None):
        attrs = attrs or self.attrs
        tag_attrs = dict(attrs, type=self.input_type, name=self.name, value=self.choice_value)
        if 'id' in attrs:
            tag_attrs['id'] = '{0}_{1}'.format(tag_attrs['id'], self.index)
        if self.is_checked():
            tag_attrs['checked'] = 'checked'
        return format_html('<input{} />', flatatt(tag_attrs))


class RadioInlineChoiceInput(widgets.RadioChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        label_attrs = ['class="radio-inline"']
        if 'id' in self.attrs:
            label_attrs.append(format_html('for="{0}_{1}"', self.attrs['id'], self.index))
        label_for = mark_safe(' '.join(label_attrs))
        return format_html('<label {0}>{1} {2}</label>', label_for, self.tag(), self.choice_label)


class RadioFieldRenderer(RadioFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = RadioChoiceInput


class RadioInlineFieldRenderer(RadioFieldRendererMixin, ChoiceFieldRenderer):
    choice_input_class = RadioInlineChoiceInput

class RadioSelect(DjngRadioSelect):
    renderer = RadioFieldRenderer
