"""
Admin configuration for the accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AcademicYear, Class, School, Section, Subject, User


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin for School model."""
    list_display = ['name', 'subdomain', 'subscription_status', 'is_active', 'created_at']
    list_filter = ['subscription_status', 'is_active', 'created_at']
    search_fields = ['name', 'subdomain', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'subdomain', 'logo', 'primary_color')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        (_('Subscription'), {
            'fields': ('subscription_status', 'subscription_start_date', 'subscription_end_date', 'max_students', 'max_teachers')
        }),
        (_('Settings'), {
            'fields': ('settings', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""
    list_display = ['username', 'email', 'first_name', 'last_name', 'school', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'school']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'profile_photo')}),
        (_('School & Role'), {'fields': ('school', 'role')}),
        (_('Address'), {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        (_('Emergency Contact'), {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'school', 'role'),
        }),
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """Admin for AcademicYear model."""
    list_display = ['year', 'school', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'school']
    search_fields = ['year', 'school__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin for Class model."""
    list_display = ['name', 'school', 'academic_year', 'class_teacher', 'is_active']
    list_filter = ['is_active', 'school', 'academic_year']
    search_fields = ['name', 'school__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin for Section model."""
    list_display = ['name', 'class_obj', 'capacity', 'room_number', 'is_active']
    list_filter = ['is_active', 'class_obj__school']
    search_fields = ['name', 'class_obj__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin for Subject model."""
    list_display = ['name', 'code', 'school', 'total_marks', 'passing_marks', 'is_active']
    list_filter = ['is_active', 'is_elective', 'is_practical', 'school']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
