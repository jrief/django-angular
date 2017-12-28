# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import mimetypes

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import signing
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.urls import reverse_lazy
from django.forms import fields, models as model_fields, widgets
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from djng import app_settings
from .widgets import DropFileWidget, DropImageWidget


class DefaultFieldMixin(object):
    render_label = True

    def has_subwidgets(self):
        return False

    def get_potential_errors(self):
        return self.get_input_required_errors()

    def get_input_required_errors(self):
        errors = []
        if self.required:
            self.widget.attrs['ng-required'] = 'true'
            for key, msg in self.error_messages.items():
                if key == 'required':
                    errors.append(('$error.required', msg))
        return errors

    def get_min_max_length_errors(self):
        errors = []
        if getattr(self, 'min_length', None):
            self.widget.attrs['ng-minlength'] = self.min_length
        if getattr(self, 'max_length', None):
            self.widget.attrs['ng-maxlength'] = self.max_length
        for item in self.validators:
            if getattr(item, 'code', None) == 'min_length':
                message = ungettext_lazy(
                    'Ensure this value has at least %(limit_value)d character',
                    'Ensure this value has at least %(limit_value)d characters',
                    'limit_value')
                errors.append(('$error.minlength', message % {'limit_value': self.min_length}))
            if getattr(item, 'code', None) == 'max_length':
                message = ungettext_lazy(
                    'Ensure this value has at most %(limit_value)d character',
                    'Ensure this value has at most %(limit_value)d characters',
                    'limit_value')
                errors.append(('$error.maxlength', message % {'limit_value': self.max_length}))
        return errors

    def get_min_max_value_errors(self):
        errors = []
        if isinstance(getattr(self, 'min_value', None), int):
            self.widget.attrs['min'] = self.min_value
        if isinstance(getattr(self, 'max_value', None), int):
            self.widget.attrs['max'] = self.max_value
        errkeys = []
        for key, msg in self.error_messages.items():
            if key == 'min_value':
                errors.append(('$error.min', msg))
                errkeys.append(key)
            if key == 'max_value':
                errors.append(('$error.max', msg))
                errkeys.append(key)
        for item in self.validators:
            if getattr(item, 'code', None) == 'min_value' and 'min_value' not in errkeys:
                errors.append(('$error.min', item.message % {'limit_value': self.min_value}))
                errkeys.append('min_value')
            if getattr(item, 'code', None) == 'max_value' and 'max_value' not in errkeys:
                errors.append(('$error.max', item.message % {'limit_value': self.max_value}))
                errkeys.append('max_value')
        return errors

    def get_invalid_value_errors(self, ng_error_key):
        errors = []
        errkeys = []
        for key, msg in self.error_messages.items():
            if key == 'invalid':
                errors.append(('$error.{0}'.format(ng_error_key), msg))
                errkeys.append(key)
        for item in self.validators:
            if getattr(item, 'code', None) == 'invalid' and 'invalid' not in errkeys:
                errmsg = getattr(item, 'message', _("This input self does not contain valid data."))
                errors.append(('$error.{0}'.format(ng_error_key), errmsg))
                errkeys.append('invalid')
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        """
        Update the dictionary of attributes used  while rendering the input widget
        """
        bound_field.form.update_widget_attrs(bound_field, attrs)
        widget_classes = self.widget.attrs.get('class', None)
        if widget_classes:
            if 'class' in attrs:
                attrs['class'] += ' ' + widget_classes
            else:
                attrs.update({'class': widget_classes})
        return attrs


class Field(DefaultFieldMixin, fields.Field):
    pass


