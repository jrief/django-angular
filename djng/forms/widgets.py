# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion
import json

from django import get_version
from django.conf import settings
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import format_html

from djng import app_settings


DJANGO_VERSION = get_version()

if LooseVersion(DJANGO_VERSION) < LooseVersion('1.11'):

    class ChoiceFieldRenderer(widgets.ChoiceFieldRenderer):
        def render(self):
            """
            Outputs a <ul ng-form="name"> for this set of choice fields to nest an ngForm.
            """
            start_tag = format_html('<ul {0}>', mark_safe(' '.join(self.field_attrs)))
            output = [start_tag]
            for widget in self:
                output.append(format_html('<li>{0}</li>', force_text(widget)))
            output.append('</ul>')
            return mark_safe('\n'.join(output))


    class CheckboxChoiceInput(widgets.CheckboxChoiceInput):
        def tag(self, attrs=None):
            attrs = attrs or self.attrs
            name = '{0}.{1}'.format(self.name, self.choice_value)
            tag_attrs = dict(attrs, type=self.input_type, name=name, value=self.choice_value)
            if 'ng-model' in attrs:
                tag_attrs['ng-model'] = "{0}['{1}']".format(attrs['ng-model'], self.choice_value)
            if self.is_checked():
                tag_attrs['checked'] = 'checked'
            return format_html('<input{0} />', flatatt(tag_attrs))


    class CheckboxFieldRendererMixin(object):
        def __init__(self, name, value, attrs, choices):
            attrs.pop('djng-error', None)
            self.field_attrs = [format_html('ng-form="{0}"', name)]
            #if attrs.pop('multiple_checkbox_required', False):
            field_names = [format_html('{0}.{1}', name, choice) for choice, dummy in choices]
            self.field_attrs.append(format_html('validate-multiple-fields="{0}"', json.dumps(field_names)))
            super(CheckboxFieldRendererMixin, self).__init__(name, value, attrs, choices)


    class CheckboxFieldRenderer(CheckboxFieldRendererMixin, ChoiceFieldRenderer):
        choice_input_class = CheckboxChoiceInput


    class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
        """
        Form fields of type 'MultipleChoiceField' using the widget 'CheckboxSelectMultiple' must behave
        slightly different from the original. This widget overrides the default functionality.
        """
        renderer = CheckboxFieldRenderer

        def id_for_label(self, id_):
            """
            Returns the label for the group of checkbox input fields
            """
            return id_

        def implode_multi_values(self, name, data):
            raise NotImplementedError("This method has been moved to its FieldMixin.")

        def convert_ajax_data(self, field_data):
            raise NotImplementedError("This method has been moved to its FieldMixin.")

        def get_field_attrs(self, field):
            raise NotImplementedError("This method has been moved to its FieldMixin.")


    class RadioFieldRendererMixin(object):
        def __init__(self, name, value, attrs, choices):
            attrs.pop('djng-error', None)
            self.field_attrs = []
            if attrs.pop('radio_select_required', False):
                self.field_attrs.append(format_html('validate-multiple-fields="{0}"', name))
            super(RadioFieldRendererMixin, self).__init__(name, value, attrs, choices)


    class RadioFieldRenderer(RadioFieldRendererMixin, ChoiceFieldRenderer):
        choice_input_class = widgets.RadioChoiceInput


    class RadioSelect(widgets.RadioSelect):
        """
        Form fields of type 'ChoiceField' using the widget 'RadioSelect' must behave
        slightly different from the original. This widget overrides the default functionality.
        """
        renderer = RadioFieldRenderer

        def id_for_label(self, id_):
            return id_

        def get_field_attrs(self, field):
            raise NotImplementedError("This method has been moved to its FieldMixin.")


class DropFileWidget(widgets.Widget):
    signer = signing.Signer()

    def __init__(self, attrs=None, area_label=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        self.area_label = area_label
        self.attrs.update({
            'ng-class': 'getClass()',
            'ngf-drop': 'uploadFiles($files)',
            'ngf-select': 'uploadFiles($files)',
        })

    def render(self, name, value, attrs=None):
        from django.contrib.staticfiles.storage import staticfiles_storage

        extra_attrs = dict(attrs, name=name)
        if value:
            background_url = self.get_background_url(value)
            if background_url:
                extra_attrs.update({
                    'style': 'background-image: url({});'.format(background_url),
                    'current-file': self.signer.sign(value.name)
                })
        if LooseVersion(DJANGO_VERSION) < LooseVersion('1.11'):
            final_attrs = self.build_attrs(extra_attrs=extra_attrs)
        else:
            final_attrs = self.build_attrs(self.attrs, extra_attrs=extra_attrs)
        elements = [format_html('<textarea {}>{}</textarea>', flatatt(final_attrs), self.area_label)]
        elements.append(format_html(
            '<img src="{}" class="{}" djng-fileupload-button="{}" ng-click="deleteImage()" ng-hide="isEmpty()" ng-cloak />',
            staticfiles_storage.url('djng/icons/trash.svg'), 'djng-fileupload-btn djng-fileupload-btn-trash', attrs['ng-model']))
        if value:
            elements.append(format_html(
                '<a href="{}" class="{}" target="_new" ng-hide="isEmpty()" ng-cloak><img src="{}" /></a>',
                value.url, 'djng-fileupload-btn djng-fileupload-btn-download',
                staticfiles_storage.url('djng/icons/download.svg')))
        return format_html('<div class="drop-box">{}</div>', mark_safe(''.join(elements)))

    def get_background_url(self, value):
        return ''  # TODO: render an icon, depending on the file type


class DropImageWidget(DropFileWidget):
    thumbnail_size = app_settings.THUMBNAIL_SIZE

    def __init__(self, **kwargs):
        if 'easy_thumbnails' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("'djng.forms.fields.ImageField' requires 'easy-thubnails' to be installed")
        super(DropImageWidget, self).__init__(**kwargs)

    def get_background_url(self, value):
        from easy_thumbnails.exceptions import InvalidImageFormatError
        from easy_thumbnails.files import get_thumbnailer

        try:
            thumbnail_options = {'crop': True, 'size': self.thumbnail_size}
            thumbnailer = get_thumbnailer(value)
            thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
            return thumbnail.url
        except InvalidImageFormatError:
            return
