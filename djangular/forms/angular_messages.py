# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.html import format_html, format_html_join
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.safestring import mark_safe, SafeText

from djangular.forms.angular_base import TupleErrorList, SafeTuple, NgFormBaseMixin



class NgMessagesFormErrorList(TupleErrorList):
	ul_format = '<ul class="{1}" ng-show="{0}.$message" ng-cloak>{3}</ul>'
	

class NgMessagesFieldErrorList(TupleErrorList):
	
    ul_format_valid = '<ul class="{1}" ng-show="{2}.$submitted || {0}.$dirty" ng-cloak>{3}</ul>'
    li_format_valid = '<li ng-show="{0}.{1}" class="{2}">{3}</li>'

    ul_format = '<ul class="{1}" ng-messages="{0}.$error" ng-show="{2}.$submitted || {0}.$dirty" ng-cloak>{3}</ul>'
    li_format = '<li ng-message="{1}" class="{2}">{3}</li>'
    """ a span is necessary due to this bug https://github.com/angular/angular.js/issues/8089 """
    li_format_bind = '<li ng-message="{1}" class="{2}"><span ng-bind="{0}.{3}"></span></li>'

    def as_ul(self):
        if not self:
            return SafeText()
        first = self[0]
        if isinstance(first, tuple):
            valid_list = []
            invalid_list = []
            for e in self:
                """ Ignore $pristine errors, as they relate to the original rejected error handling or djng-error bound-field"""
                if e[2] == '$pristine':
                    continue

                if e[3] == '$valid':
                    li_format = self.li_format_valid
                    error_list = valid_list
                elif e[5] == '$message':
                    li_format = self.li_format_bind
                    error_list = invalid_list
                else:
                    li_format = self.li_format
                    error_list = invalid_list

                msg_type = e[3].split('.')
                err_tuple = (e[0], msg_type[0] if len(msg_type) == 1 else msg_type.pop(), e[4], force_text(e[5]))
                error_list.append(format_html(li_format, *err_tuple))

            return mark_safe(format_html(self.ul_format_valid, first[0], first[1], self._get_form_name(first[0]), mark_safe(''.join(valid_list)))) \
                 + mark_safe(format_html(self.ul_format, first[0], first[1], self._get_form_name(first[0]), mark_safe(''.join(invalid_list))))

        return format_html('<ul class="errorlist">{0}</ul>',
            format_html_join('', '<li>{0}</li>', ((force_text(e),) for e in self)))

    def _get_form_name(self, value):
        parts = value.split('.')
        parts.pop()
        return '.'.join(parts)
	


class NgMessagesMixin(NgFormBaseMixin):
	
    def __init__(self, data=None, *args, **kwargs):
        self.form_error_class = kwargs.pop('form_error_class', NgMessagesFormErrorList)
        error_class = kwargs.pop('error_class', NgMessagesFieldErrorList)
        kwargs.setdefault('error_class', error_class)
        super(NgMessagesMixin, self).__init__(data, *args, **kwargs)

    def get_field_errors(self, field):
        errors = super(NgMessagesMixin, self).get_field_errors(field)
        if field.is_hidden:
            return errors
        identifier = format_html('{0}.{1}', self.form_name, field.name)
        errors.append(SafeTuple((identifier, self.field_error_css_classes, '$dirty', 'rejected', 'invalid', '$message')))
        return errors

    def non_field_errors(self):
        errors = super(NgMessagesMixin, self).non_field_errors()
        return self.form_error_class(errors)

    def get_widget_attrs(self, bound_field):
        attrs = super(NgMessagesMixin, self).get_widget_attrs(bound_field)
        attrs.update({'djng-rejected': 'validator'})
        if self.is_bound:
            self._apply_bound_error(bound_field, attrs)
        return attrs

    def _apply_bound_error(self, bound_field, attrs):
        for error in bound_field.errors:
            if error[3] == '$pristine':
                # override NgFormValidationMixin djng-error 'bound-field'
                attrs.update({'djng-error': 'bound-msgs-field'})
                attrs.update({'djng-error-msg': error[5]})
