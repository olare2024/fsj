# teachers/admin.py - ADMIN CONFIGURATION FOR OPTIMIZED KENYAN TEACHER MODEL
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.db.models import Count, Avg, Q, Sum
from django.db import models
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
import csv
from decimal import Decimal

# Import models - BE CAREFUL WITH CIRCULAR IMPORTS
# Don't import from academics.models here
from .models import (
    Department, TeacherProfile, ProfessionalStanding, PerformanceIndicator,
    TeacherTransfer, TeacherDocument, TeacherQualification, TeacherTraining,
    TeacherAssignment, TeacherAttendance, TeacherLeave, teacher_document_storage,
    generate_tsc_number, calculate_teacher_workload, get_teacher_summary,
    generate_teacher_report_card
)


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class TeacherQualificationInline(admin.TabularInline):
    """Inline for teacher qualifications"""
    model = TeacherQualification
    extra = 0
    fields = ('title', 'qualification_type', 'institution', 'completion_date', 'verification_status')
    readonly_fields = ('verification_status',)
    classes = ('collapse',)


class TeacherTrainingInline(admin.TabularInline):
    """Inline for teacher trainings"""
    model = TeacherTraining
    extra = 0
    fields = ('title', 'training_type', 'organizer', 'start_date', 'status', 'assessment_score')
    readonly_fields = ('status', 'assessment_score')
    classes = ('collapse',)


class TeacherDocumentInline(admin.TabularInline):
    """Inline for teacher documents"""
    model = TeacherDocument
    extra = 0
    fields = ('document_type', 'title', 'status', 'expiry_date', 'is_required')
    readonly_fields = ('status', 'expiry_date')
    classes = ('collapse',)


class TeacherAssignmentInline(admin.TabularInline):
    """Inline for teacher assignments"""
    model = TeacherAssignment
    extra = 0
    fields = ('assignment_type', 'subject', 'class_assigned', 'weekly_periods', 'is_active')
    classes = ('collapse',)


class TeacherAttendanceInline(admin.TabularInline):
    """Inline for teacher attendance (last 7 days)"""
    model = TeacherAttendance
    extra = 0
    max_num = 7
    can_delete = False
    fields = ('date', 'check_in_time', 'check_out_time', 'status', 'working_hours')
    readonly_fields = ('date', 'check_in_time', 'check_out_time', 'status', 'working_hours')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(date__gte=timezone.now().date() - timedelta(days=7)).order_by('-date')


class ProfessionalStandingInline(admin.TabularInline):
    """Inline for professional standing records"""
    model = ProfessionalStanding
    extra = 0
    fields = ('record_type', 'date', 'description', 'status')
    classes = ('collapse',)


class PerformanceIndicatorInline(admin.TabularInline):
    """Inline for performance indicators"""
    model = PerformanceIndicator
    extra = 0
    fields = ('academic_year', 'term', 'overall_score', 'evaluation_date')
    readonly_fields = ('overall_score', 'evaluation_date')
    classes = ('collapse',)


# ============================================================================
# CUSTOM FILTERS
# ============================================================================

class TSCStatusFilter(SimpleListFilter):
    """Filter by TSC status"""
    title = _('TSC Status')
    parameter_name = 'tsc_status'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.TSCStatus.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tsc_status=self.value())
        return queryset


class EmploymentTypeFilter(SimpleListFilter):
    """Filter by employment type"""
    title = _('Employment Type')
    parameter_name = 'employment_type'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.EmploymentType.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(employment_type=self.value())
        return queryset


class TeachingLevelFilter(SimpleListFilter):
    """Filter by teaching level"""
    title = _('Teaching Level')
    parameter_name = 'teaching_level'
    
    def lookups(self, request, model_admin):
        return TeacherProfile.TeachingLevel.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(teaching_level=self.value())
        return queryset


