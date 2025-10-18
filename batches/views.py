from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Batch, BatchSchedule, BatchAttendance, BatchGrade
from students.models import Student
from core.models import Course, Semester
import json

@login_required
def batch_list(request):
    """List all batches with filtering and search"""
    batches = Batch.objects.filter(is_active=True).select_related('coordinator').order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        batches = batches.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        batches = batches.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(batches, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Batches',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'batches/batch_list.html', context)

@login_required
def add_batch(request):
    """Add new batch (Admin only)"""
    # Check if user has admin role
    user_role = 'student'  # Default role
    try:
        user_profile = request.user.profile
        user_role = user_profile.role
    except Exception as e:
        # If user is superuser but no profile, set as admin
        if request.user.is_superuser:
            user_role = 'admin'
    
    if user_role != 'admin':
        messages.error(request, 'You do not have permission to add batches.')
        return redirect('batches:batch_list')
    
    from accounts.models import Teacher
    
    context = {
        'title': 'Add Batch',
        'teachers': Teacher.objects.filter(status='active'),
    }
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            status = request.POST.get('status', 'planning')
            coordinator_id = request.POST.get('coordinator') or None
            start_date = request.POST.get('start_date') or None
            end_date = request.POST.get('end_date') or None
            
            # Validate required fields
            if not name:
                messages.error(request, 'Batch name is required.')
                return render(request, 'batches/add_batch.html', context)
            
            if not code:
                messages.error(request, 'Batch code is required.')
                return render(request, 'batches/add_batch.html', context)
            
            # Check if batch code already exists
            if Batch.objects.filter(code=code).exists():
                messages.error(request, f'Batch code "{code}" already exists. Please choose a different code.')
                return render(request, 'batches/add_batch.html', context)
            
            # Create batch with simplified data
            batch = Batch.objects.create(
                name=name,
                code=code,
                status=status,
                coordinator_id=coordinator_id,
                start_date=start_date,
                end_date=end_date,
            )
            
            messages.success(request, f'Batch {batch.name} created successfully!')
            return redirect('batches:batch_detail', batch_id=batch.id)
            
        except Exception as e:
            messages.error(request, f'Error creating batch: {str(e)}')
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Batch creation error: {str(e)}")
    
    return render(request, 'batches/add_batch.html', context)

@login_required
def edit_batch(request, batch_id):
    """Edit batch (Admin only)"""
    # Check if user has admin role
    user_role = 'student'  # Default role
    try:
        user_profile = request.user.profile
        user_role = user_profile.role
    except Exception as e:
        # If user is superuser but no profile, set as admin
        if request.user.is_superuser:
            user_role = 'admin'
    
    if user_role != 'admin':
        messages.error(request, 'You do not have permission to edit batches.')
        return redirect('batches:batch_list')
    
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Update batch information
            batch.name = request.POST.get('name')
            batch.code = request.POST.get('code')
            batch.status = request.POST.get('status', 'planning')
            batch.coordinator_id = request.POST.get('coordinator') or None
            
            # Parse dates
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            
            if start_date_str:
                from datetime import datetime
                batch.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                batch.start_date = None
                
            if end_date_str:
                from datetime import datetime
                batch.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                batch.end_date = None
            
            batch.save()
            
            messages.success(request, f'Batch {batch.name} updated successfully!')
            return redirect('batches:batch_detail', batch_id=batch.id)
            
        except Exception as e:
            messages.error(request, f'Error updating batch: {str(e)}')
    
    from accounts.models import Teacher
    
    context = {
        'title': f'Edit Batch: {batch.name}',
        'batch': batch,
        'teachers': Teacher.objects.filter(is_active=True),
    }
    
    return render(request, 'batches/edit_batch.html', context)

@login_required
def delete_batch(request, batch_id):
    """Delete batch (Admin only)"""
    if not request.user.profile.role == 'admin':
        messages.error(request, 'You do not have permission to delete batches.')
        return redirect('batches:batch_list')
    
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Soft delete - set is_active to False
            batch.is_active = False
            batch.save()
            
            messages.success(request, f'Batch {batch.name} has been deleted successfully!')
            return redirect('batches:batch_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting batch: {str(e)}')
    
    context = {
        'title': f'Delete Batch: {batch.name}',
        'batch': batch,
    }
    
    return render(request, 'batches/delete_batch.html', context)

@login_required
def batch_detail(request, batch_id):
    """Batch detail view"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    # Get batch students
    students = batch.students.filter(is_active=True).select_related('user')
    
    # Get batch schedule
    schedule = batch.schedules.all().select_related('course', 'instructor')
    
    # Get recent attendance
    recent_attendance = BatchAttendance.objects.filter(batch=batch).order_by('-date')[:10]
    
    context = {
        'title': f'Batch - {batch.name}',
        'batch': batch,
        'students': students,
        'schedule': schedule,
        'recent_attendance': recent_attendance,
    }
    
    return render(request, 'batches/batch_detail.html', context)

@login_required
def batch_students(request, batch_id):
    """Batch students view"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    students = batch.students.filter(is_active=True).select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': f'Students - {batch.name}',
        'batch': batch,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'batches/batch_students.html', context)

