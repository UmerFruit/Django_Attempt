from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/whiteboard/(?P<whiteboard_id>\d+)/$', consumers.WhiteboardConsumer.as_asgi()),
]
