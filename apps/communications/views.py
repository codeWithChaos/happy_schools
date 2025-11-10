from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Case, When, BooleanField
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.accounts.models import Class, User
from .models import Announcement, Message, Notification


# ============================================================================
# ANNOUNCEMENT VIEWS
# ============================================================================

class AnnouncementAccessMixin(UserPassesTestMixin):
    """Mixin to restrict announcement management to admin and teachers"""
    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']


class AnnouncementListView(LoginRequiredMixin, ListView):
    """List all announcements"""
    model = Announcement
    template_name = 'communications/announcements/list.html'
    context_object_name = 'announcements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Announcement.objects.filter(
            school=self.request.school
        ).select_related('created_by').prefetch_related('target_classes')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(is_published=True)
        elif status == 'draft':
            queryset = queryset.filter(is_published=False)
        elif status == 'expired':
            queryset = queryset.filter(expiry_date__lt=timezone.now())
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by target audience
        target = self.request.GET.get('target')
        if target:
            queryset = queryset.filter(target_audience=target)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Announcements'
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['target_filter'] = self.request.GET.get('target', '')
        context['search'] = self.request.GET.get('search', '')
        context['priorities'] = Announcement.PRIORITY_CHOICES
        context['target_audiences'] = Announcement.TARGET_AUDIENCE_CHOICES
        return context


class AnnouncementCreateView(AnnouncementAccessMixin, LoginRequiredMixin, CreateView):
    """Create new announcement"""
    model = Announcement
    template_name = 'communications/announcements/form.html'
    fields = ['title', 'content', 'priority', 'target_audience', 'target_classes', 
              'attachment', 'is_published', 'publish_date', 'expiry_date', 'is_pinned']
    success_url = reverse_lazy('communications:announcement_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter classes by school
        form.fields['target_classes'].queryset = Class.objects.filter(
            school=self.request.school
        )
        # Add CSS classes
        for field_name, field in form.fields.items():
            if field_name == 'target_classes':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'size': '5'})
            elif field_name in ['content']:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'rows': '4'})
            elif field_name in ['is_published', 'is_pinned']:
                field.widget.attrs.update({'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'})
            elif field_name in ['publish_date', 'expiry_date']:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'type': 'datetime-local'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        return form
    
    def form_valid(self, form):
        form.instance.school = self.request.school
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Announcement created successfully.')
        return super().form_valid(form)


class AnnouncementUpdateView(AnnouncementAccessMixin, LoginRequiredMixin, UpdateView):
    """Update announcement"""
    model = Announcement
    template_name = 'communications/announcements/form.html'
    fields = ['title', 'content', 'priority', 'target_audience', 'target_classes', 
              'attachment', 'is_published', 'publish_date', 'expiry_date', 'is_pinned']
    success_url = reverse_lazy('communications:announcement_list')
    
    def get_queryset(self):
        return Announcement.objects.filter(school=self.request.school)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['target_classes'].queryset = Class.objects.filter(
            school=self.request.school
        )
        for field_name, field in form.fields.items():
            if field_name == 'target_classes':
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'size': '5'})
            elif field_name in ['content']:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'rows': '4'})
            elif field_name in ['is_published', 'is_pinned']:
                field.widget.attrs.update({'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'})
            elif field_name in ['publish_date', 'expiry_date']:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm', 'type': 'datetime-local'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'})
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Announcement updated successfully.')
        return super().form_valid(form)


class AnnouncementDeleteView(AnnouncementAccessMixin, LoginRequiredMixin, DeleteView):
    """Delete announcement"""
    model = Announcement
    template_name = 'communications/announcements/confirm_delete.html'
    success_url = reverse_lazy('communications:announcement_list')
    
    def get_queryset(self):
        return Announcement.objects.filter(school=self.request.school)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Announcement deleted successfully.')
        return super().delete(request, *args, **kwargs)


class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    """View announcement details"""
    model = Announcement
    template_name = 'communications/announcements/detail.html'
    context_object_name = 'announcement'
    
    def get_queryset(self):
        return Announcement.objects.filter(
            school=self.request.school
        ).select_related('created_by').prefetch_related('target_classes')


# ============================================================================
# MESSAGE VIEWS
# ============================================================================

