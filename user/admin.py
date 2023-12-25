from django.contrib import admin

from user.models import User, Token


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "email"]
    list_display = ["email", "username", "first_name", "last_name"]


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["username", "key"]

    def username(self, instance):
        return instance.user.username
