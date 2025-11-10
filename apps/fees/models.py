"""
Models for the fees app.
Handles fee structure and payment management.
"""
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class FeeStructure(models.Model):
    """
    Fee Structure model defining fees for different classes.
    """
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('examination', 'Examination Fee'),
        ('library', 'Library Fee'),
        ('laboratory', 'Laboratory Fee'),
        ('sports', 'Sports Fee'),
        ('transport', 'Transport Fee'),
        ('hostel', 'Hostel Fee'),
        ('computer', 'Computer Fee'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    
    FREQUENCY_CHOICES = [
        ('one_time', 'One Time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('annually', 'Annually'),
    ]
    
    # School and academic year
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        verbose_name=_('School')
    )
    academic_year = models.ForeignKey(
        'accounts.AcademicYear',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        verbose_name=_('Academic Year')
    )
    
    # Fee details
    name = models.CharField(_('Fee Name'), max_length=100)
    fee_type = models.CharField(_('Fee Type'), max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    
    # Applicability
    class_applicable = models.ForeignKey(
        'accounts.Class',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        verbose_name=_('Applicable to Class'),
        null=True,
        blank=True
    )
    
    # Payment schedule
    frequency = models.CharField(_('Frequency'), max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    due_date = models.DateField(_('Due Date'))
    late_fee_applicable = models.BooleanField(_('Late Fee Applicable'), default=True)
    late_fee_amount = models.DecimalField(_('Late Fee Amount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Description
    description = models.TextField(_('Description'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'fee_structures'
        verbose_name = _('Fee Structure')
        verbose_name_plural = _('Fee Structures')
        ordering = ['academic_year', 'class_applicable', 'fee_type']
        indexes = [
            models.Index(fields=['school', 'academic_year']),
            models.Index(fields=['class_applicable', 'fee_type']),
        ]
    
    def __str__(self):
        class_name = self.class_applicable.name if self.class_applicable else "All Classes"
        return f"{self.name} - {class_name} ({self.academic_year.year})"


class FeePayment(models.Model):
    """
    Fee Payment model for recording fee payments.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('mobile_payment', 'Mobile Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Student and fee structure
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fee_payments',
        verbose_name=_('Student')
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_('Fee Structure')
    )
    
    # Payment details
    amount_paid = models.DecimalField(_('Amount Paid'), max_digits=10, decimal_places=2)
    late_fee = models.DecimalField(_('Late Fee'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(_('Discount'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('Total Amount'), max_digits=10, decimal_places=2)
    
    # Payment information
    payment_date = models.DateField(_('Payment Date'))
    payment_method = models.CharField(_('Payment Method'), max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(_('Payment Status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    
    # Transaction details
    transaction_id = models.CharField(_('Transaction ID'), max_length=100, blank=True)
    receipt_number = models.CharField(_('Receipt Number'), max_length=50, unique=True)
    
    # Check details (if applicable)
    check_number = models.CharField(_('Check Number'), max_length=50, blank=True)
    check_date = models.DateField(_('Check Date'), null=True, blank=True)
    bank_name = models.CharField(_('Bank Name'), max_length=100, blank=True)
    
    # Collected by
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='collected_payments',
        verbose_name=_('Collected By'),
        null=True,
        blank=True
    )
    
    # Notes
    remarks = models.TextField(_('Remarks'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'fee_payments'
        verbose_name = _('Fee Payment')
        verbose_name_plural = _('Fee Payments')
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'payment_date']),
            models.Index(fields=['receipt_number']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['fee_structure', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.receipt_number} - ${self.total_amount}"
    
    def save(self, *args, **kwargs):
        """Calculate total amount before saving."""
        self.total_amount = self.amount_paid + self.late_fee - self.discount
        super().save(*args, **kwargs)
    
    def is_completed(self):
        """Check if payment is completed."""
        return self.payment_status == 'completed'
