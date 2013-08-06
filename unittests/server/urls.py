from django.conf.urls.defaults import url, patterns
from django.views.generic import View
from django.http import HttpResponse


class MyView(View):
    def get(self, request):
        htmlsource = '<a></a>'
        return HttpResponse(htmlsource)


urlpatterns = patterns('',
    url(r'^autolabelform/$', 'djangular.tests.forms.render_autolabel_form', name='autolabel'),
    url(r'^404.html', MyView.as_view()),
)
