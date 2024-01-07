from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django.db.models import Q

from core.settings import LOGGER as logger
from base.models import Country, Language, PushToken, Notification
from base.utils import request_sanitizer, token_required, Cache, paginator
from base.serializers import notification_serializer


@csrf_exempt
@ratelimit(key="ip", rate="10/m", block=True)
@request_sanitizer
@require_GET
def fetch_countries(request):
    cached_countries = Country.fetch_countries()
    if cached_countries:
        countries = [
            {
                "id": country["id"],
                "name": country["name"],
                "image": country["image"],
                "short_name": country["short_name"],
                "phone_code": country["phone_code"],
                "currency": country["currency"],
                "currency_code": country["currency_code"],
            }
            for country in cached_countries
        ]
    else:
        countries = list(
            Country.objects.values(
                "id",
                "name",
                "image",
                "short_name",
                "phone_code",
                "currency",
                "currency_code",
            )
        )
        Cache(Country, "base_cache_country").save_values()

    return JsonResponse({"success": True, "info": countries})


@csrf_exempt
@ratelimit(key="ip", rate="10/m", block=True)
@request_sanitizer
@require_GET
def fetch_languages(request):
    cached_languages = Language.fetch_languages()
    if cached_languages:
        languages = [
            {
                "id": language["id"],
                "name": language["name"],
                "short_code": language["short_code"],
                "image": language["image"],
            }
            for language in cached_languages
        ]
        return JsonResponse({"success": True, "info": languages})
    else:
        languages = list(Language.objects.values("id", "name", "short_code", "image"))
        Cache(Language, "base_cache_language").save_values()
    return JsonResponse({"success": True, "info": languages})


@csrf_exempt
@ratelimit(key="ip", rate="10/m", block=True)
@request_sanitizer
@token_required
@require_POST
def push_token(request):
    try:
        body = request.sanitized_data
        body["user"] = request.user
        checker = PushToken.objects.filter(**body)
        if checker.exists():
            return JsonResponse(
                {
                    "success": True,
                    "info": "Push token is already saved",
                }
            )
        PushToken.objects.create(**body)
        return JsonResponse({"success": True, "info": "Push token saved successfully"})
    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})


@csrf_exempt
@ratelimit(key="ip", rate="10/m", block=True)
@token_required
@request_sanitizer
def fetch_notifications(request):
    body = request.sanitized_data
    email = request.user.email
    page = body.get("page", 1)
    push_tokens = PushToken.objects.values_list("fcm_token", flat=True).filter(
        user__email=email
    )

    if not isinstance(page, int):
        return {
            "success": False,
            "info": "Page number should be an integer",
        }

    filters = {}

    special_filter = Q(general=True) | Q(recipients__overlap=push_tokens)

    response = paginator(
        page,
        Notification,
        notification_serializer,
        filters,
        special_filter=special_filter,
        serializer_params={"user_email": email},
    )

    return JsonResponse(response)
