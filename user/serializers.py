import arrow
from base.utils import includer, excluder
from core.settings import REDIS, LOGGER as logger


def user_serializer(user, fields=[], exclude=[]):
    try:
        last_seen = REDIS.get(f"{user.username}_last_seen")
        last_seen = arrow.get(float(last_seen)).datetime
    except Exception as e:
        logger.warning(e)
        logger.warning("cannot fetch user last seen from redis")
        last_seen = None

    valid_fields = {
        "id": user.id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}",
        "image": user.image,
        "verified": user.verified,
        "phone": user.phone,
        "last_seen": last_seen,
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
