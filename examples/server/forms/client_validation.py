# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# start tutorial
from djng.forms import NgFormValidationMixin
from . import subscribe_form


class SubscribeForm(NgFormValidationMixin, subscribe_form.SubscribeForm):
    # Apart from an additional mixin class, the Form declaration from the
    # 'Classic Subscription' view, has been reused here.
    pass
    