@login_required
def batch_schedule(request, batch_id):
    """Batch schedule view"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    schedule = batch.schedules.all().select_related('course', 'instructor').order_by('day_of_week', 'start_time')
    
    # Group schedule by day
    schedule_by_day = {}
    for item in schedule:
        day = item.get_day_of_week_display()
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(item)
    
    context = {
        'title': f'Schedule - {batch.name}',
        'batch': batch,
        'schedule_by_day': schedule_by_day,
    }
    
    return render(request, 'batches/batch_schedule.html', context)

@login_required
def batch_attendance(request, batch_id):
    """Batch attendance view"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    # Get attendance records
    attendance_records = BatchAttendance.objects.filter(batch=batch).select_related('student__user', 'course').order_by('-date')
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        attendance_records = attendance_records.filter(date=date_filter)
    
    # Filter by course
    course_filter = request.GET.get('course', '')
    if course_filter:
        attendance_records = attendance_records.filter(course_id=course_filter)
    
    # Pagination
    paginator = Paginator(attendance_records, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': f'Attendance - {batch.name}',
        'batch': batch,
        'page_obj': page_obj,
        'date_filter': date_filter,
        'course_filter': course_filter,
        'courses': batch.courses.all(),
    }
    
    return render(request, 'batches/batch_attendance.html', context)

@login_required
def batch_grades(request, batch_id):
    """Batch grades view"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    # Get grade records
    grades = BatchGrade.objects.filter(batch=batch).select_related('student__user', 'course', 'semester').order_by('-updated_at')
    
    # Filter by course
    course_filter = request.GET.get('course', '')
    if course_filter:
        grades = grades.filter(course_id=course_filter)
    
    # Filter by semester
    semester_filter = request.GET.get('semester', '')
    if semester_filter:
        grades = grades.filter(semester_id=semester_filter)
    
    # Pagination
    paginator = Paginator(grades, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': f'Grades - {batch.name}',
        'batch': batch,
        'page_obj': page_obj,
        'course_filter': course_filter,
        'semester_filter': semester_filter,
        'courses': batch.courses.all(),
        'semesters': Semester.objects.filter(is_active=True),
    }
    
    return render(request, 'batches/batch_grades.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class BatchAPIView(View):
    """Batch API for AJAX requests"""
    
    def get(self, request, batch_id):
        """Get batch data"""
        try:
            batch = Batch.objects.get(id=batch_id, is_active=True)
            
            data = {
                'id': str(batch.id),
                'name': batch.name,
                'code': batch.code,
                'status': batch.status,
                'total_students': batch.total_students,
            }
            
            return JsonResponse(data)
            
        except Batch.DoesNotExist:
            return JsonResponse({'error': 'Batch not found'}, status=404)
    
    def post(self, request, batch_id):
        """Update batch data"""
        try:
            batch = Batch.objects.get(id=batch_id, is_active=True)
            data = json.loads(request.body)
            
            # Update allowed fields
            if 'status' in data:
                batch.status = data['status']
            
            batch.save()
            
            return JsonResponse({'success': True})
            
        except Batch.DoesNotExist:
            return JsonResponse({'error': 'Batch not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)