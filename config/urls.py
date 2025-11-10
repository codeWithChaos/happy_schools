from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Students
    path('students/', include('apps.students.urls')),
    
    # Attendance
    path('attendance/', include('apps.attendance.urls')),
    
    # Fees
    path('fees/', include('apps.fees.urls')),
    
    # Timetable
    path('timetable/', include('apps.timetable.urls')),
    
    # Examinations
    path('examinations/', include('apps.examinations.urls')),
    
    # Communications
    path('communications/', include('apps.communications.urls')),
    
    # Root redirect to dashboard (authenticated users) or registration
    path('', RedirectView.as_view(pattern_name='dashboard:index', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
