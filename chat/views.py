from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django_ratelimit.decorators import ratelimit
from django.db.models import Q

from core.settings import LOGGER as logger
from chat.models import Conversation
from user.models import User
from chat.serializers import conversation_serializer
from base.utils import request_sanitizer, token_required, paginator


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@token_required
@require_POST
def start_conversation(request):
    try:
        user = request.user
        body = request.sanitized_data

        receiver = User.objects.get(id=body["receiver_id"])
        checker = Conversation.objects.select_related("initiator", "receiver").filter(
            Q(initiator=user, receiver=receiver) | Q(initiator=receiver, receiver=user)
        )

        if checker.exists():
            conversation = conversation_serializer(
                checker.first(), exclude=["last_message"]
            )
        else:
            conversation = Conversation.objects.create(
                initiator=user, receiver=receiver
            )
            conversation = conversation_serializer(
                conversation, exclude=["last_message"]
            )
        return JsonResponse({"success": True, "info": conversation})

    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@token_required
@require_GET
def fetch_conversations(request):
    user = request.user
    body = request.sanitized_data
    page_number = body.get("page", 1)
    drop = body.get("drop", 20)
    filters = body.get("filters", {})
    special_filter = Q(initiator=user) | Q(receiver=user)
    select_related = ["initiator", "receiver"]

    if not isinstance(page_number, int):
        return {
            "success": False,
            "info": "Page number should be an integer",
        }

    if not isinstance(drop, int):
        return {
            "success": False,
            "info": "Page drop should be an integer",
        }

    response = paginator(
        page_number,
        Conversation,
        conversation_serializer,
        filters,
        select_related=select_related,
        special_filter=special_filter,
        serializer_excluders=["messages"],
    )

    return JsonResponse(response)
