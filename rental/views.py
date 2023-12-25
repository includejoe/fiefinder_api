from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django_ratelimit.decorators import ratelimit
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage


from core.settings import LOGGER as logger
from base.models import Location
from rental.models import Rental
from rental.serializers import rental_serializer
from base.utils import request_sanitizer, token_required, partial_update, type_checker


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

    rentals = Rental.objects.select_related("user", "location").filter(**filters)
    paginator = Paginator(rentals, drop)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    try:
        previous_page = page.previous_page_number()
    except Exception as e:
        logger.warning(str(e))
        previous_page = page.number
    try:
        next_page = page.next_page_number()
    except Exception as e:
        logger.warning(str(e))
        next_page = page.number

    rentals = [rental_serializer(rental) for rental in page.object_list]

    return JsonResponse(
        {
            "success": True,
            "info": rentals,
            "paginator": {
                "previous_page": previous_page,
                "next_page": next_page,
                "next": page.has_next(),
                "prev": page.has_previous(),
            },
        }
    )


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
