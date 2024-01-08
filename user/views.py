from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate

from core.settings import LOGGER as logger, REDIS
from base.models import Country
from user.models import User, Token
from base.utils import (
    request_sanitizer,
    token_required,
    partial_update,
)


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@require_POST
def signup(request):
    try:
        body = request.sanitized_data
        email = body["email"]
        phone = body["phone"]
        country = Country.fetch_countries(country=body["country"])

        if len(body["password"]) < 6:
            return JsonResponse(
                {
                    "success": False,
                    "info": "Password must be more than 6 characters",
                }
            )

        if len(phone) < 9:
            return JsonResponse(
                {
                    "success": False,
                    "info": "Invalid phone number",
                }
            )

        phone = phone[-9:]

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "success": False,
                    "info": "This email already exists",
                }
            )

        user = User(
            email=email,
            username=body.get("username", None),
            first_name=body["first_name"],
            last_name=body["last_name"],
            phone="{}{}".format(country["phone_code"], phone),
            gender=body["gender"],
            country_id=country["id"],
        )
        user.set_password(body["password"])
        user.save()

        return JsonResponse(
            {
                "success": True,
                "info": "Sign up successful, login to continue.",
            }
        )
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse(
            {
                "success": False,
                "info": "Invalid request data",
            }
        )


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@require_POST
def login_user(request):
    try:
        body = request.sanitized_data
        email = body["email"]
        password = body["password"]
        checker = User.objects.filter(email=email).values("deleted", "suspended")

        if not checker.exists():
            return JsonResponse({"success": False, "info": "Invalid credentials"})

        user = checker.first()
        if user["deleted"]:
            return JsonResponse(
                {"success": False, "info": "This account does not exist"}
            )
        if user["suspended"]:
            return JsonResponse(
                {"success": False, "info": "This account has been suspended"}
            )
        user = authenticate(request=request, username=email, password=password)
        if user is None:
            return JsonResponse({"success": False, "info": "Invalid credentials"})

        token_checker = Token.objects.filter(user=user)
        if token_checker.exists():
            token = token_checker[0]
        else:
            token = Token.objects.create(user=user)
        login(request, user)
        return JsonResponse(
            {
                "success": True,
                "info": {
                    "token": token.key,
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "gender": user.gender,
                    "email": user.email,
                    "country": user.country.name,
                    "phone": user.phone,
                    "image": user.image,
                    "verified": user.verified,
                },
            }
        )
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse(
            {
                "success": False,
                "info": "Invalid request data",
            }
        )


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@request_sanitizer
@token_required
@require_POST
def update_user(request):
    body = request.sanitized_data
    user = request.user
    email = request.user.email
    current_password = body.pop("current_password", None)
    new_password = body.pop("new_password", None)

    try:
        if current_password and new_password:
            current_password = body["current_password"]
            new_password = body["new_password"]

            if check_password(new_password, user.password):
                return JsonResponse(
                    {
                        "success": True,
                        "info": "New password can not be same as current password",
                    },
                )

            if check_password(current_password, user.password):
                user.set_password(new_password)
                user.save()
            else:
                return JsonResponse(
                    {"success": False, "info": "Current password is incorrect"},
                )

        update_fields = partial_update(body, exclude=["email", "username", "password"])
        User.objects.filter(email=email).update(**update_fields)
        return JsonResponse({"success": True, "info": "User updated successfully"})
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse(
            {"success": False, "info": "Invalid request body"},
        )


@csrf_exempt
@ratelimit(key="ip", rate="5/m", block=True)
@token_required
@request_sanitizer
@require_POST
def logout_user(request):
    user = request.user
    Token.objects.filter(user=user).delete()
    logout(request)
    template = "{}_login_details".format(user.username)
    del REDIS[template]
    return JsonResponse({"success": True, "info": "Logout Successful"})
