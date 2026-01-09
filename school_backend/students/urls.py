"""
URLs for students app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Student Profile URLs
router.register(
    r'profiles', 
    views.StudentProfileViewSet, 
    basename='student-profile'
)

# Student Enrollment URLs
router.register(
    r'enrollments', 
    views.StudentEnrollmentViewSet, 
    basename='student-enrollment'
)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Student Dashboard
    path(
        'dashboard/', 
        views.student_dashboard, 
        name='student-dashboard'
    ),
    
    # Search Students
    path(
        'search/', 
        views.search_students, 
        name='student-search'
    ),
    
    # Statistics
    path(
        'statistics/', 
        views.student_statistics, 
        name='student-statistics'
    ),
    
    # Bulk Promotion
    path(
        'bulk-promote/', 
        views.bulk_promote_students, 
        name='bulk-promote-students'
    ),
    
    # Generate Reports
    path(
        'generate-report/', 
        views.generate_student_report, 
        name='generate-student-report'
    ),
    
    # ========================================
    # SPECIALIZED ENDPOINTS
    # ========================================
    
    # Student Profile Custom Actions
    path(
        'profiles/<uuid:pk>/enrollments/', 
        views.StudentProfileViewSet.as_view({'get': 'enrollments'}),
        name='student-profile-enrollments'
    ),
    path(
        'profiles/<uuid:pk>/academic-info/', 
        views.StudentProfileViewSet.as_view({'get': 'academic_info'}),
        name='student-profile-academic-info'
    ),
    path(
        'profiles/<uuid:pk>/contact-info/', 
        views.StudentProfileViewSet.as_view({'get': 'contact_info'}),
        name='student-profile-contact-info'
    ),
    path(
        'profiles/<uuid:pk>/parent-info/', 
        views.StudentProfileViewSet.as_view({'get': 'parent_info'}),
        name='student-profile-parent-info'
    ),
    path(
        'profiles/<uuid:pk>/medical-info/', 
        views.StudentProfileViewSet.as_view({'get': 'medical_info'}),
        name='student-profile-medical-info'
    ),
    path(
        'profiles/<uuid:pk>/generate-report/', 
        views.StudentProfileViewSet.as_view({'get': 'generate_report'}),
        name='student-profile-generate-report'
    ),
    path(
        'profiles/<uuid:pk>/update-academic/', 
        views.StudentProfileViewSet.as_view({'post': 'update_academic'}),
        name='student-profile-update-academic'
    ),
    path(
        'profiles/<uuid:pk>/update-behavioral/', 
        views.StudentProfileViewSet.as_view({'post': 'update_behavioral'}),
        name='student-profile-update-behavioral'
    ),
    path(
        'profiles/<uuid:pk>/update-health/', 
        views.StudentProfileViewSet.as_view({'post': 'update_health'}),
        name='student-profile-update-health'
    ),
    path(
        'profiles/<uuid:pk>/update-extracurricular/', 
        views.StudentProfileViewSet.as_view({'post': 'update_extracurricular'}),
        name='student-profile-update-extracurricular'
    ),
    path(
        'profiles/<uuid:pk>/update-fee-info/', 
        views.StudentProfileViewSet.as_view({'post': 'update_fee_info'}),
        name='student-profile-update-fee-info'
    ),
    path(
        'profiles/<uuid:pk>/add-community-service/', 
        views.StudentProfileViewSet.as_view({'post': 'add_community_service'}),
        name='student-profile-add-community-service'
    ),
    path(
        'profiles/<uuid:pk>/add-test-score/', 
        views.StudentProfileViewSet.as_view({'post': 'add_test_score'}),
        name='student-profile-add-test-score'
    ),
    path(
        'profiles/<uuid:pk>/promote/', 
        views.StudentProfileViewSet.as_view({'post': 'promote'}),
        name='student-profile-promote'
    ),
    
    # Student Profile Bulk Operations
    path(
        'profiles/bulk-update/', 
        views.StudentProfileViewSet.as_view({'post': 'bulk_update'}),
        name='student-profiles-bulk-update'
    ),
    path(
        'profiles/import/', 
        views.StudentProfileViewSet.as_view({'post': 'import_students'}),
        name='student-profiles-import'
    ),
    
    # Enrollment Custom Actions
    path(
        'enrollments/bulk-create/', 
        views.StudentEnrollmentViewSet.as_view({'post': 'bulk_create'}),
        name='enrollments-bulk-create'
    ),
    path(
        'enrollments/<uuid:pk>/update-status/', 
        views.StudentEnrollmentViewSet.as_view({'post': 'update_status'}),
        name='enrollment-update-status'
    ),
    path(
        'enrollments/current/', 
        views.StudentEnrollmentViewSet.as_view({'get': 'current_enrollments'}),
        name='enrollments-current'
    ),
    path(
        'enrollments/by-class/', 
        views.StudentEnrollmentViewSet.as_view({'get': 'by_class'}),
        name='enrollments-by-class'
    ),
    
    # ========================================
    # REPORTING ENDPOINTS
    # ========================================
    
    # Student Demographics Report
    path(
        'reports/demographics/',
        views.StudentDemographicsReportView.as_view(),
        name='student-demographics-report'
    ),
    
    # Academic Performance Report
    path(
        'reports/academic-performance/',
        views.AcademicPerformanceReportView.as_view(),
        name='academic-performance-report'
    ),
    
    # Attendance Report
    path(
        'reports/attendance/',
        views.AttendanceReportView.as_view(),
        name='attendance-report'
    ),
    
    # Financial Status Report
    path(
        'reports/financial-status/',
        views.FinancialStatusReportView.as_view(),
        name='financial-status-report'
    ),
    
    # CBC Pathway Report
    path(
        'reports/cbc-pathways/',
        views.CBCPathwayReportView.as_view(),
        name='cbc-pathway-report'
    ),
]

# ==================== API DOCUMENTATION INFO ====================
"""Students Module API Endpoints:
CORE MODELS (ViewSets - CRUD operations available):
Each ViewSet provides standard CRUD operations (GET, POST, PUT, PATCH, DELETE)
- Student Profiles:        /api/v1/students/profiles/
  • GET /{id}/enrollments/       - Get enrollments for a student profile
  • GET /{id}/academic-info/     - Get academic info for a student profile
  • GET /{id}/contact-info/      - Get contact info for a student profile
  • GET /{id}/parent-info/       - Get parent info for a student profile
  • GET /{id}/medical-info/      - Get medical info for a student profile
  • GET /{id}/generate-report/   - Generate report for a student profile
  • POST /{id}/update-academic/  - Update academic details for a student profile
  • POST /{id}/update-behavioral/ - Update behavioral details for a student profile
  • POST /{id}/update-health/    - Update health details for a student profile
  • POST /{id}/update-extracurricular/ - Update extracurricular details for a student profile
  • POST /{id}/update-fee-info/  - Update fee information for a student profile
  • POST /{id}/add-community-service/ - Add community service record for a student profile
  • POST /{id}/add-test-score/   - Add test score for a student profile
  • POST /{id}/promote/          - Promote a student profile to the next class
  • POST /bulk-update/           - Bulk update student profiles
  • POST /import/                - Import student profiles in bulk
