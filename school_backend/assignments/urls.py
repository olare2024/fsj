"""
URL configuration for the Assignments module.
Organized by functionality and user roles.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # ViewSets
    AssignmentViewSet,
    StudentAssignmentViewSet,
    AssignmentCategoryViewSet,
    AssignmentGroupViewSet,
    AssignmentCommentViewSet,
    
    # Dashboard and Overview
    assignment_dashboard,
    teacher_assignment_stats,
    upcoming_deadlines,
    assignment_calendar,
    assignment_timeline,
    assignment_search,
    
    # Student-specific
    student_progress_report,
    notifications,
    
    # Assignment operations
    create_assignment_comment,
    create_assignment_reminder,
    get_assignment_groups,
    
    # Group management
    join_assignment_group,
    leave_assignment_group,
    transfer_group_leadership,
    
    # Grading operations
    bulk_grade,
    import_grades,
    export_grades,
    
    # Analytics and reports
    assignment_analytics,
    class_performance_report,
    
    # Batch operations
    batch_update_assignment_status,
    export_assignment_template,
    
    # System and admin
    send_assignment_reminders,
    assignments_health_check,
    system_stats,
    fix_student_assignments,
    recalculate_assignment_statistics,
    DebugURLsView,

)

# ==================== ROUTER CONFIGURATION ====================

# Main router for standard REST endpoints
router = DefaultRouter()
router.register(r'categories', AssignmentCategoryViewSet, basename='assignment-category')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'student-assignments', StudentAssignmentViewSet, basename='student-assignment')
router.register(r'groups', AssignmentGroupViewSet, basename='assignment-group')
router.register(r'comments', AssignmentCommentViewSet, basename='assignment-comment')

# ==================== URL PATTERNS ====================

urlpatterns = [
    # ==================== MAIN API ROUTES ====================
    
    # Include router URLs (REST API endpoints)
    # This handles POST /api/v1/assignments/ automatically
    path('', include(router.urls)),
    
    # ==================== DASHBOARD AND OVERVIEW ====================
    
    path('dashboard/', assignment_dashboard, name='assignment-dashboard'),
    path('teacher-stats/', teacher_assignment_stats, name='teacher-assignment-stats'),
    path('upcoming-deadlines/', upcoming_deadlines, name='upcoming-deadlines'),
    path('calendar/', assignment_calendar, name='assignment-calendar'),
    path('timeline/', assignment_timeline, name='assignment-timeline'),
    path('search/', assignment_search, name='assignment-search'),
    
    # ==================== STUDENT-SPECIFIC ENDPOINTS ====================
    
    path('progress-report/', student_progress_report, name='student-progress-report'),
    path('progress-report/<uuid:student_id>/', student_progress_report, name='student-progress-report-by-id'),
    path('notifications/', notifications, name='assignment-notifications'),
    
    # ==================== CUSTOM ACTIONS (via router or explicit) ====================
    
    # These actions are already available through the router as:
    # POST /api/v1/assignments/{id}/publish/
    # POST /api/v1/assignments/{id}/close/
    # POST /api/v1/assignments/{id}/duplicate/
    # GET /api/v1/assignments/{id}/stats/
    # GET /api/v1/assignments/{id}/submissions/
    # POST /api/v1/assignments/bulk-create/
    # GET /api/v1/assignments/export/
    
    # Student assignment actions (via router):
    # POST /api/v1/student-assignments/{id}/submit/
    # POST /api/v1/student-assignments/{id}/grade/
    
    # ==================== GRADING OPERATIONS ====================
    
    path('assignments/<uuid:assignment_id>/bulk-grade/', bulk_grade, name='assignment-bulk-grade'),
    path('assignments/<uuid:assignment_id>/import-grades/', import_grades, name='assignment-import-grades'),
    path('assignments/<uuid:assignment_id>/export-grades/', export_grades, name='assignment-export-grades'),
    
    # ==================== ANALYTICS AND REPORTS ====================
    
    path('assignments/<uuid:assignment_id>/analytics/', assignment_analytics, name='assignment-analytics'),
    path('class-performance-report/', class_performance_report, name='class-performance-report'),
    path('class-performance-report/<uuid:classroom_id>/', class_performance_report, name='class-performance-report-by-id'),
    
    # ==================== GROUP MANAGEMENT ====================
    
    path('assignments/<uuid:assignment_id>/all-groups/', get_assignment_groups, name='assignment-all-groups'),
    path('groups/<uuid:group_id>/join/', join_assignment_group, name='assignment-group-join'),
    path('groups/<uuid:group_id>/leave/', leave_assignment_group, name='assignment-group-leave'),
    path('groups/<uuid:group_id>/transfer-leadership/', transfer_group_leadership, name='assignment-group-transfer-leadership'),
    
    # ==================== COMMENTS AND COMMUNICATION ====================
    
    path('assignments/<uuid:assignment_id>/create-comment/', create_assignment_comment, name='assignment-create-comment'),
    
    # ==================== REMINDERS AND NOTIFICATIONS ====================
    
    path('assignments/<uuid:assignment_id>/create-reminder/', create_assignment_reminder, name='assignment-create-reminder'),
    path('assignments/<uuid:assignment_id>/send-reminders/', send_assignment_reminders, name='assignment-send-reminders'),
    
    # ==================== BATCH OPERATIONS ====================
    
    path('assignments/export-template/', export_assignment_template, name='assignment-export-template'),
    path('assignments/batch-update-status/', batch_update_assignment_status, name='assignment-batch-update-status'),
    
    # ==================== SYSTEM AND ADMIN ENDPOINTS ====================
    
    path('health-check/', assignments_health_check, name='assignments-health-check'),
    path('system-stats/', system_stats, name='assignment-system-stats'),
    path('assignments/<uuid:assignment_id>/fix-student-assignments/', fix_student_assignments, name='fix-student-assignments'),
    path('recalculate-statistics/', recalculate_assignment_statistics, name='recalculate-assignment-statistics'),



    path('debug-urls/', DebugURLsView.as_view(), name='debug-urls'),
]

# ==================== URL NAMESPACE ====================

app_name = 'assignments'