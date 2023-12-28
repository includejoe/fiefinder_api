from base.utils import includer, excluder


def user_serializer(user, fields=[], exclude=[]):
    valid_fields = {
        "id": user.id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}",
        "image": user.image,
        "verified": user.image,
        "phone": user.phone,
    }

    if fields:
        return includer(valid_fields, fields)

    if exclude:
        return excluder(valid_fields, exclude)

    return valid_fields
