# teachers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'teacher-profiles', views.TeacherProfileViewSet)
router.register(r'documents', views.TeacherDocumentViewSet)
router.register(r'qualifications', views.TeacherQualificationViewSet)
router.register(r'trainings', views.TeacherTrainingViewSet)
router.register(r'assignments', views.TeacherAssignmentViewSet)
router.register(r'attendance', views.TeacherAttendanceViewSet)
router.register(r'leaves', views.TeacherLeaveViewSet)
router.register(r'professional-standings', views.ProfessionalStandingViewSet)
router.register(r'performance-indicators', views.PerformanceIndicatorViewSet)
router.register(r'transfers', views.TeacherTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom endpoints
    path('my-profile/', views.CurrentTeacherProfileView.as_view(), name='my-profile'),
    path('dashboard/teacher/', views.TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('export/', views.ExportTeachersView.as_view(), name='export-teachers'),
    
    # Bulk operations
    path('bulk/create/', views.BulkCreateTeachersView.as_view(), name='bulk-create-teachers'),
    path('bulk/update/', views.BulkUpdateTeachersView.as_view(), name='bulk-update-teachers'),
    path('bulk/delete/', views.BulkDeleteTeachersView.as_view(), name='bulk-delete-teachers'),
    path('bulk/activate/', views.BulkActivateTeachersView.as_view(), name='bulk-activate-teachers'),
    
    # Reports
    path('reports/', views.TeacherReportView.as_view(), name='teacher-reports'),
    
    # Notifications
    path('send-notification/', views.SendNotificationView.as_view(), name='send-notification'),
    path('sync-tsc/', views.SyncTSCDataView.as_view(), name='sync-tsc'),
    
    # Search
    path('search/', views.TeacherSearchView.as_view(), name='teacher-search'),
    path('public/', views.PublicTeacherListView.as_view(), name='public-teachers'),
    
    # Statistics
    path('statistics/summary/', views.TeacherStatisticsView.as_view(), name='teacher-statistics'),
    path('statistics/department/', views.DepartmentStatisticsView.as_view(), name='department-statistics'),
    path('statistics/attendance/', views.AttendanceStatisticsView.as_view(), name='attendance-statistics'),
    
    # My endpoints
    path('my-assignments/', views.MyAssignmentsView.as_view(), name='my-assignments'),
    
    # Expiring documents
    path('documents/expiring-soon/', views.ExpiringDocumentsView.as_view(), name='expiring-documents'),
    
    # Pending approvals
    path('leaves/pending/', views.PendingLeavesView.as_view(), name='pending-leaves'),
    path('transfers/pending/', views.PendingTransfersView.as_view(), name='pending-transfers'),
    
    # Debug endpoint
    path('debug/', views.APIDebugView.as_view(), name='api-debug'),
]