# teachers/admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
import csv
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.admin import SimpleListFilter

# ============================================================================
# IMPORT MODELS AT THE TOP USING RELATIVE IMPORTS
# ============================================================================
from .models import (
    Department, TeacherProfile, ProfessionalStanding,
    PerformanceIndicator, TeacherTransfer, TeacherDocument,
    TeacherQualification, TeacherTraining, TeacherAssignment,
    TeacherAttendance, TeacherLeave
)


# ============================================================================
# CUSTOM FILTERS
# ============================================================================

class TSCStatusFilter(SimpleListFilter):
    title = 'TSC Status'
    parameter_name = 'tsc_status'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.TSCStatus.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tsc_status=self.value())
        return queryset


class TeachingLevelFilter(SimpleListFilter):
    title = 'Teaching Level'
    parameter_name = 'teaching_level'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.TeachingLevel.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(teaching_level=self.value())
        return queryset


class EmploymentStatusFilter(SimpleListFilter):
    title = 'Employment Status'
    parameter_name = 'employment_status'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.EmploymentStatus.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(employment_status=self.value())
        return queryset


class DepartmentFilter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'department'
    
    def lookups(self, request, model_admin):
        departments = Department.objects.all()
        return [(d.id, str(d)) for d in departments]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(department_id=self.value())
        return queryset


class CBCTrainedFilter(SimpleListFilter):
    title = 'CBC Trained'
    parameter_name = 'cbc_trained'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(cbc_trained=True)
        elif self.value() == 'no':
            return queryset.filter(cbc_trained=False)
        return queryset