class MessageInboxView(LoginRequiredMixin, ListView):
    """View inbox messages"""
    model = Message
    template_name = 'communications/messages/inbox.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Message.objects.filter(
            recipient=self.request.user,
            is_deleted_by_recipient=False
        ).select_related('sender', 'parent_message')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'unread':
            queryset = queryset.filter(is_read=False)
        elif status == 'read':
            queryset = queryset.filter(is_read=True)
        elif status == 'starred':
            queryset = queryset.filter(is_starred=True)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) | 
                Q(content__icontains=search) |
                Q(sender__first_name__icontains=search) |
                Q(sender__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Inbox'
        context['unread_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_deleted_by_recipient=False,
            is_read=False
        ).count()
        context['status_filter'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class MessageSentView(LoginRequiredMixin, ListView):
    """View sent messages"""
    model = Message
    template_name = 'communications/messages/sent.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Message.objects.filter(
            sender=self.request.user,
            is_deleted_by_sender=False
        ).select_related('recipient')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) | 
                Q(content__icontains=search) |
                Q(recipient__first_name__icontains=search) |
                Q(recipient__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Sent Messages'
        context['search'] = self.request.GET.get('search', '')
        return context


class MessageComposeView(LoginRequiredMixin, View):
    """Compose new message"""
    template_name = 'communications/messages/compose.html'
    
    def get(self, request):
        # Get recipient_id from query params for reply
        recipient_id = request.GET.get('recipient_id')
        parent_id = request.GET.get('parent_id')
        
        # Get all users from the same school except current user
        users = User.objects.filter(
            school=request.school
        ).exclude(id=request.user.id).order_by('first_name', 'last_name')
        
        context = {
            'page_title': 'Compose Message',
            'users': users,
            'recipient_id': recipient_id,
            'parent_id': parent_id,
        }
        
        # If replying, pre-fill subject
        if parent_id:
            parent_message = get_object_or_404(Message, id=parent_id)
            context['reply_subject'] = f"Re: {parent_message.subject}"
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if not all([recipient_id, subject, content]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('communications:message_compose')
        
        try:
            recipient = User.objects.get(id=recipient_id, school=request.school)
            
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                content=content,
                parent_message_id=parent_id if parent_id else None
            )
            
            # Handle attachment
            if 'attachment' in request.FILES:
                message.attachment = request.FILES['attachment']
                message.save()
            
            # Create notification for recipient
            Notification.objects.create(
                recipient=recipient,
                notification_type='message',
                title='New Message',
                message=f'{request.user.get_full_name()} sent you a message: {subject}',
                action_url=reverse('communications:message_detail', kwargs={'pk': message.id})
            )
            
            messages.success(request, 'Message sent successfully.')
            return redirect('communications:message_sent')
        except User.DoesNotExist:
            messages.error(request, 'Invalid recipient.')
            return redirect('communications:message_compose')


class MessageDetailView(LoginRequiredMixin, DetailView):
    """View message details"""
    model = Message
    template_name = 'communications/messages/detail.html'
    context_object_name = 'message'
    
    def get_queryset(self):
        # User can view messages they sent or received
        return Message.objects.filter(
            Q(sender=self.request.user, is_deleted_by_sender=False) |
            Q(recipient=self.request.user, is_deleted_by_recipient=False)
        ).select_related('sender', 'recipient', 'parent_message')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark as read if user is the recipient
        if obj.recipient == self.request.user and not obj.is_read:
            obj.mark_as_read()
        return obj


class MessageDeleteView(LoginRequiredMixin, View):
    """Delete message (soft delete)"""
    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        
        # Soft delete based on user role
        if message.sender == request.user:
            message.is_deleted_by_sender = True
        elif message.recipient == request.user:
            message.is_deleted_by_recipient = True
        else:
            messages.error(request, 'You do not have permission to delete this message.')
            return redirect('communications:message_inbox')
        
        message.save()
        messages.success(request, 'Message deleted successfully.')
        
        # Redirect based on where user came from
        if message.sender == request.user:
            return redirect('communications:message_sent')
        else:
            return redirect('communications:message_inbox')


class MessageToggleStarView(LoginRequiredMixin, View):
    """Toggle message star status"""
    def post(self, request, pk):
        message = get_object_or_404(
            Message,
            pk=pk,
            recipient=request.user,
            is_deleted_by_recipient=False
        )
        
        message.is_starred = not message.is_starred
        message.save()
        
        return redirect('communications:message_detail', pk=pk)


# ============================================================================
# NOTIFICATION VIEWS
# ============================================================================

class NotificationListView(LoginRequiredMixin, ListView):
    """List all notifications"""
    model = Notification
    template_name = 'communications/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'unread':
            queryset = queryset.filter(is_read=False)
        elif status == 'read':
            queryset = queryset.filter(is_read=True)
        
        # Filter by type
        notification_type = self.request.GET.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notifications'
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        context['status_filter'] = self.request.GET.get('status', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['notification_types'] = Notification.NOTIFICATION_TYPE_CHOICES
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    """Mark notification as read"""
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )
        notification.mark_as_read()
        
        # Redirect to action URL if provided
        if notification.action_url:
            return redirect(notification.action_url)
        
        return redirect('communications:notification_list')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    """Mark all notifications as read"""
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        messages.success(request, 'All notifications marked as read.')
        return redirect('communications:notification_list')


class NotificationDeleteView(LoginRequiredMixin, View):
    """Delete notification"""
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )
        notification.delete()
        
        messages.success(request, 'Notification deleted successfully.')
        return redirect('communications:notification_list')
