# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView


class NgFormDataValidView(TemplateView):
    """
    This view just displays a success message, when a valid form was posted successfully.
    """
    template_name = 'form-data-valid.html'
