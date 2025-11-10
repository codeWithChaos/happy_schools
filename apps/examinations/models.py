"""
Models for the examinations app.
Handles exams, results, and grade management.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Exam(models.Model):
    """
    Exam model for managing examinations.
    """
    EXAM_TYPE_CHOICES = [
        ('unit_test', 'Unit Test'),
        ('mid_term', 'Mid Term'),
        ('final', 'Final Exam'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
        ('entrance', 'Entrance Exam'),
        ('placement', 'Placement Test'),
    ]
    
    # School and academic year
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name=_('School')
    )
    academic_year = models.ForeignKey(
        'accounts.AcademicYear',
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name=_('Academic Year')
    )
    
    # Exam details
    name = models.CharField(_('Exam Name'), max_length=200)
    exam_type = models.CharField(_('Exam Type'), max_length=20, choices=EXAM_TYPE_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    
    # Applicable to
    classes = models.ManyToManyField(
        'accounts.Class',
        related_name='exams',
        verbose_name=_('Classes')
    )
    
    # Schedule
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    
    # Result settings
    result_declaration_date = models.DateField(_('Result Declaration Date'), null=True, blank=True)
    is_result_published = models.BooleanField(_('Is Result Published'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'exams'
        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'academic_year']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='exam_end_date_after_start_date'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.year})"
    
    def is_ongoing(self):
        """Check if exam is currently ongoing."""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date


class ExamResult(models.Model):
    """
    Exam Result model for storing student marks.
    """
    GRADE_CHOICES = [
        ('A+', 'A+ (Outstanding)'),
        ('A', 'A (Excellent)'),
        ('B+', 'B+ (Very Good)'),
        ('B', 'B (Good)'),
        ('C+', 'C+ (Above Average)'),
        ('C', 'C (Average)'),
        ('D', 'D (Below Average)'),
        ('F', 'F (Fail)'),
    ]
    
    # Exam and student
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name=_('Exam')
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_results',
        verbose_name=_('Student')
    )
    subject = models.ForeignKey(
        'accounts.Subject',
        on_delete=models.CASCADE,
        related_name='exam_results',
        verbose_name=_('Subject')
    )
    
    # Marks
    marks_obtained = models.DecimalField(
        _('Marks Obtained'),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_marks = models.PositiveIntegerField(_('Maximum Marks'), default=100)
    
    # Grade
    grade = models.CharField(_('Grade'), max_length=2, choices=GRADE_CHOICES, blank=True)
    
    # Theory and practical split (if applicable)
    theory_marks = models.DecimalField(
        _('Theory Marks'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    practical_marks = models.DecimalField(
        _('Practical Marks'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_passed = models.BooleanField(_('Is Passed'), default=False)
    is_absent = models.BooleanField(_('Is Absent'), default=False)
    
    # Comments
    remarks = models.TextField(_('Remarks'), blank=True)
    teacher_comments = models.TextField(_('Teacher Comments'), blank=True)
    
    # Entered by
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='entered_results',
        verbose_name=_('Entered By'),
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'exam_results'
        verbose_name = _('Exam Result')
        verbose_name_plural = _('Exam Results')
        ordering = ['-exam__start_date', 'student', 'subject']
        unique_together = [['exam', 'student', 'subject']]
        indexes = [
            models.Index(fields=['exam', 'student']),
            models.Index(fields=['student', 'subject']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(marks_obtained__lte=models.F('max_marks')),
                name='marks_lte_max_marks'
            ),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.exam.name}"
    
    def calculate_grade(self):
        """Calculate grade based on percentage."""
        if self.is_absent or self.marks_obtained is None:
            return 'F'
        
        percentage = (float(self.marks_obtained) / self.max_marks) * 100
        
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        elif percentage >= 33:
            return 'D'
        else:
            return 'F'
    
    def check_pass_status(self):
        """Check if student passed based on passing marks."""
        if self.is_absent:
            return False
        passing_marks = self.subject.passing_marks
        return self.marks_obtained >= passing_marks
    
    def save(self, *args, **kwargs):
        """Calculate grade and pass status before saving."""
        if not self.is_absent:
            self.grade = self.calculate_grade()
            self.is_passed = self.check_pass_status()
        super().save(*args, **kwargs)
    
    def get_percentage(self):
        """Get percentage scored."""
        if self.is_absent or self.marks_obtained is None:
            return 0
        return round((float(self.marks_obtained) / self.max_marks) * 100, 2)
