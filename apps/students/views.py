from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import Student, Guardian, Teacher
from apps.accounts.models import Class
from .forms import StudentForm, StudentUpdateForm


class StudentAccessMixin(UserPassesTestMixin):
    """Mixin to restrict student views to admin and teacher roles"""
    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']


class StudentListView(LoginRequiredMixin, StudentAccessMixin, ListView):
    """Student list view with filtering and search"""
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.filter(school=self.request.school).select_related(
            'user', 'class_assigned'
        ).prefetch_related('guardians')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(admission_number__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        # Filter by class
        class_id = self.request.GET.get('class', '')
        if class_id:
            queryset = queryset.filter(class_assigned_id=class_id)
        
        # Filter by active status
        status = self.request.GET.get('status', '')
        if status:
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
        
        # Filter by gender
        gender = self.request.GET.get('gender', '')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        return queryset.order_by('admission_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Students'
        context['classes'] = Class.objects.filter(school=self.request.school)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_class'] = self.request.GET.get('class', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_gender'] = self.request.GET.get('gender', '')
        context['total_students'] = Student.objects.filter(school=self.request.school).count()
        context['active_students'] = Student.objects.filter(school=self.request.school, is_active=True).count()
        return context


class StudentDetailView(LoginRequiredMixin, StudentAccessMixin, DetailView):
    """Student detail/profile view"""
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        return Student.objects.filter(school=self.request.school).select_related(
            'user', 'class_assigned'
        ).prefetch_related('guardians')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Student Profile: {self.object.user.get_full_name()}'
        return context


class StudentCreateView(LoginRequiredMixin, StudentAccessMixin, CreateView):
    """Create new student"""
    model = Student
    template_name = 'students/form.html'
    form_class = StudentForm
    
    def test_func(self):
        # Only admin can create students
        return self.request.user.role == 'admin'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs
    
    def form_valid(self, form):
        try:
            form.instance.school = self.request.school
            student = form.save()
            messages.success(
                self.request, 
                f'Student {student.user.get_full_name()} ({student.admission_number}) created successfully!'
            )
            self.object = student
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating student: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Show all form errors as messages
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f'{error}')
                else:
                    messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('students:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New Student'
        context['form_action'] = 'Create'
        return context


class StudentUpdateView(LoginRequiredMixin, StudentAccessMixin, UpdateView):
    """Update existing student"""
    model = Student
    template_name = 'students/form.html'
    form_class = StudentUpdateForm
    
    def test_func(self):
        # Only admin can update students
        return self.request.user.role == 'admin'
    
    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'Student {form.instance.admission_number} updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('students:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Student: {self.object.user.get_full_name()}'
        context['form_action'] = 'Update'
        return context


class StudentDeleteView(LoginRequiredMixin, StudentAccessMixin, DeleteView):
    """Delete student"""
    model = Student
    template_name = 'students/confirm_delete.html'
    success_url = reverse_lazy('students:list')
    
    def test_func(self):
        # Only admin can delete students
        return self.request.user.role == 'admin'
    
    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(request, f'Student {student.admission_number} deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Student: {self.object.user.get_full_name()}'
        return context
