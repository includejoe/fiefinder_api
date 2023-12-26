def user_serializer(user):
    return (
        {
            "id": user.id,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}",
            "image": user.image,
            "verified": user.image,
            "phone": user.phone,
        },
    )