class CBCTrainingFilter(SimpleListFilter):
    """Filter by CBC training status"""
    title = _('CBC Trained')
    parameter_name = 'cbc_trained'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', _('Trained')),
            ('no', _('Not Trained')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(cbc_trained=True)
        elif self.value() == 'no':
            return queryset.filter(cbc_trained=False)
        return queryset


class TPDExpiryFilter(SimpleListFilter):
    """Filter by TPD expiry status"""
    title = _('TPD Expiry Status')
    parameter_name = 'tpd_expiry'
    
    def lookups(self, request, model_admin):
        return (
            ('expired', _('Expired')),
            ('expiring_30', _('Expiring in 30 days')),
            ('expiring_60', _('Expiring in 60 days')),
            ('expiring_90', _('Expiring in 90 days')),
            ('valid', _('Valid')),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'expired':
            return queryset.filter(tpd_next_renewal_date__lt=today)
        elif self.value() == 'expiring_30':
            return queryset.filter(
                tpd_next_renewal_date__range=[today, today + timedelta(days=30)]
            )
        elif self.value() == 'expiring_60':
            return queryset.filter(
                tpd_next_renewal_date__range=[today, today + timedelta(days=60)]
            )
        elif self.value() == 'expiring_90':
            return queryset.filter(
                tpd_next_renewal_date__range=[today, today + timedelta(days=90)]
            )
        elif self.value() == 'valid':
            return queryset.filter(tpd_next_renewal_date__gte=today)
        return queryset


class WorkloadFilter(SimpleListFilter):
    """Filter by workload status"""
    title = _('Workload Status')
    parameter_name = 'workload'
    
    def lookups(self, request, model_admin):
        return (
            ('overloaded', _('Overloaded (>100%)')),
            ('optimal', _('Optimal (80-100%)')),
            ('underutilized', _('Underutilized (<80%)')),
        )
    
    def queryset(self, request, queryset):
        # Note: This is a simplified implementation
        # In production, you'd want to calculate workload properly
        if self.value() == 'overloaded':
            return queryset.filter(weekly_periods__gt=45)
        elif self.value() == 'optimal':
            return queryset.filter(weekly_periods__range=[36, 45])
        elif self.value() == 'underutilized':
            return queryset.filter(weekly_periods__lt=36)
        return queryset


# ============================================================================
# CUSTOM ACTIONS
# ============================================================================

def mark_cbc_trained(modeladmin, request, queryset):
    """Mark selected teachers as CBC trained"""
    updated = queryset.update(
        cbc_trained=True,
        cbc_training_date=timezone.now().date()
    )
    modeladmin.message_user(request, f'{updated} teachers marked as CBC trained.')
mark_cbc_trained.short_description = _("Mark as CBC trained")


def update_tpd_module(modeladmin, request, queryset):
    """Update TPD module for selected teachers"""
    module_number = request.POST.get('module_number', 1)
    try:
        module_number = int(module_number)
        if 1 <= module_number <= 6:
            updated = 0
            for teacher in queryset:
                if teacher.update_tpd_module(module_number):
                    updated += 1
            modeladmin.message_user(request, f'TPD module updated for {updated} teachers.')
        else:
            modeladmin.message_user(request, 'Module number must be between 1 and 6.', level='error')
    except ValueError:
        modeladmin.message_user(request, 'Invalid module number.', level='error')
update_tpd_module.short_description = _("Update TPD module")


def generate_tsc_report(modeladmin, request, queryset):
    """Generate TSC compliance report for selected teachers"""
    # Redirect to a custom view or generate report
    teacher_ids = ','.join(str(t.id) for t in queryset)
    url = reverse('admin:teachers_teacherprofile_report') + f'?ids={teacher_ids}'
    return HttpResponseRedirect(url)
generate_tsc_report.short_description = _("Generate TSC compliance report")


def export_teacher_data(modeladmin, request, queryset):
    """Export teacher data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teachers_export.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    headers = [
        'TSC Number', 'Full Name', 'ID Number', 'Date of Birth', 'Gender',
        'Employment Type', 'Teaching Level', 'Highest Qualification',
        'KCSE Mean Grade', 'Department', 'Designation', 'CBC Trained',
        'TPD Module', 'Employment Date', 'Years of Service'
    ]
    writer.writerow(headers)
    
    # Write data
    for teacher in queryset:
        writer.writerow([
            teacher.tsc_number,
            teacher.full_name,
            teacher.teacher.id_number,
            teacher.teacher.date_of_birth,
            teacher.teacher.get_gender_display(),
            teacher.get_employment_type_display(),
            teacher.get_teaching_level_display(),
            teacher.get_highest_qualification_display(),
            teacher.get_kcse_mean_grade_display(),
            str(teacher.department) if teacher.department else '',
            teacher.get_designation_display(),
            'Yes' if teacher.cbc_trained else 'No',
            teacher.tpd_current_module,
            teacher.employment_date,
            teacher.years_of_service
        ])
    
    return response
export_teacher_data.short_description = _("Export to CSV")


def calculate_workload_action(modeladmin, request, queryset):
    """Recalculate workload for selected teachers"""
    updated = 0
    for teacher in queryset:
        workload = calculate_teacher_workload(teacher.id)
        teacher.weekly_periods = workload['total_periods']
        teacher.teaching_load_hours = Decimal(workload['total_hours'])
        teacher.save()
        updated += 1
    
    modeladmin.message_user(request, f'Workload recalculated for {updated} teachers.')
calculate_workload_action.short_description = _("Recalculate workload")


# ============================================================================
# ADMIN CLASSES
# ============================================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model"""
    
    list_display = ('name', 'code', 'tsc_category', 'cbc_pathway', 'hod_link', 'teacher_count', 'is_active')
    list_filter = ('tsc_category', 'cbc_pathway', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_per_page = 25
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Classification', {
            'fields': ('tsc_category', 'cbc_pathway')
        }),
        ('Leadership', {
            'fields': ('hod',)
        }),
        ('Location', {
            'fields': ('location', 'building', 'room_number')
        }),
        ('Academic', {
            'fields': ('academic_year',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def hod_link(self, obj):
        """Display HOD as link"""
        if obj.hod:
            url = reverse('admin:teachers_teacherprofile_change', args=[obj.hod.id])
            return format_html('<a href="{}">{}</a>', url, obj.hod.full_name)
        return '-'
    hod_link.short_description = _('Head of Department')
    
    def teacher_count(self, obj):
        """Display count of active teachers"""
        return obj.teacher_count
    teacher_count.short_description = _('Active Teachers')
    
    actions = ['activate_departments', 'deactivate_departments']
    
    def activate_departments(self, request, queryset):
        """Activate selected departments"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} departments activated.')
    activate_departments.short_description = _("Activate selected departments")
    
    def deactivate_departments(self, request, queryset):
        """Deactivate selected departments"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} departments deactivated.')
    deactivate_departments.short_description = _("Deactivate selected departments")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherProfile model"""
    
    # Display configuration
    list_display = (
        'tsc_number', 'full_name_link', 'teaching_level', 'department',
        'designation', 'cbc_trained_badge', 'tpd_status_badge',
        'employment_status_badge', 'tsc_compliance_badge', 'is_active'
    )
    
    list_filter = (
        TSCStatusFilter,
        EmploymentTypeFilter,
        TeachingLevelFilter,
        'employment_status',
        'designation',
        CBCTrainingFilter,
        TPDExpiryFilter,
        WorkloadFilter,
        'department',
        'is_active',
    )
    
    search_fields = (
        'tsc_number', 'teacher__first_name', 'teacher__last_name',
        'teacher__id_number', 'teacher__email', 'teacher__phone_number'
    )
    
    list_per_page = 25
    ordering = ('teacher__last_name', 'teacher__first_name')
    
    # Fieldsets for detail view
    fieldsets = (
        ('Personal Information', {
            'fields': ('teacher', 'full_name_display', 'tsc_number')
        }),
        
        ('TSC Registration', {
            'fields': (
                'tsc_status', 'tsc_registration_date', 'tsc_category',
                'tsc_payroll_number', 'tsc_compliance'
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
                'employment_date', 'confirmation_date', 'retirement_date',
                'last_promotion_date', 'years_of_service_display'
            )
        }),
        
        ('Professional Information', {
            'fields': (
                'department', 'designation', 'cbc_trained',
                'cbc_training_date', 'cbc_training_level',
                'tpd_current_module', 'tpd_last_completed_date',
                'tpd_next_renewal_date', 'tpd_license_number'
            )
        }),
        
        ('Teaching Load', {
            'fields': (
                'weekly_periods', 'teaching_load_hours',
                'workload_percentage', 'subjects', 'classes'
            )
        }),
        
        ('Additional Information', {
            'fields': (
                'teacher_registration_number', 'knec_registration_number',
                'sacco_name', 'sacco_number', 'blood_group',
                'bank_name', 'bank_account_number', 'bank_branch',
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            ),
            'classes': ('collapse',)
        }),
        
        ('Performance & Salary', {
            'fields': (
                'performance_rating', 'last_appraisal_date',
                'next_appraisal_date', 'appraisal_score',
                'salary_scale', 'basic_salary', 'house_allowance',
                'commuter_allowance', 'total_salary_display'
            ),
            'classes': ('collapse',)
        }),
        
        ('Role Flags', {
            'fields': (
                'is_class_teacher', 'is_head_of_department',
                'is_deputy_principal', 'is_principal',
                'is_curriculum_coordinator', 'is_guidance_counselor',
                'is_games_master'
            ),
            'classes': ('collapse',)
        }),
        
        ('Administrative', {
            'fields': ('notes', 'achievements')
        }),
        
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    # Inlines
    inlines = [
        TeacherQualificationInline,
        TeacherTrainingInline,
        TeacherDocumentInline,
        TeacherAssignmentInline,
        TeacherAttendanceInline,
        ProfessionalStandingInline,
        PerformanceIndicatorInline,
    ]
    
    # Readonly fields
    readonly_fields = (
        'full_name_display', 'tsc_compliance', 'years_of_service_display',
        'workload_percentage', 'total_salary_display', 'created_at', 'updated_at'
    )
    
    # Custom actions
    actions = [
        mark_cbc_trained,
        update_tpd_module,
        generate_tsc_report,
        export_teacher_data,
        calculate_workload_action,
        'activate_teachers',
        'deactivate_teachers',
        'generate_performance_reports',
    ]
    
    # Custom form
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add custom CSS classes
        form.base_fields['tsc_number'].widget.attrs.update({'class': 'tsc-field'})
        form.base_fields['employment_date'].widget.attrs.update({'class': 'datepicker'})
        form.base_fields['cbc_trained'].widget.attrs.update({'class': 'boolean-field'})
        
        return form
    
    # Custom methods for display
    def full_name_link(self, obj):
        """Display teacher name as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.full_name)
    full_name_link.short_description = _('Name')
    full_name_link.admin_order_field = 'teacher__last_name'
    
    def full_name_display(self, obj):
        """Display full name in detail view"""
        return obj.full_name
    full_name_display.short_description = _('Full Name')
    
    def cbc_trained_badge(self, obj):
        """Display CBC trained status as badge"""
        if obj.cbc_trained:
            return format_html(
                '<span class="badge badge-success" style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 12px;">✓ CBC</span>'
            )
        return format_html(
            '<span class="badge badge-secondary" style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 12px;">✗ CBC</span>'
        )
    cbc_trained_badge.short_description = _('CBC')
    
    def tpd_status_badge(self, obj):
        """Display TPD status as badge"""
        if obj.tpd_next_renewal_date:
            today = timezone.now().date()
            days_remaining = (obj.tpd_next_renewal_date - today).days
            
            if days_remaining < 0:
                color = '#dc3545'  # Red for expired
                text = f'TPD Expired'
            elif days_remaining <= 30:
                color = '#ffc107'  # Yellow for expiring soon
                text = f'TPD {days_remaining}d'
            else:
                color = '#28a745'  # Green for valid
                text = f'TPD M{obj.tpd_current_module}'
            
            return format_html(
                f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">{text}</span>'
            )
        return format_html(
            '<span class="badge badge-secondary" style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 12px;">No TPD</span>'
        )
    tpd_status_badge.short_description = _('TPD')
    
    def employment_status_badge(self, obj):
        """Display employment status as badge"""
        colors = {
            'active': '#28a745',
            'on_leave': '#17a2b8',
            'study_leave': '#17a2b8',
            'maternity_leave': '#17a2b8',
            'paternity_leave': '#17a2b8',
            'sick_leave': '#17a2b8',
            'suspended': '#ffc107',
            'terminated': '#dc3545',
            'retired': '#6c757d',
            'resigned': '#dc3545',
            'transferred': '#007bff',
            'deceased': '#343a40',
        }
        
        color = colors.get(obj.employment_status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_employment_status_display()}</span>'
        )
    employment_status_badge.short_description = _('Status')
    
    def tsc_compliance_badge(self, obj):
        """Display TSC compliance as badge"""
        if obj.tsc_compliant:
            return format_html(
                '<span class="badge badge-success" style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 12px;">✓ TSC</span>'
            )
        return format_html(
            '<span class="badge badge-danger" style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 12px;">✗ TSC</span>'
        )
    tsc_compliance_badge.short_description = _('TSC Compliant')
    
    def tsc_compliance(self, obj):
        """Display TSC compliance details"""
        return format_html(
            '<strong>Compliant:</strong> {}<br>'
            '<strong>Requirements:</strong><br>'
            '• TSC Registered: {}<br>'
            '• Qualifications: {}<br>'
            '• KCSE: {}<br>'
            '• CBC Trained: {}<br>'
            '• TPD Valid: {}',
            'Yes' if obj.tsc_compliant else 'No',
            '✓' if obj.tsc_status in ['registered', 'provisional'] else '✗',
            '✓' if obj.highest_qualification else '✗',
            '✓' if obj._check_kcse_requirements() else '✗',
            '✓' if obj.cbc_trained or obj.teaching_level != TeacherProfile.TeachingLevel.JUNIOR_SECONDARY else '✗',
            '✓' if obj.tpd_next_renewal_date and obj.tpd_next_renewal_date >= timezone.now().date() else '✗'
        )
    tsc_compliance.short_description = _('TSC Compliance Details')
    
    def years_of_service_display(self, obj):
        """Display years of service"""
        years = obj.years_of_service
        return f'{years} year(s)' if years > 0 else 'Less than 1 year'
    years_of_service_display.short_description = _('Years of Service')
    
    def workload_percentage(self, obj):
        """Display workload percentage"""
        workload = obj.calculate_workload()
        percentage = workload.get('workload_percentage', 0)
        
        color = '#dc3545' if percentage > 100 else '#ffc107' if percentage > 80 else '#28a745'
        
        return format_html(
            f'<div style="display: flex; align-items: center;">'
            f'<div style="width: 100px; height: 20px; background-color: #e9ecef; border-radius: 10px; margin-right: 10px;">'
            f'<div style="width: {min(percentage, 100)}%; height: 100%; background-color: {color}; border-radius: 10px;"></div>'
            f'</div>'
            f'<span>{percentage:.1f}%</span>'
            f'</div>'
        )
    workload_percentage.short_description = _('Workload %')
    
    def total_salary_display(self, obj):
        """Display total salary"""
        total = obj.total_salary
        return f'KSh {total:,.2f}' if total else 'Not set'
    total_salary_display.short_description = _('Total Salary')
    
    # Custom actions
    def activate_teachers(self, request, queryset):
        """Activate selected teachers"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} teachers activated.')
    activate_teachers.short_description = _("Activate selected teachers")
    
    def deactivate_teachers(self, request, queryset):
        """Deactivate selected teachers"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} teachers deactivated.')
    deactivate_teachers.short_description = _("Deactivate selected teachers")
    
    def generate_performance_reports(self, request, queryset):
        """Generate performance reports for selected teachers"""
        # This would generate PDF reports
        # For now, just show a message
        self.message_user(
            request,
            f'Performance reports would be generated for {queryset.count()} teachers.',
            level='info'
        )
    generate_performance_reports.short_description = _("Generate performance reports")
    
    # Custom save logic
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        # Generate TSC number if not provided
        if not obj.tsc_number:
            obj.tsc_number = generate_tsc_number()
        
        # Update user role based on teacher designation
        if obj.is_principal:
            obj.teacher.role = 'head_teacher'
        elif obj.is_deputy_principal or obj.is_head_of_department:
            obj.teacher.role = 'curriculum_coordinator'
        else:
            obj.teacher.role = 'teacher'
        
        # Update staff_id from TSC number
        if not obj.teacher.staff_id and obj.tsc_number:
            obj.teacher.staff_id = obj.tsc_number
        
        obj.teacher.save()
        super().save_model(request, obj, form, change)
    
    # Custom change view
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        
        # Add summary data to context
        try:
            teacher = TeacherProfile.objects.get(id=object_id)
            extra_context['teacher_summary'] = get_teacher_summary(teacher.id)
        except TeacherProfile.DoesNotExist:
            pass
        
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )
    
    # Custom list view with totals
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Calculate totals
        total_teachers = TeacherProfile.objects.filter(is_active=True).count()
        active_teachers = TeacherProfile.objects.filter(
            is_active=True, employment_status='active'
        ).count()
        tsc_compliant = TeacherProfile.objects.filter(
            is_active=True
        ).filter(
            Q(tsc_status__in=['registered', 'provisional']) &
            Q(highest_qualification__isnull=False) &
            Q(cbc_trained=True)
        ).count()
        
        extra_context.update({
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'tsc_compliant': tsc_compliant,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # Add custom media (CSS/JS)
    class Media:
        css = {
            'all': ('admin/css/teacher_admin.css',)
        }
        js = ('admin/js/teacher_admin.js',)


@admin.register(TeacherDocument)
class TeacherDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherDocument model"""
    
    list_display = (
        'teacher_link', 'document_type', 'title', 'status_badge',
        'expiry_date_display', 'is_required', 'verified_by', 'is_active'
    )
    
    list_filter = ('document_type', 'status', 'is_required', 'is_active')
    search_fields = ('teacher__teacher__first_name', 'teacher__teacher__last_name', 'title')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'document_type', 'title', 'description')
        }),
        ('Document File', {
            'fields': ('document_file', 'file_size', 'upload_date')
        }),
        ('Status & Verification', {
            'fields': ('status', 'expiry_date', 'is_required', 'verified_by',
                      'verification_date', 'verification_notes')
        }),
        ('Administrative', {
            'fields': ('is_archived', 'is_active')
        }),
    )
    
    readonly_fields = ('file_size', 'upload_date')
    
    actions = ['verify_documents', 'mark_expired', 'export_document_list']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'pending': '#ffc107',
            'verified': '#28a745',
            'rejected': '#dc3545',
            'expired': '#6c757d',
            'missing': '#dc3545',
            'under_review': '#17a2b8',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = _('Status')
    
    def expiry_date_display(self, obj):
        """Display expiry date with color coding"""
        if obj.expiry_date:
            today = timezone.now().date()
            days_to_expiry = (obj.expiry_date - today).days
            
            if days_to_expiry < 0:
                color = '#dc3545'
                text = f'Expired {abs(days_to_expiry)}d ago'
            elif days_to_expiry <= 30:
                color = '#ffc107'
                text = f'{days_to_expiry}d to expiry'
            else:
                color = '#28a745'
                text = obj.expiry_date.strftime('%Y-%m-%d')
            
            return format_html(
                f'<span style="color: {color};">{text}</span>'
            )
        return '-'
    expiry_date_display.short_description = _('Expiry Date')
    
    def verify_documents(self, request, queryset):
        """Verify selected documents"""
        updated = queryset.update(
            status='verified',
            verified_by=request.user,
            verification_date=timezone.now()
        )
        self.message_user(request, f'{updated} documents verified.')
    verify_documents.short_description = _("Verify selected documents")
    
    def mark_expired(self, request, queryset):
        """Mark selected documents as expired"""
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} documents marked as expired.')
    mark_expired.short_description = _("Mark as expired")
    
    def export_document_list(self, request, queryset):
        """Export document list to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teacher_documents.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        headers = [
            'Teacher', 'Document Type', 'Title', 'Status',
            'Upload Date', 'Expiry Date', 'Verified By', 'Verification Date'
        ]
        writer.writerow(headers)
        
        # Write data
        for doc in queryset:
            writer.writerow([
                doc.teacher.full_name,
                doc.get_document_type_display(),
                doc.title,
                doc.get_status_display(),
                doc.upload_date.strftime('%Y-%m-%d'),
                doc.expiry_date.strftime('%Y-%m-%d') if doc.expiry_date else '',
                doc.verified_by.get_full_name() if doc.verified_by else '',
                doc.verification_date.strftime('%Y-%m-%d') if doc.verification_date else ''
            ])
        
        return response
    export_document_list.short_description = _("Export to CSV")


@admin.register(TeacherQualification)
class TeacherQualificationAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherQualification model"""
    
    list_display = (
        'teacher_link', 'title', 'qualification_type',
        'institution', 'completion_date', 'verification_status_badge',
        'is_active'
    )
    
    list_filter = ('qualification_type', 'verification_status', 'is_active')
    search_fields = ('teacher__teacher__first_name', 'title', 'institution')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'qualification_type', 'title')
        }),
        ('Institution Details', {
            'fields': ('institution', 'institution_location', 'field_of_study')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'completion_date', 'is_completed')
        }),
        ('Certificate Details', {
            'fields': ('certificate_number', 'grade_classification')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verified_by',
                      'verification_date', 'verification_notes', 'document')
        }),
    )
    
    actions = ['verify_qualifications', 'mark_completed']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def verification_status_badge(self, obj):
        """Display verification status as badge"""
        colors = {
            'not_verified': '#6c757d',
            'pending': '#ffc107',
            'verified': '#28a745',
            'rejected': '#dc3545',
        }
        
        color = colors.get(obj.verification_status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_verification_status_display()}</span>'
        )
    verification_status_badge.short_description = _('Verification')
    
    def verify_qualifications(self, request, queryset):
        """Verify selected qualifications"""
        updated = queryset.update(
            verification_status='verified',
            verified_by=request.user,
            verification_date=timezone.now().date()
        )
        self.message_user(request, f'{updated} qualifications verified.')
    verify_qualifications.short_description = _("Verify selected qualifications")
    
    def mark_completed(self, request, queryset):
        """Mark selected qualifications as completed"""
        updated = queryset.update(is_completed=True)
        self.message_user(request, f'{updated} qualifications marked as completed.')
    mark_completed.short_description = _("Mark as completed")


@admin.register(TeacherTraining)
class TeacherTrainingAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherTraining model"""
    
    list_display = (
        'teacher_link', 'title', 'training_type', 'organizer',
        'start_date', 'status_badge', 'assessment_score', 'is_certified'
    )
    
    list_filter = ('training_type', 'training_mode', 'status', 'is_certified', 'is_active')
    search_fields = ('teacher__teacher__first_name', 'title', 'organizer')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'training_type', 'title', 'description')
        }),
        ('Organization', {
            'fields': ('organizer', 'training_mode')
        }),
        ('Dates & Duration', {
            'fields': ('start_date', 'end_date', 'duration_hours')
        }),
        ('Certification', {
            'fields': ('is_certified', 'certificate_number',
                      'certificate_issued_date', 'certificate_validity_years')
        }),
        ('Assessment', {
            'fields': ('assessment_score', 'feedback', 'status', 'document')
        }),
    )
    
    actions = ['mark_completed', 'generate_certificates']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'registered': '#17a2b8',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#6c757d',
            'failed': '#dc3545',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = _('Status')
    
    def mark_completed(self, request, queryset):
        """Mark selected trainings as completed"""
        for training in queryset:
            training.complete_training()
        self.message_user(request, f'{queryset.count()} trainings marked as completed.')
    mark_completed.short_description = _("Mark as completed")
    
    def generate_certificates(self, request, queryset):
        """Generate certificates for completed trainings"""
        # This would generate PDF certificates
        # For now, just show a message
        self.message_user(
            request,
            f'Certificates would be generated for {queryset.count()} trainings.',
            level='info'
        )
    generate_certificates.short_description = _("Generate certificates")


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherAssignment model"""
    
    list_display = (
        'teacher_link', 'assignment_type', 'subject_link', 'class_link',
        'weekly_periods', 'workload_hours_display', 'is_active', 'start_date'
    )
    
    list_filter = ('assignment_type', 'academic_year', 'is_active')
    search_fields = ('teacher__teacher__first_name', 'subject__name', 'class_assigned__name')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'assignment_type', 'title', 'description')
        }),
        ('Academic Details', {
            'fields': ('academic_year', 'term', 'subject', 'class_assigned', 'stream')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'weekly_periods')
        }),
        ('Workload', {
            'fields': ('workload_factor', 'workload_hours', 'adjusted_workload_hours')
        }),
        ('Status', {
            'fields': ('is_active', 'is_primary_assignment', 'notes')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date')
        }),
    )
    
    readonly_fields = ('workload_hours', 'adjusted_workload_hours')
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def subject_link(self, obj):
        """Display subject as link if exists"""
        if obj.subject:
            # Use the correct app label for subject
            try:
                url = reverse('admin:academics_subject_change', args=[obj.subject.id])
                return format_html('<a href="{}">{}</a>', url, obj.subject.name)
            except:
                return obj.subject.name
        return '-'
    subject_link.short_description = _('Subject')
    
    def class_link(self, obj):
        """Display class as link if exists"""
        if obj.class_assigned:
            # Use the correct app label for class
            try:
                url = reverse('admin:academics_class_change', args=[obj.class_assigned.id])
                return format_html('<a href="{}">{}</a>', url, obj.class_assigned.name)
            except:
                return obj.class_assigned.name
        return '-'
    class_link.short_description = _('Class')
    
    def workload_hours_display(self, obj):
        """Display workload hours"""
        return f'{obj.workload_hours:.1f} hrs'
    workload_hours_display.short_description = _('Workload Hours')
    
    def workload_hours(self, obj):
        """Calculate workload hours"""
        return obj.workload_hours
    workload_hours.short_description = _('Workload Hours')
    
    def adjusted_workload_hours(self, obj):
        """Calculate adjusted workload hours"""
        return obj.adjusted_workload_hours
    adjusted_workload_hours.short_description = _('Adjusted Workload Hours')


@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherAttendance model"""
    
    list_display = (
        'teacher_link', 'date', 'check_in_time', 'check_out_time',
        'status_badge', 'working_hours', 'is_late_badge', 'is_early_departure_badge'
    )
    
    list_filter = ('status', 'date', 'is_late', 'is_early_departure')
    search_fields = ('teacher__teacher__first_name',)
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'date')
        }),
        ('Attendance Details', {
            'fields': ('check_in_time', 'check_out_time', 'status')
        }),
        ('Late/Early Details', {
            'fields': ('is_late', 'late_minutes', 'is_early_departure', 'early_departure_minutes')
        }),
        ('Working Hours', {
            'fields': ('working_hours', 'notes')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verification_time')
        }),
    )
    
    actions = ['mark_present', 'mark_absent', 'generate_attendance_report']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'present': '#28a745',
            'absent': '#dc3545',
            'late': '#ffc107',
            'half_day': '#17a2b8',
            'leave': '#007bff',
            'off_duty': '#6c757d',
            'training': '#6f42c1',
            'sick': '#e83e8c',
            'emergency': '#fd7e14',
            'other': '#6c757d',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = _('Status')
    
    def is_late_badge(self, obj):
        """Display late status as badge"""
        if obj.is_late:
            return format_html(
                '<span class="badge badge-warning" style="background-color: #ffc107; color: white; padding: 3px 8px; border-radius: 12px;">'
                f'Late {obj.late_minutes}m</span>'
            )
        return '-'
    is_late_badge.short_description = _('Late')
    
    def is_early_departure_badge(self, obj):
        """Display early departure status as badge"""
        if obj.is_early_departure:
            return format_html(
                '<span class="badge badge-warning" style="background-color: #ffc107; color: white; padding: 3px 8px; border-radius: 12px;">'
                f'Early {obj.early_departure_minutes}m</span>'
            )
        return '-'
    is_early_departure_badge.short_description = _('Early Departure')
    
    def mark_present(self, request, queryset):
        """Mark selected attendance records as present"""
        updated = queryset.update(status='present')
        self.message_user(request, f'{updated} records marked as present.')
    mark_present.short_description = _("Mark as present")
    
    def mark_absent(self, request, queryset):
        """Mark selected attendance records as absent"""
        updated = queryset.update(status='absent')
        self.message_user(request, f'{updated} records marked as absent.')
    mark_absent.short_description = _("Mark as absent")
    
    def generate_attendance_report(self, request, queryset):
        """Generate attendance report"""
        # This would generate a report
        # For now, just show a message
        self.message_user(
            request,
            f'Attendance report would be generated for {queryset.count()} records.',
            level='info'
        )
    generate_attendance_report.short_description = _("Generate attendance report")


