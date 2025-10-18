from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Teacher, Parent, UserActivity, UserSession

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role']
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'No Role'
    get_role.short_description = 'Role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'designation', 'specialization', 'status', 'hire_date']
    list_filter = ['designation', 'employment_type', 'status', 'hire_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    autocomplete_fields = ['user']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Professional Information', {
            'fields': ('designation', 'specialization')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'salary', 'employment_type', 'status')
        }),
        ('Academic Information', {
            'fields': ('qualifications', 'experience_years')
        }),
        ('Contact Information', {
            'fields': ('office_room', 'office_hours')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'phone', 'is_emergency_contact', 'emergency_priority']
    list_filter = ['relationship', 'is_emergency_contact', 'emergency_priority']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'relationship')
        }),
        ('Contact Information', {
            'fields': ('phone', 'occupation', 'employer')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('is_emergency_contact', 'emergency_priority')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'created_at', 'ip_address']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'action', 'description']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'metadata')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'ip_address', 'last_activity', 'is_active']
    list_filter = ['is_active', 'last_activity']
    search_fields = ['user__username', 'session_key', 'ip_address']
    autocomplete_fields = ['user']
    readonly_fields = ['session_key', 'last_activity', 'created_at', 'updated_at']