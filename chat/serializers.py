from base.utils import includer, excluder

from user.serializers import user_serializer


def message_serializer(message, fields=[], exclude=[]):
    valid_fields = {
        "id": message.id,
        "text": message.text,
        "created_at": str(message.created_at),
        "sender": user_serializer(message.sender, exclude=["last_seen"]),
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields


def conversation_serializer(conversation, fields=[], exclude=[]):
    valid_fields = {
        "id": conversation.id,
        "initiator": user_serializer(conversation.initiator),
        "receiver": user_serializer(conversation.receiver),
        "last_message": message_serializer(conversation.message_set.last())
        if conversation.message_set.exists()
        else None,
        "messages": [
            message_serializer(message) for message in conversation.message_set.all()
        ]
        if conversation.message_set.exists()
        else [],
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
