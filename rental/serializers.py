from base.utils import includer, excluder

from user.serializers import user_serializer


def rental_serializer(rental, fields=[], exclude=[]):
    valid_fields = {
        "id": rental.id,
        "category": rental.category.name,
        "description": rental.description,
        "price_per_month": rental.price_per_month,
        "lease_type": rental.lease_type,
        "lease_term": rental.lease_term,
        "images": rental.images,
        "available": rental.available,
        "location": {
            "country": rental.location.country.name,
            "region_or_state": rental.location.region_or_state,
            "city_or_town": rental.location.city_or_town,
            "street": rental.location.street,
            "landmark": rental.location.landmark,
            "latitude": rental.location.latitude,
            "longitude": rental.location.longitude,
        },
        "created_at": rental.created_at,
        "user": user_serializer(rental.user),
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
