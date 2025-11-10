from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    # List all timetable entries
    path('', views.TimetableListView.as_view(), name='list'),
    
    # Class-specific timetable view
    path('class/<int:class_id>/section/<int:section_id>/', views.ClassTimetableView.as_view(), name='class_view'),
    
    # Teacher-specific timetable view
    path('teacher/', views.TeacherTimetableView.as_view(), name='my_timetable'),
    path('teacher/<int:teacher_id>/', views.TeacherTimetableView.as_view(), name='teacher_view'),
    
    # CRUD operations
    path('create/', views.TimetableCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TimetableUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TimetableDeleteView.as_view(), name='delete'),
]