class TPDStatusFilter(SimpleListFilter):
    title = 'TPD Status'
    parameter_name = 'tpd_status'
    
    def lookups(self, request, model_admin):
        return (
            ('expiring_soon', 'TPD Expiring Soon (30 days)'),
            ('expired', 'TPD Expired'),
            ('valid', 'TPD Valid'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        if self.value() == 'expiring_soon':
            return queryset.filter(
                tpd_next_renewal_date__range=[today, thirty_days_later]
            )
        elif self.value() == 'expired':
            return queryset.filter(
                tpd_next_renewal_date__lt=today
            )
        elif self.value() == 'valid':
            return queryset.filter(
                tpd_next_renewal_date__gte=today
            )
        return queryset


# ============================================================================
# FIXED INLINE ADMIN CLASSES WITH EXPLICIT MODEL DEFINITIONS
# ============================================================================

class TeacherQualificationInline(admin.TabularInline):
    """Inline for teacher qualifications"""
    model = TeacherQualification
    extra = 0
    fields = ('title', 'qualification_type', 'institution', 'year_of_graduation', 
              'verification_status', 'is_completed')
    readonly_fields = ('verification_status',)
    fk_name = 'teacher'  # Explicitly specify the ForeignKey field


class TeacherTrainingInline(admin.TabularInline):
    """Inline for teacher trainings"""
    model = TeacherTraining
    extra = 0
    fields = ('title', 'training_type', 'organizer', 'start_date', 'end_date', 
              'status', 'is_certified')
    readonly_fields = ('status',)
    fk_name = 'teacher'


class TeacherDocumentInline(admin.TabularInline):
    """Inline for teacher documents"""
    model = TeacherDocument
    extra = 0
    fields = ('document_type', 'title', 'status', 'expiry_date', 
              'is_required', 'file_preview')
    readonly_fields = ('file_preview',)
    fk_name = 'teacher'
    
    def file_preview(self, obj):
        if obj.document_file:
            return format_html(
                '<a href="{}" target="_blank">View Document</a>',
                obj.document_file.url
            )
        return "-"
    file_preview.short_description = "Document"


class TeacherAssignmentInline(admin.TabularInline):
    """Inline for teacher assignments"""
    model = TeacherAssignment
    extra = 0
    fields = ('subject', 'class_assigned', 'assignment_type', 'start_date', 
              'end_date', 'weekly_periods', 'is_active')
    readonly_fields = ('is_active',)
    fk_name = 'teacher'


class PerformanceIndicatorInline(admin.TabularInline):
    """Inline for performance indicators"""
    model = PerformanceIndicator
    extra = 0
    fields = ('academic_year', 'term', 'overall_score', 'student_performance_average', 
              'punctuality_score', 'evaluation_date')
    readonly_fields = ('overall_score', 'student_performance_average', 'punctuality_score')
    fk_name = 'teacher'


class TeacherAttendanceInline(admin.TabularInline):
    """Inline for attendance records"""
    model = TeacherAttendance
    extra = 0
    fields = ('date', 'check_in_time', 'check_out_time', 'status', 
              'working_hours', 'is_late')
    readonly_fields = ('working_hours', 'is_late')
    fk_name = 'teacher'


class TeacherLeaveInline(admin.TabularInline):
    """Inline for leave applications - TEACHER TAKING LEAVE"""
    model = TeacherLeave
    fk_name = 'teacher'  # CRITICAL: Uses the 'teacher' ForeignKey
    extra = 0
    fields = ('leave_type', 'start_date', 'end_date', 'days_requested', 
              'status', 'approved_by', 'approval_date')
    readonly_fields = ('status', 'approved_by', 'approval_date')
    verbose_name = "Leaves Taken"
    verbose_name_plural = "Leaves Taken"


class TeacherLeaveCoveringInline(admin.TabularInline):
    """Inline for leaves being covered by teacher"""
    model = TeacherLeave
    fk_name = 'cover_teacher'  # CRITICAL: Uses the 'cover_teacher' ForeignKey
    extra = 0
    fields = ('teacher_link', 'leave_type', 'start_date', 'end_date', 
              'days_requested', 'status')
    readonly_fields = ('status',)
    verbose_name = "Leaves Covering"
    verbose_name_plural = "Leaves Covering"
    
    def teacher_link(self, obj):
        if obj.teacher:
            url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
            return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
        return "-"
    teacher_link.short_description = "Teacher on Leave"


# ============================================================================
# IMPORT-EXPORT RESOURCES
# ============================================================================

class TeacherProfileResource(resources.ModelResource):
    """Resource for importing/exporting TeacherProfile"""
    
    class Meta:
        model = TeacherProfile
        skip_unchanged = True
        report_skipped = True
        exclude = ('id', 'created_at', 'updated_at', 'is_active')
        import_id_fields = ['tsc_number']


# ============================================================================
# TEACHER PROFILE ADMIN - FIXED
# ============================================================================

@admin.register(TeacherProfile)
class TeacherProfileAdmin(ImportExportModelAdmin):
    """Admin for TeacherProfile model"""
    resource_class = TeacherProfileResource
    
    # List display
    list_display = (
        'full_name', 'tsc_number', 'department', 
        'teaching_level', 'employment_status', 'cbc_trained_badge',
        'tsc_compliant_badge', 'tpd_status', 'is_active'
    )
    
    # List filters
    list_filter = (
        TSCStatusFilter,
        TeachingLevelFilter,
        EmploymentStatusFilter,
        DepartmentFilter,
        CBCTrainedFilter,
        TPDStatusFilter,
        'employment_type',
        'designation',
        'is_active',
    )
    
    # Search
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__email',
        'tsc_number', 'tsc_payroll_number', 'teacher_registration_number'
    )
    
    # Pagination
    list_per_page = 25
    
    # Inlines - START WITH EMPTY, THEN ADD ONE BY ONE
    inlines = [
        # Start with just one inline to test
        TeacherQualificationInline,
        # Then add others after confirming it works
        # TeacherTrainingInline,
        # TeacherDocumentInline,
        # TeacherAssignmentInline,
        # TeacherLeaveInline,
        # TeacherLeaveCoveringInline,
        # PerformanceIndicatorInline,
        # TeacherAttendanceInline,
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        ('Personal Information', {
            'fields': ('teacher', 'full_name_display', 'age_display')
        }),
        ('TSC Registration (Mandatory)', {
            'fields': (
                'tsc_number', 'tsc_registration_date', 'tsc_status', 
                'tsc_category', 'tsc_payroll_number'
            )
        }),
        ('Academic Qualifications', {
            'fields': (
                'highest_qualification', 'qualification_institution', 
                'year_of_graduation', 'kcse_mean_grade', 'kcse_index_number', 
                'kcse_year', 'teaching_subjects'
            )
        }),
        ('Employment Information', {
            'fields': (
                'employment_type', 'employment_status', 'teaching_level',
                'department', 'designation', 'employment_date', 
                'confirmation_date', 'retirement_date', 'last_promotion_date'
            )
        }),
        ('Professional Development', {
            'fields': (
                'cbc_trained', 'cbc_training_date', 'cbc_training_level',
                'tpd_current_module', 'tpd_last_completed_date', 
                'tpd_next_renewal_date', 'tpd_license_number'
            )
        }),
        ('Teaching Load & Performance', {
            'fields': (
                'weekly_periods', 'teaching_load_hours', 'performance_rating',
                'last_appraisal_date', 'next_appraisal_date', 'appraisal_score'
            )
        }),
        ('Additional Information', {
            'fields': (
                'teacher_registration_number', 'knec_registration_number',
                'sacco_name', 'sacco_number', 'blood_group',
                'bank_name', 'bank_account_number', 'bank_branch'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Salary Information', {
            'fields': (
                'salary_scale', 'basic_salary', 'house_allowance',
                'commuter_allowance'
            )
        }),
        ('Administrative', {
            'fields': (
                'subjects', 'classes', 'notes', 'achievements', 'is_active'
            )
        }),
    )
    
    # Readonly fields
    readonly_fields = ('full_name_display', 'age_display', 'years_of_service_display')
    
    # Custom methods for display
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = "Full Name"
    
    def age_display(self, obj):
        return obj.age if obj.age else "N/A"
    age_display.short_description = "Age"
    
    def years_of_service_display(self, obj):
        return obj.years_of_service
    years_of_service_display.short_description = "Years of Service"
    
    def cbc_trained_badge(self, obj):
        if obj.cbc_trained:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px;">✓ CBC Trained</span>'
            )
        return format_html(
            '<span style="background-color: #f44336; color: white; padding: 3px 8px; border-radius: 3px;">✗ Not Trained</span>'
        )
    cbc_trained_badge.short_description = "CBC Training"
    
    def tsc_compliant_badge(self, obj):
        if obj.tsc_compliant:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px;">✓ TSC Compliant</span>'
            )
        return format_html(
            '<span style="background-color: #f44336; color: white; padding: 3px 8px; border-radius: 3px;">✗ Non-Compliant</span>'
        )
    tsc_compliant_badge.short_description = "TSC Compliance"
    
    def tpd_status(self, obj):
        if not obj.tpd_next_renewal_date:
            return "N/A"
        
        today = timezone.now().date()
        days_remaining = (obj.tpd_next_renewal_date - today).days
        
        if days_remaining > 90:
            color = "#4CAF50"
            status = "Valid"
        elif days_remaining > 0:
            color = "#FF9800"
            status = f"{days_remaining}d left"
        else:
            color = "#f44336"
            status = "Expired"
        
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 3px;">{status}</span>'
        )
    tpd_status.short_description = "TPD Status"
    
    # Custom actions
    actions = [
        'mark_as_tsc_compliant',
        'mark_as_cbc_trained',
        'generate_tsc_reports',
        'export_teacher_summary',
        'deactivate_teachers',
        'activate_teachers',
    ]
    
    def mark_as_tsc_compliant(self, request, queryset):
        """Mark selected teachers as TSC compliant"""
        updated = queryset.update(tsc_status='registered')
        self.message_user(
            request, 
            f"Successfully marked {updated} teachers as TSC compliant."
        )
    mark_as_tsc_compliant.short_description = "Mark as TSC compliant"
    
    def mark_as_cbc_trained(self, request, queryset):
        """Mark selected teachers as CBC trained"""
        updated = queryset.update(cbc_trained=True, cbc_training_date=timezone.now().date())
        self.message_user(
            request,
            f"Successfully marked {updated} teachers as CBC trained."
        )
    mark_as_cbc_trained.short_description = "Mark as CBC trained"
    
    def generate_tsc_reports(self, request, queryset):
        """Generate TSC reports for selected teachers"""
        self.message_user(
            request,
            f"TSC reports generation initiated for {queryset.count()} teachers."
        )
    generate_tsc_reports.short_description = "Generate TSC reports"
    
    def export_teacher_summary(self, request, queryset):
        """Export teacher summary as CSV"""
        meta = self.model._meta
        field_names = [
            'full_name', 'tsc_number', 'department', 'teaching_level',
            'employment_status', 'cbc_trained', 'tsc_status'
        ]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=teacher_summary.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([
                obj.full_name,
                obj.tsc_number,
                str(obj.department) if obj.department else '',
                obj.get_teaching_level_display(),
                obj.get_employment_status_display(),
                'Yes' if obj.cbc_trained else 'No',
                obj.get_tsc_status_display()
            ])
        
        return response
    export_teacher_summary.short_description = "Export summary as CSV"
    
    def deactivate_teachers(self, request, queryset):
        """Deactivate selected teachers"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} teachers."
        )
    deactivate_teachers.short_description = "Deactivate teachers"
    
    def activate_teachers(self, request, queryset):
        """Activate selected teachers"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} teachers."
        )
    activate_teachers.short_description = "Activate teachers"


