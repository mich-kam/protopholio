from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FailedLogin, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(FailedLogin)
class FailedLoginAdmin(admin.ModelAdmin):
    """Journal en lecture seule : utile pour repérer une tentative d'intrusion."""

    list_display = ("identifier", "created_at")
    search_fields = ("identifier",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
