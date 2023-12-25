from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from base.utils import Cache


class Country(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    short_name = models.CharField(max_length=5, blank=True, null=True)
    phone_code = models.CharField(max_length=5, blank=True, null=True)
    currency = models.CharField(max_length=120, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    image = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-name"]
        verbose_name_plural = "Countries"
        indexes = [models.Index(fields=["name"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Cache(Country, "base_cache_country").save_values()

    @staticmethod
    def fetch_countries(country=None, country_id=None):
        cached_data = Cache(Country, "base_cache_country").fetch_values()
        if country:
            countries = [
                country_ for country_ in cached_data if country_["name"] == country
            ]
            if len(countries) > 0:
                return countries[0]
            return None
        if country_id:
            countries = [
                country_ for country_ in cached_data if country_["id"] == country_id
            ]
            if len(countries) > 0:
                return countries[0]
            return None
        return cached_data


class Location(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    region_or_state = models.CharField(max_length=128, blank=True, null=True)
    city_or_town = models.CharField(max_length=128, blank=True, null=True)
    street = models.CharField(max_length=128, blank=True, null=True)
    landmark = models.CharField(max_length=128, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )


class Language(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    short_code = models.CharField(max_length=5, blank=True, null=True)
    image = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-name"]
        indexes = [models.Index(fields=["name", "short_code"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Cache(Language, "base_cache_language").save_values()

    @staticmethod
    def fetch_languages(language_id=None):
        cached_data = Cache(Language, "base_cache_language").fetch_values()
        if language_id:
            languages = [
                language for language in cached_data if language["id"] == language_id
            ]
            if len(languages) > 0:
                return languages[0]
            return None

        return Cache(Language, "base_cache_language").fetch_values()


class PushToken(models.Model):
    fcm_token = models.CharField(max_length=256, blank=True, null=True)
    device = models.CharField(max_length=450, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    class Meta:
        indexes = [models.Index(fields=["fcm_token"])]


class Notification(models.Model):
    title = models.CharField(blank=False, null=False, max_length=256)
    message = models.TextField(blank=False, null=False)
    opened_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        symmetrical=False,
    )
    general = models.BooleanField(default=False)
    recipients = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "title",
                    "message",
                ]
            ),
        ]
