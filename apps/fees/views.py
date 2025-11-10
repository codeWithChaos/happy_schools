"""
Views for the fees app.
Handles fee structure management, student fee assignments, and payment collection.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from datetime import date, datetime
import uuid

from apps.accounts.models import Class, AcademicYear
from apps.students.models import Student
from .models import FeeStructure, FeePayment


class FeeAccessMixin(UserPassesTestMixin):
    """Mixin to restrict fee views to admin users only."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'


class FeeStructureListView(LoginRequiredMixin, FeeAccessMixin, ListView):
    """
    List view for fee structures.
    Shows all fee structures with filtering by academic year, class, and fee type.
    """
    model = FeeStructure
    template_name = 'fees/structure_list.html'
    context_object_name = 'fee_structures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FeeStructure.objects.select_related(
            'school',
            'academic_year',
            'class_applicable'
        ).filter(school=self.request.school)
        
        # Filter by academic year
        academic_year_id = self.request.GET.get('academic_year')
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        
        # Filter by class
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(class_applicable_id=class_id)
        
        # Filter by fee type
        fee_type = self.request.GET.get('fee_type')
        if fee_type:
            queryset = queryset.filter(fee_type=fee_type)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset.order_by('-academic_year', 'class_applicable__name', 'fee_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['academic_years'] = AcademicYear.objects.filter(
            school=self.request.school
        ).order_by('-year')
        
        context['classes'] = Class.objects.filter(
            school=self.request.school,
            is_active=True
        ).order_by('name')
        
        context['fee_type_choices'] = FeeStructure.FEE_TYPE_CHOICES
        
        # Current filter values
        context['current_academic_year'] = self.request.GET.get('academic_year', '')
        context['current_class'] = self.request.GET.get('class', '')
        context['current_fee_type'] = self.request.GET.get('fee_type', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        
        return context


class FeeStructureCreateView(LoginRequiredMixin, FeeAccessMixin, CreateView):
    """Create view for fee structures."""
    model = FeeStructure
    template_name = 'fees/structure_form.html'
    fields = ['name', 'fee_type', 'amount', 'academic_year', 'class_applicable', 
              'frequency', 'due_date', 'late_fee_applicable', 'late_fee_amount', 'description']
    success_url = reverse_lazy('fees:structure_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter academic years and classes by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(
            school=self.request.school
        ).order_by('-year')
        form.fields['class_applicable'].queryset = Class.objects.filter(
            school=self.request.school,
            is_active=True
        ).order_by('name')
        return form
    
    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Fee structure created successfully.')
        return super().form_valid(form)


class FeeStructureUpdateView(LoginRequiredMixin, FeeAccessMixin, UpdateView):
    """Update view for fee structures."""
    model = FeeStructure
    template_name = 'fees/structure_form.html'
    fields = ['name', 'fee_type', 'amount', 'academic_year', 'class_applicable', 
              'frequency', 'due_date', 'late_fee_applicable', 'late_fee_amount', 'description', 'is_active']
    success_url = reverse_lazy('fees:structure_list')
    
    def get_queryset(self):
        return FeeStructure.objects.filter(school=self.request.school)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter academic years and classes by school
        form.fields['academic_year'].queryset = AcademicYear.objects.filter(
            school=self.request.school
        ).order_by('-year')
        form.fields['class_applicable'].queryset = Class.objects.filter(
            school=self.request.school,
            is_active=True
        ).order_by('name')
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Fee structure updated successfully.')
        return super().form_valid(form)


class FeeStructureDeleteView(LoginRequiredMixin, FeeAccessMixin, DeleteView):
    """Delete view for fee structures."""
    model = FeeStructure
    template_name = 'fees/structure_confirm_delete.html'
    success_url = reverse_lazy('fees:structure_list')
    
    def get_queryset(self):
        return FeeStructure.objects.filter(school=self.request.school)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Fee structure deleted successfully.')
        return super().delete(request, *args, **kwargs)


class StudentFeeListView(LoginRequiredMixin, FeeAccessMixin, ListView):
    """List view for student fees with payment status."""
    model = Student
    template_name = 'fees/student_fee_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Student.objects.select_related(
            'user',
            'class_assigned',
            'section'
        ).filter(school=self.request.school, is_active=True)
        
        # Search by student name or admission number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(admission_number__icontains=search)
            )
        
        # Filter by class
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(class_assigned_id=class_id)
        
        # Filter by section
        section_id = self.request.GET.get('section')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        return queryset.order_by('class_assigned__name', 'section__name', 'roll_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['classes'] = Class.objects.filter(
            school=self.request.school,
            is_active=True
        ).order_by('name')
        
        context['search'] = self.request.GET.get('search', '')
        context['current_class'] = self.request.GET.get('class', '')
        context['current_section'] = self.request.GET.get('section', '')
        
        # Calculate fee statistics for each student
        for student in context['students']:
            # Get applicable fee structures for this student's class
            fee_structures = FeeStructure.objects.filter(
                school=self.request.school,
                class_applicable=student.class_assigned,
                is_active=True
            )
            
            # Get payments made by this student
            payments = FeePayment.objects.filter(
                student=student,
                payment_status='completed'
            )
            
            # Calculate totals
            student.total_fees = fee_structures.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            student.total_paid = payments.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            student.balance = student.total_fees - student.total_paid
        
        return context


