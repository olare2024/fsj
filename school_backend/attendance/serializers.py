"""
Serializers for Attendance models.
Fixed import issues with fallback serializers.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    StudentAttendance, TeacherAttendance, StaffAttendance,
    AttendanceSchedule, AttendanceRule, AttendanceReport,
    AttendanceException, BulkAttendanceUpload
)

# ===== FIXED IMPORTS WITH FALLBACKS =====

# Try importing from accounts, but create fallbacks if they don't exist
try:
    from accounts.serializers import StudentProfileSerializer, TeacherProfileSerializer
except ImportError:
    # Create fallback serializers
    class StudentProfileSerializer(serializers.Serializer):
        """Fallback student profile serializer"""
        id = serializers.UUIDField(read_only=True)
        user = serializers.SerializerMethodField()
        admission_number = serializers.CharField(read_only=True)
        
        def get_user(self, obj):
            if hasattr(obj, 'student'):
                return {'full_name': obj.student.get_full_name()}
            elif hasattr(obj, 'user'):
                return {'full_name': obj.user.get_full_name()}
            return {'full_name': 'Unknown Student'}
    
    class TeacherProfileSerializer(serializers.Serializer):
        """Fallback teacher profile serializer"""
        id = serializers.UUIDField(read_only=True)
        user = serializers.SerializerMethodField()
        teacher_id = serializers.CharField(read_only=True)
        
        def get_user(self, obj):
            if hasattr(obj, 'teacher'):
                return {'full_name': obj.teacher.get_full_name()}
            elif hasattr(obj, 'user'):
                return {'full_name': obj.user.get_full_name()}
            return {'full_name': 'Unknown Teacher'}

# Try importing academic serializers with fallbacks
try:
    from academics.serializers import ClassSerializer, AcademicYearSerializer, AcademicTermSerializer
except ImportError:
    class ClassSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        display_name = serializers.CharField(read_only=True)
    
    class AcademicYearSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)
    
    class AcademicTermSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)


class StudentAttendanceSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to safely get data
    student_name = serializers.SerializerMethodField()
    student_admission_number = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    academic_year_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    is_on_time = serializers.ReadOnlyField()
    attendance_value = serializers.ReadOnlyField()

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'student', 'student_name', 'student_admission_number',
            'class_enrolled', 'class_name', 'academic_year', 'academic_year_name',
            'term', 'term_name', 'date', 'session', 'status', 'time_in',
            'time_out', 'late_minutes', 'reason', 'medical_certificate',
            'parent_notified', 'parent_notification_time', 'recorded_by',
            'recorded_by_name', 'verified_by', 'verified_by_name',
            'verification_time', 'notes', 'is_on_time', 'attendance_value',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        try:
            if hasattr(obj.student, 'student'):
                return obj.student.student.get_full_name()
            elif hasattr(obj.student, 'get_full_name'):
                return obj.student.get_full_name()
        except:
            pass
        return "Unknown Student"
    
    def get_student_admission_number(self, obj):
        try:
            return obj.student.admission_number
        except:
            return "N/A"
    
    def get_class_name(self, obj):
        try:
            return obj.class_enrolled.name
        except:
            return "Unknown Class"
    
    def get_academic_year_name(self, obj):
        try:
            return obj.academic_year.name
        except:
            return "Unknown Year"
    
    def get_term_name(self, obj):
        try:
            if obj.term:
                return obj.term.get_name_display()
        except:
            pass
        return "No Term"
    
    def get_recorded_by_name(self, obj):
        try:
            if obj.recorded_by:
                return obj.recorded_by.get_full_name()
        except:
            pass
        return "Unknown"
    
    def get_verified_by_name(self, obj):
        try:
            if obj.verified_by:
                return obj.verified_by.get_full_name()
        except:
            pass
        return None


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_id = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAttendance
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_id', 'date', 'status',
            'check_in_time', 'check_out_time', 'late_minutes', 'leave_application',
            'notes', 'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_teacher_name(self, obj):
        try:
            if hasattr(obj.teacher, 'teacher'):
                return obj.teacher.teacher.get_full_name()
            elif hasattr(obj.teacher, 'get_full_name'):
                return obj.teacher.get_full_name()
        except:
            pass
        return "Unknown Teacher"
    
    def get_teacher_id(self, obj):
        try:
            return obj.teacher.teacher_id
        except:
            return "N/A"
    
    def get_recorded_by_name(self, obj):
        try:
            if obj.recorded_by:
                return obj.recorded_by.get_full_name()
        except:
            pass
        return "Unknown"


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffAttendance
        fields = [
            'id', 'staff_member', 'staff_name', 'staff_category', 'date', 'status',
            'check_in_time', 'check_out_time', 'work_hours', 'notes', 'recorded_by',
            'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_staff_name(self, obj):
        try:
            return obj.staff_member.get_full_name()
        except:
            return "Unknown Staff"
    
    def get_recorded_by_name(self, obj):
        try:
            if obj.recorded_by:
                return obj.recorded_by.get_full_name()
        except:
            pass
        return "Unknown"


class AttendanceScheduleSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.SerializerMethodField()
    applicable_classes_names = serializers.SerializerMethodField()
    applicable_staff_names = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSchedule
        fields = [
            'id', 'academic_year', 'academic_year_name', 'day', 'start_time',
            'end_time', 'is_teaching_day', 'is_holiday', 'holiday_name',
            'is_exam_day', 'is_event_day', 'event_name', 'applicable_classes',
            'applicable_classes_names', 'applicable_staff', 'applicable_staff_names',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_academic_year_name(self, obj):
        try:
            return obj.academic_year.name
        except:
            return "Unknown Year"
    
    def get_applicable_classes_names(self, obj):
        try:
            return [cls.name for cls in obj.applicable_classes.all()]
        except:
            return []
    
    def get_applicable_staff_names(self, obj):
        try:
            return [staff.get_full_name() for staff in obj.applicable_staff.all()]
        except:
            return []


class AttendanceRuleSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRule
        fields = [
            'id', 'name', 'attendance_type', 'academic_year', 'academic_year_name',
            'late_threshold_minutes', 'half_day_threshold_minutes',
            'minimum_attendance_percentage', 'working_hours_per_day',
            'send_parent_notifications', 'parent_notification_threshold',
            'send_admin_alerts', 'admin_alert_threshold', 'auto_generate_reports',
            'report_frequency', 'is_active', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_academic_year_name(self, obj):
        try:
            return obj.academic_year.name
        except:
            return "Unknown Year"
    
    def get_created_by_name(self, obj):
        try:
            if obj.created_by:
                return obj.created_by.get_full_name()
        except:
            pass
        return "Unknown"


class AttendanceReportSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    generated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceReport
        fields = [
            'id', 'report_type', 'title', 'academic_year', 'academic_year_name',
            'term', 'term_name', 'start_date', 'end_date', 'generated_date',
            'report_data', 'summary', 'report_file', 'generated_by',
            'generated_by_name', 'is_published', 'created_at'
        ]
        read_only_fields = ['id', 'generated_date', 'created_at']
    
    def get_academic_year_name(self, obj):
        try:
            return obj.academic_year.name
        except:
            return "Unknown Year"
    
    def get_term_name(self, obj):
        try:
            if obj.term:
                return obj.term.get_name_display()
        except:
            pass
        return "No Term"
    
    def get_generated_by_name(self, obj):
        try:
            if obj.generated_by:
                return obj.generated_by.get_full_name()
        except:
            pass
        return "Unknown"


class AttendanceExceptionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    staff_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceException
        fields = [
            'id', 'student', 'student_name', 'teacher', 'teacher_name',
            'staff_member', 'staff_name', 'exception_type', 'start_date',
            'end_date', 'reason', 'supporting_document', 'approved_by',
            'approved_by_name', 'approved_date', 'is_approved',
            'affects_attendance_calculation', 'notes', 'target_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        try:
            if obj.student and hasattr(obj.student, 'student'):
                return obj.student.student.get_full_name()
        except:
            pass
        return None
    
    def get_teacher_name(self, obj):
        try:
            if obj.teacher and hasattr(obj.teacher, 'teacher'):
                return obj.teacher.teacher.get_full_name()
        except:
            pass
        return None
    
    def get_staff_name(self, obj):
        try:
            if obj.staff_member:
                return obj.staff_member.get_full_name()
        except:
            pass
        return None
    
    def get_approved_by_name(self, obj):
        try:
            if obj.approved_by:
                return obj.approved_by.get_full_name()
        except:
            pass
        return None
    
    def get_target_name(self, obj):
        # Try each type in order
        name = self.get_student_name(obj)
        if name:
            return name
        
        name = self.get_teacher_name(obj)
        if name:
            return name
        
        name = self.get_staff_name(obj)
        if name:
            return name
        
        return None


class BulkAttendanceUploadSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    academic_year_name = serializers.SerializerMethodField()

    class Meta:
        model = BulkAttendanceUpload
        fields = [
            'id', 'uploaded_by', 'uploaded_by_name', 'academic_year', 'academic_year_name',
            'upload_file', 'upload_date', 'status', 'total_records', 'successful_records',
            'failed_records', 'error_log', 'processed_date', 'created_at'
        ]
        read_only_fields = ['id', 'upload_date', 'created_at']
    
    def get_uploaded_by_name(self, obj):
        try:
            return obj.uploaded_by.get_full_name()
        except:
            return "Unknown"
    
    def get_academic_year_name(self, obj):
        try:
            return obj.academic_year.name
        except:
            return "Unknown Year"


class BulkAttendanceCreateSerializer(serializers.Serializer):
    class_enrolled = serializers.UUIDField()
    date = serializers.DateField()
    session = serializers.ChoiceField(choices=StudentAttendance.SESSION_CHOICES)
    attendance_data = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_attendance_data(self, value):
        required_fields = ['student_id', 'status']
        for record in value:
            for field in required_fields:
                if field not in record:
                    raise serializers.ValidationError(f"Each record must contain '{field}' field")
        return value


class AttendanceStatisticsSerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    excused_days = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_daily_attendance = serializers.DecimalField(max_digits=5, decimal_places=2)
    trend_data = serializers.DictField()


class ClassAttendanceSummarySerializer(serializers.Serializer):
    # Use fallback ClassSerializer
    class_info = ClassSerializer()
    total_students = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    date = serializers.DateField()