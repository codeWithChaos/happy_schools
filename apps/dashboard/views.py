from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value, DecimalField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from apps.accounts.models import User, Class
from apps.students.models import Student as StudentProfile, Teacher
from apps.attendance.models import Attendance
from apps.fees.models import FeeStructure, FeePayment
from apps.examinations.models import Exam, ExamResult
from apps.communications.models import Announcement, Message, Notification


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view - redirects to role-specific dashboard
    """
    template_name = 'dashboard/index.html'
    
    def get_template_names(self):
        user = self.request.user
        if user.role == 'admin':
            return ['dashboard/admin_dashboard.html']
        elif user.role == 'teacher':
            return ['dashboard/teacher_dashboard.html']
        elif user.role == 'student':
            return ['dashboard/student_dashboard.html']
        elif user.role == 'parent':
            return ['dashboard/parent_dashboard.html']
        return ['dashboard/index.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dashboard'
        user = self.request.user
        
        if user.role == 'admin':
            context.update(self.get_admin_context())
        elif user.role == 'teacher':
            context.update(self.get_teacher_context())
        elif user.role == 'student':
            context.update(self.get_student_context())
        elif user.role == 'parent':
            context.update(self.get_parent_context())
        
        return context
    
    def get_admin_context(self):
        """Get admin dashboard statistics"""
        school = self.request.school
        today = timezone.now().date()
        
        # Student statistics
        total_students = StudentProfile.objects.filter(school=school, is_active=True).count()
        total_teachers = Teacher.objects.filter(school=school, is_active=True).count()
        total_classes = Class.objects.filter(school=school).count()
        
        # Attendance statistics for today
        today_attendance = Attendance.objects.filter(
            student__school=school,
            date=today
        ).aggregate(
            total=Count('id'),
            present=Count(Case(When(status='present', then=1))),
            absent=Count(Case(When(status='absent', then=1))),
            late=Count(Case(When(status='late', then=1)))
        )
        
        attendance_percentage = 0
        if today_attendance['total'] > 0:
            attendance_percentage = round(
                (today_attendance['present'] / today_attendance['total']) * 100, 1
            )
        
        # Fee statistics
        fee_stats = FeePayment.objects.filter(
            student__school=school
        ).aggregate(
            total_collected=Sum('amount_paid'),
            pending_amount=Sum(
                Case(
                    When(payment_status='pending', then=F('total_amount') - F('amount_paid')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            )
        )
        
        total_collected = fee_stats['total_collected'] or Decimal('0')
        pending_amount = fee_stats['pending_amount'] or Decimal('0')
        
        # Recent exams
        recent_exams = Exam.objects.filter(
            school=school
        ).prefetch_related('classes').order_by('-start_date')[:5]
        
        # Upcoming exams
        upcoming_exams = Exam.objects.filter(
            school=school,
            start_date__gte=today
        ).prefetch_related('classes').order_by('start_date')[:5]
        
        # Recent announcements
        recent_announcements = Announcement.objects.filter(
            school=school,
            is_published=True
        ).select_related('created_by').order_by('-created_at')[:5]
        
        # Attendance trend (last 7 days)
        week_ago = today - timedelta(days=7)
        attendance_trend = Attendance.objects.filter(
            student__school=school,
            date__gte=week_ago,
            date__lte=today
        ).values('date').annotate(
            total=Count('id'),
            present=Count(Case(When(status='present', then=1))),
            percentage=Case(
                When(total__gt=0, then=F('present') * 100.0 / F('total')),
                default=Value(0),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('date')
        
        # Fee collection trend (last 30 days)
        month_ago = today - timedelta(days=30)
        fee_trend = FeePayment.objects.filter(
            student__school=school,
            payment_date__gte=month_ago,
            payment_date__lte=today
        ).annotate(
            day=TruncDate('payment_date')
        ).values('day').annotate(
            total_amount=Sum('amount_paid')
        ).order_by('day')
        
        # Recent activities
        recent_payments = FeePayment.objects.filter(
            student__school=school
        ).select_related('student__user', 'collected_by').order_by('-payment_date')[:5]
        
        # Unread messages count
        unread_messages = Message.objects.filter(
            recipient=self.request.user,
            is_read=False,
            is_deleted_by_recipient=False
        ).count()
        
        # Unread notifications count
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        return {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'today_attendance': today_attendance,
            'attendance_percentage': attendance_percentage,
            'total_collected': total_collected,
            'pending_amount': pending_amount,
            'recent_exams': recent_exams,
            'upcoming_exams': upcoming_exams,
            'recent_announcements': recent_announcements,
            'attendance_trend': list(attendance_trend),
            'fee_trend': list(fee_trend),
            'recent_payments': recent_payments,
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
        }
    
    def get_teacher_context(self):
        """Get teacher dashboard statistics"""
        school = self.request.school
        teacher = Teacher.objects.filter(user=self.request.user).first()
        today = timezone.now().date()
        
        # Classes taught by this teacher
        teacher_classes = Class.objects.filter(
            school=school,
            class_teacher=teacher
        ) if teacher else Class.objects.none()
        
        total_classes = teacher_classes.count()
        
        # Students in teacher's classes
        total_students = StudentProfile.objects.filter(
            school=school,
            current_class__in=teacher_classes,
            is_active=True
        ).count()
        
        # Today's attendance for teacher's classes
        today_attendance = Attendance.objects.filter(
            student__current_class__in=teacher_classes,
            date=today
        ).aggregate(
            total=Count('id'),
            present=Count(Case(When(status='present', then=1))),
            absent=Count(Case(When(status='absent', then=1)))
        )
        
        # Upcoming exams for teacher's classes
        upcoming_exams = Exam.objects.filter(
            school=school,
            classes__in=teacher_classes,
            start_date__gte=today
        ).prefetch_related('classes').order_by('start_date')[:5]
        
        # Recent announcements
        recent_announcements = Announcement.objects.filter(
            school=school,
            is_published=True,
            target_audience__in=['all', 'teachers']
        ).select_related('created_by').order_by('-created_at')[:5]
        
        # Unread messages
        unread_messages = Message.objects.filter(
            recipient=self.request.user,
            is_read=False,
            is_deleted_by_recipient=False
        ).count()
        
        # Unread notifications
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        return {
            'total_classes': total_classes,
            'total_students': total_students,
            'today_attendance': today_attendance,
            'upcoming_exams': upcoming_exams,
            'recent_announcements': recent_announcements,
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
            'teacher_classes': teacher_classes,
        }
    
    def get_student_context(self):
        """Get student dashboard statistics"""
        school = self.request.school
        student = StudentProfile.objects.filter(user=self.request.user).first()
        today = timezone.now().date()
        
        if not student:
            return {}
        
        # Attendance statistics (last 30 days)
        month_ago = today - timedelta(days=30)
        attendance_stats = Attendance.objects.filter(
            student=student,
            date__gte=month_ago
        ).aggregate(
            total=Count('id'),
            present=Count(Case(When(status='present', then=1))),
            absent=Count(Case(When(status='absent', then=1))),
            late=Count(Case(When(status='late', then=1)))
        )
        
        attendance_percentage = 0
        if attendance_stats['total'] > 0:
            attendance_percentage = round(
                (attendance_stats['present'] / attendance_stats['total']) * 100, 1
            )
        
        # Fee statistics
        fee_stats = FeePayment.objects.filter(
            student=student
        ).aggregate(
            total_paid=Sum('amount_paid'),
            total_due=Sum(
                Case(
                    When(payment_status='pending', then=F('total_amount') - F('amount_paid')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            )
        )
        
        # Recent exam results
        recent_results = ExamResult.objects.filter(
            student=student
        ).select_related('exam').order_by('-exam__start_date')[:5]
        
        # Upcoming exams
        upcoming_exams = Exam.objects.filter(
            school=school,
            classes=student.current_class,
            start_date__gte=today
        ).order_by('start_date')[:5]
        
        # Recent announcements
        recent_announcements = Announcement.objects.filter(
            school=school,
            is_published=True,
            target_audience__in=['all', 'students']
        ).select_related('created_by').order_by('-created_at')[:5]
        
        # Unread messages
        unread_messages = Message.objects.filter(
            recipient=self.request.user,
            is_read=False,
            is_deleted_by_recipient=False
        ).count()
        
        # Unread notifications
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        return {
            'student': student,
            'attendance_stats': attendance_stats,
            'attendance_percentage': attendance_percentage,
            'total_paid': fee_stats['total_paid'] or Decimal('0'),
            'total_due': fee_stats['total_due'] or Decimal('0'),
            'recent_results': recent_results,
            'upcoming_exams': upcoming_exams,
            'recent_announcements': recent_announcements,
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
        }
    
    def get_parent_context(self):
        """Get parent dashboard statistics"""
        school = self.request.school
        today = timezone.now().date()
        
        # Get children (students with this parent)
        children = StudentProfile.objects.filter(
            school=school,
            parent=self.request.user,
            is_active=True
        ).select_related('current_class', 'user')
        
        children_data = []
        for child in children:
            # Attendance stats (last 30 days)
            month_ago = today - timedelta(days=30)
            attendance_stats = Attendance.objects.filter(
                student=child,
                date__gte=month_ago
            ).aggregate(
                total=Count('id'),
                present=Count(Case(When(status='present', then=1))),
                absent=Count(Case(When(status='absent', then=1)))
            )
            
            attendance_percentage = 0
            if attendance_stats['total'] > 0:
                attendance_percentage = round(
                    (attendance_stats['present'] / attendance_stats['total']) * 100, 1
                )
            
            # Fee stats
            fee_stats = FeePayment.objects.filter(
                student=child
            ).aggregate(
                total_due=Sum(
                    Case(
                        When(payment_status='pending', then=F('total_amount') - F('amount_paid')),
                        default=Value(0),
                        output_field=DecimalField()
                    )
                )
            )
            
            # Recent results
            recent_results = ExamResult.objects.filter(
                student=child
            ).select_related('exam').order_by('-exam__start_date')[:3]
            
            children_data.append({
                'student': child,
                'attendance_percentage': attendance_percentage,
                'total_due': fee_stats['total_due'] or Decimal('0'),
                'recent_results': recent_results,
            })
        
        # Recent announcements for parents
        recent_announcements = Announcement.objects.filter(
            school=school,
            is_published=True,
            target_audience__in=['all', 'parents']
        ).select_related('created_by').order_by('-created_at')[:5]
        
        # Unread messages
        unread_messages = Message.objects.filter(
            recipient=self.request.user,
            is_read=False,
            is_deleted_by_recipient=False
        ).count()
        
        # Unread notifications
        unread_notifications = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        return {
            'children': children_data,
            'recent_announcements': recent_announcements,
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
        }


class SearchView(LoginRequiredMixin, TemplateView):
    """
    Global search view
    """
    template_name = 'dashboard/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        context['page_title'] = f'Search: {query}' if query else 'Search'
        
        if query and len(query) >= 2:
            school = self.request.school
            user = self.request.user
            
            # Search students (if admin or teacher)
            if user.role in ['admin', 'teacher']:
                students = StudentProfile.objects.filter(
                    school=school,
                    user__first_name__icontains=query
                ) | StudentProfile.objects.filter(
                    school=school,
                    user__last_name__icontains=query
                ) | StudentProfile.objects.filter(
                    school=school,
                    admission_number__icontains=query
                )
                context['students'] = students.select_related('user', 'current_class')[:10]
            
            # Search teachers (if admin)
            if user.role == 'admin':
                teachers = Teacher.objects.filter(
                    school=school,
                    user__first_name__icontains=query
                ) | Teacher.objects.filter(
                    school=school,
                    user__last_name__icontains=query
                ) | Teacher.objects.filter(
                    school=school,
                    employee_id__icontains=query
                )
                context['teachers'] = teachers.select_related('user')[:10]
            
            # Search announcements
            announcements = Announcement.objects.filter(
                school=school,
                is_published=True,
                title__icontains=query
            ) | Announcement.objects.filter(
                school=school,
                is_published=True,
                content__icontains=query
            )
            context['announcements'] = announcements.select_related('created_by').order_by('-created_at')[:10]
            
            # Search exams (if not parent)
            if user.role != 'parent':
                exams = Exam.objects.filter(
                    school=school,
                    name__icontains=query
                )
                context['exams'] = exams.prefetch_related('classes')[:10]
        
        return context
