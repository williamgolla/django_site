from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from django_messages.views import *

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='inbox/'), name='messages'),
    url(r'^inbox/$', inbox, name='inbox'),
    url(r'^outbox/$', outbox, name='outbox'),
    url(r'^compose/$', compose, name='compose'),
    url(r'^compose/(?P<recipient>[\w.@+-]+)/$', compose, name='compose_to'),
    url(r'^reply/(?P<message_id>[\d]+)/$', reply, name='reply'),
    url(r'^view/(?P<message_id>[\d]+)/$', view, name='detail'),
    url(r'^delete/(?P<message_id>[\d]+)/$', delete, name='delete'),
    url(r'^undelete/(?P<message_id>[\d]+)/$', undelete, name='undelete'),
    url(r'^trash/$', trash, name='trash'),
)
