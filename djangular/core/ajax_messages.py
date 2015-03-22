import json

from django.contrib import messages


def process_response(request, response):
    if request.is_ajax() and _contentTypeIsJson(response):
           try:
               content = json.loads(response.content)
           except ValueError:
               return response

           django_messages = _getMessages(request)

           if len(django_messages) > 0:
               content = {u'data': content,
                          u'django_messages': django_messages}

               response.content = json.dumps(content)

    return response

def _contentTypeIsJson(response):
    return response['Content-Type'] == "application/json"

def _getMessages(request):
    django_messages = []
    for message in messages.get_messages(request):
        django_messages.append({
            "level": message.level,
            "message": message.message,
            "extra_tags": message.tags,
    })
    return django_messages