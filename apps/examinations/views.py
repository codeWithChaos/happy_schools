from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View

from apps.accounts.models import Class, Section, Subject, AcademicYear
from apps.students.models import Student
from .models import Exam, ExamResult


class ExamAccessMixin(UserPassesTestMixin):
    """Mixin to ensure only admin and teachers can manage exams."""
    
    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']


class ExamListView(LoginRequiredMixin, ExamAccessMixin, ListView):
    """List view for exams."""
    model = Exam
    template_name = 'examinations/list.html'
    context_object_name = 'exams'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Exam.objects.filter(
            school=self.request.school
        ).select_related('academic_year').prefetch_related('classes')
        
        # Filters
        academic_year_id = self.request.GET.get('academic_year')
        exam_type = self.request.GET.get('exam_type')
        search = self.request.GET.get('search', '')
        
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.filter(school=self.request.school)
        context['exam_types'] = Exam.EXAM_TYPE_CHOICES
        context['academic_year_filter'] = self.request.GET.get('academic_year', '')
        context['exam_type_filter'] = self.request.GET.get('exam_type', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class ExamCreateView(LoginRequiredMixin, ExamAccessMixin, CreateView):
    """Create a new exam."""
    model = Exam
    template_name = 'examinations/form.html'
    fields = ['academic_year', 'name', 'exam_type', 'description', 'classes', 
              'start_date', 'end_date', 'result_declaration_date']
    success_url = reverse_lazy('examinations:list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter querysets by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.request.school)
        form.fields['classes'].queryset = Class.objects.filter(school=self.request.school)
        
        # Add CSS classes
        for field_name, field in form.fields.items():
            if field_name == 'classes':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'size': '5'})
            elif field_name == 'description':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'rows': '3'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        
        return form
    
    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, "Exam created successfully.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Exam'
        return context


class ExamUpdateView(LoginRequiredMixin, ExamAccessMixin, UpdateView):
    """Update an existing exam."""
    model = Exam
    template_name = 'examinations/form.html'
    fields = ['academic_year', 'name', 'exam_type', 'description', 'classes', 
              'start_date', 'end_date', 'result_declaration_date', 'is_result_published', 'is_active']
    success_url = reverse_lazy('examinations:list')
    
    def get_queryset(self):
        return Exam.objects.filter(school=self.request.school)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter querysets by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.request.school)
        form.fields['classes'].queryset = Class.objects.filter(school=self.request.school)
        
        # Add CSS classes
        for field_name, field in form.fields.items():
            if field_name in ['is_result_published', 'is_active']:
                field.widget.attrs.update({'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'})
            elif field_name == 'classes':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'size': '5'})
            elif field_name == 'description':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'rows': '3'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        
        return form
    
    def form_valid(self, form):
        messages.success(self.request, "Exam updated successfully.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Exam'
        return context


class ExamDeleteView(LoginRequiredMixin, ExamAccessMixin, DeleteView):
    """Delete an exam."""
    model = Exam
    template_name = 'examinations/confirm_delete.html'
    success_url = reverse_lazy('examinations:list')
    
    def get_queryset(self):
        return Exam.objects.filter(school=self.request.school)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Exam deleted successfully.")
        return super().delete(request, *args, **kwargs)


class ExamDetailView(LoginRequiredMixin, ExamAccessMixin, DetailView):
    """Detail view for an exam with results overview."""
    model = Exam
    template_name = 'examinations/detail.html'
    context_object_name = 'exam'
    
    def get_queryset(self):
        return Exam.objects.filter(school=self.request.school).prefetch_related('classes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        
        # Get results statistics
        results = ExamResult.objects.filter(exam=exam)
        context['total_results'] = results.count()
        context['total_students'] = results.values('student').distinct().count()
        
        # Calculate averages per subject
        subject_stats = results.values('subject__name').annotate(
            avg_marks=Avg('marks_obtained'),
            pass_count=Count('id', filter=Q(is_passed=True)),
            fail_count=Count('id', filter=Q(is_passed=False)),
            absent_count=Count('id', filter=Q(is_absent=True))
        ).order_by('subject__name')
        
        context['subject_stats'] = subject_stats
        
        return context


class EnterMarksView(LoginRequiredMixin, ExamAccessMixin, View):
    """View to enter marks for students."""
    
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, school=request.school)
        
        # Get filters
        class_id = request.GET.get('class')
        section_id = request.GET.get('section')
        subject_id = request.GET.get('subject')
        
        classes = exam.classes.all()
        sections = Section.objects.none()
        subjects = Subject.objects.filter(school=request.school)
        students = Student.objects.none()
        
        if class_id:
            sections = Section.objects.filter(class_obj_id=class_id)
        
        if class_id and section_id and subject_id:
            # Get students for the selected class and section
            students = Student.objects.filter(
                class_assigned_id=class_id,
                section_id=section_id,
                user__school=request.school
            ).select_related('user', 'class_assigned', 'section')
            
            # Get existing results
            existing_results = ExamResult.objects.filter(
                exam=exam,
                subject_id=subject_id,
                student__in=students
            ).select_related('student__user')
            
            # Create a dict for easy lookup
            results_dict = {result.student_id: result for result in existing_results}
            
            # Attach results to students
            for student in students:
                student.result = results_dict.get(student.id)
        
        context = {
            'exam': exam,
            'classes': classes,
            'sections': sections,
            'subjects': subjects,
            'students': students,
            'class_filter': class_id,
            'section_filter': section_id,
            'subject_filter': subject_id,
        }
        
        return render(request, 'examinations/enter_marks.html', context)
    
    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, school=request.school)
        
        class_id = request.POST.get('class')
        section_id = request.POST.get('section')
        subject_id = request.POST.get('subject')
        
        if not all([class_id, section_id, subject_id]):
            messages.error(request, "Please select class, section, and subject.")
            return redirect('examinations:enter_marks', exam_id=exam_id)
        
        subject = get_object_or_404(Subject, id=subject_id, school=request.school)
        students = Student.objects.filter(
            class_assigned_id=class_id,
            section_id=section_id,
            user__school=request.school
        )
        
        # Process form data
        for student in students:
            student_key = f"student_{student.id}"
            marks_key = f"marks_{student.id}"
            absent_key = f"absent_{student.id}"
            
            if student_key in request.POST:
                marks = request.POST.get(marks_key, 0)
                is_absent = absent_key in request.POST
                
                try:
                    marks = float(marks) if marks else 0
                    
                    # Create or update result
                    result, created = ExamResult.objects.update_or_create(
                        exam=exam,
                        student=student,
                        subject=subject,
                        defaults={
                            'marks_obtained': marks,
                            'max_marks': subject.total_marks,
                            'is_absent': is_absent,
                            'entered_by': request.user
                        }
                    )
                except ValueError:
                    messages.error(request, f"Invalid marks for {student.user.get_full_name()}")
                    continue
        
        messages.success(request, "Marks saved successfully.")
        return redirect(f"{request.path}?class={class_id}&section={section_id}&subject={subject_id}")