@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherLeave model"""
    
    list_display = (
        'teacher_link', 'leave_type_badge', 'start_date', 'end_date',
        'days_requested', 'status_badge', 'applied_date', 'approved_by_link'
    )
    
    list_filter = ('leave_type', 'status', 'applied_date')
    search_fields = ('teacher__teacher__first_name', 'reason')
    list_per_page = 25
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'leave_type')
        }),
        ('Leave Period', {
            'fields': ('start_date', 'end_date', 'days_requested')
        }),
        ('Details', {
            'fields': ('reason', 'contact_address', 'contact_phone', 'emergency_contact')
        }),
        ('Status & Approval', {
            'fields': ('status', 'applied_date', 'approved_by', 'approval_date',
                      'approval_notes', 'rejected_by', 'rejection_date',
                      'rejection_reason')
        }),
        ('Cover & Handover', {
            'fields': ('cover_teacher', 'handover_notes', 'documents')
        }),
    )
    
    actions = ['approve_leave', 'reject_leave', 'generate_leave_report']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def leave_type_badge(self, obj):
        """Display leave type as badge"""
        colors = {
            'annual': '#28a745',
            'sick': '#e83e8c',
            'maternity': '#6f42c1',
            'paternity': '#007bff',
            'study': '#17a2b8',
            'compassionate': '#fd7e14',
            'emergency': '#dc3545',
            'unpaid': '#6c757d',
            'other': '#6c757d',
        }
        
        color = colors.get(obj.leave_type, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_leave_type_display()}</span>'
        )
    leave_type_badge.short_description = _('Leave Type')
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d',
            'in_progress': '#007bff',
            'completed': '#17a2b8',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = _('Status')
    
    def approved_by_link(self, obj):
        """Display approver as link"""
        if obj.approved_by:
            url = reverse('admin:accounts_user_change', args=[obj.approved_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.approved_by.get_full_name())
        return '-'
    approved_by_link.short_description = _('Approved By')
    
    def approve_leave(self, request, queryset):
        """Approve selected leave applications"""
        for leave in queryset:
            leave.approve_leave(request.user)
        self.message_user(request, f'{queryset.count()} leave applications approved.')
    approve_leave.short_description = _("Approve selected leaves")
    
    def reject_leave(self, request, queryset):
        """Reject selected leave applications"""
        for leave in queryset:
            leave.reject_leave(request.user, 'Rejected via admin action')
        self.message_user(request, f'{queryset.count()} leave applications rejected.')
    reject_leave.short_description = _("Reject selected leaves")
    
    def generate_leave_report(self, request, queryset):
        """Generate leave report"""
        # This would generate a report
        # For now, just show a message
        self.message_user(
            request,
            f'Leave report would be generated for {queryset.count()} applications.',
            level='info'
        )
    generate_leave_report.short_description = _("Generate leave report")


@admin.register(PerformanceIndicator)
class PerformanceIndicatorAdmin(admin.ModelAdmin):
    """Admin configuration for PerformanceIndicator model"""
    
    list_display = (
        'teacher_link', 'academic_year', 'term', 'overall_score_badge',
        'evaluation_date', 'evaluator_link'
    )
    
    list_filter = ('academic_year', 'term')
    search_fields = ('teacher__teacher__first_name',)
    list_per_page = 25
    date_hierarchy = 'evaluation_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'academic_year', 'term')
        }),
        ('Academic Performance', {
            'fields': ('student_performance_average', 'completion_rate', 'improvement_rate')
        }),
        ('Professional Conduct', {
            'fields': ('punctuality_score', 'lesson_preparation_score', 'record_keeping_score')
        }),
        ('Student Engagement', {
            'fields': ('student_engagement_score', 'parent_satisfaction_score')
        }),
        ('Professional Development', {
            'fields': ('pd_completion_score', 'innovation_score')
        }),
        ('Overall', {
            'fields': ('overall_score', 'evaluator', 'evaluation_date', 'notes')
        }),
    )
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def overall_score_badge(self, obj):
        """Display overall score with color coding"""
        score = obj.overall_score or 0
        
        if score >= 4.0:
            color = '#28a745'
            label = 'Excellent'
        elif score >= 3.0:
            color = '#17a2b8'
            label = 'Good'
        elif score >= 2.0:
            color = '#ffc107'
            label = 'Average'
        elif score >= 1.0:
            color = '#fd7e14'
            label = 'Needs Improvement'
        else:
            color = '#dc3545'
            label = 'Poor'
        
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{label} ({score:.2f}/5.00)</span>'
        )
    overall_score_badge.short_description = _('Overall Score')
    
    def evaluator_link(self, obj):
        """Display evaluator as link"""
        if obj.evaluator:
            url = reverse('admin:accounts_user_change', args=[obj.evaluator.id])
            return format_html('<a href="{}">{}</a>', url, obj.evaluator.get_full_name())
        return '-'
    evaluator_link.short_description = _('Evaluator')


@admin.register(ProfessionalStanding)
class ProfessionalStandingAdmin(admin.ModelAdmin):
    """Admin configuration for ProfessionalStanding model"""
    
    list_display = (
        'teacher_link', 'record_type_badge', 'date', 'description_preview',
        'status', 'issued_by_link'
    )
    
    list_filter = ('record_type', 'status', 'date')
    search_fields = ('teacher__teacher__first_name', 'description', 'reference_number')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'record_type', 'date', 'description', 'reference_number')
        }),
        ('Issuance', {
            'fields': ('issued_by', 'status')
        }),
        ('Resolution', {
            'fields': ('resolution_date', 'resolution_notes')
        }),
        ('Document', {
            'fields': ('document',)
        }),
    )
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def record_type_badge(self, obj):
        """Display record type as badge"""
        colors = {
            'disciplinary': '#dc3545',
            'warning': '#ffc107',
            'commendation': '#28a745',
            'promotion': '#007bff',
            'transfer': '#17a2b8',
            'other': '#6c757d',
        }
        
        color = colors.get(obj.record_type, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_record_type_display()}</span>'
        )
    record_type_badge.short_description = _('Record Type')
    
    def description_preview(self, obj):
        """Display description preview"""
        if obj.description:
            preview = obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
            return preview
        return '-'
    description_preview.short_description = _('Description')
    
    def issued_by_link(self, obj):
        """Display issued by as link"""
        if obj.issued_by:
            url = reverse('admin:accounts_user_change', args=[obj.issued_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.issued_by.get_full_name())
        return '-'
    issued_by_link.short_description = _('Issued By')


@admin.register(TeacherTransfer)
class TeacherTransferAdmin(admin.ModelAdmin):
    """Admin configuration for TeacherTransfer model"""
    
    list_display = (
        'teacher_link', 'transfer_type_badge', 'from_school', 'to_school',
        'effective_date', 'status_badge', 'applied_date'
    )
    
    list_filter = ('transfer_type', 'status', 'applied_date')
    search_fields = ('teacher__teacher__first_name', 'reason')
    list_per_page = 25
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('teacher', 'transfer_type')
        }),
        ('Schools', {
            'fields': ('from_school', 'to_school')
        }),
        ('Transfer Details', {
            'fields': ('effective_date', 'reason')
        }),
        ('Approval Workflow', {
            'fields': ('applied_date', 'approved_by_sending', 'approved_by_receiving', 'approved_by_tsc')
        }),
        ('Handover', {
            'fields': ('handover_completed', 'handover_date', 'handover_notes')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    
    actions = ['approve_transfer', 'reject_transfer', 'complete_handover']
    
    def teacher_link(self, obj):
        """Display teacher as link"""
        url = reverse('admin:teachers_teacherprofile_change', args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', url, obj.teacher.full_name)
    teacher_link.short_description = _('Teacher')
    
    def transfer_type_badge(self, obj):
        """Display transfer type as badge"""
        colors = {
            'inter_school': '#007bff',
            'intra_school': '#17a2b8',
            'promotional': '#28a745',
            'requested': '#6f42c1',
            'disciplinary': '#dc3545',
        }
        
        color = colors.get(obj.transfer_type, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_transfer_type_display()}</span>'
        )
    transfer_type_badge.short_description = _('Transfer Type')
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'completed': '#17a2b8',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span class="badge" style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = _('Status')
    
    def approve_transfer(self, request, queryset):
        """Approve selected transfers"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} transfers approved.')
    approve_transfer.short_description = _("Approve selected transfers")
    
    def reject_transfer(self, request, queryset):
        """Reject selected transfers"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} transfers rejected.')
    reject_transfer.short_description = _("Reject selected transfers")
    
    def complete_handover(self, request, queryset):
        """Complete handover for selected transfers"""
        updated = queryset.update(
            handover_completed=True,
            handover_date=timezone.now().date(),
            status='completed'
        )
        self.message_user(request, f'{updated} transfers marked as completed with handover.')
    complete_handover.short_description = _("Complete handover")


# ============================================================================
# DASHBOARD CUSTOMIZATION
# ============================================================================

# Custom admin index to show teacher statistics
def teacher_statistics(request):
    """Display teacher statistics on admin index"""
    from django.db.models import Count, Q
    
    total_teachers = TeacherProfile.objects.filter(is_active=True).count()
    active_teachers = TeacherProfile.objects.filter(
        is_active=True, employment_status='active'
    ).count()
    
    tsc_registered = TeacherProfile.objects.filter(
        is_active=True,
        tsc_status__in=['registered', 'provisional', 'intern']
    ).count()
    
    cbc_trained = TeacherProfile.objects.filter(
        is_active=True, cbc_trained=True
    ).count()
    
    on_leave = TeacherProfile.objects.filter(
        is_active=True,
        employment_status__in=['on_leave', 'study_leave', 'maternity_leave',
                             'paternity_leave', 'sick_leave']
    ).count()
    
    # Teachers with expiring TPD (within 30 days)
    today = timezone.now().date()
    expiring_tpd = TeacherProfile.objects.filter(
        is_active=True,
        tpd_next_renewal_date__range=[today, today + timedelta(days=30)]
    ).count()
    
    return {
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'tsc_registered': tsc_registered,
        'cbc_trained': cbc_trained,
        'on_leave': on_leave,
        'expiring_tpd': expiring_tpd,
    }


# Add custom admin site
class TeacherAdminSite(admin.AdminSite):
    """Custom admin site for teacher management"""
    
    site_header = "Kenyan Teacher Management System"
    site_title = "Teacher Admin"
    index_title = "Teacher Administration Dashboard"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(teacher_statistics(request))
        return super().index(request, extra_context)


# ============================================================================
# ADMIN REGISTRATION SUMMARY
# ============================================================================
"""
This admin.py file provides comprehensive administration for the Kenyan Teacher Management System.

