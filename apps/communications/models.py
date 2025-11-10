"""
Models for the communications app.
Handles announcements, messages, and notifications.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Announcement(models.Model):
    """
    Announcement model for school-wide or targeted announcements.
    """
    TARGET_AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('parents', 'Parents Only'),
        ('teachers', 'Teachers Only'),
        ('staff', 'Staff Only'),
        ('specific_class', 'Specific Class'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # School relationship
    school = models.ForeignKey(
        'accounts.School',
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_('School')
    )
    
    # Announcement details
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    priority = models.CharField(_('Priority'), max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Targeting
    target_audience = models.CharField(_('Target Audience'), max_length=20, choices=TARGET_AUDIENCE_CHOICES, default='all')
    target_classes = models.ManyToManyField(
        'accounts.Class',
        related_name='announcements',
        verbose_name=_('Target Classes'),
        blank=True,
        help_text=_('Select classes if target audience is "Specific Class"')
    )
    
    # Attachments
    attachment = models.FileField(_('Attachment'), upload_to='announcements/', null=True, blank=True)
    
    # Publishing
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_announcements',
        verbose_name=_('Created By'),
        null=True
    )
    is_published = models.BooleanField(_('Is Published'), default=False)
    publish_date = models.DateTimeField(_('Publish Date'), null=True, blank=True)
    expiry_date = models.DateTimeField(_('Expiry Date'), null=True, blank=True)
    
    # Pinning
    is_pinned = models.BooleanField(_('Is Pinned'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['school', 'is_published']),
            models.Index(fields=['target_audience']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_active(self):
        """Check if announcement is currently active."""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_published:
            return False
        
        if self.publish_date and self.publish_date > now:
            return False
        
        if self.expiry_date and self.expiry_date < now:
            return False
        
        return True


class Message(models.Model):
    """
    Message model for direct messaging between users.
    """
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    # Sender and recipient
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Sender')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('Recipient')
    )
    
    # Message content
    subject = models.CharField(_('Subject'), max_length=200)
    content = models.TextField(_('Content'))
    
    # Attachment
    attachment = models.FileField(_('Attachment'), upload_to='messages/', null=True, blank=True)
    
    # Status
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='sent')
    is_read = models.BooleanField(_('Is Read'), default=False)
    read_at = models.DateTimeField(_('Read At'), null=True, blank=True)
    
    # Flags
    is_starred = models.BooleanField(_('Is Starred'), default=False)
    is_archived = models.BooleanField(_('Is Archived'), default=False)
    is_deleted_by_sender = models.BooleanField(_('Deleted by Sender'), default=False)
    is_deleted_by_recipient = models.BooleanField(_('Deleted by Recipient'), default=False)
    
    # Reply to (for threading)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='replies',
        verbose_name=_('Reply To'),
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'is_deleted_by_sender']),
            models.Index(fields=['recipient', 'is_deleted_by_recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.recipient.get_full_name()}: {self.subject}"
    
    def mark_as_read(self):
        """Mark message as read."""
        from django.utils import timezone
        self.is_read = True
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'status', 'read_at', 'updated_at'])


class Notification(models.Model):
    """
    Notification model for in-app notifications.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('message', 'New Message'),
        ('attendance', 'Attendance Alert'),
        ('fee', 'Fee Reminder'),
        ('exam', 'Exam Notification'),
        ('result', 'Result Published'),
        ('timetable', 'Timetable Update'),
        ('system', 'System Notification'),
    ]
    
    # Recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient')
    )
    
    # Notification details
    notification_type = models.CharField(_('Type'), max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=200)
    message = models.TextField(_('Message'))
    
    # Action link (optional)
    action_url = models.CharField(_('Action URL'), max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(_('Is Read'), default=False)
    read_at = models.DateTimeField(_('Read At'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.get_full_name()}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
