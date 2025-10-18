from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'facebook_url', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'email', 'phone', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'facebook_url')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new contact
            obj.created_by = request.user
        super().save_model(request, obj, form, change)