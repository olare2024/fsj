"""
URL Configuration for Academics App

This module defines all URL patterns for the academic management system,
including REST API endpoints, views, and special endpoints for setup checks,
reports, and exports.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = DefaultRouter()

# Academic Structure
router.register(r'academic-years', views.AcademicYearViewSet)
router.register(r'academic-terms', views.AcademicTermViewSet)
router.register(r'grade-levels', views.GradeLevelViewSet)
router.register(r'subjects', views.SubjectViewSet)

# Competency-Based Education
router.register(r'competency-areas', views.CompetencyAreaViewSet)
router.register(r'competency-assessments', views.CompetencyAssessmentViewSet)

# Infrastructure
router.register(r'classrooms', views.ClassroomViewSet)

# Class and Enrollment Management
router.register(r'classes', views.ClassViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)

# Bulk Enrollment Operations
router.register(r'enrollment-bulk', views.EnrollmentBulkViewSet, basename='enrollment-bulk')

# Assessment and Grading
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'grades', views.GradeViewSet)

# Bulk Grade Operations
router.register(r'grade-bulk', views.GradeBulkViewSet, basename='grade-bulk')

# Academic Reports
router.register(r'transcripts', views.TranscriptViewSet)
router.register(r'academic-reports', views.AcademicReportViewSet)

# Attendance
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'attendance-reports', views.AttendanceReportViewSet)

# Timetable and Scheduling
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'teacher-assignments', views.TeacherAssignmentViewSet)

# Events and Configuration
router.register(r'academic-events', views.AcademicEventViewSet)
router.register(r'grading-scales', views.GradingScaleViewSet)
router.register(r'academic-configuration', views.AcademicConfigurationViewSet)

# ============================================================================
# NESTED ROUTERS FOR RELATED ENDPOINTS
# ============================================================================

# Academic Year nested routes
academic_year_router = routers.NestedDefaultRouter(
    router, r'academic-years', lookup='academic_year'
)
academic_year_router.register(
    r'terms', views.AcademicTermViewSet, basename='academic-year-terms'
)
academic_year_router.register(
    r'classes', views.ClassViewSet, basename='academic-year-classes'
)
academic_year_router.register(
    r'assessments', views.AssessmentViewSet, basename='academic-year-assessments'
)
academic_year_router.register(
    r'enrollments', views.EnrollmentViewSet, basename='academic-year-enrollments'
)

# Academic Term nested routes
academic_term_router = routers.NestedDefaultRouter(
    router, r'academic-terms', lookup='academic_term'
)
academic_term_router.register(
    r'assessments', views.AssessmentViewSet, basename='academic-term-assessments'
)
academic_term_router.register(
    r'attendance', views.AttendanceViewSet, basename='academic-term-attendance'
)
academic_term_router.register(
    r'schedules', views.ScheduleViewSet, basename='academic-term-schedules'
)

# Grade Level nested routes
grade_level_router = routers.NestedDefaultRouter(
    router, r'grade-levels', lookup='grade_level'
)
grade_level_router.register(
    r'subjects', views.SubjectViewSet, basename='grade-level-subjects'
)
grade_level_router.register(
    r'classes', views.ClassViewSet, basename='grade-level-classes'
)
grade_level_router.register(
    r'competency-areas', views.CompetencyAreaViewSet, basename='grade-level-competency-areas'
)

# Subject nested routes
subject_router = routers.NestedDefaultRouter(
    router, r'subjects', lookup='subject'
)
subject_router.register(
    r'assessments', views.AssessmentViewSet, basename='subject-assessments'
)
subject_router.register(
    r'grades', views.GradeViewSet, basename='subject-grades'
)

# Class nested routes
class_router = routers.NestedDefaultRouter(
    router, r'classes', lookup='class'
)
class_router.register(
    r'students', views.EnrollmentViewSet, basename='class-students'
)
class_router.register(
    r'assessments', views.AssessmentViewSet, basename='class-assessments'
)
class_router.register(
    r'attendance', views.AttendanceViewSet, basename='class-attendance'
)
class_router.register(
    r'schedules', views.ScheduleViewSet, basename='class-schedules'
)

# Student (Enrollment) nested routes
enrollment_router = routers.NestedDefaultRouter(
    router, r'enrollments', lookup='enrollment'
)
enrollment_router.register(
    r'grades', views.GradeViewSet, basename='enrollment-grades'
)
enrollment_router.register(
    r'attendance', views.AttendanceViewSet, basename='enrollment-attendance'
)
enrollment_router.register(
    r'reports', views.AcademicReportViewSet, basename='enrollment-reports'
)

# ============================================================================
# SPECIAL ENDPOINTS (API VIEWS)
# ============================================================================

setup_endpoints = [
    # Setup check endpoints
    path(
        'setup/check/',
        views.setup_check,
        name='setup-check'
    ),
    path(
        'setup/essential-data/',
        views.essential_data,
        name='essential-data'
    ),
]

dashboard_endpoints = [
    # Dashboard and analytics
    path(
        'dashboard/statistics/',
        views.dashboard_statistics,
        name='dashboard-statistics'
    ),
    path(
        'dashboard/class-performance/',
        views.class_performance,
        name='class-performance'
    ),
    path(
        'dashboard/student-progress/<int:student_id>/',
        views.student_progress,
        name='student-progress'
    ),
]

export_endpoints = [
    # Export endpoints
    path(
        'export/grades/',
        views.export_grades,
        name='export-grades'
    ),
    path(
        'export/attendance/',
        views.export_attendance,
        name='export-attendance'
    ),
]

utility_endpoints = [
    # Utility endpoints
    path(
        'classes/<int:pk>/timetable/',
        views.ClassViewSet.as_view({'get': 'timetable'}, name='class-timetable'),
    ),
    path(
        'classes/<int:pk>/students/',
        views.ClassViewSet.as_view({'get': 'students'}, name='class-students'),
    ),
    path(
        'classes/<int:pk>/subjects/',
        views.ClassViewSet.as_view({'get': 'subjects'}, name='class-subjects'),
    ),
    path(
        'classes/<int:pk>/attendance-summary/',
        views.ClassViewSet.as_view({'get': 'attendance_summary'}, name='class-attendance-summary'),
    ),
    path(
        'classes/<int:pk>/performance-summary/',
        views.ClassViewSet.as_view({'get': 'performance_summary'}, name='class-performance-summary'),
    ),
    
    # Subject endpoints
    path(
        'subjects/<int:pk>/teachers/',
        views.SubjectViewSet.as_view({'get': 'teachers'}, name='subject-teachers'),
    ),
    path(
        'subjects/<int:pk>/assessments/',
        views.SubjectViewSet.as_view({'get': 'assessments'}, name='subject-assessments'),
    ),
    path(
        'subjects/<int:pk>/performance/',
        views.SubjectViewSet.as_view({'get': 'performance'}, name='subject-performance'),
    ),
    
    # Assessment endpoints
    path(
        'assessments/<int:pk>/publish/',
        views.AssessmentViewSet.as_view({'post': 'publish'}, name='assessment-publish'),
    ),
    path(
        'assessments/<int:pk>/grades/',
        views.AssessmentViewSet.as_view({'get': 'grades'}, name='assessment-grades'),
    ),
    path(
        'assessments/<int:pk>/statistics/',
        views.AssessmentViewSet.as_view({'get': 'statistics'}, name='assessment-statistics'),
    ),
    
    # Enrollment endpoints
    path(
        'enrollments/<int:pk>/change-status/',
        views.EnrollmentViewSet.as_view({'post': 'change_status'}, name='enrollment-change-status'),
    ),
    path(
        'enrollments/<int:pk>/subject-enrollments/',
        views.EnrollmentViewSet.as_view({'get': 'subject_enrollments'}, name='enrollment-subject-enrollments'),
    ),
    path(
        'enrollments/<int:pk>/academic-performance/',
        views.EnrollmentViewSet.as_view({'get': 'academic_performance'}, name='enrollment-academic-performance'),
    ),
    path(
        'enrollments/<int:pk>/attendance-summary/',
        views.EnrollmentViewSet.as_view({'get': 'attendance_summary'}, name='enrollment-attendance-summary'),
    ),
    
    # Academic Year endpoints
    path(
        'academic-years/<int:pk>/set-current/',
        views.AcademicYearViewSet.as_view({'post': 'set_current'}, name='academic-year-set-current'),
    ),
    path(
        'academic-years/<int:pk>/terms/',
        views.AcademicYearViewSet.as_view({'get': 'terms'}, name='academic-year-terms'),
    ),
    path(
        'academic-years/<int:pk>/statistics/',
        views.AcademicYearViewSet.as_view({'get': 'statistics'}, name='academic-year-statistics'),
    ),
    
    # Academic Term endpoints
    path(
        'academic-terms/<int:pk>/set-current/',
        views.AcademicTermViewSet.as_view({'post': 'set_current'}, name='academic-term-set-current'),
    ),
    path(
        'academic-terms/<int:pk>/schedule/',
        views.AcademicTermViewSet.as_view({'get': 'schedule'}, name='academic-term-schedule'),
    ),
    path(
        'academic-terms/<int:pk>/attendance-summary/',
        views.AcademicTermViewSet.as_view({'get': 'attendance_summary'}, name='academic-term-attendance-summary'),
    ),
    path(
        'academic-terms/<int:pk>/performance-summary/',
        views.AcademicTermViewSet.as_view({'get': 'performance_summary'}, name='academic-term-performance-summary'),
    ),
    
    # Grade Level endpoints
    path(
        'grade-levels/<int:pk>/classes/',
        views.GradeLevelViewSet.as_view({'get': 'classes'}, name='grade-level-classes'),
    ),
    path(
        'grade-levels/<int:pk>/subjects/',
        views.GradeLevelViewSet.as_view({'get': 'subjects'}, name='grade-level-subjects'),
    ),
    path(
        'grade-levels/<int:pk>/competency-areas/',
        views.GradeLevelViewSet.as_view({'get': 'competency_areas'}, name='grade-level-competency-areas'),
    ),
    
    # Classroom endpoints
    path(
        'classrooms/<int:pk>/schedule/',
        views.ClassroomViewSet.as_view({'get': 'schedule'}, name='classroom-schedule'),
    ),
    path(
        'classrooms/<int:pk>/current-usage/',
        views.ClassroomViewSet.as_view({'get': 'current_usage'}, name='classroom-current-usage'),
    ),
    
    # Transcript endpoints
    path(
        'transcripts/<int:pk>/generate/',
        views.TranscriptViewSet.as_view({'post': 'generate'}, name='transcript-generate'),
    ),
    
    # Academic Report endpoints
    path(
        'academic-reports/<int:pk>/generate/',
        views.AcademicReportViewSet.as_view({'post': 'generate'}, name='academic-report-generate'),
    ),
    path(
        'academic-reports/<int:pk>/publish/',
        views.AcademicReportViewSet.as_view({'post': 'publish'}, name='academic-report-publish'),
    ),
    
    # Attendance endpoints
    path(
        'attendance/daily-summary/',
        views.AttendanceViewSet.as_view({'get': 'daily_summary'}, name='attendance-daily-summary'),
    ),
    path(
        'attendance/class-summary/',
        views.AttendanceViewSet.as_view({'get': 'class_summary'}, name='attendance-class-summary'),
    ),
    
    # Attendance Report endpoints
    path(
        'attendance-reports/<int:pk>/update-statistics/',
        views.AttendanceReportViewSet.as_view({'post': 'update_statistics'}, name='attendance-report-update-statistics'),
    ),
    path(
        'attendance-reports/<int:pk>/notify-parent/',
        views.AttendanceReportViewSet.as_view({'post': 'notify_parent'}, name='attendance-report-notify-parent'),
    ),
    
    # Schedule endpoints
    path(
        'schedules/class-timetable/',
        views.ScheduleViewSet.as_view({'get': 'class_timetable'}, name='schedule-class-timetable'),
    ),
    path(
        'schedules/teacher-timetable/',
        views.ScheduleViewSet.as_view({'get': 'teacher_timetable'}, name='schedule-teacher-timetable'),
    ),
    path(
        'schedules/weekly-schedule/',
        views.ScheduleViewSet.as_view({'get': 'weekly_schedule'}, name='schedule-weekly-schedule'),
    ),
    
    # Competency Area endpoints
    path(
        'competency-areas/<int:pk>/assessments/',
        views.CompetencyAreaViewSet.as_view({'get': 'assessments'}, name='competency-area-assessments'),
    ),
    path(
        'competency-areas/<int:pk>/statistics/',
        views.CompetencyAreaViewSet.as_view({'get': 'statistics'}, name='competency-area-statistics'),
    ),
    
    # Grading Scale endpoints
    path(
        'grading-scales/<int:pk>/calculate-grade/',
        views.GradingScaleViewSet.as_view({'get': 'calculate_grade'}, name='grading-scale-calculate-grade'),
    ),
    
    # Academic Event endpoints
    path(
        'academic-events/upcoming/',
        views.AcademicEventViewSet.as_view({'get': 'upcoming_events'}, name='academic-event-upcoming'),
    ),
    path(
        'academic-events/by-date/',
        views.AcademicEventViewSet.as_view({'get': 'events_by_date'}, name='academic-event-by-date'),
    ),
]

# ============================================================================
# URL PATTERNS
# ============================================================================

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    path('', include(academic_year_router.urls)),
    path('', include(academic_term_router.urls)),
    path('', include(grade_level_router.urls)),
    path('', include(subject_router.urls)),
    path('', include(class_router.urls)),
    path('', include(enrollment_router.urls)),
    
    # Setup endpoints
    *setup_endpoints,
    
    # Dashboard endpoints
    *dashboard_endpoints,
    
    # Export endpoints
    *export_endpoints,
    
    # Utility endpoints
    *utility_endpoints,
]

# ============================================================================
# URL NAMES AND DOCUMENTATION
# ============================================================================

"""
URL Structure Documentation for Kenyan CBC Academic System:

