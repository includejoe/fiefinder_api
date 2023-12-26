from django.urls import path

from base.views import fetch_countries, fetch_languages

app_name = "base"

urlpatterns = [
    path("countries/", fetch_countries, name="fetch_countries"),
    path("languages/", fetch_languages, name="fetch_languages"),
]