# ============================================================================
# OTHER ADMIN CLASSES (WITHOUT INLINES INITIALLY)
# ============================================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin for Department model"""
    list_display = ('name', 'code', 'tsc_category', 'cbc_pathway', 
                   'hod_link', 'teacher_count', 'is_active')
    list_filter = ('tsc_category', 'cbc_pathway', 'is_active')
    search_fields = ('name', 'code', 'description')
    
    def hod_link(self, obj):
        if obj.hod:
            url = reverse('admin:teachers_teacherprofile_change', args=[obj.hod.id])
            return format_html('<a href="{}">{}</a>', url, obj.hod.full_name)
        return "-"
    hod_link.short_description = "Head of Department"
    
    def teacher_count(self, obj):
        return obj.teacher_count
    teacher_count.short_description = "Teachers"


# ============================================================================
# SIMPLE ADMIN CLASSES FOR OTHER MODELS
# ============================================================================

@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('teacher__teacher__first_name', 'teacher__teacher__last_name')

@admin.register(TeacherQualification)
class TeacherQualificationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'title', 'qualification_type', 'institution')
    list_filter = ('qualification_type', 'verification_status')

@admin.register(TeacherTraining)
class TeacherTrainingAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'title', 'training_type', 'organizer', 'status')
    list_filter = ('training_type', 'status')

@admin.register(TeacherDocument)
class TeacherDocumentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'document_type', 'title', 'status', 'upload_date')
    list_filter = ('document_type', 'status')

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_assigned', 'assignment_type', 'is_active')
    list_filter = ('assignment_type', 'is_active')

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date')

@admin.register(PerformanceIndicator)
class PerformanceIndicatorAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'academic_year', 'overall_score', 'evaluation_date')
    list_filter = ('academic_year',)

@admin.register(ProfessionalStanding)
class ProfessionalStandingAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'record_type', 'date', 'status')
    list_filter = ('record_type', 'status')

@admin.register(TeacherTransfer)
class TeacherTransferAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'transfer_type', 'status', 'effective_date')
    list_filter = ('transfer_type', 'status')