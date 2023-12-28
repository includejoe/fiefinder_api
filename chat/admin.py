from django.contrib import admin

from chat.models import Conversation, Message


# Register your models here.
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["initiator", "receiver"]

    def initiator(self, instance):
        return instance.initiator.username

    def receiver(self, instance):
        return instance.receiver.username


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "text", "created_at"]

    def sender(self, instance):
        return instance.sender.username
