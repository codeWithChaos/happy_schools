"""
URL configuration for the fees app.
"""
from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    # Fee Structure Management
    path('structures/', views.FeeStructureListView.as_view(), name='structure_list'),
    path('structures/create/', views.FeeStructureCreateView.as_view(), name='structure_create'),
    path('structures/<int:pk>/edit/', views.FeeStructureUpdateView.as_view(), name='structure_edit'),
    path('structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='structure_delete'),
    
    # Student Fee Management
    path('students/', views.StudentFeeListView.as_view(), name='student_list'),
    path('students/<int:student_id>/collect/', views.CollectFeeView.as_view(), name='collect'),
    
    # Payment & Receipt
    path('receipt/<int:payment_id>/', views.FeeReceiptView.as_view(), name='receipt'),
    path('history/', views.PaymentHistoryView.as_view(), name='history'),
    
    # Reports
    path('reports/', views.FeeReportView.as_view(), name='reports'),
    
    # Default redirect to student list
    path('', views.StudentFeeListView.as_view(), name='list'),
]
