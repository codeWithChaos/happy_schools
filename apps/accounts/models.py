"""
Models for the accounts app.
Handles multi-tenancy (School), custom user model, and authentication.
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class School(models.Model):
    """
    School model - The tenant model for multi-tenancy.
    Each school is a separate tenant with isolated data.
    """
    SUBSCRIPTION_STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(_('School Name'), max_length=200)
    subdomain = models.SlugField(
        _('Subdomain'),
        max_length=50,
        unique=True,
        help_text=_('Unique subdomain for this school (e.g., demo.schoolmanagement.com)')
    )
    
    # Contact information
    email = models.EmailField(_('Contact Email'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(_('Contact Phone'), validators=[phone_regex], max_length=17)
    
    # Address
    address_line1 = models.CharField(_('Address Line 1'), max_length=255)
    address_line2 = models.CharField(_('Address Line 2'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State/Province'), max_length=100)
    postal_code = models.CharField(_('Postal Code'), max_length=20)
    country = models.CharField(_('Country'), max_length=100, default='United States')
    
    # Subscription details
    subscription_status = models.CharField(
        _('Subscription Status'),
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='trial'
    )
    subscription_start_date = models.DateField(_('Subscription Start Date'), null=True, blank=True)
    subscription_end_date = models.DateField(_('Subscription End Date'), null=True, blank=True)
    max_students = models.PositiveIntegerField(_('Maximum Students'), default=100)
    max_teachers = models.PositiveIntegerField(_('Maximum Teachers'), default=20)
    
    # School branding
    logo = models.ImageField(_('School Logo'), upload_to='schools/logos/', null=True, blank=True)
    primary_color = models.CharField(_('Primary Color'), max_length=7, default='#4F46E5')
    
    # Settings (stored as JSON for flexibility)
    settings = models.JSONField(_('School Settings'), default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'schools'
        verbose_name = _('School')
        verbose_name_plural = _('Schools')
        ordering = ['name']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['subscription_status']),
        ]
    
    def __str__(self):
        return self.name
    
    def is_subscription_active(self):
        """Check if school's subscription is active."""
        return self.subscription_status == 'active'
    
    def can_add_students(self):
        """Check if school can add more students."""
        from apps.students.models import Student
        current_count = Student.objects.filter(school=self, is_active=True).count()
        return current_count < self.max_students
    
    def can_add_teachers(self):
        """Check if school can add more teachers."""
        teacher_count = User.objects.filter(
            school=self,
            role='teacher',
            is_active=True
        ).count()
        return teacher_count < self.max_teachers


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports multiple roles: admin, teacher, student, parent.
    """
    ROLE_CHOICES = [
        ('admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    
    # Link to school (tenant)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('School'),
        null=True,
        blank=True
    )
    
    # Role
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )
    
    # Profile information
    profile_photo = models.ImageField(
        _('Profile Photo'),
        upload_to='users/profiles/',
        null=True,
        blank=True
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    
    # Address
    address_line1 = models.CharField(_('Address Line 1'), max_length=255, blank=True)
    address_line2 = models.CharField(_('Address Line 2'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State/Province'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(_('Emergency Contact Name'), max_length=200, blank=True)
    emergency_contact_phone = models.CharField(
        _('Emergency Contact Phone'),
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    emergency_contact_relation = models.CharField(_('Emergency Contact Relation'), max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['school', 'role']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
        unique_together = [['school', 'email']]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = super().get_full_name()
        return full_name if full_name else self.username
    
    def is_admin(self):
        """Check if user is a school admin."""
        return self.role == 'admin'
    
    def is_teacher(self):
        """Check if user is a teacher."""
        return self.role == 'teacher'
    
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def is_parent(self):
        """Check if user is a parent."""
        return self.role == 'parent'


class AcademicYear(models.Model):
    """
    Academic Year model for managing school years.
    Each school can have multiple academic years.
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='academic_years',
        verbose_name=_('School')
    )
    year = models.CharField(
        _('Academic Year'),
        max_length=20,
        help_text=_('e.g., 2024-2025')
    )
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    is_active = models.BooleanField(_('Is Active'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'academic_years'
        verbose_name = _('Academic Year')
        verbose_name_plural = _('Academic Years')
        ordering = ['-start_date']
        unique_together = [['school', 'year']]
        indexes = [
            models.Index(fields=['school', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='end_date_after_start_date'
            ),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.year}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active academic year per school."""
        if self.is_active:
            # Deactivate other academic years for this school
            AcademicYear.objects.filter(
                school=self.school,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Class(models.Model):
    """
    Class/Grade model (e.g., Grade 1, Grade 2, etc.).
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_('School')
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_('Academic Year')
    )
    name = models.CharField(
        _('Class Name'),
        max_length=50,
        help_text=_('e.g., Grade 1, Grade 2, Class 10')
    )
    class_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='taught_classes',
        verbose_name=_('Class Teacher'),
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'}
    )
    description = models.TextField(_('Description'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'classes'
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
        ordering = ['name']
        unique_together = [['school', 'academic_year', 'name']]
        indexes = [
            models.Index(fields=['school', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.year})"


class Section(models.Model):
    """
    Section model for dividing classes (e.g., Section A, Section B).
    """
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_('Class')
    )
    name = models.CharField(
        _('Section Name'),
        max_length=20,
        help_text=_('e.g., A, B, C')
    )
    capacity = models.PositiveIntegerField(
        _('Capacity'),
        default=30,
        help_text=_('Maximum number of students')
    )
    room_number = models.CharField(_('Room Number'), max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'sections'
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ['name']
        unique_together = [['class_obj', 'name']]
        indexes = [
            models.Index(fields=['class_obj']),
        ]
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"
    
    def get_student_count(self):
        """Get the current number of students in this section."""
        from apps.students.models import Student
        return Student.objects.filter(section=self, is_active=True).count()
    
    def is_full(self):
        """Check if section is at capacity."""
        return self.get_student_count() >= self.capacity


class Subject(models.Model):
    """
    Subject model for managing school subjects.
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name=_('School')
    )
    name = models.CharField(_('Subject Name'), max_length=100)
    code = models.CharField(_('Subject Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    # Subject classification
    is_elective = models.BooleanField(_('Is Elective'), default=False)
    is_practical = models.BooleanField(_('Has Practical'), default=False)
    
    # Credits/Marks
    total_marks = models.PositiveIntegerField(_('Total Marks'), default=100)
    passing_marks = models.PositiveIntegerField(_('Passing Marks'), default=40)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'subjects'
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['name']
        unique_together = [['school', 'name']]
        indexes = [
            models.Index(fields=['school', 'code']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(passing_marks__lte=models.F('total_marks')),
                name='passing_marks_lte_total_marks'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
