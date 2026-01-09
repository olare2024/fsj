from django.urls import path
from . import views

urlpatterns = [
    # Student management endpoints
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/bulk-upload/', views.BulkUploadStudentsView.as_view(), name='student-bulk-upload'),
]