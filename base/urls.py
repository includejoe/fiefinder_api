from django.urls import path

from base.views import fetch_countries, fetch_languages, push_token, fetch_notifications

app_name = "base"

urlpatterns = [
    path("countries/", fetch_countries, name="fetch_countries"),
    path("languages/", fetch_languages, name="fetch_languages"),
    path("push_token/", push_token, name="push_token"),
    path("notifications/", fetch_notifications, name="fetch_notifications"),
]
