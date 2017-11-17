# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes

from django import VERSION as DJANGO_VERSION
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import signing
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from djng import app_settings


if DJANGO_VERSION < (1, 11):

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


    class CheckboxInput(widgets.CheckboxInput):
        def __init__(self, label, attrs=None, check_test=None):
            # the label is rendered by the Widget class rather than by BoundField.label_tag()
            self.choice_label = label
            super(CheckboxInput, self).__init__(attrs, check_test)


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
            multifields_required = attrs.pop('multifields_required', None)
            if multifields_required is not None:
                self.field_attrs.append(format_html('djng-multifields-required="{}"', str(multifields_required).lower()))
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

    def __init__(self, area_label, fileupload_url, attrs=None):
        self.area_label = area_label
        self.fileupload_url = fileupload_url
        super(DropFileWidget, self).__init__(attrs)
        self.filetype = 'file'

    def render(self, name, value, attrs=None):
        from django.contrib.staticfiles.storage import staticfiles_storage

        extra_attrs = dict(attrs)
        extra_attrs.update({
            'name': name,
            'class': 'djng-{}-uploader'.format(self.filetype),
            'djng-fileupload-url': self.fileupload_url,
            'ngf-drop': 'uploadFile($file, "{0}", "{id}", "{ng-model}")'.format(self.filetype, **attrs),
            'ngf-select': 'uploadFile($file, "{0}", "{id}", "{ng-model}")'.format(self.filetype, **attrs),
        })
        self.update_attributes(extra_attrs, value)
        if DJANGO_VERSION < (1, 11):
            final_attrs = self.build_attrs(extra_attrs=extra_attrs)
        else:
            final_attrs = self.build_attrs(self.attrs, extra_attrs=extra_attrs)
        elements = [format_html('<textarea {}>{}</textarea>', flatatt(final_attrs), self.area_label)]

        # add a spinnging wheel
        spinner_attrs = {
            'class': 'glyphicon glyphicon-refresh glyphicon-spin',
            'ng-cloak': True,
        }
        elements.append(format_html('<span {}></span>', flatatt(spinner_attrs)))

        # add a delete icon
        icon_attrs = {
            'src': staticfiles_storage.url('djng/icons/{}/trash.svg'.format(self.filetype)),
            'class': 'djng-btn-trash',
            'title': _("Delete File"),
            'djng-fileupload-button ': True,
            'ng-click': 'deleteImage("{id}", "{ng-model}")'.format(**attrs),
            'ng-cloak': True,
        }
        elements.append(format_html('<img {} />', flatatt(icon_attrs)))

        # add a download icon
        if value:
            download_attrs = {
                'href': value.url,
                'class': 'djng-btn-download',
                'title': _("Download File"),
                'download': True,
                'ng-cloak': True,
            }
            download_icon = staticfiles_storage.url('djng/icons/{}/download.svg'.format(self.filetype))
            elements.append(format_html('<a {}><img src="{}" /></a>', flatatt(download_attrs), download_icon))

        return format_html('<div class="drop-box">{}</div>', mark_safe(''.join(elements)))

    def update_attributes(self, attrs, value):
        if value:
            try:
                content_type, _ = mimetypes.guess_type(value.file.name)
                extension = mimetypes.guess_extension(content_type)[1:]
            except (IOError, IndexError, TypeError):
                extension = '_blank'
            background_url = staticfiles_storage.url('djng/icons/{}.png'.format(extension))
            attrs.update({
                'style': 'background-image: url({});'.format(background_url),
                'current-file': self.signer.sign(value.name)
            })


class DropImageWidget(DropFileWidget):
    def __init__(self, area_label, fileupload_url, attrs=None):
        super(DropImageWidget, self).__init__(area_label, fileupload_url, attrs=attrs)
        self.filetype = 'image'

    def update_attributes(self, attrs, value):
        if value:
            background_url = self.get_background_url(value)
            if background_url:
                attrs.update({
                    'style': 'background-image: url({});'.format(background_url),
                    'current-file': self.signer.sign(value.name)
                })

    def get_background_url(self, value):
        from easy_thumbnails.exceptions import InvalidImageFormatError
        from easy_thumbnails.files import get_thumbnailer

        try:
            thumbnailer = get_thumbnailer(value)
            thumbnail = thumbnailer.get_thumbnail(app_settings.THUMBNAIL_OPTIONS)
            return thumbnail.url
        except InvalidImageFormatError:
            return
