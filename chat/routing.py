from django.urls import re_path
from . import consumers
from collaboration import consumers as collaboration_consumers
websocket_urlpatterns =[
    re_path(r"ws/diagram/chat/", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/diagram/collaborate/", collaboration_consumers.CollaborationConsumer.as_asgi()),
    re_path(r"ws/diagram/access/", collaboration_consumers.CollaborationConsumer.as_asgi()),
    
    # re_path(r"ws/diagram/chat/(?P<room_id>[0-9a-f-]{36})/", consumers.ChatConsumer.as_asgi())
]