from base.utils import includer, excluder

from user.serializers import user_serializer
from base.serializers import location_serializer


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
        "location": location_serializer(rental.location),
        "created_at": rental.created_at,
        "user": user_serializer(rental.user),
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
