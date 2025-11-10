"""
Views for the attendance app.
Handles attendance marking, viewing, and reporting.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Case, When, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, FormView
from datetime import date, timedelta

from apps.accounts.models import Class, Section
from apps.students.models import Student
from .models import Attendance


class AttendanceAccessMixin(UserPassesTestMixin):
    """Mixin to restrict attendance views to admin and teacher roles."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class AttendanceListView(LoginRequiredMixin, AttendanceAccessMixin, ListView):
    """
    List view for attendance records.
    Shows attendance records with filtering by date, class, section, and status.
    """
    model = Attendance
    template_name = 'attendance/list.html'
    context_object_name = 'attendance_records'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'student__user',
            'student__class_assigned',
            'student__section',
            'marked_by'
        ).filter(student__school=self.request.school)
        
        # Search by student name or admission number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__admission_number__icontains=search)
            )
        
        # Filter by date
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        else:
            # Default to today
            queryset = queryset.filter(date=timezone.now().date())
        
        # Filter by class
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(student__class_assigned_id=class_id)
        
        # Filter by section
        section_id = self.request.GET.get('section')
        if section_id:
            queryset = queryset.filter(student__section_id=section_id)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-date', 'student__user__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['classes'] = Class.objects.filter(
            school=self.request.school,
            is_active=True
        ).order_by('name')
        
        context['sections'] = Section.objects.filter(
            class_obj__school=self.request.school,
            is_active=True
        ).order_by('class_obj__name', 'name')
        
        context['status_choices'] = Attendance.STATUS_CHOICES
        
        # Current filter values
        context['current_date'] = self.request.GET.get('date', timezone.now().date().isoformat())
        context['current_class'] = self.request.GET.get('class', '')
        context['current_section'] = self.request.GET.get('section', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        
        # Statistics for the current filter
        records = self.get_queryset()
        context['total_records'] = records.count()
        context['present_count'] = records.filter(status__in=['present', 'late', 'half_day']).count()
        context['absent_count'] = records.filter(status__in=['absent', 'excused']).count()
        context['late_count'] = records.filter(status='late').count()
        
        return context


class MarkAttendanceView(LoginRequiredMixin, AttendanceAccessMixin, View):
    """
    View for marking attendance for a class/section.
    Shows all students and allows bulk marking of attendance.
    """
    template_name = 'attendance/mark_attendance.html'
    
    def get(self, request):
        # Get filter parameters
        class_id = request.GET.get('class')
        section_id = request.GET.get('section')
        attendance_date = request.GET.get('date', timezone.now().date().isoformat())
        
        context = {
            'classes': Class.objects.filter(school=request.school, is_active=True).order_by('name'),
            'sections': Section.objects.filter(class_obj__school=request.school, is_active=True).order_by('class_obj__name', 'name'),
            'status_choices': Attendance.STATUS_CHOICES,
            'selected_class': class_id,
            'selected_section': section_id,
            'attendance_date': attendance_date,
        }
        
        # If class and section are selected, get students
        if class_id and section_id:
            students = Student.objects.filter(
                school=request.school,
                class_assigned_id=class_id,
                section_id=section_id,
                is_active=True
            ).select_related('user').order_by('roll_number', 'user__first_name')
            
            # Get existing attendance records for this date
            existing_attendance = {
                att.student_id: att 
                for att in Attendance.objects.filter(
                    student__in=students,
                    date=attendance_date
                )
            }
            
            # Prepare student data with existing attendance
            students_data = []
            for student in students:
                attendance_record = existing_attendance.get(student.id)
                students_data.append({
                    'student': student,
                    'attendance': attendance_record,
                    'status': attendance_record.status if attendance_record else 'present',
                    'remarks': attendance_record.remarks if attendance_record else '',
                })
            
            context['students'] = students_data
            context['selected_class_obj'] = Class.objects.get(id=class_id)
            context['selected_section_obj'] = Section.objects.get(id=section_id)
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        class_id = request.POST.get('class')
        section_id = request.POST.get('section')
        attendance_date = request.POST.get('date')
        
        if not all([class_id, section_id, attendance_date]):
            messages.error(request, 'Please select class, section, and date.')
            return redirect('attendance:mark')
        
        # Get all students in the class/section
        students = Student.objects.filter(
            school=request.school,
            class_assigned_id=class_id,
            section_id=section_id,
            is_active=True
        )
        
        created_count = 0
        updated_count = 0
        
        # Process attendance for each student
        for student in students:
            student_id = str(student.id)
            status = request.POST.get(f'status_{student_id}')
            remarks = request.POST.get(f'remarks_{student_id}', '')
            
            if status:
                # Create or update attendance record
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        if created_count > 0:
            messages.success(request, f'Attendance marked for {created_count} students.')
        if updated_count > 0:
            messages.success(request, f'Attendance updated for {updated_count} students.')
        
        # Redirect back to the same page with filters
        return redirect(f"{reverse('attendance:mark')}?class={class_id}&section={section_id}&date={attendance_date}")


class AttendanceReportView(LoginRequiredMixin, AttendanceAccessMixin, View):
    """
    View for attendance reports and analytics.
    Shows attendance statistics by date range, class, or individual student.
    """
    template_name = 'attendance/report.html'
    
    def get(self, request):
        # Get filter parameters
        report_type = request.GET.get('report_type', 'daily')
        start_date = request.GET.get('start_date', (timezone.now().date() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end_date', timezone.now().date().isoformat())
        class_id = request.GET.get('class')
        section_id = request.GET.get('section')
        student_id = request.GET.get('student')
        
        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'classes': Class.objects.filter(school=request.school, is_active=True).order_by('name'),
            'sections': Section.objects.filter(class_obj__school=request.school, is_active=True).order_by('class_obj__name', 'name'),
            'selected_class': class_id,
            'selected_section': section_id,
            'selected_student': student_id,
        }
        
        # Base queryset
        queryset = Attendance.objects.filter(
            student__school=request.school,
            date__range=[start_date, end_date]
        )
        
        # Apply filters
        if class_id:
            queryset = queryset.filter(student__class_assigned_id=class_id)
        if section_id:
            queryset = queryset.filter(student__section_id=section_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        if report_type == 'daily':
            # Daily summary
            daily_stats = queryset.values('date').annotate(
                total=Count('id'),
                present=Count(Case(When(status__in=['present', 'late', 'half_day'], then=1), output_field=IntegerField())),
                absent=Count(Case(When(status__in=['absent', 'excused'], then=1), output_field=IntegerField())),
                late=Count(Case(When(status='late', then=1), output_field=IntegerField())),
            ).order_by('-date')[:30]
            
            context['daily_stats'] = daily_stats
            
        elif report_type == 'student':
            # Student-wise summary
            student_stats = queryset.values(
                'student__id',
                'student__user__first_name',
                'student__user__last_name',
                'student__admission_number',
                'student__class_assigned__name',
                'student__section__name',
            ).annotate(
                total_days=Count('id'),
                present_days=Count(Case(When(status__in=['present', 'late', 'half_day'], then=1), output_field=IntegerField())),
                absent_days=Count(Case(When(status__in=['absent', 'excused'], then=1), output_field=IntegerField())),
                late_days=Count(Case(When(status='late', then=1), output_field=IntegerField())),
            ).order_by('student__user__first_name')
            
            # Calculate attendance percentage
            for stat in student_stats:
                if stat['total_days'] > 0:
                    stat['attendance_percentage'] = round((stat['present_days'] / stat['total_days']) * 100, 2)
                else:
                    stat['attendance_percentage'] = 0
            
            context['student_stats'] = student_stats
            
        elif report_type == 'class':
            # Class-wise summary
            class_stats = queryset.values(
                'student__class_assigned__id',
                'student__class_assigned__name',
                'student__section__name',
            ).annotate(
                total_records=Count('id'),
                present_count=Count(Case(When(status__in=['present', 'late', 'half_day'], then=1), output_field=IntegerField())),
                absent_count=Count(Case(When(status__in=['absent', 'excused'], then=1), output_field=IntegerField())),
            ).order_by('student__class_assigned__name', 'student__section__name')
            
            # Calculate attendance percentage
            for stat in class_stats:
                if stat['total_records'] > 0:
                    stat['attendance_percentage'] = round((stat['present_count'] / stat['total_records']) * 100, 2)
                else:
                    stat['attendance_percentage'] = 0
            
            context['class_stats'] = class_stats
        
        # Overall statistics
        total_records = queryset.count()
        present_records = queryset.filter(status__in=['present', 'late', 'half_day']).count()
        absent_records = queryset.filter(status__in=['absent', 'excused']).count()
        
        context['overall_stats'] = {
            'total_records': total_records,
            'present_records': present_records,
            'absent_records': absent_records,
            'attendance_percentage': round((present_records / total_records * 100), 2) if total_records > 0 else 0,
        }
        
        return render(request, self.template_name, context)


class StudentAttendanceDetailView(LoginRequiredMixin, AttendanceAccessMixin, DetailView):
    """
    Detail view for individual student's attendance history.
    """
    model = Student
    template_name = 'attendance/student_detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        return Student.objects.filter(
            school=self.request.school,
            is_active=True
        ).select_related('user', 'class_assigned', 'section')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range (default: last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        
        if start_date_param:
            start_date = date.fromisoformat(start_date_param)
        if end_date_param:
            end_date = date.fromisoformat(end_date_param)
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            student=self.object,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        context['attendance_records'] = attendance_records
        
        # Calculate statistics
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status__in=['present', 'late', 'half_day']).count()
        absent_days = attendance_records.filter(status__in=['absent', 'excused']).count()
        late_days = attendance_records.filter(status='late').count()
        
        context['stats'] = {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': round((present_days / total_days * 100), 2) if total_days > 0 else 0,
        }
        
        return context
