# academics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'academic-years', views.AcademicYearViewSet, basename='academic-year')
router.register(r'academic-terms', views.AcademicTermViewSet, basename='academic-term')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subject-assignments', views.SubjectAssignmentViewSet, basename='subject-assignment')
router.register(r'student-enrollments', views.StudentEnrollmentViewSet, basename='student-enrollment')
router.register(r'lesson-plans', views.LessonPlanViewSet, basename='lesson-plan')
router.register(r'syllabi', views.SyllabusViewSet, basename='syllabus')
router.register(r'academic-events', views.AcademicEventViewSet, basename='academic-event')

urlpatterns = [
    # ==================== ROUTER-BASED ENDPOINTS ====================
    path('', include(router.urls)),
    
    # ==================== DASHBOARD & ANALYTICS ====================
    path('dashboard/', views.AcademicDashboardView.as_view(), name='academic-dashboard'),
    path('statistics/classes/', views.ClassStatisticsView.as_view(), name='class-statistics'),
    path('statistics/teacher-workload/', views.TeacherWorkloadView.as_view(), name='teacher-workload'),
    path('search/', views.AcademicSearchView.as_view(), name='academic-search'),
    
    # ==================== EXPORT & BULK OPERATIONS ====================
    path('enrollments/export-csv/', views.ExportEnrollmentsCSVView.as_view(), name='export-enrollments-csv'),
    path('calendar/', views.AcademicCalendarView.as_view(), name='academic-calendar'),
    
    # ==================== UTILITY ENDPOINTS ====================
    path('overview/', views.AcademicOverviewView.as_view(), name='academic-overview'),
]

# ==================== API DOCUMENTATION INFO ====================
"""
Academic Module API Endpoints:

CORE MODELS (ViewSets - CRUD operations available):
Each ViewSet provides standard CRUD operations (GET, POST, PUT, PATCH, DELETE)

- Academic Years:           /api/v1/academics/academic-years/
  • GET /current/          - Get current academic year
  • POST /{id}/set_current/ - Set academic year as current
  • GET /{id}/statistics/  - Academic year statistics
  
- Academic Terms:          /api/v1/academics/academic-terms/
  • POST /{id}/set_current/ - Set term as current
  • GET /{id}/events/      - Term events
  • GET /{id}/progress/    - Term progress

- Subjects:                /api/v1/academics/subjects/
  • GET /{id}/teachers/    - Subject teachers
  • GET /categories/       - Subject categories
  • GET /by_curriculum/    - Subjects by curriculum
  • GET /{id}/syllabus/    - Subject syllabus
  • GET /{id}/assignments/ - Subject assignments

- Classes:                 /api/v1/academics/classes/
  • GET /{id}/students/    - Class students
  • GET /{id}/subjects/    - Class subjects
  • GET /{id}/timetable/   - Class timetable
  • GET /{id}/statistics/  - Class statistics
  • POST /{id}/assign_class_teacher/ - Assign class teacher

- Subject Assignments:     /api/v1/academics/subject-assignments/
  • POST /bulk_assign/     - Bulk assign subjects
  • GET /teacher_workload/ - Teacher workload
  • GET /by_teacher/       - Assignments by teacher

- Student Enrollments:     /api/v1/academics/student-enrollments/
  • POST /bulk_enroll/     - Bulk enroll students
  • GET /export_csv/       - Export to CSV
  • GET /report/           - Enrollment reports
  • GET /active/           - Active enrollments only

- Lesson Plans:            /api/v1/academics/lesson-plans/
  • GET /upcoming/         - Upcoming lesson plans
  • GET /weekly/           - Weekly lesson plans
  • POST /{id}/mark_completed/ - Mark as completed

- Syllabi:                 /api/v1/academics/syllabi/
  • POST /{id}/mark_topic_completed/ - Mark topic completed
  • GET /{id}/progress/    - Syllabus progress

- Academic Events:         /api/v1/academics/academic-events/
  • GET /upcoming/         - Upcoming events
  • GET /calendar/         - Calendar events

DASHBOARD & ANALYTICS:
- GET /api/v1/academics/dashboard/       - Comprehensive dashboard data
- GET /api/v1/academics/statistics/classes/ - Class statistics
- GET /api/v1/academics/statistics/teacher-workload/ - Teacher workload analysis
- GET /api/v1/academics/search/          - Search across academic models
- GET /api/v1/academics/overview/        - Academic overview (alias for dashboard)

EXPORT & UTILITIES:
- GET /api/v1/academics/enrollments/export-csv/ - Export enrollments to CSV
- GET /api/v1/academics/calendar/        - Calendar data for external widgets

FILTERING & QUERY PARAMETERS:
Most list endpoints support:
• ?academic_year={uuid}    - Filter by academic year
• ?is_active=true/false    - Filter active/inactive
• ?search={query}          - Search across fields
• ?ordering={field}        - Order results
• ?page={number}           - Pagination
• ?page_size={number}      - Items per page (max 100)

REQUEST/RESPONSE FORMAT:
• All endpoints return JSON
• Bulk operations return HTTP 207 for partial success
• Errors follow standard HTTP status codes with detailed messages
• Dates in ISO 8601 format (YYYY-MM-DD)
• UUIDs for all resource identifiers

PERMISSIONS:
• All endpoints require authentication
• Some operations may require staff/admin permissions
• Data filtering based on user role

VERSIONING:
• API version in URL path (/api/v1/)
• Backward compatibility maintained
• New features may require version bump
"""