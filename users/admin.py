from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Customize how the CustomUser model is displayed in the admin interface
    list_display = ('id', 'username', 'email', 'password', 'is_active', 'is_admin', 'is_staff', 'is_superadmin')
    list_filter = ('id', 'email', 'is_staff')
    search_fields = ('id', 'email')
    fieldsets = (
        ('Personal Info', {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_superadmin', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id', 'username', 'email', 'password', 'is_active', 'is_admin', 'is_staff', 'is_superadmin'),
        }),
    )

# Register your models here.
admin.site.register(User, CustomUserAdmin)