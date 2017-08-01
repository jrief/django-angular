# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class AppSettings(object):
    def _setting(self, name, default=None):
        from django.conf import settings
        return getattr(settings, name, default)

    @property
    def upload_storage(self):
        import os
        from django.core.files.storage import FileSystemStorage

        media_root = self._setting('MEDIA_ROOT', '')
        upload_temp = self._setting('DJNG_UPLOAD_TEMP', 'upload_temp')
        return FileSystemStorage(location=os.path.join(media_root, upload_temp))

    @property
    def THUMBNAIL_OPTIONS(self):
        """
        Set the size as a 2-tuple for thumbnailed images after uploading them.
        """
        from django.core.exceptions import ImproperlyConfigured

        size = self._setting('DJNG_THUMBNAIL_SIZE', (200, 200))
        if not (isinstance(size, (list, tuple)) and len(size) == 2 and isinstance(size[0], int) and isinstance(size[1], int)):
            raise ImproperlyConfigured("'DJNG_THUMBNAIL_SIZE' must be a 2-tuple of integers.")
        return {'crop': True, 'size': size}


import sys
app_settings = AppSettings()
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
