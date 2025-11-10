"""
URL configuration for the attendance app.
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceListView.as_view(), name='list'),
    path('mark/', views.MarkAttendanceView.as_view(), name='mark'),
    path('report/', views.AttendanceReportView.as_view(), name='report'),
    path('student/<int:pk>/', views.StudentAttendanceDetailView.as_view(), name='student_detail'),
]
