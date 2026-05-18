from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'role', 'phone', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'phone']
    fieldsets     = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('username', 'password1', 'password2', 'role', 'phone'),
        }),
    )