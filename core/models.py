from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid

class BaseModel(models.Model):
    """Base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Currency(BaseModel):
    """Currency model for multi-currency support"""
    code = models.CharField(max_length=3, unique=True)  # USD, BDT, AUD, INR, PKR
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Currencies"


class AcademicYear(BaseModel):
    """Academic year model"""
    name = models.CharField(max_length=50)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other academic years to not current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Semester(BaseModel):
    """Semester model"""
    name = models.CharField(max_length=50)  # e.g., "Fall 2024", "Spring 2025"
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other semesters to not current
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Course(BaseModel):
    """Course model"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField()
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class FeeStructure(BaseModel):
    """Fee structure model for different programs"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    installment_count = models.PositiveIntegerField(default=2)  # 2 or 3 installments
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.currency.format_currency(self.total_amount, self.currency.code)}"
    
    def get_installment_amount(self):
        """Calculate amount per installment"""
        return self.total_amount / self.installment_count

class Notification(BaseModel):
    """Notification model"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=[
        ('payment_due', 'Payment Due'),
        ('payment_received', 'Payment Received'),
        ('grade_posted', 'Grade Posted'),
        ('announcement', 'Announcement'),
        ('reminder', 'Reminder'),
    ])
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"