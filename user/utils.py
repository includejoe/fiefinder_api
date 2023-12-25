from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        phone,
        password=None,
        is_superuser=False,
    ):
        if not email:
            raise ValueError("user must have an email")

        user = self.model(email=self.normalize_email(email))
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.set_password(password)
        user.is_superuser = is_superuser
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, phone, password):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
