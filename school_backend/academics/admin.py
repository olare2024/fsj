"""
academics/admin.py
Admin configurations for academic models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg, Q

from .models import (
    # Core Models
    AcademicYear, AcademicTerm, Subject, Class, SubTopic,
    # Assignment Models
    SubjectAssignment, StudentEnrollment, StudentClassAssignment,
    # Planning Models
    LessonPlan, Syllabus, AcademicEvent, Stream,
    # CBC Models
    CBCAssessment, CBCPortfolio, PathwaySelection,
    CompetencyTracking, CurriculumMapping,
)


# ============================================================================
# ADMIN FILTERS
# ============================================================================

class AcademicYearFilter(admin.SimpleListFilter):
    """Filter by academic year."""
    title = _('Academic Year')
    parameter_name = 'academic_year'

    def lookups(self, request, model_admin):
        academic_years = AcademicYear.objects.filter(is_active=True).order_by('-start_date')
        return [(ay.id, ay.name) for ay in academic_years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(academic_year_id=self.value())
        return queryset


class IsActiveFilter(admin.SimpleListFilter):
    """Filter by active status."""
    title = _('Active Status')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Active')),
            ('no', _('Inactive')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_active=True)
        elif self.value() == 'no':
            return queryset.filter(is_active=False)
        return queryset


class CBCPathwayFilter(admin.SimpleListFilter):
    """Filter by CBC pathway."""
    title = _('CBC Pathway')
    parameter_name = 'cbc_pathway'

    def lookups(self, request, model_admin):
        return [
            ('stem', _('STEM')),
            ('social_sciences', _('Social Sciences')),
            ('arts_sports', _('Arts & Sports')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cbc_pathway=self.value())
        return queryset


class EducationLevelFilter(admin.SimpleListFilter):
    """Filter by education level."""
    title = _('Education Level')
    parameter_name = 'education_level'

    def lookups(self, request, model_admin):
        return [
            ('early_years', _('Early Years')),
            ('middle_school', _('Middle School')),
            ('senior_school', _('Senior School')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(education_level=self.value())
        return queryset


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class AcademicTermInline(admin.TabularInline):
    """Inline for academic terms."""
    model = AcademicTerm
    extra = 0
    fields = ('name', 'start_date', 'end_date', 'is_current', 'is_active')
    readonly_fields = ('is_current',)
    ordering = ('term_order',)


class SubjectAssignmentInline(admin.TabularInline):
    """Inline for subject assignments."""
    model = SubjectAssignment
    extra = 0
    fields = ('subject', 'teacher', 'periods_per_week', 'is_class_teacher', 'is_active')
    autocomplete_fields = ('subject', 'teacher')
    show_change_link = True


class StudentEnrollmentInline(admin.TabularInline):
    """Inline for student enrollments."""
    model = StudentEnrollment
    extra = 0
    fields = ('student', 'roll_number', 'status', 'enrollment_date')
    autocomplete_fields = ('student',)
    show_change_link = True
    readonly_fields = ('enrollment_date',)


class SubTopicInline(admin.TabularInline):
    """Inline for sub-topics."""
    model = SubTopic
    extra = 0
    fields = ('name', 'order', 'estimated_hours', 'priority', 'is_completed')
    ordering = ('order',)


class CBCAssessmentInline(admin.TabularInline):
    """Inline for CBC assessments."""
    model = CBCAssessment
    extra = 0
    fields = ('assessment_type', 'assessment_date', 'proficiency_level', 'total_score')
    readonly_fields = ('total_score',)
    ordering = ('-assessment_date',)


class LessonPlanInline(admin.TabularInline):
    """Inline for lesson plans."""
    model = LessonPlan
    extra = 0
    fields = ('title', 'date', 'duration_minutes', 'is_completed')
    readonly_fields = ('is_completed',)
    ordering = ('-date',)


# ============================================================================
# CORE MODEL ADMINS
# ============================================================================

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """Admin configuration for AcademicYear model."""
    
    list_display = (
        'name', 'code', 'curriculum_system', 'start_date', 'end_date',
        'is_current', 'is_configured', 'is_locked', 'is_active',
        'duration_days_display', 'progress_percentage_display'
    )
    
    list_filter = (
        'curriculum_system', 'is_current', 'is_configured', 'is_locked',
        'is_active', 'academic_structure', 'grading_system'
    )
    
    search_fields = ('name', 'code', 'description')
    
    readonly_fields = (
        'duration_days', 'progress_percentage', 'status',
        'curriculum_info_display', 'statistics_display'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name', 'code', 'start_date', 'end_date',
                'description', 'is_current', 'is_active'
            )
        }),
        (_('Curriculum Configuration'), {
            'fields': (
                'curriculum_system', 'academic_structure', 'grading_system',
                'term_structure', 'total_terms', 'language_mode',
                'additional_languages', 'assessment_model', 'external_exams'
            )
        }),
        (_('System Configuration'), {
            'fields': (
                'fee_structure', 'currency', 'important_dates',
                'holiday_calendar', 'cbc_configuration',
                'international_config', 'report_config', 'metadata'
            )
        }),
        (_('Status and Permissions'), {
            'fields': (
                'is_configured', 'is_locked', 'allow_admissions',
                'allow_assessments', 'allow_transcripts'
            )
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': (
                'duration_days', 'progress_percentage', 'status',
                'curriculum_info_display', 'statistics_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AcademicTermInline]
    
    actions = ['mark_as_current', 'lock_academic_year', 'unlock_academic_year']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            term_count=Count('terms'),
            class_count=Count('classes')
        )
    
    def duration_days_display(self, obj):
        """Display duration in days with formatting."""
        return f"{obj.duration_days} days"
    duration_days_display.short_description = _('Duration')
    duration_days_display.admin_order_field = 'duration_days'
    
    def progress_percentage_display(self, obj):
        """Display progress percentage with colored bar."""
        percentage = obj.progress_percentage
        color = 'green' if percentage > 75 else 'orange' if percentage > 50 else 'red'
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'border-radius: 3px; padding: 2px;">{}%</div></div>',
            percentage, color, int(percentage)
        )
    progress_percentage_display.short_description = _('Progress')
    progress_percentage_display.admin_order_field = 'progress_percentage'
    
    def curriculum_info_display(self, obj):
        """Display curriculum information."""
        info = obj.curriculum_info
        return format_html(
            '<strong>System:</strong> {}<br>'
            '<strong>Structure:</strong> {}<br>'
            '<strong>Grading:</strong> {}<br>'
            '<strong>Assessment:</strong> {}',
            info['system'], info['structure'], info['grading'], info['assessment']
        )
    curriculum_info_display.short_description = _('Curriculum Info')
    
    def statistics_display(self, obj):
        """Display academic year statistics."""
        stats = obj.get_statistics()
        return format_html(
            '<strong>Students:</strong> {}<br>'
            '<strong>Teachers:</strong> {}<br>'
            '<strong>Classes:</strong> {}<br>'
            '<strong>Subjects:</strong> {}',
            stats.get('total_students', 0),
            stats.get('total_teachers', 0),
            stats.get('total_classes', 0),
            stats.get('total_subjects', 0)
        )
    statistics_display.short_description = _('Statistics')
    
    def mark_as_current(self, request, queryset):
        """Mark selected academic years as current."""
        if queryset.count() > 1:
            self.message_user(
                request,
                _('Only one academic year can be current at a time.'),
                level='error'
            )
            return
        
        academic_year = queryset.first()
        academic_year.is_current = True
        academic_year.save()
        self.message_user(
            request,
            _('Successfully marked {} as current academic year.').format(academic_year.name)
        )
    mark_as_current.short_description = _('Mark as current academic year')
    
    def lock_academic_year(self, request, queryset):
        """Lock selected academic years."""
        updated = queryset.update(is_locked=True)
        self.message_user(
            request,
            _('Successfully locked {} academic years.').format(updated)
        )
    lock_academic_year.short_description = _('Lock academic years')
    
    def unlock_academic_year(self, request, queryset):
        """Unlock selected academic years."""
        updated = queryset.update(is_locked=False)
        self.message_user(
            request,
            _('Successfully unlocked {} academic years.').format(updated)
        )
    unlock_academic_year.short_description = _('Unlock academic years')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    """Admin configuration for AcademicTerm model."""
    
    list_display = (
        'name', 'academic_year', 'start_date', 'end_date', 'is_current',
        'duration_days_display', 'teaching_weeks', 'progress_percentage_display',
        'is_active'
    )
    
    list_filter = (
        'academic_year', 'name', 'is_current', IsActiveFilter,
        AcademicYearFilter
    )
    
    search_fields = (
        'academic_year__name', 'name', 'academic_year__code'
    )
    
    readonly_fields = (
        'duration_days', 'teaching_weeks', 'progress_percentage',
        'status', 'is_currently_active'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'academic_year', 'name', 'term_order',
                'start_date', 'end_date', 'is_current', 'is_active'
            )
        }),
        (_('Term Configuration'), {
            'fields': (
                'assessment_periods', 'holidays', 'important_dates',
                'term_fees'
            )
        }),
        (_('Computed Fields'), {
            'fields': (
                'duration_days', 'teaching_weeks', 'progress_percentage',
                'status', 'is_currently_active'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('academic_year')
    
    def duration_days_display(self, obj):
        """Display duration in days."""
        return f"{obj.duration_days} days"
    duration_days_display.short_description = _('Duration')
    duration_days_display.admin_order_field = 'duration_days'
    
    def progress_percentage_display(self, obj):
        """Display progress percentage with colored bar."""
        percentage = obj.progress_percentage
        color = 'green' if percentage > 75 else 'orange' if percentage > 50 else 'red'
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'border-radius: 3px; padding: 2px;">{}%</div></div>',
            percentage, color, int(percentage)
        )
    progress_percentage_display.short_description = _('Progress')
    progress_percentage_display.admin_order_field = 'progress_percentage'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin configuration for Subject model."""
    
    list_display = (
        'name', 'code', 'category', 'curriculum', 'is_cbc_core',
        'is_compulsory', 'credits', 'periods_per_week',
        'weekly_hours_display', 'is_active'
    )
    
    list_filter = (
        'category', 'curriculum', 'is_cbc_core', 'is_compulsory',
        'is_examined', 'is_elective', 'department', CBCPathwayFilter,
        IsActiveFilter
    )
    
    search_fields = ('name', 'code', 'description')
    
    readonly_fields = ('weekly_hours', 'is_cbc_subject', 'subject_info_display')
    
    filter_horizontal = ('prerequisites',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name', 'code', 'description', 'category', 'curriculum',
                'is_active'
            )
        }),
        (_('CBC Configuration'), {
            'fields': (
                'cbc_competency_area', 'cbc_pathway', 'is_cbc_core',
                'is_compulsory'
            ),
            'classes': ('collapse',)
        }),
        (_('Academic Requirements'), {
            'fields': (
                'grade_levels', 'credits', 'periods_per_week',
                'practical_weight', 'assessment_methods', 'project_based'
            )
        }),
        (_('Resources and Materials'), {
            'fields': (
                'resources_required', 'recommended_books',
                'syllabus_link', 'notes'
            ),
            'classes': ('collapse',)
        }),
        (_('Relationships'), {
            'fields': (
                'prerequisites', 'department', 'minimum_qualification'
            )
        }),
        (_('Status Flags'), {
            'fields': (
                'is_examined', 'is_elective'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': (
                'weekly_hours', 'is_cbc_subject', 'subject_info_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SubTopicInline]
    
    def weekly_hours_display(self, obj):
        """Display weekly hours."""
        return f"{obj.weekly_hours} hrs/week"
    weekly_hours_display.short_description = _('Weekly Hours')
    
    def subject_info_display(self, obj):
        """Display comprehensive subject information."""
        info = obj.subject_info
        return format_html(
            '<strong>Category:</strong> {}<br>'
            '<strong>Curriculum:</strong> {}<br>'
            '<strong>CBC:</strong> {}<br>'
            '<strong>Core:</strong> {}<br>'
            '<strong>Compulsory:</strong> {}<br>'
            '<strong>Weekly Hours:</strong> {}<br>'
            '<strong>Credits:</strong> {}<br>'
            '<strong>Practical Weight:</strong> {}%',
            info['category'], info['curriculum'], info['is_cbc'],
            info['is_core'], info['is_compulsory'], info['weekly_hours'],
            info['credits'], info['practical_weight']
        )
    subject_info_display.short_description = _('Subject Information')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin configuration for Class model."""
    
    list_display = (
        'display_name', 'academic_year', 'grade_level', 'education_level',
        'class_teacher_display', 'current_strength', 'capacity',
        'occupancy_rate_display', 'is_active'
    )
    
    list_filter = (
        AcademicYearFilter, 'grade_level', 'education_level', 'stream',
        'cbc_pathway', 'senior_track', 'primary_curriculum',
        EducationLevelFilter, IsActiveFilter
    )
    
    search_fields = (
        'name', 'section', 'room_number', 'class_teacher__user__first_name',
        'class_teacher__user__last_name', 'academic_year__name'
    )
    
    readonly_fields = (
        'display_name', 'available_seats', 'is_full', 'occupancy_rate',
        'is_cbc_class', 'cbc_info_display', 'academic_info_display',
        'class_statistics_display'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name', 'grade_level', 'section', 'stream', 'room_number',
                'academic_year', 'class_teacher', 'description', 'is_active'
            )
        }),
        (_('CBC Configuration'), {
            'fields': (
                'education_level', 'cbc_pathway', 'senior_track',
                'portfolio_required', 'project_work_required',
                'community_service_hours'
            )
        }),
        (_('Curriculum Information'), {
            'fields': (
                'primary_curriculum', 'additional_curriculums'
            )
        }),
        (_('Class Configuration'), {
            'fields': (
                'capacity', 'current_strength', 'schedule',
                'assessment_config', 'class_rules', 'class_color'
            )
        }),
        (_('Facilities and Technology'), {
            'fields': (
                'facilities', 'technology_level', 'special_programs'
            ),
            'classes': ('collapse',)
        }),
        (_('Performance Tracking'), {
            'fields': (
                'average_performance', 'attendance_rate',
                'parent_engagement_level'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': (
                'display_name', 'available_seats', 'is_full', 'occupancy_rate',
                'is_cbc_class', 'cbc_info_display', 'academic_info_display',
                'class_statistics_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SubjectAssignmentInline, StudentEnrollmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'academic_year', 'class_teacher__user'
        ).annotate(
            student_count=Count('enrollments', filter=Q(enrollments__status='active'))
        )
    
    def class_teacher_display(self, obj):
        """Display class teacher name."""
        if obj.class_teacher:
            return obj.class_teacher.full_name
        return '-'
    class_teacher_display.short_description = _('Class Teacher')
    class_teacher_display.admin_order_field = 'class_teacher__user__last_name'
    
    def occupancy_rate_display(self, obj):
        """Display occupancy rate with colored bar."""
        rate = obj.occupancy_rate
        color = 'green' if rate < 80 else 'orange' if rate < 95 else 'red'
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'border-radius: 3px; padding: 2px;">{}%</div></div>',
            rate, color, int(rate)
        )
    occupancy_rate_display.short_description = _('Occupancy')
    occupancy_rate_display.admin_order_field = 'occupancy_rate'
    
    def cbc_info_display(self, obj):
        """Display CBC information."""
        if not obj.is_cbc_class:
            return _('Not a CBC class')
        
        info = obj.cbc_info
        return format_html(
            '<strong>Education Level:</strong> {}<br>'
            '<strong>Senior School:</strong> {}<br>'
            '<strong>Portfolio Required:</strong> {}<br>'
            '<strong>Project Required:</strong> {}<br>'
            '<strong>Community Service:</strong> {} hours',
            info['education_level'], info['is_senior_school'],
            info['requires_portfolio'], info['requires_project'],
            info['community_service_hours']
        )
    cbc_info_display.short_description = _('CBC Information')
    
    def academic_info_display(self, obj):
        """Display academic information."""
        info = obj.academic_info
        return format_html(
            '<strong>Grade Level:</strong> {}<br>'
            '<strong>Education Level:</strong> {}<br>'
            '<strong>Curriculum:</strong> {}<br>'
            '<strong>CBC:</strong> {}<br>'
            '<strong>Academic Year:</strong> {}',
            info['grade_level'], info['education_level'],
            info['curriculum'], info['is_cbc'], info['academic_year']
        )
    academic_info_display.short_description = _('Academic Information')
    
    def class_statistics_display(self, obj):
        """Display class statistics."""
        stats = obj.get_class_statistics()
        return format_html(
            '<strong>Students:</strong> {}<br>'
            '<strong>Attendance Rate:</strong> {}%<br>'
            '<strong>Occupancy Rate:</strong> {}%<br>'
            '<strong>Available Seats:</strong> {}<br>'
            '<strong>Subjects:</strong> {}<br>'
            '<strong>Teachers:</strong> {}',
            stats.get('total_students', 0),
            stats.get('attendance_rate', 0),
            stats.get('occupancy_rate', 0),
            stats.get('available_seats', 0),
            stats.get('subjects_count', 0),
            stats.get('teachers_count', 0)
        )
    class_statistics_display.short_description = _('Class Statistics')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    """Admin configuration for SubTopic model."""
    
    list_display = (
        'full_name', 'subject', 'order', 'estimated_hours',
        'priority', 'is_completed', 'is_active'
    )
    
    list_filter = (
        'subject', 'priority', 'is_completed', IsActiveFilter,
        'subject__curriculum'
    )
    
    search_fields = (
        'topic', 'name', 'description', 'subject__name', 'subject__code'
    )
    
    readonly_fields = (
        'full_name', 'estimated_periods', 'is_cbc_aligned',
        'difficulty_assessment', 'resource_summary_display'
    )
    
    filter_horizontal = ('prerequisite_topics',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'subject', 'topic', 'name', 'code', 'description',
                'order', 'is_active'
            )
        }),
        (_('Academic Details'), {
            'fields': (
                'competency_alignment', 'learning_objectives',
                'key_concepts', 'skills_developed'
            )
        }),
        (_('Time and Priority'), {
            'fields': (
                'estimated_hours', 'priority'
            )
        }),
        (_('Teaching Resources'), {
            'fields': (
                'teaching_resources', 'assessment_methods',
                'differentiation_strategies', 'project_connections'
            ),
            'classes': ('collapse',)
        }),
        (_('Prerequisites'), {
            'fields': ('prerequisite_topics',),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': (
                'is_completed', 'completion_date'
            )
        }),
        (_('Computed Fields'), {
            'fields': (
                'full_name', 'estimated_periods', 'is_cbc_aligned',
                'difficulty_assessment', 'resource_summary_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject')
    
    def resource_summary_display(self, obj):
        """Display resource summary."""
        summary = obj.get_resource_summary()
        return format_html(
            '<strong>Total Resources:</strong> {}<br>'
            '<strong>Digital Resources:</strong> {}<br>'
            '<strong>Physical Resources:</strong> {}<br>'
            '<strong>Special Equipment:</strong> {}',
            summary['total_resources'], summary['digital_resources'],
            summary['physical_resources'], summary['special_equipment']
        )
    resource_summary_display.short_description = _('Resource Summary')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# ASSIGNMENT MODEL ADMINS
# ============================================================================

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for SubjectAssignment model."""
    
    list_display = (
        'teacher_display', 'subject', 'class_assigned', 'academic_year',
        'periods_per_week', 'teaching_load_hours_display', 'is_class_teacher',
        'assignment_status', 'is_active'
    )
    
    list_filter = (
        AcademicYearFilter, 'assignment_status', 'role_type',
        'is_class_teacher', 'subject__curriculum', IsActiveFilter
    )
    
    search_fields = (
        'teacher__user__first_name', 'teacher__user__last_name',
        'teacher__staff_id', 'subject__name', 'subject__code',
        'class_assigned__name', 'academic_year__name'
    )
    
    readonly_fields = (
        'teaching_load_hours', 'is_current', 'assignment_duration_days',
        'is_cbc_assignment', 'competency_info_display',
        'workload_score_display', 'assignment_summary_display'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'subject', 'teacher', 'class_assigned', 'academic_year',
                'periods_per_week', 'is_class_teacher', 'role_type',
                'assignment_status', 'is_active'
            )
        }),
        (_('CBC Requirements'), {
            'fields': (
                'cbc_competency_focus', 'project_supervision_required',
                'portfolio_assessment_duty'
            ),
            'classes': ('collapse',)
        }),
        (_('Schedule and Responsibilities'), {
            'fields': (
                'teaching_schedule', 'assessment_responsibilities',
                'additional_responsibilities', 'responsibility_allowance'
            ),
            'classes': ('collapse',)
        }),
        (_('Dates and Performance'), {
            'fields': (
                'assigned_date', 'effective_from', 'effective_until',
                'performance_rating', 'last_performance_review'
            )
        }),
        (_('Computed Fields'), {
            'fields': (
                'teaching_load_hours', 'is_current', 'assignment_duration_days',
                'is_cbc_assignment', 'competency_info_display',
                'workload_score_display', 'assignment_summary_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher__user', 'subject', 'class_assigned', 'academic_year'
        )
    
    def teacher_display(self, obj):
        """Display teacher name."""
        return obj.teacher.full_name
    teacher_display.short_description = _('Teacher')
    teacher_display.admin_order_field = 'teacher__user__last_name'
    
    def teaching_load_hours_display(self, obj):
        """Display teaching load hours."""
        return f"{obj.teaching_load_hours} hrs/week"
    teaching_load_hours_display.short_description = _('Teaching Load')
    
    def competency_info_display(self, obj):
        """Display competency information."""
        if not obj.is_cbc_assignment:
            return _('Not a CBC assignment')
        
        info = obj.competency_info
        return format_html(
            '<strong>Competency Focus:</strong> {}<br>'
            '<strong>Subject Competency:</strong> {}<br>'
            '<strong>Project Supervision:</strong> {}<br>'
            '<strong>Portfolio Assessment:</strong> {}',
            ', '.join(info['competency_focus']) if info['competency_focus'] else 'None',
            info['subject_competency'] or 'None',
            info['requires_project_supervision'],
            info['requires_portfolio_assessment']
        )
    competency_info_display.short_description = _('Competency Information')
    
    def workload_score_display(self, obj):
        """Display workload score with colored bar."""
        score = obj.workload_score
        color = 'green' if score < 70 else 'orange' if score < 90 else 'red'
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'border-radius: 3px; padding: 2px;">{}%</div></div>',
            score, color, int(score)
        )
    workload_score_display.short_description = _('Workload Score')
    
    def assignment_summary_display(self, obj):
        """Display assignment summary."""
        summary = obj.get_assignment_summary()
        return format_html(
            '<strong>Teacher:</strong> {}<br>'
            '<strong>Subject:</strong> {}<br>'
            '<strong>Class:</strong> {}<br>'
            '<strong>Periods/Week:</strong> {}<br>'
            '<strong>Teaching Hours:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Current:</strong> {}',
            summary['teacher'], summary['subject'], summary['class'],
            summary['periods_per_week'], summary['teaching_hours'],
            summary['assignment_status'], summary['is_current']
        )
    assignment_summary_display.short_description = _('Assignment Summary')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for StudentEnrollment model."""
    
    list_display = (
        'student_display', 'class_enrolled', 'academic_year',
        'roll_number', 'status', 'enrollment_date', 'is_current',
        'fee_status', 'is_active'
    )
    
    list_filter = (
        AcademicYearFilter, 'status', 'fee_status', 'house',
        'cbc_pathway_selection', 'portfolio_status', 'is_active'
    )
    
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'enrollment_number',
        'class_enrolled__name', 'academic_year__name'
    )
    
    readonly_fields = (
        'enrollment_number', 'is_current', 'enrollment_duration',
        'is_cbc_enrollment', 'cbc_info_display', 'academic_progress_display',
        'enrollment_summary_display'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'class_enrolled', 'academic_year',
                'enrollment_date', 'enrollment_number', 'roll_number',
                'status', 'status_changed_date', 'status_reason',
                'is_active'
            )
        }),
        (_('CBC Information'), {
            'fields': (
                'cbc_pathway_selection', 'senior_track_selection',
                'portfolio_status', 'community_service_hours_completed'
            ),
            'classes': ('collapse',)
        }),
        (_('House and Activities'), {
            'fields': (
                'house', 'extracurricular_activities'
            ),
            'classes': ('collapse',)
        }),
        (_('Previous School'), {
            'fields': (
                'previous_school', 'transfer_certificate',
                'previous_performance'
            ),
            'classes': ('collapse',)
        }),
        (_('Financial Information'), {
            'fields': (
                'fee_status', 'fee_arrears'
            )
        }),
        (_('Parent and Support'), {
            'fields': (
                'parent_engagement_level', 'special_needs',
                'support_services', 'academic_support_level'
            ),
            'classes': ('collapse',)
        }),
        (_('Performance Tracking'), {
            'fields': (
                'average_performance', 'attendance_percentage'
            )
        }),
        (_('Computed Fields'), {
            'fields': (
                'is_current', 'enrollment_duration', 'is_cbc_enrollment',
                'cbc_info_display', 'academic_progress_display',
                'enrollment_summary_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Remarks and Metadata'), {
            'fields': (
                'remarks', 'enrollment_metadata'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'class_enrolled', 'academic_year'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def cbc_info_display(self, obj):
        """Display CBC information."""
        if not obj.is_cbc_enrollment:
            return _('Not a CBC enrollment')
        
        info = obj.cbc_info
        return format_html(
            '<strong>Pathway:</strong> {}<br>'
            '<strong>Senior Track:</strong> {}<br>'
            '<strong>Portfolio Status:</strong> {}<br>'
            '<strong>Community Service:</strong> {} of {} hours<br>'
            '<strong>Portfolio Required:</strong> {}<br>'
            '<strong>Project Required:</strong> {}',
            info['pathway'], info['senior_track'], info['portfolio_status'],
            info['community_service_hours']['completed'],
            info['community_service_hours']['required'],
            info['requires_portfolio'], info['requires_project']
        )
    cbc_info_display.short_description = _('CBC Information')
    
    def academic_progress_display(self, obj):
        """Display academic progress."""
        progress = obj.academic_progress
        if not progress:
            return _('No academic data available')
        
        return format_html(
            '<strong>Average Score:</strong> {}<br>'
            '<strong>Total Grades:</strong> {}<br>'
            '<strong>Passing Grades:</strong> {}<br>'
            '<strong>Pass Rate:</strong> {}%',
            progress['average_score'], progress['total_grades'],
            progress['passing_grades'], progress['pass_rate']
        )
    academic_progress_display.short_description = _('Academic Progress')
    
    def enrollment_summary_display(self, obj):
        """Display enrollment summary."""
        summary = obj.enrollment_summary
        return format_html(
            '<strong>Student:</strong> {}<br>'
            '<strong>Class:</strong> {}<br>'
            '<strong>Academic Year:</strong> {}<br>'
            '<strong>Enrollment Date:</strong> {}<br>'
            '<strong>Enrollment Number:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Roll Number:</strong> {}<br>'
            '<strong>Duration:</strong> {} days<br>'
            '<strong>Current:</strong> {}',
            summary['student'], summary['class'], summary['academic_year'],
            summary['enrollment_date'], summary['enrollment_number'],
            summary['status'], summary['roll_number'],
            summary['enrollment_duration_days'], summary['is_current']
        )
    enrollment_summary_display.short_description = _('Enrollment Summary')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentClassAssignment)
class StudentClassAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for StudentClassAssignment model."""
    
    list_display = (
        'student_display', 'class_assigned', 'subject_display',
        'academic_year', 'status', 'is_current', 'performance_level',
        'is_active'
    )
    
    list_filter = (
        AcademicYearFilter, 'status', 'performance_level',
        'is_core_subject', 'is_elective_subject', 'learning_style',
        IsActiveFilter
    )
    
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'class_assigned__name',
        'subject__name', 'academic_year__name'
    )
    
    readonly_fields = (
        'is_current', 'assignment_duration', 'is_cbc_assignment',
        'subject_info_display', 'assignment_summary_display'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'class_assigned', 'subject', 'academic_year',
                'assignment_date', 'effective_from', 'effective_until',
                'status', 'status_changed_date', 'is_active'
            )
        }),
        (_('Academic Details'), {
            'fields': (
                'seating_position', 'locker_number', 'desk_number',
                'assigned_teacher', 'learning_style'
            ),
            'classes': ('collapse',)
        }),
        (_('CBC Configuration'), {
            'fields': (
                'is_core_subject', 'is_elective_subject',
                'competency_tracking_enabled', 'project_work_assigned'
            ),
            'classes': ('collapse',)
        }),
        (_('Performance and Support'), {
            'fields': (
                'performance_level', 'last_assessment_date',
                'special_accommodations'
            )
        }),
        (_('Computed Fields'), {
            'fields': (
                'is_current', 'assignment_duration', 'is_cbc_assignment',
                'subject_info_display', 'assignment_summary_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Remarks and Metadata'), {
            'fields': (
                'remarks', 'assignment_metadata'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'class_assigned', 'subject', 'academic_year',
            'assigned_teacher__user'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def subject_display(self, obj):
        """Display subject name."""
        return obj.subject.name if obj.subject else _('General Assignment')
    subject_display.short_description = _('Subject')
    subject_display.admin_order_field = 'subject__name'
    
    def subject_info_display(self, obj):
        """Display subject information."""
        info = obj.subject_info
        if not info:
            return _('No subject assigned')
        
        return format_html(
            '<strong>Name:</strong> {}<br>'
            '<strong>Code:</strong> {}<br>'
            '<strong>Category:</strong> {}<br>'
            '<strong>Credits:</strong> {}<br>'
            '<strong>Periods/Week:</strong> {}<br>'
            '<strong>Weekly Hours:</strong> {}<br>'
            '<strong>Core:</strong> {}<br>'
            '<strong>Elective:</strong> {}',
            info['name'], info['code'], info['category'], info['credits'],
            info['periods_per_week'], info['weekly_hours'],
            info['is_core'], info['is_elective']
        )
    subject_info_display.short_description = _('Subject Information')
    
    def assignment_summary_display(self, obj):
        """Display assignment summary."""
        summary = obj.assignment_summary
        return format_html(
            '<strong>Student:</strong> {}<br>'
            '<strong>Class:</strong> {}<br>'
            '<strong>Subject:</strong> {}<br>'
            '<strong>Academic Year:</strong> {}<br>'
            '<strong>Assignment Date:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Current:</strong> {}<br>'
            '<strong>Duration:</strong> {} days',
            summary['student'], summary['class'], summary['subject'],
            summary['academic_year'], summary['assignment_date'],
            summary['status'], summary['is_current'],
            summary['assignment_duration_days']
        )
    assignment_summary_display.short_description = _('Assignment Summary')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# PLANNING MODEL ADMINS
# ============================================================================

@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    """Admin configuration for LessonPlan model."""
    
    list_display = (
        'title', 'subject', 'class_assigned', 'teacher_display',
        'date', 'duration_minutes', 'is_completed', 'is_active'
    )
    
    list_filter = (
        'subject', 'class_assigned__academic_year', 'is_completed',
        IsActiveFilter, 'class_assigned__grade_level'
    )
    
    search_fields = (
        'title', 'subject__name', 'class_assigned__name',
        'teacher__user__first_name', 'teacher__user__last_name'
    )
    
    readonly_fields = ('lesson_duration_hours',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'title', 'subject', 'sub_topic', 'class_assigned',
                'teacher', 'date', 'duration_minutes', 'is_active'
            )
        }),
        (_('Lesson Components'), {
            'fields': (
                'learning_objectives', 'materials_needed',
                'introduction', 'development', 'conclusion'
            )
        }),
        (_('Assessment and Differentiation'), {
            'fields': (
                'assessment_methods', 'differentiation_strategies'
            ),
            'classes': ('collapse',)
        }),
        (_('Homework and Follow-up'), {
            'fields': (
                'homework_assignment', 'next_lesson_preview'
            )
        }),
        (_('Status and Reflection'), {
            'fields': (
                'is_completed', 'actual_duration_minutes',
                'teacher_reflection'
            )
        }),
        (_('Computed Fields'), {
            'fields': ('lesson_duration_hours',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'subject', 'class_assigned', 'teacher__user', 'sub_topic'
        )
    
    def teacher_display(self, obj):
        """Display teacher name."""
        return obj.teacher.full_name
    teacher_display.short_description = _('Teacher')
    teacher_display.admin_order_field = 'teacher__user__last_name'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    """Admin configuration for Syllabus model."""
    
    list_display = (
        'subject', 'academic_year', 'version', 'is_approved',
        'total_topics_display', 'total_weeks_display', 'is_active'
    )
    
    list_filter = (
        'subject', 'academic_year', 'is_approved', IsActiveFilter
    )
    
    search_fields = (
        'title', 'subject__name', 'academic_year__name',
        'version', 'objectives'
    )
    
    readonly_fields = ('total_topics', 'total_weeks', 'competency_coverage_display')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'subject', 'academic_year', 'title', 'version',
                'is_approved', 'approved_by', 'approval_date',
                'is_active'
            )
        }),
        (_('Curriculum Standards'), {
            'fields': ('curriculum_standards',)
        }),
        (_('Content Outline'), {
            'fields': ('topics',)
        }),
        (_('Learning Resources'), {
            'fields': (
                'recommended_books', 'teaching_resources'
            ),
            'classes': ('collapse',)
        }),
        (_('Assessment Framework'), {
            'fields': ('assessment_framework',)
        }),
        (_('Competency Mapping'), {
            'fields': (
                'competency_mapping', 'cbc_competencies',
                'project_requirements'
            ),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': (
                'objectives', 'methodology', 'syllabus_file', 'notes'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': (
                'total_topics', 'total_weeks', 'competency_coverage_display'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'subject', 'academic_year', 'approved_by'
        )
    
    def total_topics_display(self, obj):
        """Display total topics."""
        return obj.total_topics
    total_topics_display.short_description = _('Topics')
    total_topics_display.admin_order_field = 'total_topics'
    
    def total_weeks_display(self, obj):
        """Display total weeks."""
        return obj.total_weeks
    total_weeks_display.short_description = _('Weeks')
    total_weeks_display.admin_order_field = 'total_weeks'
    
    def competency_coverage_display(self, obj):
        """Display competency coverage."""
        coverage = obj.get_competency_coverage()
        if not coverage:
            return _('No competency mapping available')
        
        items = []
        for competency, count in list(coverage.items())[:5]:  # Show top 5
            items.append(f"{competency}: {count}")
        
        return format_html('<br>'.join(items))
    competency_coverage_display.short_description = _('Competency Coverage')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    """Admin configuration for AcademicEvent model."""
    
    list_display = (
        'title', 'event_type', 'academic_year', 'term',
        'start_date', 'end_date', 'location', 'is_published',
        'priority', 'is_active'
    )
    
    list_filter = (
        'event_type', 'academic_year', 'priority', 'is_published',
        'is_cancelled', IsActiveFilter
    )
    
    search_fields = (
        'title', 'description', 'location', 'organizer__username',
        'academic_year__name', 'term__name'
    )
    
    readonly_fields = ('duration_hours', 'is_upcoming', 'is_ongoing', 'is_past')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'title', 'description', 'event_type', 'start_date',
                'end_date', 'location', 'is_active'
            )
        }),
        (_('Academic Context'), {
            'fields': (
                'academic_year', 'term'
            )
        }),
        (_('Participants and Status'), {
            'fields': (
                'target_audience', 'is_published', 'is_cancelled',
                'priority', 'organizer'
            )
        }),
        (_('Resources and Attendance'), {
            'fields': (
                'resources', 'requires_attendance',
                'reminder_days_before'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': (
                'duration_hours', 'is_upcoming', 'is_ongoing', 'is_past'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'academic_year', 'term', 'organizer'
        )
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    """Admin configuration for Stream model."""
    
    list_display = (
        'name', 'code', 'education_level', 'curriculum',
        'pathway_display', 'is_active'
    )
    
    list_filter = (
        'education_level', 'curriculum', 'pathway', IsActiveFilter
    )
    
    search_fields = ('name', 'code', 'description')
    
    readonly_fields = ('pathway_display',)
    
    filter_horizontal = ('core_subjects', 'elective_subjects')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name', 'code', 'description', 'education_level',
                'curriculum', 'pathway', 'is_active'
            )
        }),
        (_('Requirements and Pathways'), {
            'fields': (
                'minimum_requirements', 'career_pathways'
            ),
            'classes': ('collapse',)
        }),
        (_('Subjects'), {
            'fields': (
                'core_subjects', 'elective_subjects'
            )
        }),
        (_('Computed Fields'), {
            'fields': ('pathway_display',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def pathway_display(self, obj):
        """Display pathway."""
        return obj.get_pathway_display() if obj.pathway else '-'
    pathway_display.short_description = _('Pathway')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# CBC MODEL ADMINS
# ============================================================================

@admin.register(CBCAssessment)
class CBCAssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for CBCAssessment model."""
    
    list_display = (
        'student_display', 'subject', 'academic_year',
        'assessment_type', 'assessment_date', 'proficiency_level',
        'total_score_display', 'is_active'
    )
    
    list_filter = (
        'assessment_type', 'proficiency_level', 'academic_year',
        'subject__curriculum', IsActiveFilter
    )
    
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'subject__name',
        'academic_year__name'
    )
    
    readonly_fields = ('total_score', 'is_national_exam')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'subject', 'academic_year', 'class_assigned',
                'assessment_type', 'assessment_date', 'is_active'
            )
        }),
        (_('Assessment Scores'), {
            'fields': (
                'competency_scores', 'practical_score',
                'theory_score', 'project_score'
            )
        }),
        (_('CBC Descriptors'), {
            'fields': (
                'proficiency_level', 'teacher_comments',
                'portfolio_evidence'
            )
        }),
        (_('Computed Fields'), {
            'fields': ('total_score', 'is_national_exam'),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'subject', 'academic_year', 'class_assigned'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def total_score_display(self, obj):
        """Display total score."""
        score = obj.total_score
        if score is None:
            return '-'
        
        # Color code based on score
        color = 'green' if score >= 70 else 'orange' if score >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, score
        )
    total_score_display.short_description = _('Total Score')
    total_score_display.admin_order_field = 'total_score'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CBCPortfolio)
class CBCPortfolioAdmin(admin.ModelAdmin):
    """Admin configuration for CBCPortfolio model."""
    
    list_display = (
        'student_display', 'academic_year', 'portfolio_title',
        'portfolio_type', 'artifacts_count_display', 'is_complete',
        'submission_date', 'is_active'
    )
    
    list_filter = (
        'portfolio_type', 'academic_year', 'is_complete', IsActiveFilter
    )
    
    search_fields = (
        'portfolio_title', 'student__user__first_name',
        'student__user__last_name', 'student__admission_number',
        'academic_year__name'
    )
    
    readonly_fields = ('artifacts_count',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'academic_year', 'portfolio_title',
                'portfolio_type', 'description', 'is_active'
            )
        }),
        (_('Portfolio Content'), {
            'fields': (
                'artifacts', 'skills_demonstrated'
            )
        }),
        (_('Reflection and Feedback'), {
            'fields': (
                'reflection', 'teacher_feedback'
            ),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': (
                'is_complete', 'submission_date'
            )
        }),
        (_('Computed Fields'), {
            'fields': ('artifacts_count',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'academic_year'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def artifacts_count_display(self, obj):
        """Display artifacts count."""
        return obj.artifacts_count
    artifacts_count_display.short_description = _('Artifacts')
    artifacts_count_display.admin_order_field = 'artifacts_count'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PathwaySelection)
class PathwaySelectionAdmin(admin.ModelAdmin):
    """Admin configuration for PathwaySelection model."""
    
    list_display = (
        'student_display', 'academic_year', 'preferred_pathway',
        'alternative_pathway', 'senior_track', 'is_approved',
        'selection_date', 'parent_consent', 'is_active'
    )
    
    list_filter = (
        'preferred_pathway', 'senior_track', 'is_approved',
        'parent_consent', 'academic_year', IsActiveFilter
    )
    
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'academic_year__name',
        'student_statement', 'teacher_recommendation'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'academic_year', 'preferred_pathway',
                'alternative_pathway', 'senior_track', 'is_active'
            )
        }),
        (_('Selection Details'), {
            'fields': (
                'selection_date', 'is_approved', 'approved_by',
                'approval_date'
            )
        }),
        (_('Rationale and Consent'), {
            'fields': (
                'student_statement', 'parent_consent',
                'teacher_recommendation'
            ),
            'classes': ('collapse',)
        }),
        (_('Career Aspirations'), {
            'fields': ('career_interests',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'academic_year', 'approved_by'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompetencyTracking)
class CompetencyTrackingAdmin(admin.ModelAdmin):
    """Admin configuration for CompetencyTracking model."""
    
    list_display = (
        'student_display', 'academic_year', 'competency_area',
        'baseline_level', 'current_level', 'target_level',
        'has_improved_display', 'last_assessed', 'is_active'
    )
    
    list_filter = (
        'competency_area', 'current_level', 'academic_year',
        IsActiveFilter
    )
    
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'academic_year__name',
        'teacher_comments'
    )
    
    readonly_fields = ('has_improved',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'student', 'academic_year', 'competency_area',
                'is_active'
            )
        }),
        (_('Assessment Levels'), {
            'fields': (
                'baseline_level', 'current_level', 'target_level'
            )
        }),
        (_('Evidence and Tracking'), {
            'fields': (
                'evidence', 'teacher_comments', 'last_assessed',
                'next_review'
            ),
            'classes': ('collapse',)
        }),
        (_('Computed Fields'), {
            'fields': ('has_improved',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student__user', 'academic_year'
        )
    
    def student_display(self, obj):
        """Display student name."""
        return obj.student.full_name
    student_display.short_description = _('Student')
    student_display.admin_order_field = 'student__user__last_name'
    
    def has_improved_display(self, obj):
        """Display improvement status."""
        if obj.has_improved is None:
            return '-'
        
        if obj.has_improved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Improved</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;">No improvement</span>'
            )
    has_improved_display.short_description = _('Improved')
    has_improved_display.admin_order_field = 'has_improved'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CurriculumMapping)
class CurriculumMappingAdmin(admin.ModelAdmin):
    """Admin configuration for CurriculumMapping model."""
    
    list_display = (
        'curriculum_system', 'grade_level', 'subject',
        'standard_code', 'is_active'
    )
    
    list_filter = (
        'curriculum_system', 'grade_level', 'subject__curriculum',
        IsActiveFilter
    )
    
    search_fields = (
        'standard_code', 'standard_description',
        'subject__name', 'subject__code'
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'curriculum_system', 'grade_level', 'subject',
                'standard_code', 'standard_description', 'is_active'
            )
        }),
        (_('Competency Alignment'), {
            'fields': (
                'aligned_competencies', 'learning_outcomes',
                'assessment_criteria'
            ),
            'classes': ('collapse',)
        }),
        (_('Resources and Links'), {
            'fields': (
                'resources', 'international_equivalents'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject')
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields."""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

class AcademicsAdminSite(admin.AdminSite):
    """Custom admin site for academics module."""
    
    site_header = _('Academic Management System')
    site_title = _('Academic Management')
    index_title = _('Academic Management Dashboard')
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request, app_label)
        
        # Custom ordering of apps
        ordering = {
            'academics': 1,
            'students': 2,
            'teachers': 3,
            'attendance': 4,
            'grading': 5,
            'accounts': 6,
            'auth': 7,
        }
        
        # Sort apps by custom ordering
        app_list.sort(key=lambda x: ordering.get(x['app_label'], 999))
        
        # Custom ordering of models within academics app
        for app in app_list:
            if app['app_label'] == 'academics':
                model_ordering = {
                    'academicyear': 1,
                    'academicterm': 2,
                    'subject': 3,
                    'class': 4,
                    'subtopic': 5,
                    'subjectassignment': 6,
                    'studentenrollment': 7,
                    'studentclassassignment': 8,
                    'lessonplan': 9,
                    'syllabus': 10,
                    'academicevent': 11,
                    'stream': 12,
                    'cbcassessment': 13,
                    'cbcportfolio': 14,
                    'pathwayselection': 15,
                    'competencytracking': 16,
                    'curriculummapping': 17,
                }
                app['models'].sort(key=lambda x: model_ordering.get(x['object_name'].lower(), 999))
        
        return app_list




# ============================================================================
# DEFAULT ADMIN REGISTRATION
# ============================================================================

