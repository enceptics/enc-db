from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'role')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')}
        ),
    )

    def profile_username(self, obj):
        # Check if the profile exists and has a user associated with it
        if hasattr(obj, 'profile') and obj.profile.user:
            return obj.profile.user.email
        return ''

    profile_username.short_description = 'Profile Username'

# Register your custom User model
admin.site.register(User, CustomUserAdmin)
