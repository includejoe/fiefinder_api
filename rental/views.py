from django.db.models.functions import Cos, Sin, Radians
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django_ratelimit.decorators import ratelimit
from django.db import transaction
from django.db.models import F, ExpressionWrapper, DecimalField

from core.settings import LOGGER as logger
from base.models import Location
from rental.models import Rental, RentalCategory
from rental.serializers import rental_serializer
from rental.utils import Acos
from base.utils import (
    request_sanitizer,
    token_required,
    partial_update,
    type_checker,
    paginator,
    Cache,
)


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@token_required
@require_POST
def index(request):
    user = request.user
    body = request.sanitized_data
    type_ = body.pop("type", "")

    try:
        type_response = type_checker(type_, ["create", "update", "delete"])
        if not type_response["success"]:
            return JsonResponse({"success": False, "info": type_response["info"]})

        if type_ == "create":
            with transaction.atomic():
                location_data = body.pop("location", None)
                if location_data is None:
                    return JsonResponse(
                        {"success": False, "info": "Location data is required"}
                    )
                body["location"] = Location.objects.create(**location_data)
                body["user"] = user
                Rental.objects.create(**body)
                return JsonResponse(
                    {
                        "success": True,
                        "info": "Rental created successfully",
                    }
                )

        if type_ == "update":
            rental = (
                Rental.objects.select_related("user")
                .filter(id=body["id"])
                .values("user__email")
            )

            if rental[0]["user__email"] != user.email:
                return JsonResponse(
                    {
                        "success": False,
                        "info": "You are not authorized to update this rental",
                    }
                )

            update_fields = partial_update(body, exclude=["id", "location_id", "user"])
            rental.update(**update_fields)
            return JsonResponse(
                {"success": True, "info": "Rental updated successfully"}
            )

        if type_ == "delete":
            rental = (
                Rental.objects.select_related("user")
                .filter(id=body["id"])
                .values("user__email")
            )

            if rental[0]["user__email"] != user.email:
                return JsonResponse(
                    {
                        "success": False,
                        "info": "You are not authorized to delete this rental",
                    }
                )
            Rental.objects.filter(id=body["id"]).delete()
            return JsonResponse(
                {"success": True, "info": "Rental deleted successfully"}
            )

    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})


@csrf_exempt
@request_sanitizer
def fetch_rentals(request):
    body = request.sanitized_data
    page_number = body.get("page", 1)
    drop = body.get("drop", 20)
    filters = body.get("filters", {})
    select_related = ["user", "location"]
    longitude = filters.pop("longitude", None)
    latitude = filters.pop("latitude", None)
    annotate = {}

    print(filters)

    try:
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

        if longitude and latitude:
            # todo: implement accurate calculation of distance

            latitude_expr = Radians(F("location__latitude"))
            longitude_expr = Radians(F("location__longitude"))

            annotate = {
                "distance": ExpressionWrapper(
                    6371
                    * Acos(
                        Cos(Radians(latitude))
                        * Cos(latitude_expr)
                        * Cos(Radians(longitude) - longitude_expr)
                        + Sin(Radians(latitude)) * Sin(latitude_expr)
                    ),
                    output_field=DecimalField(),
                )
            }

            # filters = {"distance__lte": 30, **filters}

        response = paginator(
            page_number,
            Rental,
            rental_serializer,
            {"available": True, **filters},
            annotate=annotate,
            select_related=select_related,
        )

        return JsonResponse(response)
    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})


@csrf_exempt
@request_sanitizer
@require_GET
def fetch_rental(request, rental_id):
    try:
        rental = Rental.objects.select_related("user", "location").filter(id=rental_id)
        if not rental.exists():
            return JsonResponse({"success": False, "info": "Rental not found"})
        rental = rental_serializer(rental.first())
        return JsonResponse({"success": True, "info": rental})
    except Exception as e:
        logger.exception(str(e))
        return JsonResponse({"success": False, "info": "Invalid request body"})


@csrf_exempt
@ratelimit(key="ip", rate="10/m", block=True)
@request_sanitizer
@require_GET
def fetch_categories(request):
    cached_categories = RentalCategory.fetch_categories()
    if cached_categories:
        categories = cached_categories
    else:
        categories = list(RentalCategory.objects.values())
        Cache(RentalCategory, "base_cache_rental_category").save_values()
    return JsonResponse({"success": True, "info": categories})
