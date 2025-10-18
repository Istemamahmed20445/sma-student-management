from django.contrib import admin
from .models import Batch, BatchSchedule, BatchAttendance, BatchGrade

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'academic_year', 'status', 'total_students']
    list_filter = ['academic_year', 'status', 'start_date']
    search_fields = ['name', 'code']
    autocomplete_fields = ['academic_year', 'semester', 'coordinator', 'fee_structure']
    readonly_fields = ['total_students', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'academic_year', 'semester')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Students', {
            'fields': ('total_students',)
        }),
        ('Academic Details', {
            'fields': ('coordinator', 'courses', 'fee_structure')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['courses']

@admin.register(BatchSchedule)
class BatchScheduleAdmin(admin.ModelAdmin):
    list_display = ['batch', 'course', 'instructor', 'day_of_week', 'start_time', 'end_time', 'room']
    list_filter = ['batch', 'course', 'day_of_week', 'instructor']
    search_fields = ['batch__name', 'course__name', 'room']
    autocomplete_fields = ['batch', 'course', 'instructor']

@admin.register(BatchAttendance)
class BatchAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'course', 'date', 'status']
    list_filter = ['batch', 'course', 'status', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__student_id']
    autocomplete_fields = ['batch', 'student', 'course']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(BatchGrade)
class BatchGradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'course', 'total_score', 'letter_grade', 'semester']
    list_filter = ['batch', 'course', 'semester', 'letter_grade']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__student_id']
    autocomplete_fields = ['batch', 'student', 'course', 'semester', 'instructor']
    readonly_fields = ['total_score', 'letter_grade', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'batch', 'course', 'semester', 'instructor')
        }),
        ('Scores', {
            'fields': ('assignment_score', 'quiz_score', 'midterm_score', 'final_score')
        }),
        ('Weights', {
            'fields': ('assignment_weight', 'quiz_weight', 'midterm_weight', 'final_weight')
        }),
        ('Results', {
            'fields': ('total_score', 'letter_grade', 'notes')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )