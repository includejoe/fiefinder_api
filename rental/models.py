from django.db import models
from django.contrib.postgres.fields import ArrayField

from base.models import Location
from user.models import User


class RentalCategory(models.Model):
    name = models.CharField(max_length=256, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-name"]
        verbose_name_plural = "Rental Categories"
        indexes = [models.Index(fields=["name"])]


class Rental(models.Model):
    category = models.ForeignKey(
        RentalCategory,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    description = models.TextField()
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lease_type = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        choices=(("monthly", "monthly"), ("yearly", "yearly")),
        default="yearly",
    )
    lease_term = models.PositiveSmallIntegerField(default=1)
    images = ArrayField(models.URLField(), blank=True, null=True)
    available = models.BooleanField(default=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
