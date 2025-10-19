from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Student, StudentApplication, StudentDocument
from core.models import Currency
from batches.models import Batch
import json

@login_required
def student_list(request):
    """List all students with filtering and search"""
    students = Student.objects.filter(is_active=True).select_related('user', 'batch').order_by('student_id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Filter by batch
    batch_filter = request.GET.get('batch', '')
    if batch_filter:
        students = students.filter(batch_id=batch_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        students = students.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get selected batch for display
    selected_batch = None
    if batch_filter:
        try:
            selected_batch = Batch.objects.get(id=batch_filter, is_active=True)
        except Batch.DoesNotExist:
            selected_batch = None
    
    context = {
        'title': 'Students',
        'page_obj': page_obj,
        'batches': Batch.objects.filter(is_active=True),
        'search_query': search_query,
        'batch_filter': batch_filter,
        'status_filter': status_filter,
        'total_students': students.count(),
        'selected_batch': selected_batch,
    }
    
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, student_id):
    """Student detail view"""
    try:
        student = Student.objects.get(student_id=student_id, is_active=True)
        
        # Get student's grades
        from batches.models import BatchGrade, BatchAttendance
        from fees.models import StudentPayment, PaymentTransaction
        
        grades = BatchGrade.objects.filter(student=student).order_by('-semester__start_date')
        attendance = BatchAttendance.objects.filter(student=student).order_by('-date')[:10]
        
        # Get payment information
        payments = StudentPayment.objects.filter(student=student).order_by('-created_at')
        recent_transactions = PaymentTransaction.objects.filter(
            payment__student=student
        ).order_by('-payment_date')[:10]
        
        # Calculate total payment information
        total_paid = sum(payment.get_total_paid() for payment in payments)
        total_amount = sum(payment.total_amount for payment in payments)
        
        # Create total payment object
        class TotalPayment:
            def __init__(self, total_amount, total_paid, currency, status):
                self.total_amount = total_amount or 0
                self.total_paid = total_paid or 0
                self.currency = currency
                self.status = status
                self.remaining = self.total_amount - self.total_paid
            
            def get_status_display(self):
                if self.total_paid >= self.total_amount:
                    return 'Completed'
                elif self.total_paid > 0:
                    return 'Partial'
                else:
                    return 'Pending'
        
        total_payment = None
        if payments.exists():
            latest_payment = payments.first()
            total_payment = TotalPayment(
                total_amount,
                total_paid,
                latest_payment.currency,
                'completed' if total_paid >= total_amount else 'partial'
            )
        
        context = {
            'title': f'Student - {student.user.get_full_name()}',
            'student': student,
            'grades': grades,
            'attendance': attendance,
            'payments': payments,
            'recent_transactions': recent_transactions,
            'total_payment': total_payment,
        }
        
        return render(request, 'students/student_detail.html', context)
    except Student.DoesNotExist:
        return redirect('students:student_not_found')

def student_not_found(request):
    """Student not found page"""
    context = {
        'title': 'Student Not Found - Shahriar\'s Medical Academy',
    }
    return render(request, 'students/student_not_found.html', context)

@login_required
def student_application_list(request):
    """List student applications"""
    applications = StudentApplication.objects.filter(is_active=True).select_related('preferred_batch', 'preferred_currency').order_by('-application_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Department filtering removed
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Student Applications',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'students/application_list.html', context)

@login_required
def student_application_detail(request, application_id):
    """Student application detail view"""
    application = get_object_or_404(StudentApplication, id=application_id, is_active=True)
    
    context = {
        'title': f'Application - {application.get_full_name()}',
        'application': application,
    }
    
    return render(request, 'students/application_detail.html', context)

@login_required
@require_http_methods(["POST"])
def update_application_status(request, application_id):
    """Update application status"""
    application = get_object_or_404(StudentApplication, id=application_id)
    
    new_status = request.POST.get('status')
    review_notes = request.POST.get('review_notes', '')
    
    if new_status in ['accepted', 'rejected', 'waitlisted']:
        application.status = new_status
        application.reviewed_by = request.user
        application.review_notes = review_notes
        application.save()
        
        messages.success(request, f'Application status updated to {new_status.title()}')
    else:
        messages.error(request, 'Invalid status')
    
    return redirect('students:application_detail', application_id=application_id)

def student_application_form(request):
    """Student application form"""
    if request.method == 'POST':
        # Handle form submission
        try:
            # Create application
            application = StudentApplication.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                nationality=request.POST.get('nationality'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                country=request.POST.get('country'),
                preferred_batch_id=request.POST.get('preferred_batch') or None,
                preferred_currency_id=request.POST.get('preferred_currency'),
                installment_preference=int(request.POST.get('installment_preference', 2)),
                previous_education=request.POST.get('previous_education', ''),
                work_experience=request.POST.get('work_experience', ''),
                motivation_letter=request.POST.get('motivation_letter', ''),
                emergency_contact_name=request.POST.get('emergency_contact_name'),
                emergency_contact_phone=request.POST.get('emergency_contact_phone'),
                emergency_contact_relationship=request.POST.get('emergency_contact_relationship'),
            )
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('students:application_success', application_id=application.id)
            
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
    
    context = {
        'title': 'Student Application',
        'batches': Batch.objects.filter(is_active=True, status='active'),
        'currencies': Currency.objects.filter(is_active=True),
    }
    
    return render(request, 'students/application_form.html', context)

def application_success(request, application_id):
    """Application submission success page"""
    application = get_object_or_404(StudentApplication, id=application_id)
    
    context = {
        'title': 'Application Submitted',
        'application': application,
    }
    
    return render(request, 'students/application_success.html', context)

@login_required
def add_student(request):
    """Add new student (Admin only)"""
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
        messages.error(request, 'You do not have permission to add students.')
        return redirect('students:student_list')
    
    if request.method == 'POST':
        try:
            # Generate unique username if not provided or if it already exists
            username = request.POST.get('username')
            if not username:
                # Generate username from first and last name
                first_name = request.POST.get('first_name', '').lower().replace(' ', '')
                last_name = request.POST.get('last_name', '').lower().replace(' ', '')
                username = f"{first_name}.{last_name}"
            
            # Ensure username is unique
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user first
            email = request.POST.get('email', '').strip()
            if not email:
                email = None  # Set to None if empty to avoid unique constraint issues
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=request.POST.get('password', 'student123'),  # Default password
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Parse enrollment date
            from datetime import datetime
            enrollment_date_str = request.POST.get('enrollment_date')
            enrollment_date = datetime.strptime(enrollment_date_str, '%Y-%m-%d').date() if enrollment_date_str else None
            
            # Create student profile
            student = Student.objects.create(
                user=user,
                phone=request.POST.get('phone', ''),
                batch_id=request.POST.get('batch') or None,
                enrollment_date=enrollment_date,
                note=request.POST.get('note', ''),
            )
            
            # Handle payment information - Create simple payment record
            total_amount = request.POST.get('total_amount')
            first_installment = request.POST.get('first_installment')
            currency_id = request.POST.get('currency')
            payment_method = request.POST.get('payment_method', 'installments')
            
            if total_amount and float(total_amount) > 0:
                from core.models import Currency
                from fees.models import StudentPayment, PaymentTransaction
                from accounts.models import UserProfile
                
                try:
                    # Ensure the current user has a profile
                    if not hasattr(request.user, 'profile'):
                        UserProfile.objects.create(
                            user=request.user,
                            role='admin',  # Admin creating the student
                            phone='',
                            address='',
                            bio='',
                            language='en',
                            timezone='UTC',
                            theme='light',
                            is_verified=False
                        )
                    
                    # Get selected currency
                    currency = Currency.objects.get(id=currency_id) if currency_id else Currency.objects.filter(is_default=True).first()
                    if not currency:
                        currency = Currency.objects.first()
                    
                    batch = student.batch
                    total_amount = float(total_amount)
                    first_installment = float(first_installment) if first_installment else 0
                    
                    # Get or create payment record
                    payment, created = StudentPayment.objects.get_or_create(
                        student=student,
                        batch=batch,
                        defaults={
                            'total_amount': total_amount,
                            'currency': currency,
                            'payment_method': payment_method,
                            'created_by': request.user.profile,
                            'notes': f'Payment for student enrollment'
                        }
                    )
                    
                    # If payment already exists (created by signal), update it
                    if not created:
                        payment.total_amount = total_amount
                        payment.currency = currency
                        payment.payment_method = payment_method
                        payment.created_by = request.user.profile
                        payment.notes = f'Payment for student enrollment'
                        payment.save()
                    
                    # If first installment is provided, create a transaction
                    if first_installment > 0:
                        PaymentTransaction.objects.create(
                            payment=payment,
                            amount=first_installment,
                            payment_method='cash',
                            notes=f'First installment payment',
                            processed_by=request.user.profile
                        )
                    
                    messages.success(request, f'Student {student.user.get_full_name()} added successfully with payment record!')
                    
                except Exception as e:
                    # If payment creation fails, still create the student but log the error
                    messages.warning(request, f'Student created successfully, but payment setup failed: {str(e)}')
            else:
                messages.success(request, f'Student {student.user.get_full_name()} added successfully!')
            return redirect('students:student_detail', student_id=student.student_id)
            
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
    
    from core.models import Currency
    
    context = {
        'title': 'Add Student',
        'batches': Batch.objects.filter(is_active=True),
        'currencies': Currency.objects.filter(is_active=True),
    }
    
    return render(request, 'students/add_student.html', context)

@login_required
def edit_student(request, student_id):
    """Edit student (Admin only)"""
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
        messages.error(request, 'You do not have permission to edit students.')
        return redirect('students:student_list')
    
    student = get_object_or_404(Student, student_id=student_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Check if this is a status update or installment creation
            if request.POST.get('update_status') == 'true':
                # Handle payment status update
                payment_status = request.POST.get('payment_status')
                if payment_status == 'complete':
                    # Mark all pending installments as paid
                    from fees.models import FeeInstallment
                    pending_installments = FeeInstallment.objects.filter(
                        student=student,
                        status='pending'
                    )
                    for installment in pending_installments:
                        installment.status = 'paid'
                        installment.payment_date = timezone.now().date()
                        installment.save()
                    messages.success(request, f'All pending installments for {student.get_full_name()} marked as complete!')
                else:
                    # Mark all paid installments as pending (remaining)
                    from fees.models import FeeInstallment
                    paid_installments = FeeInstallment.objects.filter(
                        student=student,
                        status='paid'
                    )
                    for installment in paid_installments:
                        installment.status = 'pending'
                        installment.payment_date = None
                        installment.save()
                    messages.success(request, f'Payment status for {student.get_full_name()} updated to remaining!')
                
                return redirect('students:edit_student', student_id=student.student_id)
            
            elif request.POST.get('add_installments') == 'true':
                # Handle installment creation
                installment_amount = request.POST.get('installment_amount')
                installment_count = request.POST.get('installment_count')
                currency_id = request.POST.get('installment_currency')
                
                if installment_amount and installment_count:
                    from fees.models import FeeInstallment
                    from core.models import Currency
                    from datetime import datetime, timedelta
                    
                    try:
                        currency = Currency.objects.get(id=currency_id)
                        amount = float(installment_amount)
                        count = int(installment_count)
                        
                        # Create installments
                        for i in range(count):
                            # Calculate due date (30 days apart)
                            due_date = timezone.now().date() + timedelta(days=30 * (i + 1))
                            
                            FeeInstallment.objects.create(
                                student=student,
                                batch=student.batch,
                                amount=amount,
                                currency=currency,
                                due_date=due_date,
                                status='pending'
                            )
                        
                        messages.success(request, f'Successfully created {count} installments of {amount} {currency.code} each for {student.get_full_name()}!')
                        
                    except (ValueError, Currency.DoesNotExist) as e:
                        messages.error(request, f'Error creating installments: {str(e)}')
                else:
                    messages.error(request, 'Please provide both amount and count for installments.')
                
                return redirect('students:edit_student', student_id=student.student_id)
            
            else:
                # Regular form update
                # Update user information
                student.user.first_name = request.POST.get('first_name')
                student.user.last_name = request.POST.get('last_name')
                student.user.email = request.POST.get('email')
                student.user.save()
                
                # Update student information
                student.phone = request.POST.get('phone', '')
                student.batch_id = request.POST.get('batch') or None
                student.note = request.POST.get('note', '')  # Add note field
                
                # Parse enrollment date
                enrollment_date_str = request.POST.get('enrollment_date')
                if enrollment_date_str:
                    from datetime import datetime
                    student.enrollment_date = datetime.strptime(enrollment_date_str, '%Y-%m-%d').date()
                
                student.save()
                
                messages.success(request, f'Student {student.get_full_name()} updated successfully!')
                return redirect('students:student_detail', student_id=student.student_id)
            
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    from core.models import Currency
    
    context = {
        'title': f'Edit Student: {student.get_full_name()}',
        'student': student,
        'batches': Batch.objects.filter(is_active=True),
        'currencies': Currency.objects.filter(is_active=True),
    }
    
    return render(request, 'students/edit_student.html', context)

@login_required
def delete_student(request, student_id):
    """Delete student (Admin only)"""
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
        messages.error(request, 'You do not have permission to delete students.')
        return redirect('students:student_list')
    
    student = get_object_or_404(Student, student_id=student_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Soft delete - set is_active to False
            student.is_active = False
            student.user.is_active = False
            student.save()
            student.user.save()
            
            messages.success(request, f'Student {student.get_full_name()} has been deleted successfully!')
            return redirect('students:student_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting student: {str(e)}')
    
    context = {
        'title': f'Delete Student: {student.get_full_name()}',
        'student': student,
    }
    
    return render(request, 'students/delete_student.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class StudentAPIView(View):
    """Student API for AJAX requests"""
    
    def get(self, request, student_id):
        """Get student data"""
        try:
            student = Student.objects.get(student_id=student_id, is_active=True)
            
            data = {
                'id': str(student.id),
                'student_id': student.student_id,
                'name': student.get_full_name(),
                'email': student.user.email,
                'department': student.department.name,
                'batch': student.batch.name if student.batch else None,
                'status': student.status,
                'enrollment_date': student.enrollment_date.isoformat(),
            }
            
            return JsonResponse(data)
            
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    
    def post(self, request, student_id):
        """Update student data"""
        try:
            student = Student.objects.get(student_id=student_id, is_active=True)
            data = json.loads(request.body)
            
            # Update allowed fields
            if 'status' in data:
                student.status = data['status']
            
            student.save()
            
            return JsonResponse({'success': True})
            
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def check_duplicate_student(request):
    """Check for existing students by name or phone"""
    try:
        data = json.loads(request.body)
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        
        duplicates = []
        
        # Check by name - improved case-insensitive matching
        if first_name and last_name:
            # Create multiple search patterns for better matching
            search_patterns = [
                Q(user__first_name__iexact=first_name) & Q(user__last_name__iexact=last_name),
                Q(user__first_name__icontains=first_name) & Q(user__last_name__icontains=last_name),
                Q(user__first_name__iexact=last_name) & Q(user__last_name__iexact=first_name),
                Q(user__first_name__icontains=last_name) & Q(user__last_name__icontains=first_name),
            ]
            
            # Combine all patterns with OR
            combined_query = search_patterns[0]
            for pattern in search_patterns[1:]:
                combined_query |= pattern
            
            name_matches = Student.objects.filter(
                combined_query,
                is_active=True
            ).select_related('user', 'batch')
            
            for student in name_matches:
                duplicates.append({
                    'id': student.student_id,
                    'name': student.user.get_full_name(),
                    'email': student.user.email,
                    'phone': student.phone,
                    'batch': student.batch.name if student.batch else 'Not Assigned',
                    'status': student.get_status_display(),
                    'match_type': 'name'
                })
        
        # Check by phone
        if phone:
            phone_matches = Student.objects.filter(
                phone__icontains=phone,
                is_active=True
            ).select_related('user', 'batch')
            
            for student in phone_matches:
                # Avoid duplicates if already found by name
                if not any(d['id'] == student.student_id for d in duplicates):
                    duplicates.append({
                        'id': student.student_id,
                        'name': student.user.get_full_name(),
                        'email': student.user.email,
                        'phone': student.phone,
                        'batch': student.batch.name if student.batch else 'Not Assigned',
                        'status': student.get_status_display(),
                        'match_type': 'phone'
                    })
        
        return JsonResponse({
            'duplicates': duplicates,
            'count': len(duplicates)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)