from django.urls import path

from rental.views import index, fetch_rentals, fetch_rental

app_name = "rental"

urlpatterns = [
    path("", index, name="rental"),
    path("all/", fetch_rentals, name="fetch_rentals"),
    path("<int:rental_id>/", fetch_rental, name="fetch_rental"),
]
