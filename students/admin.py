from django.contrib import admin
from .models import Student, StudentDocument, StudentApplication

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'batch', 'status', 'enrollment_date']
    list_filter = ['batch', 'status', 'gender', 'enrollment_date']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    autocomplete_fields = ['user', 'batch']
    readonly_fields = ['student_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'student_id', 'date_of_birth', 'gender', 'nationality', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Academic Information', {
            'fields': ('batch', 'enrollment_date', 'status')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'title', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified', 'created_at']
    search_fields = ['student__student_id', 'title', 'description']
    autocomplete_fields = ['student', 'verified_by']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'preferred_batch', 'status', 'application_date']
    list_filter = ['preferred_batch', 'status', 'gender', 'application_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    autocomplete_fields = ['preferred_batch', 'preferred_currency', 'reviewed_by']
    readonly_fields = ['application_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Academic Information', {
            'fields': ('preferred_batch', 'previous_education', 'work_experience', 'motivation_letter')
        }),
        ('Fee Information', {
            'fields': ('preferred_currency', 'installment_preference')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Review Information', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('System Information', {
            'fields': ('application_date', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'