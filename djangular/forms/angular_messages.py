from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe, SafeText

from djangular.forms.angular_base import TupleErrorList
from djangular.forms.angular_base import NgFormBaseMixin


class NgMessagesTupleErrorList(TupleErrorList):
	
    msgs_format = '<div class="{1}" ng-messages="{0}.$error" ng-show="{0}.$dirty && {0}.$invalid" ng-cloak>{2}</div>'
    msg_format = '<div ng-message="{1}" class="{2}">{3}</div>'
    """ span's necessary due to this bug https://github.com/angular/angular.js/issues/8089"""
    msg_format_bind = '<div ng-message="rejected" class="{2}"><span ng-bind="{0}.{3}"></span></div>'

    def as_ul(self):
        if not self:
            return SafeText()
        first = self[0]
        if isinstance(first, tuple):
            error_list = []
            for e in self:
                if e[3] == '$valid':
                    continue
                msg_format = e[5] == '$message' and self.msg_format_bind or self.msg_format
                msg_type = e[3].split('.')
                err_tuple = (e[0], msg_type[0] if len(msg_type) == 1 else msg_type.pop(), e[4], force_text(e[5]))
                error_list.append(format_html(msg_format, *err_tuple))

        return (error_list and \
             format_html(self.msgs_format, first[0], first[1], mark_safe(''.join(error_list)))
          or '')


class NgMessagesMixin(NgFormBaseMixin):
	
    def __init__(self, data=None, *args, **kwargs):
        kwargs['error_class'] = NgMessagesTupleErrorList
        super(NgMessagesMixin, self).__init__(data, *args, **kwargs)

    def get_widget_attrs(self, bound_field):
        attrs = super(NgMessagesMixin, self).get_widget_attrs(bound_field)
        attrs['validate-rejected'] = ""
        return attrs