from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator

from djangular.core.decorators import add_messages_to_response

from server.forms.django_messages import MessagesForm



class DjangoMessagesView(FormView):
    template_name = 'django-messages.html'
    form_class = MessagesForm

    @method_decorator(add_messages_to_response)
    def post(self, request, *args, **kwargs):
        return super(DjangoMessagesView, self).post(request, *args, **kwargs)
	
    def form_valid(self, form):

        return HttpResponse(json.dumps({u'data': 'my data'}),
		                    status=200,
		                    content_type='application/json')
	
	