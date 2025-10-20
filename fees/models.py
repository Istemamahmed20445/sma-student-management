from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel, Currency
from students.models import Student
from batches.models import Batch
import uuid

class StudentPayment(BaseModel):
    """Simple student payment model - tracks total amount and payments made"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
    
    # Payment Method
    PAYMENT_METHOD_CHOICES = [
        ('installments', 'Installments'),
        ('full_payment', 'Full Payment'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='installments')
    
    # Payment Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional Information
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'batch']  # One payment per student per batch
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.batch.name} - {self.currency.code} {self.total_amount}"
    
    def get_total_paid(self):
        """Get total amount paid"""
        from django.db.models import Sum
        result = self.transactions.aggregate(total=Sum('amount'))['total']
        total = result or 0
        # Round to 2 decimal places to avoid floating point precision issues
        return round(float(total), 2)
    
    def get_remaining_amount(self):
        """Get remaining amount to be paid"""
        remaining = float(self.total_amount) - float(self.get_total_paid())
        # Round to 2 decimal places to avoid floating point precision issues
        return round(remaining, 2)
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        if self.total_amount > 0:
            return (self.get_total_paid() / self.total_amount) * 100
        return 0
    
    def is_completed(self):
        """Check if payment is completed"""
        return self.get_total_paid() >= self.total_amount
    
    def update_status(self):
        """Update status based on payments"""
        total_paid = self.get_total_paid()
        if total_paid >= self.total_amount:
            self.status = 'completed'
        elif total_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save()

class PaymentTransaction(BaseModel):
    """Individual payment transactions"""
    payment = models.ForeignKey(StudentPayment, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    # Payment Method
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('online_payment', 'Online Payment'),
        ('check', 'Check'),
        ('mobile_payment', 'Mobile Payment'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    
    # Transaction Details
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.receipt_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number
            import random
            import string
            self.receipt_number = f"RCP{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        
        super().save(*args, **kwargs)
        
        # Update payment status
        self.payment.update_status()

class PaymentImport(BaseModel):
    """Track Excel imports for payments"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='payment_imports')
    file_name = models.CharField(max_length=200)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    
    # Import Statistics
    total_rows = models.PositiveIntegerField(default=0)
    successful_imports = models.PositiveIntegerField(default=0)
    failed_imports = models.PositiveIntegerField(default=0)
    
    # Import Status
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    # Error details
    error_log = models.TextField(blank=True)
    
    def __str__(self):
        return f"Import {self.batch.name} - {self.file_name} ({self.status})"
    
    def get_success_rate(self):
        """Get success rate percentage"""
        if self.total_rows > 0:
            return (self.successful_imports / self.total_rows) * 100
        return 0