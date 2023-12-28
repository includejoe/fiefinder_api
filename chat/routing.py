from django.urls import re_path

from chat.consumers import chat_consumer_asgi

websocket_urlpatterns = [
    re_path(r"^chat/(?P<conversation_id>[^/]+)/$", chat_consumer_asgi)
]
