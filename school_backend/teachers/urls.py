# teachers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, TeacherProfileViewSet, TeacherDocumentViewSet,
    TeacherQualificationViewSet, TeacherTrainingViewSet, TeacherAssignmentViewSet,
    TeacherAttendanceViewSet, TeacherLeaveViewSet, ProfessionalStandingViewSet,
    PerformanceIndicatorViewSet, TeacherTransferViewSet, TeacherDashboardView,
    AdminDashboardView, TeacherReportView, ExportTeachersView, PublicTeacherListView,
    SendNotificationView, SyncTSCDataView, TeacherProfileByDepartmentView
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teacher-profiles', TeacherProfileViewSet, basename='teacher-profile')
router.register(r'documents', TeacherDocumentViewSet, basename='teacher-document')
router.register(r'qualifications', TeacherQualificationViewSet, basename='teacher-qualification')
router.register(r'trainings', TeacherTrainingViewSet, basename='teacher-training')
router.register(r'assignments', TeacherAssignmentViewSet, basename='teacher-assignment')
router.register(r'attendance', TeacherAttendanceViewSet, basename='teacher-attendance')
router.register(r'leaves', TeacherLeaveViewSet, basename='teacher-leave')
router.register(r'professional-standing', ProfessionalStandingViewSet, basename='professional-standing')
router.register(r'performance-indicators', PerformanceIndicatorViewSet, basename='performance-indicator')
router.register(r'transfers', TeacherTransferViewSet, basename='teacher-transfer')