class CharField(DefaultFieldMixin, fields.CharField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        return errors


class DecimalField(DefaultFieldMixin, fields.DecimalField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        self.widget.attrs['ng-minlength'] = 1
        if isinstance(self.max_digits, int) and self.max_digits > 0:
            self.widget.attrs['ng-maxlength'] = self.max_digits + 1
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class EmailField(DefaultFieldMixin, fields.EmailField):
    def get_potential_errors(self):
        self.widget.attrs['email-pattern'] = self.get_email_regex()
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('email'))
        return errors

    def get_email_regex(self):
        """
        Return a regex pattern matching valid email addresses. Uses the same
        logic as the django validator, with the folowing exceptions:

        - Internationalized domain names not supported
        - IP addresses not supported
        - Strips lookbehinds (not supported in javascript regular expressions)
        """
        validator = self.default_validators[0]
        user_regex = validator.user_regex.pattern.replace('\Z', '@')
        domain_patterns = ([re.escape(domain) + '$' for domain in
                            validator.domain_whitelist] +
                           [validator.domain_regex.pattern.replace('\Z', '$')])
        domain_regex = '({0})'.format('|'.join(domain_patterns))
        email_regex = user_regex + domain_regex
        return re.sub(r'\(\?\<[^()]*?\)', '', email_regex)  # Strip lookbehinds


class DateField(DefaultFieldMixin, fields.DateField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('date'))
        return errors


class DateTimeField(DefaultFieldMixin, fields.DateTimeField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('datetime'))
        return errors


class TimeField(DefaultFieldMixin, fields.TimeField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('time'))
        return errors


class DurationField(DefaultFieldMixin, fields.DurationField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_invalid_value_errors('duration'))
        return errors


class FloatField(DefaultFieldMixin, fields.FloatField):
    """
    The internal ``django.forms.FloatField`` does not handle the step value in its number widget.
    """
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super(FloatField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(FloatField, self).widget_attrs(widget)
        attrs.update(step=self.step)
        return attrs

    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class IntegerField(DefaultFieldMixin, fields.IntegerField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_value_errors())
        errors.extend(self.get_invalid_value_errors('number'))
        return errors


class SlugField(DefaultFieldMixin, fields.SlugField):
    pass


class RegexField(DefaultFieldMixin, fields.RegexField):
    # Presumably Python Regex can't be translated 1:1 into JS regex. Any hints on how to convert these?
    def get_potential_errors(self):
        self.widget.attrs['ng-pattern'] = '/{0}/'.format(self.regex.pattern)
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        errors.extend(self.get_invalid_value_errors('pattern'))
        return errors


class BooleanField(DefaultFieldMixin, fields.BooleanField):
    render_label = False

    def has_subwidgets(self):
        return True

    def update_widget_attrs(self, bound_field, attrs):
        bound_field.form.update_widget_attrs(bound_field, attrs)
        return attrs

    def update_widget_rendering_context(self, context):
        context['widget'].update(field_label=self.label)
        return context

    def get_converted_widget(self, widgets_module):
        if not isinstance(self.widget, widgets.CheckboxInput):
            return
        try:
            new_widget = import_string(widgets_module + '.CheckboxInput')(self.label)
        except ImportError:
            new_widget = import_string('djng.forms.widgets.CheckboxInput')(self.label)
        new_widget.__dict__.update(self.widget.__dict__)
        return new_widget


class NullBooleanField(DefaultFieldMixin, fields.NullBooleanField):
    pass


class URLField(DefaultFieldMixin, fields.URLField):
    pass


class MultipleFieldMixin(DefaultFieldMixin):
    def get_multiple_choices_required(self):
        """
        Add only the required message, but no 'ng-required' attribute to the input fields,
        otherwise all Checkboxes of a MultipleChoiceField would require the property "checked".
        """
        errors = []
        if self.required:
            msg = _("At least one checkbox has to be selected.")
            errors.append(('$error.multifield', msg))
        return errors


class ChoiceField(MultipleFieldMixin, fields.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        if isinstance(self.widget, widgets.Select) and self.initial is None and len(self.choices):
            self.initial = self.choices[0][0]

    def has_subwidgets(self):
        return isinstance(self.widget, widgets.RadioSelect)

    def get_potential_errors(self):
        if isinstance(self.widget, widgets.RadioSelect):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        bound_field.form.update_widget_attrs(bound_field, attrs)
        if isinstance(self.widget, widgets.RadioSelect):
            if self.required and 'ng-model' in attrs:
                require_model = format_html("!{}", attrs['ng-model'])
                attrs.update({'ng-required': require_model})
        return attrs

    def get_converted_widget(self, widgets_module):
        if not isinstance(self.widget, widgets.RadioSelect):
            return
        try:
            new_widget = import_string(widgets_module + '.RadioSelect')()
        except ImportError:
            new_widget = import_string('djng.forms.widgets.RadioSelect')()
        new_widget.__dict__ = self.widget.__dict__
        return new_widget


class ModelChoiceField(MultipleFieldMixin, model_fields.ModelChoiceField):
    pass


class TypedChoiceField(MultipleFieldMixin, fields.TypedChoiceField):
    def get_potential_errors(self):
        if isinstance(self.widget, widgets.RadioSelect):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors


class MultipleChoiceField(MultipleFieldMixin, fields.MultipleChoiceField):
    def has_subwidgets(self):
        return isinstance(self.widget, widgets.CheckboxSelectMultiple)

    def get_potential_errors(self):
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            errors = self.get_multiple_choices_required()
        else:
            errors = self.get_input_required_errors()
        return errors

    def update_widget_attrs(self, bound_field, attrs):
        from django import VERSION

        bound_field.form.update_widget_attrs(bound_field, attrs)
        if VERSION < (1, 11) and isinstance(self.widget, widgets.CheckboxSelectMultiple):
            attrs.update(multifields_required=self.required)
        return attrs

    def get_converted_widget(self, widgets_module):
        if not isinstance(self.widget, widgets.CheckboxSelectMultiple):
            return
        try:
            new_widget = import_string(widgets_module + '.CheckboxSelectMultiple')()
        except ImportError:
            new_widget = import_string('djng.forms.widgets.CheckboxSelectMultiple')()
        new_widget.__dict__ = self.widget.__dict__
        return new_widget

    def implode_multi_values(self, name, data):
        """
        Due to the way Angular organizes it model, when Form data is sent via a POST request,
        then for this kind of widget, the posted data must to be converted into a format suitable
        for Django's Form validation.
        """
        mkeys = [k for k in data.keys() if k.startswith(name + '.')]
        mvls = [data.pop(k)[0] for k in mkeys]
        if mvls:
            data.setlist(name, mvls)

    def convert_ajax_data(self, field_data):
        """
        Due to the way Angular organizes it model, when this Form data is sent using Ajax,
        then for this kind of widget, the sent data has to be converted into a format suitable
        for Django's Form validation.
        """
        data = [key for key, val in field_data.items() if val]
        return data

    def update_widget_rendering_context(self, context):
        if isinstance(self.widget, widgets.CheckboxSelectMultiple):
            context['widget']['attrs']['djng-multifields-required'] = str(self.required).lower()
            ng_model = mark_safe(context['widget']['attrs'].pop('ng-model', ''))
            if ng_model:
                for group, options, index in context['widget']['optgroups']:
                    for option in options:
                        option['name'] = format_html('{name}.{value}', **option)
                        option['attrs']['ng-model'] = format_html('{0}[\'{value}\']', ng_model, **option)
        return context


class ModelMultipleChoiceField(MultipleFieldMixin, model_fields.ModelMultipleChoiceField):
    pass


class TypedMultipleChoiceField(MultipleFieldMixin, fields.TypedMultipleChoiceField):
    """
    TODO: this class must be adopted to upcoming use-cases.
    """
    pass


class UUIDField(DefaultFieldMixin, fields.UUIDField):
    def get_potential_errors(self):
        errors = self.get_input_required_errors()
        errors.extend(self.get_min_max_length_errors())
        return errors


class FileFieldMixin(DefaultFieldMixin):
    def to_python(self, value):
        # handle previously existing file
        try:
            current_file = None
            if ':' in value['current_file']:
                current_file = self.signer.unsign(value['current_file'])
        except signing.BadSignature:
            raise ValidationError("Got bogus upstream data")
        except (KeyError, TypeError):
            pass

        # handle new uploaded image
        try:
            obj = ''
            if ':' in value['temp_name']:
                temp_name = self.signer.unsign(value['temp_name'])
                temp_file = self.storage.open(temp_name, 'rb')
                file_size = self.storage.size(temp_name)
                if file_size < settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                    obj = InMemoryUploadedFile(
                        file=temp_file,
                        field_name=None,
                        name=value['file_name'],
                        charset=value['charset'],
                        content_type=value['content_type'],
                        content_type_extra=value['content_type_extra'],
                        size=file_size,
                    )
                else:
                    obj = TemporaryUploadedFile(
                        value['file_name'],
                        value['content_type'],
                        0,
                        value['charset'],
                        content_type_extra=value['content_type_extra'],
                    )
                    while True:
                        chunk = temp_file.read(0x10000)
                        if not chunk:
                            break
                        obj.file.write(chunk)
                    obj.file.seek(0)
                    obj.file.size = file_size
                self.storage.delete(temp_name)
                self.remove_current(current_file)
            elif value['temp_name'] == 'delete':
                self.remove_current(current_file)
        except signing.BadSignature:
            raise ValidationError("Got bogus upstream data")
        except (IOError, KeyError, TypeError):
            obj = current_file
        except Exception as excp:
            raise ValidationError("File upload failed. {}: {}".format(excp.__class__.__name__, excp))
        return obj

    def remove_current(self, filename):
        if filename:
            default_storage.delete(filename)


class FileField(FileFieldMixin, fields.FileField):
    storage = app_settings.upload_storage
    signer = signing.Signer()

    def __init__(self, *args, **kwargs):
        accept = kwargs.pop('accept', '*/*')
        fileupload_url = kwargs.pop('fileupload_url', reverse_lazy('fileupload'))
        area_label = kwargs.pop('area_label', _("Drop file here or click to upload"))
        attrs = {
            'accept': accept,
            'ngf-pattern': accept,
        }
        kwargs.update(widget=DropFileWidget(area_label, fileupload_url, attrs=attrs))
        super(FileField, self).__init__(*args, **kwargs)

    @classmethod
    def preview(cls, file_obj):
        available_name = cls.storage.get_available_name(file_obj.name)
        temp_name = cls.storage.save(available_name, file_obj)
        extension = mimetypes.guess_extension(file_obj.content_type)
        if extension:
            extension = extension[1:]
        else:
            extension = '_blank'
        icon_url = staticfiles_storage.url('djng/icons/{}.png'.format(extension))
        return {
            'url': 'url({})'.format(icon_url),
            'temp_name': cls.signer.sign(temp_name),
            'file_name': file_obj.name,
            'file_size': file_obj.size,
            'charset': file_obj.charset,
            'content_type': file_obj.content_type,
            'content_type_extra': file_obj.content_type_extra,
        }


class ImageField(FileFieldMixin, fields.ImageField):
    storage = app_settings.upload_storage
    signer = signing.Signer()

    def __init__(self, *args, **kwargs):
        if 'easy_thumbnails' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("'djng.forms.fields.ImageField' requires 'easy-thubnails' to be installed")
        accept = kwargs.pop('accept', 'image/*')
        fileupload_url = kwargs.pop('fileupload_url', reverse_lazy('fileupload'))
        area_label = kwargs.pop('area_label', _("Drop image here or click to upload"))
        attrs = {
            'accept': accept,
            'ngf-pattern': accept,
        }
        kwargs.update(widget=DropImageWidget(area_label, fileupload_url, attrs=attrs))
        super(ImageField, self).__init__(*args, **kwargs)

    def remove_current(self, image_name):
        from easy_thumbnails.models import Source, Thumbnail

        try:
            source = Source.objects.get(name=image_name)
            for thumb in Thumbnail.objects.filter(source=source):
                default_storage.delete(thumb.name)
                thumb.delete()
            source.delete()
        except Source.DoesNotExist:
            pass
        super(ImageField, self).remove_current(image_name)

    @classmethod
    def preview(cls, file_obj):
        from easy_thumbnails.files import get_thumbnailer
        from easy_thumbnails.templatetags.thumbnail import data_uri

        available_name = cls.storage.get_available_name(file_obj.name)
        temp_name = cls.storage.save(available_name, file_obj)
        thumbnailer = get_thumbnailer(cls.storage.path(temp_name), relative_name=available_name)
        thumbnail = thumbnailer.generate_thumbnail(app_settings.THUMBNAIL_OPTIONS)
        return {
            'url': 'url({})'.format(data_uri(thumbnail)),
            'temp_name': cls.signer.sign(temp_name),
            'file_name': file_obj.name,
            'file_size': file_obj.size,
            'charset': file_obj.charset,
            'content_type': file_obj.content_type,
            'content_type_extra': file_obj.content_type_extra,
        }