Registered Models:
1. Department - School departments with TSC classification
2. TeacherProfile - Main teacher profile with TSC integration
3. TeacherDocument - Teacher documents (certificates, IDs, etc.)
4. TeacherQualification - Academic and professional qualifications
5. TeacherTraining - Professional development and trainings
6. TeacherAssignment - Teaching and administrative assignments
7. TeacherAttendance - Daily attendance records
8. TeacherLeave - Leave applications and approvals
9. PerformanceIndicator - Teacher performance evaluations
10. ProfessionalStanding - Disciplinary and commendation records
11. TeacherTransfer - Inter/intra school transfers

Key Features:
- Custom filters for TSC status, employment type, teaching level, etc.
- Color-coded badges for quick status identification
- Inline editing for related models
- Bulk actions for common operations
- Export functionality (CSV)
- Comprehensive search and filtering
- Custom admin dashboard with statistics
- Responsive design with custom CSS/JS
- Integration with user accounts
- TSC compliance checking
- CBC training tracking
- TPD module management
- Workload calculation
- Performance monitoring

The admin interface is optimized for:
- School administrators
- TSC compliance officers
- Human resource managers
- Curriculum coordinators
- Head teachers/Principals
"""

# Note: To use the custom admin site, register it in urls.py:
# from teachers.admin import TeacherAdminSite
# teacher_admin_site = TeacherAdminSite(name='teacher_admin')
# Then register models with teacher_admin_site.register() instead of admin.site.register()