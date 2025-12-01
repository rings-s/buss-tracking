from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'full_name', 'phone_number', 'nfc_uid')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'nfc_uid')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Groups', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

    # Quick actions
    actions = ['make_admin', 'make_driver', 'make_employee', 'activate_users', 'deactivate_users']

    @admin.action(description='Set selected users as Admin')
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} user(s) set to Admin role.')

    @admin.action(description='Set selected users as Driver')
    def make_driver(self, request, queryset):
        updated = queryset.update(role='driver')
        self.message_user(request, f'{updated} user(s) set to Driver role.')

    @admin.action(description='Set selected users as Employee')
    def make_employee(self, request, queryset):
        updated = queryset.update(role='employee')
        self.message_user(request, f'{updated} user(s) set to Employee role.')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
