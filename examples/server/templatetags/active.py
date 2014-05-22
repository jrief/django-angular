from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def active(request, url):
    urlparts = reverse(url).lstrip('/').split('/')
    requestparts = request.path.lstrip('/').split('/')
    active = 'active'
    for p1, p2 in zip(urlparts, requestparts):
        if p1 != p2:
            active = ''
            break
    return active
