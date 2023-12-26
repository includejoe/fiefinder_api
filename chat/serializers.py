from base.utils import includer, excluder

from user.serializers import user_serializer


def message_serializer(message, fields=[], exclude=[]):
    valid_fields = {
        "id": message.id,
        "text": message.text,
        "created_at": message.created_at,
        "conversation": message.conversation.id,
        "sender": user_serializer(message.sender),
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields


def conversation_serializer(conversation, fields=[], exclude=[]):
    valid_fields = {
        "id": conversation.id,
        "text": conversation.text,
        "initiator": user_serializer(conversation.initiator),
        "receiver": user_serializer(conversation.receiver),
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
