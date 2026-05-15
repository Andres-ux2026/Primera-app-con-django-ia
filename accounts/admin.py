from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('role', 'is_approved')}),
    )
