from django.urls import path
from . import views

urlpatterns = [
    # Timetable Management
    path('', views.TimetableView.as_view(), name='timetable-current'),
    path('generate/', views.TimetableGenerateView.as_view(), name='timetable-generate'),
    path('publish/<uuid:timetable_id>/', views.publish_timetable, name='timetable-publish'),
    path('conflicts/check/', views.timetable_conflicts_check, name='timetable-conflicts-check'),
    
    # Class Timetables
    path('class/<uuid:class_id>/', views.ClassTimetableView.as_view(), name='class-timetable'),
    
    # Teacher Timetables
    path('teacher/', views.TeacherTimetableView.as_view(), name='teacher-timetable'),
    path('teacher/<uuid:teacher_id>/', views.TeacherTimetableView.as_view(), name='teacher-timetable-specific'),
    
    # Student Timetables
    path('student/', views.StudentTimetableView.as_view(), name='student-timetable'),
    path('student/<uuid:student_id>/', views.StudentTimetableView.as_view(), name='student-timetable-specific'),
    
    # Daily Schedule
    path('daily/', views.daily_schedule, name='daily-schedule'),
    
    # Room Management
    path('rooms/', views.RoomListView.as_view(), name='room-list'),
    path('rooms/<uuid:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    path('rooms/<uuid:room_id>/availability/', views.RoomAvailabilityView.as_view(), name='room-availability'),
    
    # Room Bookings
    path('bookings/', views.RoomBookingListView.as_view(), name='room-booking-list'),
    
    # Timetable Adjustments
    path('adjustments/', views.TimetableAdjustmentListView.as_view(), name='timetable-adjustment-list'),
    path('adjustments/<uuid:pk>/', views.TimetableAdjustmentDetailView.as_view(), name='timetable-adjustment-detail'),
    
    # Special Schedules
    path('special-schedules/', views.SpecialScheduleListView.as_view(), name='special-schedule-list'),
    
    # Teacher Availability
    path('availability/', views.TeacherAvailabilityListView.as_view(), name='teacher-availability-list'),
    
    # Timetable Conflicts
    path('conflicts/', views.TimetableConflictListView.as_view(), name='timetable-conflict-list'),
]