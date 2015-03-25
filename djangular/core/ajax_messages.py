import json

from django.contrib import messages


def process_response(request, response):
    if is_not_valid_type(request, response):
        return response
    try:
        content = json.loads(response.content.decode('utf8'))
    except ValueError:
        return response

    django_messages = _get_messages(request)

    if len(django_messages) > 0:
        content = {u'data': content,
                   u'django_messages': django_messages}

        response.content = json.dumps(content)

    return response


def is_not_valid_type(request, response):
	return not request.is_ajax() and not _content_type_is_json(response)


def _content_type_is_json(response):
    return response['Content-Type'] == "application/json"


def _get_messages(request):
    django_messages = []
    for message in messages.get_messages(request):
        django_messages.append({
            "level": message.level,
            "message": message.message,
            "type": message.tags.split(' ').pop(),
            "tags": message.tags,
    })
    return django_messages