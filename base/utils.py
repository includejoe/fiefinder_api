import json
import arrow
import bleach
import random
from functools import wraps
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import logout
from core.settings import LOGGER as logger, REDIS
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage


def partial_update(body, exclude=[]):
    return {key: value for key, value in body.items() if key not in exclude}


def includer(valid_fields, includes):
    return {field: valid_fields[field] for field in includes if field in valid_fields}


def excluder(valid_fields, excludes):
    return {
        field: valid_fields[field] for field in valid_fields if field not in excludes
    }


def generate_verification_code():
    random_digits = [random.randint(0, 9) for _ in range(6)]
    logger.warning(random_digits)
    return "".join(map(str, random_digits))


def type_checker(type_, types):
    if type_ not in types:
        logger.warning("Invalid type: %s", type_)
        return {"success": False, "info": "Invalid body type"}
    return {"success": True}


def request_sanitizer(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method not in ["POST", "GET"]:
            return JsonResponse({"info": "Invalid request data", "success": False})
        try:
            request_body_text = request.body.decode("utf-8").strip()
            sanitized_body = bleach.clean(
                request_body_text, tags=[], attributes={}, strip=True
            )
            if request.method == "GET" and sanitized_body == "":
                request.sanitized_data = {}
            else:
                if request_body_text == "":
                    request.sanitized_data = {}
                else:
                    sanitized_data = json.loads(sanitized_body)
                    request.sanitized_data = sanitized_data
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"info": "Invalid request data", "success": False})

    return _wrapped_view


def token_required(func):
    from user.models import Token

    def inner(request, *args, **kwargs):
        try:
            token = str(request.headers["Authorization"].split(" ")[1]).strip()
            token = Token.objects.select_related("user").get(key=str(token))
            request.user = token.user
            request.key = token.key
            user = token.user
            restrictions = [user.deleted, user.suspended]
            if any(restrictions):
                Token.objects.filter(user__username=user.username).delete()
            if user.deleted:
                return JsonResponse(
                    {
                        "info": "This account does not exist",
                        "success": False,
                    }
                )
            if user.suspended:
                return JsonResponse(
                    {
                        "info": "This account has been suspended",
                        "success": False,
                    }
                )

            if token.expiry_date < arrow.now().datetime:
                Token.objects.filter(key=token.key).delete()
                try:
                    template = "{}_login_details".format(user.username)
                    logout(request)
                    del REDIS[template]
                except Exception as e:
                    logger.warning(str(e))
                return JsonResponse(
                    {
                        "info": "Session has expired. Please  login again",
                        "success": False,
                    },
                )
            try:
                REDIS.set(
                    f"{user.username}_last_seen", arrow.now().datetime.timestamp()
                )
            except Exception as rd_:
                logger.warning("can't save last last seen on redis")
                logger.warning(str(rd_))
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse(
                {
                    "info": "Session has expired. Please logout and login again",
                    "expired": True,
                },
            )

    return inner


class Cache:
    def __init__(self, cls, template):
        self.cls = cls
        self.template = template

    def save_values(self):
        try:
            values = self.cls.objects.all().values()
            values_list = list(values)
            json_data = json.dumps(values_list, cls=DjangoJSONEncoder)
            REDIS.set(self.template, json_data)
        except Exception as e:
            logger.warning(str(e))
            logger.warning(f"failed to save cache data")
            # todo send an email to notify devs of this, this can cause a problem

    def fetch_values(self):
        try:
            json_data = json.loads(REDIS.get(self.template))
            return json_data
        except Exception as e:
            logger.warning(str(e))
            self.save_values()
            json_data = json.loads(REDIS.get(self.template))
            return json_data


def paginator(
    page_number,
    cls,
    serializer,
    filters,
    annotate={},
    select_related=None,
    special_filter=None,
    excludes=None,
    drop=20,
):
    if excludes is None:
        excludes = {}
    if select_related:
        obj = cls.objects.select_related(*select_related).annotate(**annotate)
        if special_filter:
            obj = (
                obj.filter(special_filter, **filters)
                .exclude(**excludes)
                .order_by("-id")
            )
        else:
            obj = obj.filter(**filters).exclude(**excludes).order_by("-id")
    else:
        if special_filter:
            obj = (
                cls.objects.filter(special_filter, **filters)
                .annotate(**annotate)
                .exclude(**excludes)
                .order_by("-id")
            )
        else:
            obj = (
                cls.objects.filter(**filters)
                .annotate(**annotate)
                .exclude(**excludes)
                .order_by("-id")
            )
    paginator = Paginator(obj, drop)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
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

    return {
        "info": [serializer(obj) for obj in page.object_list],
        "success": True,
        "paginator": {
            "success": True,
            "previous_page": previous_page,
            "next_page": next_page,
            "next": page.has_next(),
            "prev": page.has_previous(),
        },
    }
