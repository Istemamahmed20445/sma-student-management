from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from .models import Currency, AcademicYear, Semester
from .firebase_config import CurrencyConverter, initialize_firebase, get_firestore_client
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Home page view - Updated for admin role fix deployment"""
    try:
        context = {
            'title': 'Student Management System',
            'currencies': Currency.objects.filter(is_active=True),
        }
        return render(request, 'core/home.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def test_view(request):
    """Simple test view"""
    return HttpResponse("Student Management System is working!")

def debug_view(request):
    """Debug view to check system status"""
    debug_info = {
        'django_working': True,
        'user_count': User.objects.count(),
        'firebase_status': 'unknown',
        'firestore_status': 'unknown',
    }
    
    try:
        # Test Firebase initialization
        app = initialize_firebase()
        if app:
            debug_info['firebase_status'] = 'initialized'
        else:
            debug_info['firebase_status'] = 'failed'
    except Exception as e:
        debug_info['firebase_status'] = f'error: {str(e)}'
    
    try:
        # Test Firestore
        db = get_firestore_client()
        if db:
            debug_info['firestore_status'] = 'connected'
        else:
            debug_info['firestore_status'] = 'failed'
    except Exception as e:
        debug_info['firestore_status'] = f'error: {str(e)}'
    
    return JsonResponse(debug_info)

def user_debug_view(request):
    """Debug view to check user and role information"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'})
    
    user = request.user
    debug_info = {
        'username': user.username,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'profile_exists': False,
        'profile_role': None,
        'final_role': 'student',
    }
    
    try:
        profile = user.profile
        debug_info['profile_exists'] = True
        debug_info['profile_role'] = profile.role
        debug_info['final_role'] = profile.role
    except Exception as e:
        debug_info['profile_error'] = str(e)
        # If user is superuser but no profile, set as admin
        if user.is_superuser:
            debug_info['final_role'] = 'admin'
    
    return JsonResponse(debug_info)

@login_required
def dashboard(request):
    """Main dashboard view - Fixed admin role detection"""
    try:
        user = request.user
        
        # Get user role from profile - FIXED ADMIN ROLE DETECTION
        role = 'student'  # Default role
        try:
            user_profile = user.profile
            role = user_profile.role
        except Exception as e:
            logger.error(f"Profile access error for user {user.username}: {str(e)}")
            # If user is superuser but no profile, set as admin
            if user.is_superuser:
                role = 'admin'
        
        context = {
            'title': 'Dashboard',
            'user': user,
            'role': role,
        }
        
        # Role-specific dashboard data
        try:
            if role == 'admin':
                context.update(get_admin_dashboard_data())
            elif role == 'teacher':
                context.update(get_teacher_dashboard_data(user))
            elif role == 'student':
                context.update(get_student_dashboard_data(user))
        except Exception as e:
            logger.error(f"Dashboard data error: {str(e)}")
            context['error'] = 'Unable to load dashboard data'
        
        return render(request, 'core/dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard view error: {str(e)}")
        return HttpResponse(f"Dashboard error: {str(e)}", status=500)

def get_admin_dashboard_data():
    """Get admin dashboard statistics"""
    from students.models import Student, StudentApplication
    from batches.models import Batch
    from fees.models import StudentPayment

    return {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_applications': StudentApplication.objects.filter(is_active=True).count(),
        'total_batches': Batch.objects.filter(is_active=True).count(),
        'pending_applications': StudentApplication.objects.filter(status='pending').count(),
        'recent_payments': StudentPayment.objects.filter(status='completed').order_by('-created_at')[:5],
    }

def get_teacher_dashboard_data(user):
    """Get teacher dashboard data"""
    from batches.models import Batch, BatchGrade
    
    try:
        teacher = user.teacher_profile
        batches = Batch.objects.filter(coordinator=user, is_active=True)
        recent_grades = BatchGrade.objects.filter(instructor=user).order_by('-updated_at')[:5]
        
        return {
            'my_batches': batches,
            'recent_grades': recent_grades,
            'total_students': sum(batch.current_enrollment for batch in batches),
        }
    except:
        return {
            'my_batches': [],
            'recent_grades': [],
            'total_students': 0,
        }

def get_student_dashboard_data(user):
    """Get student dashboard data"""
    from students.models import Student
    from batches.models import BatchGrade, BatchAttendance
    from fees.models import StudentPayment, PaymentTransaction
    from django.utils import timezone
    
    try:
        student = user.student_profile
        recent_grades = BatchGrade.objects.filter(student=student).order_by('-updated_at')[:5]
        recent_attendance = BatchAttendance.objects.filter(student=student).order_by('-date')[:5]
        
        # Get payment information
        payments = StudentPayment.objects.filter(student=student)
        recent_transactions = PaymentTransaction.objects.filter(
            payment__student=student
        ).order_by('-payment_date')[:5]
        
        # Calculate payment status
        total_paid = sum(payment.get_total_paid() for payment in payments)
        total_due = sum(float(payment.total_amount) for payment in payments)
        remaining_amount = total_due - total_paid
        
        return {
            'student': student,
            'recent_grades': recent_grades,
            'recent_attendance': recent_attendance,
            'recent_transactions': recent_transactions,
            'payments': payments,
            'total_paid': total_paid,
            'total_due': total_due,
            'remaining_amount': remaining_amount,
            'current_gpa': getattr(student, 'get_current_gpa', lambda: 0.0)(),
        }
    except Exception as e:
        return {
            'student': None,
            'recent_grades': [],
            'recent_attendance': [],
            'recent_transactions': [],
            'payments': [],
            'total_paid': 0,
            'total_due': 0,
            'remaining_amount': 0,
            'current_gpa': 0.0,
            'error': str(e),
        }

@method_decorator(csrf_exempt, name='dispatch')
class CurrencyConverterView(View):
    """Currency conversion API view"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))
            from_currency = data.get('from_currency', 'USD')
            to_currency = data.get('to_currency', 'USD')
            
            converted_amount = CurrencyConverter.convert_currency(
                amount, from_currency, to_currency
            )
            
            return JsonResponse({
                'success': True,
                'original_amount': amount,
                'converted_amount': converted_amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'formatted_amount': CurrencyConverter.format_currency(converted_amount, to_currency)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

def currency_rates(request):
    """Get current currency exchange rates"""
    rates = CurrencyConverter.get_exchange_rates()
    return JsonResponse(rates)

@login_required
def notifications(request):
    """User notifications view"""
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')
    
    context = {
        'title': 'Notifications',
        'notifications': notifications,
    }
    
    return render(request, 'core/notifications.html', context)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=404)

@login_required
def role_test(request):
    """Simple role test view"""
    user = request.user
    
    # Get user role
    role = 'student'  # Default role
    try:
        user_profile = user.profile
        role = user_profile.role
    except Exception as e:
        if user.is_superuser:
            role = 'admin'
    
    context = {
        'username': user.username,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'role': role,
        'profile_exists': hasattr(user, 'profile'),
        'profile_role': user.profile.role if hasattr(user, 'profile') else 'No profile',
    }
    
    return render(request, 'core/role_test.html', context)