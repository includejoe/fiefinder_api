from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("shinobi/", admin.site.urls),
    path("base/", include("base.urls")),
    path("user/", include("user.urls")),
    path("rental/", include("rental.urls")),
    path("chat/", include("chat.urls")),
]
