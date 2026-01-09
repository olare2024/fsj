from django.contrib import admin
from .models import (
    StudentAttendance, TeacherAttendance, StaffAttendance,
    AttendanceSchedule, AttendanceRule, AttendanceReport,
    AttendanceException, BulkAttendanceUpload
)

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_enrolled', 'date', 'status', 'session', 'parent_notified']
    list_filter = ['status', 'date', 'session', 'class_enrolled', 'academic_year']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'status', 'check_in_time', 'check_out_time']
    list_filter = ['status', 'date']
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'staff_category', 'date', 'status', 'work_hours']
    list_filter = ['status', 'date', 'staff_category']
    search_fields = ['staff_member__first_name', 'staff_member__last_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AttendanceSchedule)
class AttendanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'day', 'start_time', 'end_time', 'is_teaching_day', 'is_holiday']
    list_filter = ['academic_year', 'day', 'is_teaching_day', 'is_holiday']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'attendance_type', 'academic_year', 'is_active']
    list_filter = ['attendance_type', 'academic_year', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'academic_year', 'start_date', 'end_date', 'is_published']
    list_filter = ['report_type', 'academic_year', 'is_published']
    readonly_fields = ['generated_date', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'

@admin.register(AttendanceException)
class AttendanceExceptionAdmin(admin.ModelAdmin):
    list_display = ['get_target_name', 'exception_type', 'start_date', 'end_date', 'is_approved']
    list_filter = ['exception_type', 'is_approved']
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'teacher__user__first_name', 'teacher__user__last_name',
        'staff_member__first_name', 'staff_member__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']

    def get_target_name(self, obj):
        if obj.student:
            return obj.student.user.get_full_name()
        elif obj.teacher:
            return obj.teacher.user.get_full_name()
        elif obj.staff_member:
            return obj.staff_member.get_full_name()
        return "Unknown"
    get_target_name.short_description = 'Target'

@admin.register(BulkAttendanceUpload)
class BulkAttendanceUploadAdmin(admin.ModelAdmin):
    list_display = ['uploaded_by', 'academic_year', 'upload_date', 'status', 'total_records', 'successful_records']
    list_filter = ['status', 'academic_year']
    readonly_fields = ['upload_date', 'processed_date', 'created_at', 'updated_at']