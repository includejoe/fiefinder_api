from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit

from core.settings import LOGGER as logger
from base.models import Country, Language, PushToken
from base.utils import request_sanitizer, token_required, Cache


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
        PushToken.objects.create(**body)
        return JsonResponse({"success": True, "info": "Push token saved successfully"})
    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})
