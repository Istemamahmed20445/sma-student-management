from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel, AcademicYear, Semester, Course
import uuid

class Batch(BaseModel):
    """Batch model for organizing students"""
    name = models.CharField(max_length=50)  # e.g., "Batch 57", "Batch 59"
    code = models.CharField(max_length=20, unique=True)  # e.g., "B57", "B59"
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='batches', null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='batches', null=True, blank=True)
    
    # Batch details
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Batch status
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Academic details
    courses = models.ManyToManyField(Course, related_name='batches', blank=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_batches')
    
    # Fee structure for this batch
    fee_structure = models.ForeignKey('core.FeeStructure', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.code}"
    
    @property
    def total_students(self):
        """Get the total number of active students in this batch"""
        return self.students.filter(is_active=True).count()
    
    
    
    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            self.code = f"B{self.name.split()[-1]}"  # Extract number from name
        super().save(*args, **kwargs)

class BatchSchedule(BaseModel):
    """Schedule for batch classes"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='schedules')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Schedule details
    day_of_week = models.CharField(max_length=10, choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.batch.name} - {self.course.name} - {self.day_of_week}"

class BatchAttendance(BaseModel):
    """Attendance tracking for batch sessions"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'date', 'course']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"

class BatchGrade(BaseModel):
    """Grade tracking for batch students"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    # Grade components
    assignment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quiz_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    midterm_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Weighted components (percentages)
    assignment_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    quiz_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    midterm_weight = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    final_weight = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    
    # Final grade
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    letter_grade = models.CharField(max_length=2, blank=True)
    
    # Grade details
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'course', 'semester']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.name} - {self.total_score}"
    
    def calculate_total_score(self):
        """Calculate total weighted score"""
        total = (
            (self.assignment_score * self.assignment_weight / 100) +
            (self.quiz_score * self.quiz_weight / 100) +
            (self.midterm_score * self.midterm_weight / 100) +
            (self.final_score * self.final_weight / 100)
        )
        return round(total, 2)
    
    def get_letter_grade(self):
        """Convert numeric score to letter grade"""
        score = self.total_score
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'F'
    
    def save(self, *args, **kwargs):
        self.total_score = self.calculate_total_score()
        self.letter_grade = self.get_letter_grade()
        super().save(*args, **kwargs)