class StudentResultsView(LoginRequiredMixin, View):
    """View student results for an exam."""
    
    def get(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam, id=exam_id, school=request.school)
        student = get_object_or_404(Student, id=student_id, user__school=request.school)
        
        # Get all results for this student in this exam
        results = ExamResult.objects.filter(
            exam=exam,
            student=student
        ).select_related('subject').order_by('subject__name')
        
        # Calculate totals
        total_marks_obtained = sum(r.marks_obtained for r in results if not r.is_absent)
        total_max_marks = sum(r.max_marks for r in results)
        percentage = (total_marks_obtained / total_max_marks * 100) if total_max_marks > 0 else 0
        
        # Check if passed all subjects
        all_passed = all(r.is_passed for r in results if not r.is_absent)
        
        context = {
            'exam': exam,
            'student': student,
            'results': results,
            'total_marks_obtained': total_marks_obtained,
            'total_max_marks': total_max_marks,
            'percentage': round(percentage, 2),
            'all_passed': all_passed,
        }
        
        return render(request, 'examinations/student_results.html', context)


class ExamReportView(LoginRequiredMixin, ExamAccessMixin, View):
    """Generate exam report with class-wise and subject-wise analysis."""
    
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, school=request.school)
        
        class_id = request.GET.get('class')
        
        # Class-wise statistics
        class_stats = []
        classes = exam.classes.all()
        
        for cls in classes:
            if class_id and str(cls.id) != class_id:
                continue
            
            students = Student.objects.filter(
                class_assigned=cls,
                user__school=request.school
            )
            
            results = ExamResult.objects.filter(
                exam=exam,
                student__class_assigned=cls
            )
            
            total_students = students.count()
            appeared = results.values('student').distinct().count()
            passed = results.filter(is_passed=True).values('student').distinct().count()
            
            if total_students > 0:
                avg_percentage = results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
                
                class_stats.append({
                    'class': cls,
                    'total_students': total_students,
                    'appeared': appeared,
                    'passed': passed,
                    'failed': appeared - passed,
                    'pass_percentage': round((passed / appeared * 100) if appeared > 0 else 0, 2),
                    'avg_marks': round(avg_percentage, 2),
                })
        
        context = {
            'exam': exam,
            'class_stats': class_stats,
            'classes': classes,
            'class_filter': class_id,
        }
        
        return render(request, 'examinations/report.html', context)
