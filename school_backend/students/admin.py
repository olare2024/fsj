"""
students/admin.py
Admin configuration for student models integrated with accounts system.
"""

from datetime import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import StudentProfile, StudentEnrollment

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin configuration for StudentProfile model."""
    
    list_display = (
        'get_full_name', 
        'admission_number', 
        'get_current_class', 
        'student_status', 
        'fee_status',
        'gpa',
        'get_enrollment_info'
    )
    
    list_filter = (
        'student_status', 
        'fee_status',
        'cbc_pathway',
        'conduct_rating',
        'is_active',
        'current_class__grade_level',
    )
    
    search_fields = (
        'user__first_name', 
        'user__last_name', 
        'admission_number',
        'upi_number',
        'nemis_number',
        'user__email',
        'user__phone_number',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'user_info',
        'contact_info',
        'parent_info',
        'medical_info_display',
        'academic_performance_display',
        'extracurricular_display',
    )
    
    fieldsets = (
        # Basic Information
        (_('Basic Information'), {
            'fields': (
                'user',
                'admission_number',
                'upi_number',
                'nemis_number',
                'student_status',
                'is_active',
            )
        }),
        
        # Academic Information
        (_('Academic Information'), {
            'fields': (
                'current_class',
                'current_academic_year',
                'cbc_pathway',
                'portfolio_status',
                'academic_performance_display',
            )
        }),
        
        # Performance Metrics
        (_('Performance Metrics'), {
            'fields': (
                'overall_grade',
                'gpa',
                'attendance_percentage',
                'rank_in_class',
                'community_service_hours_completed',
            )
        }),
        
        # Behavioral Information
        (_('Behavioral Information'), {
            'fields': (
                'conduct_rating',
                'behavioral_notes',
                'disciplinary_actions',
                'learning_style',
                'strengths',
                'weaknesses',
            )
        }),
        
        # Extracurricular
        (_('Extracurricular Activities'), {
            'fields': (
                'extracurricular_display',
                'talents',
                'club_memberships',
                'career_interests',
                'future_plans',
            )
        }),
        
        # Medical Information
        (_('Medical Information'), {
            'fields': (
                'medical_info_display',
                'health_conditions',
                'allergies',
                'dietary_restrictions',
                'medication_schedule',
            )
        }),
        
        # Transport Information
        (_('Transport Information'), {
            'fields': (
                'transport_mode',
                'bus_route',
                'bus_stop',
            )
        }),
        
        # Financial Information
        (_('Financial Information'), {
            'fields': (
                'fee_status',
                'fee_arrears',
                'scholarship_details',
            )
        }),
        
        # Previous Education
        (_('Previous Education'), {
            'fields': (
                'previous_school',
                'previous_class',
                'transfer_certificate',
                'birth_certificate',
                'recommendation_letter',
            )
        }),
        
        # System Information
        (_('System Information'), {
            'fields': (
                'user_info',
                'contact_info',
                'parent_info',
                'remarks',
                'metadata',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    raw_id_fields = ('user', 'current_class', 'current_academic_year')
    autocomplete_fields = ('current_class', 'current_academic_year')
    list_select_related = ('user', 'current_class', 'current_academic_year')
    list_per_page = 50
    
    def get_full_name(self, obj):
        """Get student's full name."""
        return obj.user.get_full_name() if obj.user else 'No User'
    get_full_name.short_description = _('Student Name')
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_current_class(self, obj):
        """Get current class display."""
        return str(obj.current_class) if obj.current_class else 'Not Assigned'
    get_current_class.short_description = _('Current Class')
    
    def get_enrollment_info(self, obj):
        """Get enrollment information."""
        enrollment = obj.get_current_enrollment()
        if enrollment:
            return f"{enrollment.roll_number} - {enrollment.get_status_display()}"
        return 'Not Enrolled'
    get_enrollment_info.short_description = _('Enrollment Info')
    
    def user_info(self, obj):
        """Display user information."""
        if obj.user:
            info = f"""
            <strong>Username:</strong> {obj.user.username}<br>
            <strong>Email:</strong> {obj.user.email}<br>
            <strong>Role:</strong> {obj.user.get_role_display()}<br>
            <strong>Profile Completed:</strong> {obj.user.profile_completed}<br>
            <strong>Is Active:</strong> {obj.user.is_active}<br>
            <strong>Date Joined:</strong> {obj.user.date_joined.strftime('%Y-%m-%d %H:%M')}
            """
            return format_html(info)
        return 'No User Account'
    user_info.short_description = _('User Account Information')
    
    def contact_info(self, obj):
        """Display contact information."""
        info = f"""
        <strong>Phone:</strong> {obj.user.phone_number or 'Not provided'}<br>
        <strong>Email:</strong> {obj.user.email}<br>
        <strong>Address:</strong> {obj.user.address or 'Not provided'}<br>
        <strong>City:</strong> {obj.user.city or 'Not provided'}<br>
        <strong>Country:</strong> {obj.user.country}
        """
        return format_html(info)
    contact_info.short_description = _('Contact Information')
    
    def parent_info(self, obj):
        """Display parent information."""
        info = f"""
        <strong>Parent Name:</strong> {obj.user.parent_name or 'Not provided'}<br>
        <strong>Parent Email:</strong> {obj.user.parent_email or 'Not provided'}<br>
        <strong>Parent Phone:</strong> {obj.user.parent_phone or 'Not provided'}<br>
        <strong>Parent Occupation:</strong> {obj.user.parent_occupation or 'Not provided'}
        """
        return format_html(info)
    parent_info.short_description = _('Parent Information')
    
    def medical_info_display(self, obj):
        """Display medical information."""
        info = f"""
        <strong>Blood Group:</strong> {obj.user.get_blood_group_display() if obj.user.blood_group else 'Not specified'}<br>
        <strong>Allergies:</strong> {obj.allergies or 'None'}<br>
        <strong>Dietary Restrictions:</strong> {', '.join(obj.dietary_restrictions) if obj.dietary_restrictions else 'None'}<br>
        <strong>Doctor:</strong> {obj.user.doctor_name or 'Not specified'}<br>
        <strong>Doctor Phone:</strong> {obj.user.doctor_phone or 'Not specified'}
        """
        return format_html(info)
    medical_info_display.short_description = _('Medical Information')
    
    def academic_performance_display(self, obj):
        """Display academic performance."""
        info = f"""
        <strong>GPA:</strong> {obj.gpa}<br>
        <strong>Attendance:</strong> {obj.attendance_percentage}%<br>
        <strong>Overall Grade:</strong> {obj.overall_grade or 'Not assigned'}<br>
        <strong>Class Rank:</strong> {obj.rank_in_class or 'Not ranked'}<br>
        <strong>Test Scores:</strong> {len(obj.test_scores) if obj.test_scores else 0} recorded
        """
        return format_html(info)
    academic_performance_display.short_description = _('Academic Performance')
    
    def extracurricular_display(self, obj):
        """Display extracurricular activities."""
        if obj.extracurricular_activities:
            activities = '<br>'.join([
                f"• {activity.get('activity', 'Activity')} ({activity.get('position', 'Member')})"
                for activity in obj.extracurricular_activities[:5]  # Show first 5
            ])
            if len(obj.extracurricular_activities) > 5:
                activities += f"<br>• ... and {len(obj.extracurricular_activities) - 5} more"
            return format_html(activities)
        return 'No extracurricular activities'
    extracurricular_display.short_description = _('Extracurricular Activities')
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user',
            'current_class',
            'current_academic_year'
        ).prefetch_related(
            'enrollments',
            'friends'
        )
    
    def get_list_display_links(self, request, list_display):
        """Set which field to link to change form."""
        return ('get_full_name',)
    
    def has_add_permission(self, request):
        """Prevent adding student profiles directly - use User creation."""
        return False
    
    def save_model(self, request, obj, form, change):
        """Handle save with user updates."""
        if not change:  # Only for new objects
            # Generate admission number if not provided
            if not obj.admission_number:
                from datetime import datetime
                current_year = datetime.now().year
                last_student = StudentProfile.objects.filter(
                    admission_number__startswith=f'DEL-STU-{current_year}-'
                ).order_by('-admission_number').first()
                
                if last_student:
                    try:
                        last_seq = int(last_student.admission_number.split('-')[-1])
                        new_seq = last_seq + 1
                    except (ValueError, IndexError):
                        new_seq = 1
                else:
                    new_seq = 1
                
                obj.admission_number = f"DEL-STU-{current_year}-{new_seq:04d}"
        
        super().save_model(request, obj, form, change)


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for StudentEnrollment model."""
    
    list_display = (
        'get_student_name',
        'admission_number',
        'get_class_display',
        'academic_year',
        'roll_number',
        'status',
        'fee_status',
        'enrollment_date',
    )
    
    list_filter = (
        'status',
        'fee_status',
        'academic_year',
        'class_enrolled__grade_level',
        'house',
        'cbc_pathway_selection',
    )
    
    search_fields = (
        'student_profile__user__first_name',
        'student_profile__user__last_name',
        'student_profile__admission_number',
        'enrollment_number',
        'student_profile__upi_number',
        'student_profile__nemis_number',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'enrollment_summary',
        'student_info',
        'class_info',
        'enrollment_number',
    )
    
    fieldsets = (
        # Core Information
        (_('Core Information'), {
            'fields': (
                'student_profile',
                'class_enrolled',
                'academic_year',
                'enrollment_number',
                'enrollment_date',
            )
        }),
        
        # Academic Information
        (_('Academic Information'), {
            'fields': (
                'roll_number',
                'status',
                'status_changed_date',
                'status_reason',
                'cbc_pathway_selection',
                'senior_track_selection',
                'house',
            )
        }),
        
        # Financial Information
        (_('Financial Information'), {
            'fields': (
                'fee_status',
                'fee_arrears',
            )
        }),
        
        # Display Information
        (_('Summary Information'), {
            'fields': (
                'enrollment_summary',
                'student_info',
                'class_info',
            ),
            'classes': ('wide',),
        }),
        
        # Additional Information
        (_('Additional Information'), {
            'fields': (
                'remarks',
                'enrollment_metadata',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # ✅ CORRECT - This should be a list, not a method
    actions = ['mark_as_active', 'mark_as_graduated', 'mark_as_transferred']
    
    raw_id_fields = ('student_profile', 'class_enrolled', 'academic_year')
    autocomplete_fields = ('student_profile', 'class_enrolled', 'academic_year')
    list_select_related = (
        'student_profile__user',
        'class_enrolled',
        'academic_year',
    )
    list_per_page = 50
    
    # ✅ CORRECT - Action methods are defined separately
    def mark_as_active(self, request, queryset):
        """Mark selected enrollments as active."""
        from django.utils import timezone
        count = queryset.update(status='active', status_changed_date=timezone.now())
        self.message_user(request, f'{count} enrollment(s) marked as active.')
    mark_as_active.short_description = _('Mark selected enrollments as active')
    
    def mark_as_graduated(self, request, queryset):
        """Mark selected enrollments as graduated."""
        from django.utils import timezone
        count = queryset.update(status='graduated', status_changed_date=timezone.now())
        self.message_user(request, f'{count} enrollment(s) marked as graduated.')
    mark_as_graduated.short_description = _('Mark selected enrollments as graduated')
    
    def mark_as_transferred(self, request, queryset):
        """Mark selected enrollments as transferred."""
        from django.utils import timezone
        count = queryset.update(status='transferred', status_changed_date=timezone.now())
        self.message_user(request, f'{count} enrollment(s) marked as transferred.')
    mark_as_transferred.short_description = _('Mark selected enrollments as transferred')
    
    def get_student_name(self, obj):
        """Get student's full name."""
        return obj.student_profile.user.get_full_name() if obj.student_profile.user else 'No User'
    get_student_name.short_description = _('Student Name')
    get_student_name.admin_order_field = 'student_profile__user__first_name'
    
    def admission_number(self, obj):
        """Get student's admission number."""
        return obj.student_profile.admission_number
    admission_number.short_description = _('Admission No.')
    admission_number.admin_order_field = 'student_profile__admission_number'
    
    def get_class_display(self, obj):
        """Get class display name."""
        return str(obj.class_enrolled) if obj.class_enrolled else 'No Class'
    get_class_display.short_description = _('Class')
    
    def enrollment_summary(self, obj):
        """Display enrollment summary."""
        info = f"""
        <strong>Student:</strong> {obj.student_profile.user.get_full_name() if obj.student_profile.user else 'No User'}<br>
        <strong>Admission No:</strong> {obj.student_profile.admission_number}<br>
        <strong>Class:</strong> {obj.class_enrolled}<br>
        <strong>Academic Year:</strong> {obj.academic_year}<br>
        <strong>Roll No:</strong> {obj.roll_number or 'Not assigned'}<br>
        <strong>Status:</strong> {obj.get_status_display()}<br>
        <strong>Enrollment Date:</strong> {obj.enrollment_date.strftime('%Y-%m-%d')}<br>
        <strong>Is Current:</strong> {obj.is_current}
        """
        return format_html(info)
    enrollment_summary.short_description = _('Enrollment Summary')
    
    def student_info(self, obj):
        """Display student information."""
        student = obj.student_profile
        info = f"""
        <strong>Name:</strong> {student.user.get_full_name() if student.user else 'No User'}<br>
        <strong>Email:</strong> {student.user.email if student.user else 'No email'}<br>
        <strong>Phone:</strong> {student.user.phone_number or 'Not provided'}<br>
        <strong>Current GPA:</strong> {student.gpa}<br>
        <strong>Attendance:</strong> {student.attendance_percentage}%<br>
        <strong>Student Status:</strong> {student.get_student_status_display()}<br>
        <strong>CBC Pathway:</strong> {student.get_cbc_pathway_display() if student.cbc_pathway else 'Not set'}
        """
        return format_html(info)
    student_info.short_description = _('Student Information')
    
    def class_info(self, obj):
        """Display class information."""
        class_obj = obj.class_enrolled
        if class_obj:
            info = f"""
            <strong>Class Name:</strong> {class_obj.display_name}<br>
            <strong>Grade Level:</strong> {class_obj.get_grade_level_display()}<br>
            <strong>Education Level:</strong> {class_obj.get_education_level_display()}<br>
            <strong>Curriculum:</strong> {class_obj.get_primary_curriculum_display() if class_obj.primary_curriculum else 'Not set'}<br>
            <strong>CBC Pathway:</strong> {class_obj.get_cbc_pathway_display() if class_obj.cbc_pathway else 'Not set'}<br>
            <strong>Capacity:</strong> {class_obj.capacity}<br>
            <strong>Current Strength:</strong> {class_obj.current_strength}
            """
            return format_html(info)
        return 'No Class Information'
    class_info.short_description = _('Class Information')
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'student_profile__user',
            'class_enrolled',
            'academic_year',
        )
    
    def get_list_display_links(self, request, list_display):
        """Set which field to link to change form."""
        return ('get_student_name',)
    
    def save_model(self, request, obj, form, change):
        """Handle save with roll number generation."""
        if not change and not obj.roll_number:
            # Auto-generate roll number
            enrollments = StudentEnrollment.objects.filter(
                class_enrolled=obj.class_enrolled,
                academic_year=obj.academic_year
            ).exclude(roll_number=None).order_by('-roll_number')
            
            if enrollments.exists():
                obj.roll_number = enrollments.first().roll_number + 1
            else:
                obj.roll_number = 1
        
        super().save_model(request, obj, form, change)

# Additional models for future expansion
class ParentGuardianAdmin(admin.ModelAdmin):
    """Admin configuration for ParentGuardian model (to be implemented)."""
    pass


class StudentAchievementAdmin(admin.ModelAdmin):
    """Admin configuration for StudentAchievement model (to be implemented)."""
    pass


class StudentBehaviorAdmin(admin.ModelAdmin):
    """Admin configuration for StudentBehavior model (to be implemented)."""
    pass