class CollectFeeView(LoginRequiredMixin, FeeAccessMixin, View):
    """View for collecting fees from students."""
    template_name = 'fees/collect_fee.html'
    
    def get(self, request, student_id):
        student = get_object_or_404(
            Student.objects.select_related('user', 'class_assigned', 'section'),
            id=student_id,
            school=request.school,
            is_active=True
        )
        
        # Get applicable fee structures for this student
        fee_structures = FeeStructure.objects.filter(
            school=request.school,
            class_applicable=student.class_assigned,
            is_active=True
        ).order_by('fee_type')
        
        # Get existing payments
        payments = FeePayment.objects.filter(
            student=student,
            payment_status='completed'
        ).select_related('fee_structure')
        
        # Calculate paid amounts per fee structure
        paid_amounts = {}
        for payment in payments:
            fee_id = payment.fee_structure_id
            if fee_id not in paid_amounts:
                paid_amounts[fee_id] = 0
            paid_amounts[fee_id] += payment.total_amount
        
        # Prepare fee structure data with balance
        fee_data = []
        for fee in fee_structures:
            paid = paid_amounts.get(fee.id, 0)
            balance = fee.amount - paid
            
            # Check if late fee is applicable
            late_fee = 0
            if fee.late_fee_applicable and date.today() > fee.due_date and balance > 0:
                late_fee = fee.late_fee_amount
            
            fee_data.append({
                'fee_structure': fee,
                'paid': paid,
                'balance': balance,
                'late_fee': late_fee,
            })
        
        context = {
            'student': student,
            'fee_data': fee_data,
            'payment_methods': FeePayment.PAYMENT_METHOD_CHOICES,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, student_id):
        student = get_object_or_404(
            Student,
            id=student_id,
            school=request.school,
            is_active=True
        )
        
        # Get selected fee structure
        fee_structure_id = request.POST.get('fee_structure')
        fee_structure = get_object_or_404(
            FeeStructure,
            id=fee_structure_id,
            school=request.school
        )
        
        # Get payment details
        amount_paid = float(request.POST.get('amount_paid', 0))
        late_fee = float(request.POST.get('late_fee', 0))
        discount = float(request.POST.get('discount', 0))
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date', date.today())
        remarks = request.POST.get('remarks', '')
        
        # Optional: check/card details
        transaction_id = request.POST.get('transaction_id', '')
        check_number = request.POST.get('check_number', '')
        check_date = request.POST.get('check_date', None)
        bank_name = request.POST.get('bank_name', '')
        
        # Generate unique receipt number
        receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create payment record
        payment = FeePayment.objects.create(
            student=student,
            fee_structure=fee_structure,
            amount_paid=amount_paid,
            late_fee=late_fee,
            discount=discount,
            payment_date=payment_date,
            payment_method=payment_method,
            payment_status='completed',
            transaction_id=transaction_id,
            receipt_number=receipt_number,
            check_number=check_number,
            check_date=check_date if check_date else None,
            bank_name=bank_name,
            collected_by=request.user,
            remarks=remarks
        )
        
        messages.success(
            request,
            f'Payment collected successfully. Receipt Number: {receipt_number}'
        )
        
        return redirect('fees:receipt', payment_id=payment.id)


class FeeReceiptView(LoginRequiredMixin, DetailView):
    """View for displaying fee receipt."""
    model = FeePayment
    template_name = 'fees/receipt.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'
    
    def get_queryset(self):
        return FeePayment.objects.select_related(
            'student__user',
            'student__class_assigned',
            'student__section',
            'fee_structure',
            'collected_by'
        ).filter(student__school=self.request.school)


class PaymentHistoryView(LoginRequiredMixin, FeeAccessMixin, ListView):
    """List view for payment history."""
    model = FeePayment
    template_name = 'fees/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = FeePayment.objects.select_related(
            'student__user',
            'student__class_assigned',
            'fee_structure',
            'collected_by'
        ).filter(student__school=self.request.school)
        
        # Search by student name or receipt number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(receipt_number__icontains=search) |
                Q(transaction_id__icontains=search)
            )
        
        # Filter by payment method
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by payment status
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        return queryset.order_by('-payment_date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['payment_methods'] = FeePayment.PAYMENT_METHOD_CHOICES
        context['payment_statuses'] = FeePayment.PAYMENT_STATUS_CHOICES
        
        # Current filter values
        context['search'] = self.request.GET.get('search', '')
        context['current_payment_method'] = self.request.GET.get('payment_method', '')
        context['current_payment_status'] = self.request.GET.get('payment_status', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        # Calculate statistics
        queryset = self.get_queryset()
        context['total_payments'] = queryset.count()
        context['total_amount'] = queryset.filter(
            payment_status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        return context


class FeeReportView(LoginRequiredMixin, FeeAccessMixin, View):
    """View for fee collection reports and analytics."""
    template_name = 'fees/report.html'
    
    def get(self, request):
        # Get date range (default: current month)
        today = date.today()
        start_date = request.GET.get('start_date', date(today.year, today.month, 1).isoformat())
        end_date = request.GET.get('end_date', today.isoformat())
        
        # Get payments in date range
        payments = FeePayment.objects.filter(
            student__school=request.school,
            payment_date__range=[start_date, end_date],
            payment_status='completed'
        )
        
        # Overall statistics
        total_collected = payments.aggregate(total=Sum('total_amount'))['total'] or 0
        total_transactions = payments.count()
        
        # By payment method
        by_method = payments.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # By fee type
        by_fee_type = payments.values(
            'fee_structure__fee_type',
            'fee_structure__name'
        ).annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # By class
        by_class = payments.values(
            'student__class_assigned__name'
        ).annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('student__class_assigned__name')
        
        # Daily collection (for chart)
        daily_collection = payments.values('payment_date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('payment_date')
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'total_collected': total_collected,
            'total_transactions': total_transactions,
            'by_method': by_method,
            'by_fee_type': by_fee_type,
            'by_class': by_class,
            'daily_collection': daily_collection,
        }
        
        return render(request, self.template_name, context)

