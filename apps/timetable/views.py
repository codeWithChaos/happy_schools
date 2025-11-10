from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.core.exceptions import ValidationError

from apps.accounts.models import Class, Section, Subject, AcademicYear, User
from .models import Timetable


class TimetableAccessMixin(UserPassesTestMixin):
    """Mixin to ensure only admin and teachers can access timetable views."""
    
    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']


class TimetableListView(LoginRequiredMixin, TimetableAccessMixin, ListView):
    """List view for class timetables."""
    model = Timetable
    template_name = 'timetable/list.html'
    context_object_name = 'timetables'
    
    def get_queryset(self):
        queryset = Timetable.objects.filter(
            school=self.request.school,
            is_active=True
        ).select_related(
            'class_assigned',
            'section',
            'subject',
            'teacher',
            'academic_year'
        ).order_by('class_assigned__name', 'section__name', 'day', 'period_number')
        
        # Filters
        class_id = self.request.GET.get('class')
        section_id = self.request.GET.get('section')
        academic_year_id = self.request.GET.get('academic_year')
        
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        if class_id:
            queryset = queryset.filter(class_assigned_id=class_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(school=self.request.school)
        context['academic_years'] = AcademicYear.objects.filter(school=self.request.school)
        context['class_filter'] = self.request.GET.get('class', '')
        context['section_filter'] = self.request.GET.get('section', '')
        context['academic_year_filter'] = self.request.GET.get('academic_year', '')
        
        # Get sections for selected class
        if context['class_filter']:
            context['sections'] = Section.objects.filter(
                class_obj_id=context['class_filter']
            )
        else:
            context['sections'] = Section.objects.filter(
                class_obj__school=self.request.school
            )
        
        return context


class ClassTimetableView(LoginRequiredMixin, TimetableAccessMixin, View):
    """View timetable for a specific class and section."""
    
    def get(self, request, class_id, section_id):
        class_obj = get_object_or_404(Class, id=class_id, school=request.school)
        section = get_object_or_404(Section, id=section_id, class_assigned=class_obj)
        
        # Get current academic year or filter
        academic_year_id = request.GET.get('academic_year')
        if academic_year_id:
            academic_year = get_object_or_404(AcademicYear, id=academic_year_id, school=request.school)
        else:
            academic_year = AcademicYear.objects.filter(
                school=request.school,
                is_current=True
            ).first()
        
        if not academic_year:
            messages.error(request, "No academic year found. Please create one first.")
            return redirect('timetable:list')
        
        # Get timetable entries
        timetable_entries = Timetable.objects.filter(
            school=request.school,
            class_assigned=class_obj,
            section=section,
            academic_year=academic_year,
            is_active=True
        ).select_related('subject', 'teacher').order_by('day', 'period_number')
        
        # Organize by day and period
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        periods = {}
        timetable_grid = {}
        
        for entry in timetable_entries:
            if entry.period_number not in periods:
                periods[entry.period_number] = {
                    'start_time': entry.start_time,
                    'end_time': entry.end_time
                }
            if entry.day not in timetable_grid:
                timetable_grid[entry.day] = {}
            timetable_grid[entry.day][entry.period_number] = entry
        
        # Sort periods by number
        sorted_periods = sorted(periods.items())
        
        context = {
            'class_obj': class_obj,
            'section': section,
            'academic_year': academic_year,
            'academic_years': AcademicYear.objects.filter(school=request.school),
            'days': days,
            'periods': sorted_periods,
            'timetable_grid': timetable_grid,
        }
        
        from django.shortcuts import render
        return render(request, 'timetable/class_view.html', context)


class TeacherTimetableView(LoginRequiredMixin, View):
    """View timetable for a specific teacher."""
    
    def get(self, request, teacher_id=None):
        # If no teacher_id, show current user's timetable (if they're a teacher)
        if teacher_id:
            teacher = get_object_or_404(User, id=teacher_id, role='teacher', school=request.school)
        else:
            if request.user.role == 'teacher':
                teacher = request.user
            else:
                messages.error(request, "Please select a teacher to view their timetable.")
                return redirect('timetable:list')
        
        # Get current academic year or filter
        academic_year_id = request.GET.get('academic_year')
        if academic_year_id:
            academic_year = get_object_or_404(AcademicYear, id=academic_year_id, school=request.school)
        else:
            academic_year = AcademicYear.objects.filter(
                school=request.school,
                is_current=True
            ).first()
        
        if not academic_year:
            messages.error(request, "No academic year found.")
            return redirect('timetable:list')
        
        # Get timetable entries
        timetable_entries = Timetable.objects.filter(
            school=request.school,
            teacher=teacher,
            academic_year=academic_year,
            is_active=True
        ).select_related('class_assigned', 'section', 'subject').order_by('day', 'period_number')
        
        # Organize by day and period
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        periods = {}
        timetable_grid = {}
        
        for entry in timetable_entries:
            if entry.period_number not in periods:
                periods[entry.period_number] = {
                    'start_time': entry.start_time,
                    'end_time': entry.end_time
                }
            if entry.day not in timetable_grid:
                timetable_grid[entry.day] = {}
            timetable_grid[entry.day][entry.period_number] = entry
        
        # Sort periods by number
        sorted_periods = sorted(periods.items())
        
        context = {
            'teacher': teacher,
            'academic_year': academic_year,
            'academic_years': AcademicYear.objects.filter(school=request.school),
            'days': days,
            'periods': sorted_periods,
            'timetable_grid': timetable_grid,
            'teachers': User.objects.filter(school=request.school, role='teacher') if request.user.role == 'admin' else None,
        }
        
        from django.shortcuts import render
        return render(request, 'timetable/teacher_view.html', context)


class TimetableCreateView(LoginRequiredMixin, TimetableAccessMixin, CreateView):
    """Create a new timetable entry."""
    model = Timetable
    template_name = 'timetable/form.html'
    fields = [
        'academic_year', 'class_assigned', 'section', 'day', 'period_number',
        'subject', 'teacher', 'start_time', 'end_time', 'room_number',
        'is_break', 'is_lab', 'remarks'
    ]
    success_url = reverse_lazy('timetable:list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter querysets by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.request.school)
        form.fields['class_assigned'].queryset = Class.objects.filter(school=self.request.school)
        form.fields['section'].queryset = Section.objects.filter(class_obj__school=self.request.school)
        form.fields['subject'].queryset = Subject.objects.filter(school=self.request.school)
        form.fields['teacher'].queryset = User.objects.filter(school=self.request.school, role='teacher')
        
        # Add CSS classes
        for field_name, field in form.fields.items():
            if field_name in ['is_break', 'is_lab']:
                field.widget.attrs.update({'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        
        return form
    
    def form_valid(self, form):
        form.instance.school = self.request.school
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Timetable entry created successfully.")
            return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Timetable Entry'
        return context


class TimetableUpdateView(LoginRequiredMixin, TimetableAccessMixin, UpdateView):
    """Update an existing timetable entry."""
    model = Timetable
    template_name = 'timetable/form.html'
    fields = [
        'academic_year', 'class_assigned', 'section', 'day', 'period_number',
        'subject', 'teacher', 'start_time', 'end_time', 'room_number',
        'is_break', 'is_lab', 'remarks', 'is_active'
    ]
    success_url = reverse_lazy('timetable:list')
    
    def get_queryset(self):
        return Timetable.objects.filter(school=self.request.school)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter querysets by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.request.school)
        form.fields['class_assigned'].queryset = Class.objects.filter(school=self.request.school)
        form.fields['section'].queryset = Section.objects.filter(class_obj__school=self.request.school)
        form.fields['subject'].queryset = Subject.objects.filter(school=self.request.school)
        form.fields['teacher'].queryset = User.objects.filter(school=self.request.school, role='teacher')
        
        # Add CSS classes
        for field_name, field in form.fields.items():
            if field_name in ['is_break', 'is_lab', 'is_active']:
                field.widget.attrs.update({'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        
        return form
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Timetable entry updated successfully.")
            return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Timetable Entry'
        return context


class TimetableDeleteView(LoginRequiredMixin, TimetableAccessMixin, DeleteView):
    """Delete a timetable entry."""
    model = Timetable
    template_name = 'timetable/confirm_delete.html'
    success_url = reverse_lazy('timetable:list')
    
    def get_queryset(self):
        return Timetable.objects.filter(school=self.request.school)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Timetable entry deleted successfully.")
        return super().delete(request, *args, **kwargs)
