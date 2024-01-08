from django.urls import path

from user.views import signup, login_user, update_user, logout_user

app_name = "user"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login_user, name="login_user"),
    path("update/", update_user, name="update_user"),
    path("logout/", logout_user, name="logout_user"),
]