BASE URL: /api/v1/academics/

1. Core Resources:
   - /academic-years/ - Academic years
   - /academic-terms/ - Academic terms
   - /grade-levels/ - Grade levels
   - /subjects/ - Subjects
   - /competency-areas/ - Competency areas for CBC
   - /competency-assessments/ - Competency assessments
   - /classrooms/ - Physical classrooms
   - /classes/ - Classes/groups
   - /enrollments/ - Student enrollments
   - /assessments/ - Assessments
   - /grades/ - Grades
   - /transcripts/ - Transcripts
   - /academic-reports/ - Academic reports
   - /attendance/ - Attendance records
   - /attendance-reports/ - Attendance reports
   - /schedules/ - Timetables/schedules
   - /teacher-assignments/ - Teacher assignments
   - /academic-events/ - Academic events
   - /grading-scales/ - Grading scales
   - /academic-configuration/ - Academic configuration

2. Bulk Operations:
   - /enrollment-bulk/bulk-create/ - Bulk create enrollments
   - /grade-bulk/bulk-create/ - Bulk create grades

3. Special Endpoints:
   - /setup/check/ - System setup check
   - /setup/essential-data/ - Essential data for UI
   - /dashboard/statistics/ - Dashboard statistics
   - /dashboard/class-performance/ - Class performance analysis
   - /dashboard/student-progress/<id>/ - Student progress tracking
   - /export/grades/ - Export grades as CSV
   - /export/attendance/ - Export attendance as CSV

4. Filtering and Search:
   All list endpoints support filtering, searching, and ordering:
   - ?search=math - Search across relevant fields
   - ?ordering=name - Order by field
   - ?is_active=true - Filter by status
   - ?academic_year=2023-2024 - Filter by academic year
   - ?term=term1 - Filter by term
   - ?status=active - Filter by enrollment status

5. Pagination:
   All list endpoints are paginated (20 items per page by default):
   - ?page=2 - Get specific page
   - ?page_size=50 - Change page size (max 100)

6. Key Actions:
   - Set current academic year: POST /academic-years/{id}/set-current/
   - Set current term: POST /academic-terms/{id}/set-current/
   - Publish assessment: POST /assessments/{id}/publish/
   - Generate transcript: POST /transcripts/{id}/generate/
   - Generate report: POST /academic-reports/{id}/generate/
   - Change enrollment status: POST /enrollments/{id}/change-status/
   - Get class timetable: GET /classes/{id}/timetable/
   - Get student progress: GET /dashboard/student-progress/{id}/

7. CBC-Specific Features:
   - Competency-based assessment endpoints
   - CBC grading system support
   - Competency area tracking
   - Kenyan curriculum alignment
"""