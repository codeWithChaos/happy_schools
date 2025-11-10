"""
Models for the timetable app.
Handles class schedules and period management.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Timetable(models.Model):
    """
    Timetable model for managing class schedules.
    """
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    # School relationship
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name=_('School')
    )
    
    # Academic year
    academic_year = models.ForeignKey(
        'accounts.AcademicYear',
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name=_('Academic Year')
    )
    
    # Class and section
    class_assigned = models.ForeignKey(
        'accounts.Class',
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name=_('Class')
    )
    section = models.ForeignKey(
        'accounts.Section',
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name=_('Section')
    )
    
    # Day and period
    day = models.CharField(_('Day'), max_length=10, choices=DAY_CHOICES)
    period_number = models.PositiveIntegerField(_('Period Number'))
    
    # Subject and teacher
    subject = models.ForeignKey(
        'accounts.Subject',
        on_delete=models.CASCADE,
        related_name='timetable_slots',
        verbose_name=_('Subject')
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='teaching_slots',
        verbose_name=_('Teacher'),
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'}
    )
    
    # Time
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    
    # Room
    room_number = models.CharField(_('Room Number'), max_length=20, blank=True)
    
    # Additional information
    is_break = models.BooleanField(_('Is Break'), default=False)
    is_lab = models.BooleanField(_('Is Lab Session'), default=False)
    remarks = models.TextField(_('Remarks'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'timetables'
        verbose_name = _('Timetable')
        verbose_name_plural = _('Timetables')
        ordering = ['day', 'period_number', 'start_time']
        unique_together = [['class_assigned', 'section', 'day', 'period_number', 'academic_year']]
        indexes = [
            models.Index(fields=['school', 'academic_year']),
            models.Index(fields=['class_assigned', 'section', 'day']),
            models.Index(fields=['teacher', 'day']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            ),
        ]
    
    def __str__(self):
        return f"{self.class_assigned.name}-{self.section.name} | {self.get_day_display()} | Period {self.period_number}"
    
    def clean(self):
        """Validate timetable entry."""
        super().clean()
        
        # Check for teacher conflicts (same teacher, same time, same day)
        if self.teacher and not self.is_break:
            conflicting_slots = Timetable.objects.filter(
                teacher=self.teacher,
                day=self.day,
                academic_year=self.academic_year,
                is_active=True
            ).exclude(pk=self.pk)
            
            for slot in conflicting_slots:
                # Check if times overlap
                if (self.start_time < slot.end_time and self.end_time > slot.start_time):
                    raise ValidationError(
                        f"Teacher {self.teacher.get_full_name()} has a conflicting slot at {slot.start_time}-{slot.end_time}"
                    )
    
    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        super().save(*args, **kwargs)
