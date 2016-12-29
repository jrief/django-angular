import json

from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib import messages

from djng.core.decorators import add_messages_to_response

from server.forms.django_messages import MessagesForm


class DjangoMessagesView(FormView):
    template_name = 'django-messages.html'
    form_class = MessagesForm

    @method_decorator(add_messages_to_response)
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                data = json.loads(request.body.decode('utf8'))
            except ValueError:
                data = {}
            self.request.POST = data

        return super(DjangoMessagesView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        for i in range(form.cleaned_data['count']):
            messages.add_message(self.request,
                                 form.cleaned_data['level'],
                                 form.cleaned_data['message'])

        return HttpResponse(
            json.dumps({'data': 'success'}),
            status=200,
            content_type='application/json')

    def form_invalid(self, form):
        return HttpResponse(
            json.dumps({'errors': form.errors}),
            status=200,
            content_type='application/json')
