from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from djangular.core.decorators import add_messages_to_response



class DjangoMessagesView(TemplateView):
    template_name = 'django-messages.html'
	
    @method_decorator(add_messages_to_response)
    def post(self, request, *args, **kwargs):

        return HttpResponse(json.dumps({u'data': 'my data'}),
		                    status=200,
		                    content_type='application/json') 
	
	