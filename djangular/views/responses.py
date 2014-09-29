import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text

class FormErrorJSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode ValidationError.
    """
    def default(self, o):
        if isinstance(o, ValidationError):
            messages = o.messages
            if len(messages) > 1:
                return [force_text(x) for x in messages]
            else:
                return force_text(messages[0])
        else:
            return super(FormErrorJSONEncoder, self).default(o)

class JSONResponse(HttpResponse):
    def __init__(self, data, encoder=FormErrorJSONEncoder, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JSONResponse, self).__init__(content=data, **kwargs)
