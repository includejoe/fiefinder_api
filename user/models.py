import os
import arrow
import random
import binascii
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from user.utils import UserManager
from base.models import Country


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, blank=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=128, default="233")
    gender = models.CharField(
        max_length=8,
        default="other",
        choices=[("male", "male"), ("female", "female"), ("other", "other")],
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    deleted = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name}{random.randint(100000, 999999)}"
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]


class Token(models.Model):
    key = models.CharField(max_length=82, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="main_auth_token",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(32)).decode()
            self.expiry_date = arrow.now().shift(days=5).datetime
        return super().save(*args, **kwargs)
