"""
Models for the attendance app.
Handles student attendance tracking and reporting.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Attendance(models.Model):
    """
    Attendance model for tracking student attendance.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('excused', 'Excused Absence'),
    ]
    
    # Student and date
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_('Student')
    )
    date = models.DateField(_('Date'))
    
    # Attendance status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    
    # Time tracking
    check_in_time = models.TimeField(_('Check-in Time'), null=True, blank=True)
    check_out_time = models.TimeField(_('Check-out Time'), null=True, blank=True)
    
    # Marked by
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='marked_attendances',
        verbose_name=_('Marked By'),
        null=True,
        blank=True
    )
    
    # Additional information
    remarks = models.TextField(_('Remarks'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'attendance'
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendance Records')
        ordering = ['-date', 'student']
        unique_together = [['student', 'date']]
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['student', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} ({self.get_status_display()})"
    
    def is_present(self):
        """Check if student was present."""
        return self.status in ['present', 'late', 'half_day']
    
    def is_absent(self):
        """Check if student was absent."""
        return self.status in ['absent', 'excused']
