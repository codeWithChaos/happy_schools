from django.urls import path
from . import views

app_name = 'examinations'

urlpatterns = [
    # Exam management
    path('', views.ExamListView.as_view(), name='list'),
    path('create/', views.ExamCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ExamUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ExamDeleteView.as_view(), name='delete'),
    
    # Marks entry
    path('<int:exam_id>/enter-marks/', views.EnterMarksView.as_view(), name='enter_marks'),
    
    # Results and reports
    path('<int:exam_id>/student/<int:student_id>/results/', views.StudentResultsView.as_view(), name='student_results'),
    path('<int:exam_id>/report/', views.ExamReportView.as_view(), name='report'),
]
