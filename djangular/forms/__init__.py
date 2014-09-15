# -*- coding: utf-8 -*-
from django import VERSION
from djangular.forms.angular_model import *
if VERSION[0] == 1 and VERSION[1] >= 5:
    from djangular.forms.angular_validation import *
