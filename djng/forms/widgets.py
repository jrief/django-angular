import mimetypes

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import signing
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from djng import app_settings


class DropFileWidget(widgets.Widget):
    signer = signing.Signer()

    def __init__(self, area_label, fileupload_url, attrs=None):
        self.area_label = area_label
        self.fileupload_url = fileupload_url
        super(DropFileWidget, self).__init__(attrs)
        self.filetype = 'file'

    def render(self, name, value, attrs=None, renderer=None):
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
