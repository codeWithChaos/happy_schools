"""
Models for the students app.
Handles student information, guardians, and teacher profiles.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Student(models.Model):
    """
    Student model linking to User model with role='student'.
    Contains student-specific information.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('User')
    )
    
    # School relationship (denormalized for performance)
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name=_('School')
    )
    
    # Student identification
    admission_number = models.CharField(_('Admission Number'), max_length=50, unique=True)
    roll_number = models.CharField(_('Roll Number'), max_length=50, blank=True)
    
    # Class assignment
    class_assigned = models.ForeignKey(
        'accounts.Class',
        on_delete=models.SET_NULL,
        related_name='students',
        verbose_name=_('Class'),
        null=True,
        blank=True
    )
    
    # Personal information
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(_('Blood Group'), max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    religion = models.CharField(_('Religion'), max_length=50, blank=True)
    nationality = models.CharField(_('Nationality'), max_length=50, default='United States')
    
    # Medical information
    medical_conditions = models.TextField(_('Medical Conditions'), blank=True)
    allergies = models.TextField(_('Allergies'), blank=True)
    
    # Academic information
    previous_school = models.CharField(_('Previous School'), max_length=200, blank=True)
    date_of_admission = models.DateField(_('Date of Admission'))
    date_of_leaving = models.DateField(_('Date of Leaving'), null=True, blank=True)
    
    # Guardian relationship
    guardians = models.ManyToManyField(
        'Guardian',
        related_name='wards',
        verbose_name=_('Guardians'),
        blank=True
    )
    
    # Transportation
    uses_transport = models.BooleanField(_('Uses School Transport'), default=False)
    transport_route = models.CharField(_('Transport Route'), max_length=100, blank=True)
    
    # Additional notes
    remarks = models.TextField(_('Remarks'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
        ordering = ['admission_number']
        indexes = [
            models.Index(fields=['school', 'class_assigned']),
            models.Index(fields=['admission_number']),
            models.Index(fields=['school', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"
    
    def get_current_class(self):
        """Get the current class."""
        if self.class_assigned:
            return f"{self.class_assigned.name}"
        return "Not Assigned"
    
    def get_age(self):
        """Calculate student's age."""
        if self.user.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.user.date_of_birth.year - (
                (today.month, today.day) < (self.user.date_of_birth.month, self.user.date_of_birth.day)
            )
        return None


class Guardian(models.Model):
    """
    Guardian/Parent model linking to User model with role='parent'.
    A guardian can have multiple wards (students).
    """
    RELATION_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('guardian', 'Legal Guardian'),
        ('other', 'Other'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='guardian_profile',
        verbose_name=_('User')
    )
    
    # School relationship
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='guardians',
        verbose_name=_('School')
    )
    
    # Guardian information
    relation = models.CharField(_('Relation'), max_length=20, choices=RELATION_CHOICES)
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True)
    annual_income = models.DecimalField(
        _('Annual Income'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Alternative contact
    alternate_phone = models.CharField(_('Alternate Phone'), max_length=17, blank=True)
    office_phone = models.CharField(_('Office Phone'), max_length=17, blank=True)
    
    # Identification
    national_id = models.CharField(_('National ID/SSN'), max_length=50, blank=True)
    
    # Authorization
    is_primary_contact = models.BooleanField(_('Is Primary Contact'), default=True)
    can_pickup_student = models.BooleanField(_('Can Pick Up Student'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'guardians'
        verbose_name = _('Guardian')
        verbose_name_plural = _('Guardians')
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['school']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_relation_display()})"
    
    def get_wards_count(self):
        """Get the number of wards."""
        return self.wards.filter(is_active=True).count()


class Teacher(models.Model):
    """
    Teacher model linking to User model with role='teacher'.
    Contains teacher-specific information.
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('substitute', 'Substitute'),
    ]
    
    QUALIFICATION_CHOICES = [
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('doctorate', 'Doctorate'),
        ('diploma', 'Diploma'),
        ('certification', 'Certification'),
    ]
    
    # Link to User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_('User')
    )
    
    # School relationship
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='teachers',
        verbose_name=_('School')
    )
    
    # Teacher identification
    employee_id = models.CharField(_('Employee ID'), max_length=50, unique=True)
    
    # Subjects taught
    subjects = models.ManyToManyField(
        'accounts.Subject',
        related_name='teachers',
        verbose_name=_('Subjects'),
        blank=True
    )
    
    # Employment details
    employment_type = models.CharField(
        _('Employment Type'),
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    date_of_joining = models.DateField(_('Date of Joining'))
    date_of_leaving = models.DateField(_('Date of Leaving'), null=True, blank=True)
    
    # Qualifications
    highest_qualification = models.CharField(
        _('Highest Qualification'),
        max_length=20,
        choices=QUALIFICATION_CHOICES,
        default='bachelor'
    )
    specialization = models.CharField(_('Specialization'), max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(_('Years of Experience'), default=0)
    
    # Salary information (encrypted in production)
    salary = models.DecimalField(
        _('Salary'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Additional details
    certifications = models.TextField(_('Certifications'), blank=True)
    languages_known = models.CharField(_('Languages Known'), max_length=200, blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(_('Emergency Contact Name'), max_length=200, blank=True)
    emergency_contact_phone = models.CharField(_('Emergency Contact Phone'), max_length=17, blank=True)
    emergency_contact_relation = models.CharField(_('Emergency Contact Relation'), max_length=50, blank=True)
    
    # Documents
    resume = models.FileField(_('Resume'), upload_to='teachers/resumes/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    
    class Meta:
        db_table = 'teachers'
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['school', 'is_active']),
            models.Index(fields=['employee_id']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_subjects_taught(self):
        """Get list of subjects taught by this teacher."""
        return ", ".join([subject.name for subject in self.subjects.all()])
    
    def get_classes_taught(self):
        """Get list of classes taught by this teacher."""
        from apps.accounts.models import Class
        return Class.objects.filter(class_teacher=self.user, is_active=True)
