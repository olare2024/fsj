from django.contrib import admin
from .models import (
    Timetable, Period, TimetableEntry, TeacherTimetable, ClassTimetable,
    Room, RoomBooking, TimetableAdjustment, SpecialSchedule,
    TimetableConflict, TeacherAvailability
)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'term', 'is_active', 'is_published', 'created_by']
    list_filter = ['academic_year', 'term', 'is_active', 'is_published']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'period_number', 'start_time', 'end_time', 'period_type', 'is_break']
    list_filter = ['timetable', 'period_type', 'is_break']
    search_fields = ['timetable__name', 'break_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'day', 'period', 'subject', 'teacher', 'class_assigned', 'room', 'is_active']
    list_filter = ['timetable', 'day', 'is_active']
    search_fields = ['subject__name', 'teacher__user__first_name', 'class_assigned__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TeacherTimetable)
class TeacherTimetableAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day', 'period_number', 'subject_name', 'class_name']
    list_filter = ['teacher', 'day']
    search_fields = ['teacher__user__first_name', 'subject_name', 'class_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ClassTimetable)
class ClassTimetableAdmin(admin.ModelAdmin):
    list_display = ['class_assigned', 'day', 'period_number', 'subject_name', 'teacher_name']
    list_filter = ['class_assigned', 'day']
    search_fields = ['class_assigned__name', 'subject_name', 'teacher_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'capacity', 'location', 'is_active', 'is_bookable']
    list_filter = ['room_type', 'is_active', 'is_bookable']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'title', 'start_datetime', 'end_datetime', 'status', 'booked_by']
    list_filter = ['room', 'booking_type', 'status']
    search_fields = ['room__name', 'title', 'booked_by__first_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TimetableAdjustment)
class TimetableAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['timetable_entry', 'adjustment_type', 'adjustment_date', 'is_active', 'is_notified']
    list_filter = ['adjustment_type', 'is_active', 'is_notified', 'adjustment_date']
    search_fields = ['timetable_entry__subject__name', 'original_teacher__user__first_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SpecialSchedule)
class SpecialScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'special_type', 'start_date', 'end_date', 'is_whole_school', 'is_published']
    list_filter = ['special_type', 'is_whole_school', 'is_published']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TimetableConflict)
class TimetableConflictAdmin(admin.ModelAdmin):
    list_display = ['conflict_type', 'severity', 'conflict_date', 'is_resolved']
    list_filter = ['conflict_type', 'severity', 'is_resolved']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'availability_type', 'day_of_week', 'start_date', 'end_date', 'is_available']
    list_filter = ['availability_type', 'is_available', 'is_approved']
    search_fields = ['teacher__user__first_name']
    readonly_fields = ['created_at', 'updated_at']