# -*- coding: utf-8 -*-
from django import VERSION
from add_placeholder import *
from angular_model import *
if VERSION[0] == 1 and VERSION[1] >= 5:
    from angular_validation import *
