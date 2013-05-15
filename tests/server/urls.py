from django.conf.urls.defaults import url, patterns, include


urlpatterns = patterns('',
    url(r'^shop/', include('shop.urls')),
)
