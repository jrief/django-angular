# -*- coding: utf-8 -*-
from django import VERSION
from forms import *
from views import *
if VERSION[0] == 1 and VERSION[1] >= 5:
    from validation import *
