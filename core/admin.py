from django.contrib import admin
from .models import Currency, AcademicYear, Semester, Course, FeeStructure, Notification

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['code', 'name']
    list_editable = ['exchange_rate', 'is_default']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['is_current', 'is_active']
    search_fields = ['name']

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['academic_year', 'is_current', 'is_active']
    search_fields = ['name']
    autocomplete_fields = ['academic_year']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'is_active']
    list_filter = ['credits', 'is_active']
    search_fields = ['code', 'name']
    filter_horizontal = ['prerequisites']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_amount', 'currency', 'installment_count', 'is_active']
    list_filter = ['currency', 'installment_count', 'is_active']
    search_fields = ['name']
    autocomplete_fields = ['currency']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    autocomplete_fields = ['recipient']
    readonly_fields = ['created_at', 'updated_at']