- Student Enrollments:     /api/v1/students/enrollments/
  • POST /bulk-create/          - Bulk create student enrollments
  • POST /{id}/update-status/   - Update status of a student enrollment
  • GET /current/               - Get current enrollments
  • GET /by-class/              - Get enrollments filtered by class
SPECIALIZED ENDPOINTS:
- Student Dashboard:        /api/v1/students/dashboard/
  • GET                         - Get dashboard data for students
- Search Students:          /api/v1/students/search/
  • GET                         - Search for students based on criteria
- Student Statistics:       /api/v1/students/statistics/
    • GET                         - Get statistical data about students
- Bulk Promote Students:    /api/v1/students/bulk-promote/
  • POST                        - Bulk promote students to the next class
- Generate Student Report:   /api/v1/students/generate-report/
    • GET                         - Generate comprehensive report for students
REPORTING ENDPOINTS:
- Student Demographics Report: /api/v1/students/reports/demographics/
  • GET                         - Get student demographics report
- Academic Performance Report:  /api/v1/students/reports/academic-performance/

    • GET                         - Get academic performance report
- Attendance Report:           /api/v1/students/reports/attendance/
    • GET                         - Get attendance report
- Financial Status Report:     /api/v1/students/reports/financial-status/
    • GET                         - Get financial status report
- CBC Pathway Report:          /api/v1/students/reports/cbc-pathways/
    • GET                         - Get CBC pathway report
"""
