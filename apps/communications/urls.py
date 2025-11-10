from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcements/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),
    
    # Messages
    path('messages/inbox/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('messages/sent/', views.MessageSentView.as_view(), name='message_sent'),
    path('messages/compose/', views.MessageComposeView.as_view(), name='message_compose'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>/star/', views.MessageToggleStarView.as_view(), name='message_star'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification_read'),
    path('notifications/mark-all-read/', views.NotificationMarkAllReadView.as_view(), name='notification_mark_all_read'),
    path('notifications/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
]
