import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from datetime import datetime, timedelta


from chat.models import Message, Conversation
from user.models import User
from chat.serializers import message_serializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from websocket
    def receive(self, text_data=None, bytes_data=None):
        # parse json data into dictionary object
        text_data_json = json.loads(text_data)

        # send message to room group
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, return_dict)

    # Receive message from room group
    def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message_text, sender_id = (
            text_data_json["message"],
            text_data_json["sender"],
        )

        conversation = Conversation.objects.get(id=str(self.room_name))
        sender = User.objects.get(id=sender_id)

        # to avoid duplicate messages
        time_threshold = datetime.now() - timedelta(minutes=1)
        similar_messages = Message.objects.filter(
            conversation__id=self.room_name,
            text=message_text,
            sender=sender,
            created_at__gte=time_threshold,
        )

        if similar_messages.exists():
            message = message_serializer(similar_messages.first())

            # Send message to WebSocket
            self.send(text_data=json.dumps(message))
        else:
            message = Message.objects.create(
                sender=sender,
                text=message_text,
                conversation=conversation,
            )
            message = message_serializer(message)
            # Send message to WebSocket
            self.send(text_data=json.dumps(message))


chat_consumer_asgi = ChatConsumer.as_asgi()