# Custom URL patterns for non-viewset views
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Dashboard URLs
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Report URLs
    path('reports/', TeacherReportView.as_view(), name='teacher-reports'),
    path('export/teachers/', ExportTeachersView.as_view(), name='export-teachers'),
    
    # Public URLs
    path('public/', PublicTeacherListView.as_view(), name='public-teacher-list'),
    
    # Custom action URLs (these are also available via viewset actions, but explicit URLs can be added)
    path('notifications/send/', SendNotificationView.as_view(), name='send-notifications'),
    path('sync/tsc/', SyncTSCDataView.as_view(), name='sync-tsc-data'),
    
    # Specialized URLs
    path('by-department/<int:department_id>/', TeacherProfileByDepartmentView.as_view(), name='teachers-by-department'),
    
    # Additional action endpoints that might be useful
    path('teacher-profiles/<int:pk>/dashboard/', TeacherProfileViewSet.as_view({'get': 'dashboard'}), name='teacher-profile-dashboard'),
    path('teacher-profiles/<int:pk>/tsc-report/', TeacherProfileViewSet.as_view({'get': 'tsc_report'}), name='teacher-tsc-report'),
    path('teacher-profiles/<int:pk>/update-tpd/', TeacherProfileViewSet.as_view({'post': 'update_tpd'}), name='update-tpd'),
    path('teacher-profiles/<int:pk>/mark-cbc-trained/', TeacherProfileViewSet.as_view({'post': 'mark_cbc_trained'}), name='mark-cbc-trained'),
    
    # Department specific endpoints
    path('departments/<int:pk>/teachers/', DepartmentViewSet.as_view({'get': 'teachers'}), name='department-teachers'),
    
    # Document endpoints
    path('documents/<int:pk>/verify/', TeacherDocumentViewSet.as_view({'post': 'verify'}), name='verify-document'),
    path('documents/expiring-soon/', TeacherDocumentViewSet.as_view({'get': 'expiring_soon'}), name='documents-expiring-soon'),
    
    # Qualification endpoints
    path('qualifications/<int:pk>/verify/', TeacherQualificationViewSet.as_view({'post': 'verify'}), name='verify-qualification'),
    
    # Training endpoints
    path('trainings/<int:pk>/complete/', TeacherTrainingViewSet.as_view({'post': 'complete'}), name='complete-training'),
    path('trainings/upcoming/', TeacherTrainingViewSet.as_view({'get': 'upcoming'}), name='upcoming-trainings'),
    
    # Assignment endpoints
    path('assignments/<int:pk>/approve/', TeacherAssignmentViewSet.as_view({'post': 'approve'}), name='approve-assignment'),
    path('assignments/<int:pk>/activate/', TeacherAssignmentViewSet.as_view({'post': 'activate'}), name='activate-assignment'),
    path('assignments/<int:pk>/deactivate/', TeacherAssignmentViewSet.as_view({'post': 'deactivate'}), name='deactivate-assignment'),
    path('assignments/current/', TeacherAssignmentViewSet.as_view({'get': 'current'}), name='current-assignments'),
    
    # Attendance endpoints
    path('attendance/bulk-update/', TeacherAttendanceViewSet.as_view({'post': 'bulk_update'}), name='bulk-update-attendance'),
    path('attendance/report/', TeacherAttendanceViewSet.as_view({'get': 'report'}), name='attendance-report'),
    path('attendance/monthly-summary/', TeacherAttendanceViewSet.as_view({'get': 'monthly_summary'}), name='monthly-attendance-summary'),
    
    # Leave endpoints
    path('leaves/<int:pk>/submit/', TeacherLeaveViewSet.as_view({'post': 'submit'}), name='submit-leave'),
    path('leaves/<int:pk>/approve/', TeacherLeaveViewSet.as_view({'post': 'approve'}), name='approve-leave'),
    path('leaves/<int:pk>/reject/', TeacherLeaveViewSet.as_view({'post': 'reject'}), name='reject-leave'),
    path('leaves/pending/', TeacherLeaveViewSet.as_view({'get': 'pending'}), name='pending-leaves'),
    path('leaves/current/', TeacherLeaveViewSet.as_view({'get': 'current'}), name='current-leaves'),
    
    # Performance indicator endpoints
    path('performance-indicators/summary/', PerformanceIndicatorViewSet.as_view({'get': 'summary'}), name='performance-summary'),
    
    # Transfer endpoints
    path('transfers/<int:pk>/approve-sending/', TeacherTransferViewSet.as_view({'post': 'approve_sending'}), name='approve-transfer-sending'),
    path('transfers/<int:pk>/approve-receiving/', TeacherTransferViewSet.as_view({'post': 'approve_receiving'}), name='approve-transfer-receiving'),
    path('transfers/<int:pk>/approve-tsc/', TeacherTransferViewSet.as_view({'post': 'approve_tsc'}), name='approve-transfer-tsc'),
    path('transfers/<int:pk>/complete/', TeacherTransferViewSet.as_view({'post': 'complete'}), name='complete-transfer'),
    path('transfers/pending/', TeacherTransferViewSet.as_view({'get': 'pending'}), name='pending-transfers'),


#    # Assignment extended actions
path('assignments/my/', TeacherAssignmentViewSet.as_view({'get': 'my_assignments'}), name='my-assignments'),
path('assignments/<int:pk>/publish/', TeacherAssignmentViewSet.as_view({'post': 'publish'}), name='publish-assignment'),
path('assignments/<int:pk>/unpublish/', TeacherAssignmentViewSet.as_view({'post': 'unpublish'}), name='unpublish-assignment'),
path('assignments/<int:pk>/close/', TeacherAssignmentViewSet.as_view({'post': 'close'}), name='close-assignment'),
path('assignments/<int:pk>/duplicate/', TeacherAssignmentViewSet.as_view({'post': 'duplicate'}), name='duplicate-assignment'),
path('assignments/statistics/', TeacherAssignmentViewSet.as_view({'get': 'statistics'}), name='assignment-statistics'),
path('assignments/<int:pk>/submissions/', TeacherAssignmentViewSet.as_view({'get': 'submissions'}), name='assignment-submissions'),
path('assignments/export/<str:format>/', TeacherAssignmentViewSet.as_view({'get': 'export'}), name='export-assignments'),







]

# Add API versioning (optional but recommended)
app_name = 'teachers'

