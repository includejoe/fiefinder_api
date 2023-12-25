from django.contrib import admin

from rental.models import RentalCategory, Rental


# Register your models here.
@admin.register(RentalCategory)
class RentalCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ["price_per_month", "lease_term", "created_at"]
