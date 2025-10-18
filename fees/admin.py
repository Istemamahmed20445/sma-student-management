from django.contrib import admin
from .models import StudentPayment, PaymentTransaction, PaymentImport

@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'total_amount', 'currency', 'get_total_paid', 'get_remaining_amount', 'status', 'created_at']
    list_filter = ['currency', 'payment_method', 'status', 'created_at']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name']
    autocomplete_fields = ['student', 'batch', 'currency', 'created_by']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('student', 'batch', 'total_amount', 'currency', 'payment_method', 'status')
        }),
        ('Details', {
            'fields': ('notes', 'created_by')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_paid(self, obj):
        return f"{obj.get_total_paid()} {obj.currency.code}"
    get_total_paid.short_description = 'Total Paid'
    
    def get_remaining_amount(self, obj):
        return f"{obj.get_remaining_amount()} {obj.currency.code}"
    get_remaining_amount.short_description = 'Remaining'

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment', 'amount', 'payment_method', 'payment_date', 'processed_by']
    list_filter = ['payment_method', 'payment_date', 'payment__batch']
    search_fields = ['receipt_number', 'payment__student__student_id']
    autocomplete_fields = ['payment', 'processed_by']
    readonly_fields = ['receipt_number', 'payment_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('payment', 'amount', 'payment_method', 'receipt_number')
        }),
        ('Payment Details', {
            'fields': ('payment_date', 'notes', 'processed_by')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentImport)
class PaymentImportAdmin(admin.ModelAdmin):
    list_display = ['batch', 'file_name', 'imported_by', 'import_date', 'status', 'successful_imports', 'failed_imports']
    list_filter = ['status', 'import_date', 'batch']
    search_fields = ['file_name', 'batch__name']
    autocomplete_fields = ['batch', 'imported_by']
    readonly_fields = ['import_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Import Information', {
            'fields': ('batch', 'file_name', 'imported_by', 'status')
        }),
        ('Statistics', {
            'fields': ('total_rows', 'successful_imports', 'failed_imports')
        }),
        ('Error Log', {
            'fields': ('error_log',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('import_date', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )