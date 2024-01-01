from base.utils import includer, excluder


def location_serializer(location, fields=[], exclude=[]):
    valid_fields = {
        "id": location.id,
        "country": location.country.name,
        "region_or_state": location.region_or_state,
        "city_or_town": location.city_or_town,
        "street": location.street,
        "landmark": location.landmark,
        "latitude": location.latitude,
        "longitude": location.longitude,
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields


def notification_serializer(notification, user_email, fields=[], exclude=[]):
    valid_fields = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "opened": notification.opened_by.filter(email=user_email).exists(),
        "created_at": notification.created_at,
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
