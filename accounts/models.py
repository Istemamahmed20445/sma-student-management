from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel
import uuid

class UserProfile(BaseModel):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Role-based information
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Personal Information
    phone = models.CharField(max_length=17, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    
    # Specialization (for teachers and staff)
    specialization = models.CharField(max_length=200, blank=True)
    
    # Additional Information
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ], default='light')
    
    # Status
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_staff(self):
        return self.role == 'staff'

class Teacher(BaseModel):
    """Teacher model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    
    # Professional Information
    designation = models.CharField(max_length=100)  # Professor, Assistant Professor, etc.
    specialization = models.CharField(max_length=200, blank=True)
    
    # Employment Details
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('visiting', 'Visiting'),
    ], default='full_time')
    
    # Academic Qualifications
    qualifications = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    
    # Contact Information
    office_room = models.CharField(max_length=20, blank=True)
    office_hours = models.TextField(blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('retired', 'Retired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Generate employee ID
            year = self.hire_date.year
            last_teacher = Teacher.objects.filter(
                hire_date__year=year
            ).order_by('-employee_id').first()
            
            if last_teacher:
                last_num = int(last_teacher.employee_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.employee_id = f"TCH-{year}-{new_num:04d}"
        
        super().save(*args, **kwargs)

class Parent(BaseModel):
    """Parent model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    
    # Relationship to student
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    
    # Contact Information
    phone = models.CharField(max_length=17)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=100, blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Emergency Contact
    is_emergency_contact = models.BooleanField(default=True)
    emergency_priority = models.PositiveIntegerField(default=1)  # 1 = primary, 2 = secondary
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_relationship_display()}"

class UserActivity(BaseModel):
    """User activity tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

class UserSession(BaseModel):
    """User session tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key} - {self.last_activity}"