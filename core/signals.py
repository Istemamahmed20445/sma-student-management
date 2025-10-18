from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .firebase_utils import student_firebase_manager
from students.models import Student, StudentApplication
from fees.models import StudentPayment, PaymentTransaction
from batches.models import BatchGrade, BatchAttendance
from accounts.models import UserProfile

@receiver(post_save, sender=Student)
def create_student_payment_record(sender, instance, created, **kwargs):
    """Automatically create a payment record when a student is added to a batch"""
    try:
        if created and instance.batch:
            # Check if payment record already exists
            existing_payment = StudentPayment.objects.filter(
                student=instance,
                batch=instance.batch
            ).exists()
            
            if not existing_payment:
                # Get default currency
                from core.models import Currency
                default_currency = Currency.objects.filter(is_default=True).first()
                if not default_currency:
                    default_currency = Currency.objects.first()
                
                if default_currency:  # Only create if we have a currency
                    # Create payment record with default amount (can be updated later)
                    StudentPayment.objects.create(
                        student=instance,
                        batch=instance.batch,
                        total_amount=0,  # Default amount, admin can update
                        currency=default_currency,
                        payment_method='installments',
                        created_by=None,  # No user profile for auto-created records
                        notes=f'Auto-created payment record for {instance.user.get_full_name()}'
                    )
                    print(f"Auto-created payment record for student {instance.student_id}")
    except Exception as e:
        print(f"Error creating payment record for student {instance.student_id}: {e}")

@receiver(post_save, sender=Student)
def sync_student_to_firebase(sender, instance, created, **kwargs):
    """Sync student data to Firebase when saved"""
    try:
        if created:
            student_firebase_manager.sync_student_to_firestore(instance)
        else:
            # Update existing document
            data = {
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
                'date_of_birth': instance.date_of_birth.isoformat() if instance.date_of_birth else None,
                'gender': instance.gender,
                'nationality': instance.nationality,
                'phone': instance.phone,
                'address': instance.address,
                'city': instance.city,
                'state': instance.state,
                'postal_code': instance.postal_code,
                'country': instance.country,
                'department_id': str(instance.department.id),
                'department_name': instance.department.name,
                'batch_id': str(instance.batch.id) if instance.batch else None,
                'batch_name': instance.batch.name if instance.batch else None,
                'status': instance.status,
                'emergency_contact_name': instance.emergency_contact_name,
                'emergency_contact_phone': instance.emergency_contact_phone,
                'emergency_contact_relationship': instance.emergency_contact_relationship,
                'is_active': instance.is_active,
            }
            student_firebase_manager.update_document('students', instance.student_id, data)
    except Exception as e:
        print(f"Error syncing student to Firebase: {e}")

@receiver(post_delete, sender=Student)
def delete_student_from_firebase(sender, instance, **kwargs):
    """Delete student data from Firebase when deleted"""
    try:
        student_firebase_manager.delete_document('students', instance.student_id)
    except Exception as e:
        print(f"Error deleting student from Firebase: {e}")

@receiver(post_save, sender=PaymentTransaction)
def sync_payment_to_firebase(sender, instance, created, **kwargs):
    """Sync payment transaction data to Firebase when saved"""
    try:
        if created:
            student_firebase_manager.sync_payment_to_firestore(instance)
        else:
            # Update existing document
            data = {
                'amount': float(instance.amount),
                'payment_method': instance.payment_method,
                'payment_date': instance.payment_date.isoformat(),
                'receipt_number': instance.receipt_number,
                'notes': instance.notes,
                'is_active': instance.is_active,
            }
            student_firebase_manager.update_document('payments', instance.receipt_number, data)
    except Exception as e:
        print(f"Error syncing payment transaction to Firebase: {e}")

@receiver(post_save, sender=UserProfile)
def sync_user_profile_to_firebase(sender, instance, created, **kwargs):
    """Sync user profile data to Firebase when saved"""
    try:
        data = {
            'user_id': str(instance.user.id),
            'username': instance.user.username,
            'email': instance.user.email,
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'role': instance.role,
            'phone': instance.phone,
            'address': instance.address,
            'date_of_birth': instance.date_of_birth.isoformat() if instance.date_of_birth else None,
            'bio': instance.bio,
            'website': instance.website,
            'language': instance.language,
            'timezone': instance.timezone,
            'theme': instance.theme,
            'is_verified': instance.is_verified,
            'is_active': instance.is_active,
        }
        
        if created:
            student_firebase_manager.create_document('user_profiles', data, str(instance.user.id))
        else:
            student_firebase_manager.update_document('user_profiles', str(instance.user.id), data)
    except Exception as e:
        print(f"Error syncing user profile to Firebase: {e}")

@receiver(post_save, sender=BatchGrade)
def sync_grade_to_firebase(sender, instance, created, **kwargs):
    """Sync grade data to Firebase when saved"""
    try:
        data = {
            'grade_id': str(instance.id),
            'student_id': instance.student.student_id,
            'student_user_id': str(instance.student.user.id),
            'batch_id': str(instance.batch.id),
            'course_id': str(instance.course.id),
            'course_name': instance.course.name,
            'assignment_score': float(instance.assignment_score),
            'quiz_score': float(instance.quiz_score),
            'midterm_score': float(instance.midterm_score),
            'final_score': float(instance.final_score),
            'total_score': float(instance.total_score),
            'letter_grade': instance.letter_grade,
            'semester_id': str(instance.semester.id),
            'semester_name': instance.semester.name,
            'instructor_id': str(instance.instructor.id) if instance.instructor else None,
            'notes': instance.notes,
            'is_active': instance.is_active,
        }
        
        if created:
            student_firebase_manager.create_document('grades', data, str(instance.id))
        else:
            student_firebase_manager.update_document('grades', str(instance.id), data)
    except Exception as e:
        print(f"Error syncing grade to Firebase: {e}")

@receiver(post_save, sender=BatchAttendance)
def sync_attendance_to_firebase(sender, instance, created, **kwargs):
    """Sync attendance data to Firebase when saved"""
    try:
        data = {
            'attendance_id': str(instance.id),
            'student_id': instance.student.student_id,
            'student_user_id': str(instance.student.user.id),
            'batch_id': str(instance.batch.id),
            'course_id': str(instance.course.id),
            'course_name': instance.course.name,
            'date': instance.date.isoformat(),
            'status': instance.status,
            'notes': instance.notes,
            'is_active': instance.is_active,
        }
        
        if created:
            student_firebase_manager.create_document('attendance', data, str(instance.id))
        else:
            student_firebase_manager.update_document('attendance', str(instance.id), data)
    except Exception as e:
        print(f"Error syncing attendance to Firebase: {e}")
