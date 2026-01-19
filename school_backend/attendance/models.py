"""
Attendance models for school management system.
Fixed all Django system check errors - NO duplicate related_name conflicts.
"""

from django.db import models
from django.conf import settings
import uuid


class StudentAttendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused Absence'),
        ('sick', 'Sick Leave'),
        ('emergency', 'Emergency Leave'),
        ('half_day', 'Half Day'),
    )

    SESSION_CHOICES = (
        ('morning', 'Morning Session'),
        ('afternoon', 'Afternoon Session'),
        ('full_day', 'Full Day'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, 
                                related_name='student_attendances')
    class_enrolled = models.ForeignKey('academics.Class', on_delete=models.CASCADE)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.AcademicTerm', on_delete=models.CASCADE, 
                             null=True, blank=True)
    
    # Attendance details
    date = models.DateField()
    session = models.CharField(max_length=20, choices=SESSION_CHOICES, default='full_day')
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    
    # Time tracking
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0, 
                                       help_text="Minutes late if status is 'late'")
    
    # Absence details
    reason = models.TextField(blank=True, null=True)
    medical_certificate = models.FileField(upload_to='attendance/medical_certificates/', 
                                           blank=True, null=True)
    parent_notified = models.BooleanField(default=False)
    parent_notification_time = models.DateTimeField(null=True, blank=True)
    
    # Record keeping - UNIQUE related_name for each ForeignKey
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, related_name='recorded_student_attendances')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, 
                                    related_name='verified_student_attendances')
    verification_time = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Attendance"
        verbose_name_plural = "Student Attendance Records"
        unique_together = ['student', 'date', 'session']
        ordering = ['-date', 'student_id']
        indexes = [
            models.Index(fields=['date', 'class_enrolled']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['status', 'date']),
        ]

    def __str__(self):
        """String representation with safe student name access"""
        try:
            # Try to get student name safely
            if hasattr(self.student, 'user'):
                student_name = self.student.user.get_full_name()
            elif hasattr(self.student, 'get_full_name'):
                student_name = self.student.get_full_name()
            elif hasattr(self.student, 'first_name') and hasattr(self.student, 'last_name'):
                student_name = f"{self.student.first_name} {self.student.last_name}"
            else:
                student_name = f"Student {self.student.id}"
        except Exception:
            student_name = "Unknown Student"
        
        return f"{student_name} - {self.date} - {self.status}"

    @property
    def is_on_time(self):
        """Check if attendance is on time"""
        return self.status != 'late' or self.late_minutes == 0

    @property
    def attendance_value(self):
        """Returns numerical value for attendance calculations"""
        if self.status in ['present', 'late']:
            return 1.0
        elif self.status == 'half_day':
            return 0.5
        elif self.status in ['excused', 'sick', 'emergency']:
            return 0.75  # Partial value for excused absences
        else:
            return 0.0


class TeacherAttendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('sick_leave', 'Sick Leave'),
        ('annual_leave', 'Annual Leave'),
        ('emergency_leave', 'Emergency Leave'),
        ('professional_development', 'Professional Development'),
        ('official_duty', 'Official Duty'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.CASCADE, 
                                related_name='teacher_attendance_records')
    
    # Attendance details
    date = models.DateField()
    status = models.CharField(max_length=30, choices=ATTENDANCE_STATUS)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0)
    
    # Leave details (if applicable)
    leave_application = models.ForeignKey(
        'teachers.TeacherLeave', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='teacher_attendance_leave_applications'  # UNIQUE related_name
    )
    
    # Record keeping - UNIQUE related_name for each ForeignKey
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, 
                                    related_name='recorded_teacher_attendances')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, 
                                    related_name='verified_teacher_attendances')  # CHANGED: UNIQUE
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Attendance"
        verbose_name_plural = "Teacher Attendance Records"
        unique_together = ['teacher', 'date']
        ordering = ['-date', 'teacher_id']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['teacher', 'date']),
        ]

    def __str__(self):
        """String representation with safe teacher name access"""
        try:
            # Try to get teacher name safely
            if hasattr(self.teacher, 'user'):
                teacher_name = self.teacher.user.get_full_name()
            elif hasattr(self.teacher, 'teacher'):
                teacher_name = self.teacher.teacher.get_full_name()
            elif hasattr(self.teacher, 'get_full_name'):
                teacher_name = self.teacher.get_full_name()
            elif hasattr(self.teacher, 'first_name') and hasattr(self.teacher, 'last_name'):
                teacher_name = f"{self.teacher.first_name} {self.teacher.last_name}"
            else:
                teacher_name = f"Teacher {self.teacher.id}"
        except Exception:
            teacher_name = "Unknown Teacher"
        
        return f"{teacher_name} - {self.date} - {self.status}"


