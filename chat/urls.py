from django.urls import path
from .views import start_conversation, fetch_conversation, fetch_conversations

app_name = "chat"

urlpatterns = [
    path("all/", fetch_conversations, name="fetch_conversations"),
    path("start/", start_conversation, name="start_conversation"),
    path("<str:conversation_id>/", fetch_conversation, name="fetch_conversation"),
]
