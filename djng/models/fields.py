from django.db.models.fields import files

from djng.forms import fields


class ImageField(files.ImageField):
    def formfield(self, **kwargs):
        defaults = {'help_text': self.help_text, 'required': not self.blank, 'label': self.verbose_name}
        defaults.update(kwargs)
        return fields.ImageField(**defaults)
