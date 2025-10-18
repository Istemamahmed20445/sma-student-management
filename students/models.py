from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from core.models import BaseModel, Currency
from batches.models import Batch
import uuid

class Student(BaseModel):
    """Student model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)  # Auto-generated
    
    # Personal Information (Optional)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Academic Information
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    enrollment_date = models.DateField()
    
    # Academic Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Emergency Contact (Optional)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Profile Image
    profile_image = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    
    # Special Notes (Optional)
    note = models.TextField(blank=True, help_text="Special notes about the student")
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate student ID based on enrollment year or current year
            if self.enrollment_date:
                year = self.enrollment_date.year
            else:
                from datetime import date
                year = date.today().year
            
            last_student = Student.objects.filter(
                enrollment_date__year=year
            ).order_by('-student_id').first()
            
            if last_student:
                last_num = int(last_student.student_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.student_id = f"STU-{year}-{new_num:04d}"
        
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_current_gpa(self):
        """Calculate current GPA"""
        grades = self.grades.filter(semester__is_current=True)
        if not grades:
            return 0.0
        
        total_points = 0
        total_credits = 0
        
        for grade in grades:
            credits = grade.course.credits
            points = self.grade_to_points(grade.letter_grade)
            total_points += points * credits
            total_credits += credits
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def grade_to_points(self, letter_grade):
        """Convert letter grade to GPA points"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        return grade_points.get(letter_grade, 0.0)

class StudentDocument(BaseModel):
    """Student document model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=[
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('birth_certificate', 'Birth Certificate'),
        ('academic_transcript', 'Academic Transcript'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ])
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_documents/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.title}"

class StudentApplication(BaseModel):
    """Student application model"""
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    nationality = models.CharField(max_length=100)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Academic Information
    preferred_batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Application Details
    application_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Fee Information
    preferred_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    installment_preference = models.PositiveIntegerField(default=2, choices=[(2, '2 Installments'), (3, '3 Installments')])
    
    # Additional Information
    previous_education = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    motivation_letter = models.TextField(blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=17)
    emergency_contact_relationship = models.CharField(max_length=50)
    
    # Review Information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - Application"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"