class StaffAttendance(models.Model):
    STAFF_CATEGORIES = (
        ('administrative', 'Administrative Staff'),
        ('support', 'Support Staff'),
        ('maintenance', 'Maintenance Staff'),
        ('security', 'Security Staff'),
        ('other', 'Other Staff'),
    )

    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'On Leave'),
        ('official_duty', 'Official Duty'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                     related_name='staff_attendance_records')  # UNIQUE
    staff_category = models.CharField(max_length=20, choices=STAFF_CATEGORIES)
    
    # Attendance details
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Record keeping
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, related_name='recorded_staff_attendance')  # UNIQUE
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Attendance"
        verbose_name_plural = "Staff Attendance Records"
        unique_together = ['staff_member', 'date']
        ordering = ['-date', 'staff_member__first_name']

    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.date} - {self.status}"


class AttendanceSchedule(models.Model):
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    
    # Schedule details
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_teaching_day = models.BooleanField(default=True)
    
    # Special day types
    is_holiday = models.BooleanField(default=False)
    holiday_name = models.CharField(max_length=100, blank=True, null=True)
    is_exam_day = models.BooleanField(default=False)
    is_event_day = models.BooleanField(default=False)
    event_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Applicable to
    applicable_classes = models.ManyToManyField('academics.Class', blank=True)
    applicable_staff = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance Schedule"
        verbose_name_plural = "Attendance Schedules"
        unique_together = ['academic_year', 'day']
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.get_day_display()} - {self.start_time} to {self.end_time}"


class AttendanceRule(models.Model):
    ATTENDANCE_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    attendance_type = models.CharField(max_length=10, choices=ATTENDANCE_TYPE_CHOICES)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    
    # Rules
    late_threshold_minutes = models.IntegerField(default=15, 
                                                 help_text="Minutes after which arrival is considered late")
    half_day_threshold_minutes = models.IntegerField(default=120, 
                                                     help_text="Minutes after which it's considered half day")
    minimum_attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, 
                                                        default=75.0)
    working_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Notifications
    send_parent_notifications = models.BooleanField(default=True)
    parent_notification_threshold = models.IntegerField(default=3, 
                                                        help_text="Consecutive absences before notifying parents")
    send_admin_alerts = models.BooleanField(default=True)
    admin_alert_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=60.0, 
                                                help_text="Attendance percentage below which to alert admin")
    
    # Automatic actions
    auto_generate_reports = models.BooleanField(default=True)
    report_frequency = models.CharField(max_length=20, choices=(
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('termly', 'Termly'),
    ), default='monthly')
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, related_name='created_attendance_rules')  # UNIQUE
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance Rule"
        verbose_name_plural = "Attendance Rules"
        unique_together = ['attendance_type', 'academic_year']
        ordering = ['attendance_type', 'academic_year']

    def __str__(self):
        return f"{self.name} - {self.attendance_type}"


class AttendanceReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('termly', 'Termly Report'),
        ('custom', 'Custom Period Report'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.AcademicTerm', on_delete=models.CASCADE, 
                             null=True, blank=True)
    
    # Report period
    start_date = models.DateField()
    end_date = models.DateField()
    generated_date = models.DateTimeField(auto_now_add=True)
    
    # Report data (stored as JSON for flexibility)
    report_data = models.JSONField(default=dict)
    summary = models.JSONField(default=dict)
    
    # File attachment
    report_file = models.FileField(upload_to='attendance/reports/', blank=True, null=True)
    
    # Metadata
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                     null=True, related_name='generated_attendance_reports')  # UNIQUE
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance Report"
        verbose_name_plural = "Attendance Reports"
        ordering = ['-generated_date']

    def __str__(self):
        return f"{self.title} - {self.generated_date.strftime('%Y-%m-%d')}"


class AttendanceException(models.Model):
    EXCEPTION_TYPES = (
        ('late_arrival', 'Late Arrival Excused'),
        ('early_departure', 'Early Departure Excused'),
        ('absence_excused', 'Absence Excused'),
        ('special_permission', 'Special Permission'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Use settings.AUTH_USER_MODEL for consistency - FIXED ForeignKey issue
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                null=True, blank=True, related_name='student_exceptions')
    teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.CASCADE, 
                                null=True, blank=True, related_name='teacher_exceptions')
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                     null=True, blank=True, related_name='staff_exceptions')
    
    # Exception details
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    supporting_document = models.FileField(upload_to='attendance/exceptions/', 
                                           blank=True, null=True)
    
    # Approval - FIXED: Use UNIQUE related_name
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, related_name='approved_attendance_exceptions')  # UNIQUE
    
    approved_date = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    # Effect
    affects_attendance_calculation = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance Exception"
        verbose_name_plural = "Attendance Exceptions"
        ordering = ['-start_date']

    def __str__(self):
        """Safe string representation for exception"""
        try:
            if self.student:
                target = self.student.get_full_name()
            elif self.teacher:
                if hasattr(self.teacher, 'user'):
                    target = self.teacher.user.get_full_name()
                else:
                    target = f"Teacher {self.teacher.id}"
            elif self.staff_member:
                target = self.staff_member.get_full_name()
            else:
                target = "Unknown"
        except Exception:
            target = "Unknown"
        
        return f"{target} - {self.exception_type} - {self.start_date} to {self.end_date}"


class BulkAttendanceUpload(models.Model):
    UPLOAD_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                    related_name='uploaded_attendance_files')  # UNIQUE
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    
    # Upload details
    upload_file = models.FileField(upload_to='attendance/bulk_uploads/')
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=UPLOAD_STATUS, default='pending')
    
    # Processing results
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    error_log = models.TextField(blank=True, null=True)
    
    # Metadata
    processed_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bulk Attendance Upload"
        verbose_name_plural = "Bulk Attendance Uploads"
        ordering = ['-upload_date']

    def __str__(self):
        return f"Bulk Upload - {self.upload_date.strftime('%Y-%m-%d')} - {self.status}"


# Helper methods for attendance calculations
class AttendanceCalculations:
    """Helper class for attendance calculations"""
    
    @staticmethod
    def calculate_attendance_percentage(present_days, total_days):
        """Calculate attendance percentage"""
        if total_days > 0:
            return (present_days / total_days) * 100
        return 0
    
    @staticmethod
    def get_status_color(status):
        """Get color for attendance status"""
        color_map = {
            'present': '#10B981',  # Green
            'absent': '#EF4444',   # Red
            'late': '#F59E0B',     # Yellow
            'excused': '#6B7280',  # Gray
            'sick': '#8B5CF6',     # Purple
            'emergency': '#DC2626', # Dark red
            'half_day': '#F97316', # Orange
        }
        return color_map.get(status, '#6B7280')
    
    @staticmethod
    def is_valid_status(status, attendance_type='student'):
        """Check if status is valid for attendance type"""
        valid_statuses = {
            'student': ['present', 'absent', 'late', 'excused', 'sick', 'emergency', 'half_day'],
            'teacher': ['present', 'absent', 'late', 'sick_leave', 'annual_leave', 
                       'emergency_leave', 'professional_development', 'official_duty'],
            'staff': ['present', 'absent', 'late', 'leave', 'official_duty'],
        }
        return status in valid_statuses.get(attendance_type, [])