from django.urls import path
from . import views

urlpatterns = [
    # Student Attendance Recording
    path('record/', views.AttendanceRecordView.as_view(), name='attendance-record'),
    path('record/bulk/', views.BulkAttendanceView.as_view(), name='bulk-attendance'),
    path('record/class/<uuid:class_id>/', views.ClassAttendanceView.as_view(), name='class-attendance'),
    
    # Attendance Management
    path('records/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('records/<uuid:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),
    
    # Attendance Reports
    path('reports/student/<uuid:student_id>/', views.StudentAttendanceReportView.as_view(), name='student-attendance-report'),
    path('reports/class/<uuid:class_id>/', views.ClassAttendanceReportView.as_view(), name='class-attendance-report'),
    path('reports/daily/', views.DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    path('reports/monthly/', views.MonthlyAttendanceReportView.as_view(), name='monthly-attendance-report'),
    path('reports/term/', views.TermAttendanceReportView.as_view(), name='term-attendance-report'),
    
    # Attendance Statistics
    path('stats/student/<uuid:student_id>/', views.StudentAttendanceStatsView.as_view(), name='student-attendance-stats'),
    path('stats/class/<uuid:class_id>/', views.ClassAttendanceStatsView.as_view(), name='class-attendance-stats'),
    path('stats/school/', views.SchoolAttendanceStatsView.as_view(), name='school-attendance-stats'),
    
    # Teacher and Staff Attendance
    path('teachers/', views.TeacherAttendanceListView.as_view(), name='teacher-attendance-list'),
    path('staff/', views.StaffAttendanceListView.as_view(), name='staff-attendance-list'),
    
    # Calendar Integration
    path('calendar/', views.attendance_calendar, name='attendance-calendar'),
]