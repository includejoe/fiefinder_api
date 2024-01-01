from django.contrib import admin

from base.models import Country, Language, Location, PushToken, Notification


# Register your models here.
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "short_name", "currency_code", "phone_code"]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "short_code"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["region_or_state", "city_or_town", "street"]


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "fcm_token"]

    def user(self, instance):
        return instance.user.email


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "message", "general", "created_at"]
