# academic/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count, Avg, Sum
import json

from .models import (
    AcademicYear, AcademicTerm, GradeLevel, Subject, Classroom, Class,
    Enrollment, SubjectEnrollment, Assessment, Grade, Transcript, Stream,
    Attendance, AttendanceReport, Schedule, TeacherAssignment, 
    AcademicReport, AcademicEvent, GradingScale, AcademicConfiguration,
    CompetencyArea, CompetencyAssessment
)


# ============================================================================
# ADMIN SITE CONFIGURATION
# ============================================================================

admin.site.site_header = _("Academic Management System")
admin.site.site_title = _("Academic Admin")
admin.site.index_title = _("Dashboard")


# ============================================================================
# INLINES
# ============================================================================

class TeacherAssignmentInline(admin.TabularInline):
    """Inline for teacher assignments"""
    model = TeacherAssignment
    extra = 1
    fields = ['teacher', 'subject', 'is_class_teacher', 'assignment_type', 'is_active']
    # REMOVED: autocomplete_fields = ['teacher', 'subject']


class ScheduleInline(admin.TabularInline):
    """Inline for schedules"""
    model = Schedule
    extra = 1
    fields = ['day_of_week', 'start_time', 'end_time', 'subject', 'teacher', 'classroom']
    # REMOVED: autocomplete_fields = ['subject', 'teacher', 'classroom']


class SubjectEnrollmentInline(admin.TabularInline):
    """Inline for subject enrollments"""
    model = SubjectEnrollment
    extra = 1
    fields = ['subject', 'teacher', 'status', 'score', 'grade']
    readonly_fields = ['score', 'grade']
    # REMOVED: autocomplete_fields = ['subject', 'teacher']


class GradeInline(admin.TabularInline):
    """Inline for grades"""
    model = Grade
    extra = 1
    fields = ['assessment', 'score', 'grade', 'percentage', 'is_absent']
    readonly_fields = ['grade', 'percentage']
    # REMOVED: autocomplete_fields = ['assessment']


class AttendanceInline(admin.TabularInline):
    """Inline for attendance"""
    model = Attendance
    extra = 1
    fields = ['date', 'status', 'check_in_time', 'check_out_time', 'reason']
    readonly_fields = ['duration_display']


# ============================================================================
# FILTERS
# ============================================================================

class AcademicYearFilter(admin.SimpleListFilter):
    """Filter by academic year"""
    title = _('Academic Year')
    parameter_name = 'academic_year'

    def lookups(self, request, model_admin):
        years = AcademicYear.objects.values_list('academic_year', flat=True).distinct()
        return [(year, year) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(academic_year=self.value())
        return queryset


class TermFilter(admin.SimpleListFilter):
    """Filter by term"""
    title = _('Term')
    parameter_name = 'term'

    def lookups(self, request, model_admin):
        return [
            ('first_term', _('First Term')),
            ('second_term', _('Second Term')),
            ('third_term', _('Third Term')),
            ('summer_term', _('Summer Term')),
            ('special_term', _('Special Term')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(term=self.value())
        return queryset


class GradeLevelFilter(admin.SimpleListFilter):
    """Filter by grade level"""
    title = _('Grade Level')
    parameter_name = 'grade_level'

    def lookups(self, request, model_admin):
        levels = GradeLevel.objects.values_list('id', 'name')
        return [(str(id), name) for id, name in levels]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(grade_level_id=self.value())
        return queryset


class IsCurrentFilter(admin.SimpleListFilter):
    """Filter for current academic year"""
    title = _('Current')
    parameter_name = 'is_current'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_current=True)
        if self.value() == 'no':
            return queryset.filter(is_current=False)
        return queryset


# ============================================================================
# ADMIN CLASSES
# ============================================================================

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """Admin for AcademicYear model"""
    list_display = ['name', 'academic_year', 'term', 'start_date', 'end_date', 'is_current', 'student_count']
    list_filter = ['academic_year', 'term', IsCurrentFilter]
    search_fields = ['name', 'academic_year']
    readonly_fields = ['created_at', 'updated_at', 'student_count_display']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'academic_year', 'term', 'is_current', 'description')
        }),
        (_('Dates'), {
            'fields': ('start_date', 'end_date',
                      ('first_term_start', 'first_term_end'),
                      ('second_term_start', 'second_term_end'),
                      ('third_term_start', 'third_term_end'))
        }),
        (_('Configuration'), {
            'fields': ('min_attendance_percentage', 'passing_grade', 'max_absent_days')
        }),
        (_('Statistics'), {
            'fields': ('student_count_display', 'created_at', 'updated_at')
        }),
    )
    actions = ['set_as_current']

    def student_count(self, obj):
        """Get total students in this academic year"""
        return Enrollment.objects.filter(
            academic_year=obj.academic_year,
            term=obj.term
        ).count()
    student_count.short_description = _('Total Students')

    def student_count_display(self, obj):
        """Display student count in readonly field"""
        return self.student_count(obj)
    student_count_display.short_description = _('Total Students')

    def set_as_current(self, request, queryset):
        """Set selected academic year as current"""
        for obj in queryset:
            obj.is_current = True
            obj.save()
        self.message_user(request, _('Selected academic years have been set as current.'))
    set_as_current.short_description = _('Set as current academic year')


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    """Admin for AcademicTerm model"""
    list_display = ['name', 'academic_year', 'term_type', 'start_date', 'end_date', 'is_current', 'is_active', 'days_remaining']
    list_filter = ['academic_year', 'term_type', 'is_current']
    search_fields = ['name', 'description']
    readonly_fields = ['duration_days', 'is_active_display', 'days_remaining_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['academic_year', 'fee_structure']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'academic_year', 'term_type', 'is_current', 'description')
        }),
        (_('Term Dates'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Important Dates'), {
            'fields': ('registration_deadline', 'fee_payment_deadline', 'examination_start',
                      'examination_end', 'closing_date', 'next_term_starts')
        }),
        (_('Term Statistics'), {
            'fields': ('total_instructional_days', 'total_holidays', 'minimum_attendance_days')
        }),
        (_('Academic Requirements'), {
            'fields': ('minimum_pass_percentage', 'assessment_weight')
        }),
        (_('Fee Structure'), {
            'fields': ('fee_structure',)
        }),
        (_('Calculated Fields'), {
            'fields': ('duration_days', 'is_active_display', 'days_remaining_display', 'created_at', 'updated_at')
        }),
    )
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = _('Active')
    
    def days_remaining(self, obj):
        return obj.days_remaining
    days_remaining.short_description = _('Days Remaining')
    
    def is_active_display(self, obj):
        return _('Yes') if obj.is_active else _('No')
    is_active_display.short_description = _('Currently Active')
    
    def days_remaining_display(self, obj):
        return obj.days_remaining
    days_remaining_display.short_description = _('Days Remaining')


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    """Admin for GradeLevel model"""
    list_display = ['name', 'code', 'level', 'order', 'age_range_min', 'age_range_max', 'student_count', 'available_slots']
    list_filter = ['level', 'curriculum']
    search_fields = ['name', 'code']
    list_editable = ['order']
    readonly_fields = ['student_count_display', 'available_slots_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'level', 'order', 'description')
        }),
        (_('Configuration'), {
            'fields': ('age_range_min', 'age_range_max', 'next_grade', 'curriculum', 'max_students')
        }),
        (_('Statistics'), {
            'fields': ('student_count_display', 'available_slots_display', 'created_at', 'updated_at')
        }),
    )
    # REMOVED: autocomplete_fields = ['next_grade']

    def student_count(self, obj):
        return obj.student_count
    student_count.short_description = _('Current Students')

    def student_count_display(self, obj):
        return obj.student_count
    student_count_display.short_description = _('Current Students')

    def available_slots(self, obj):
        return obj.available_slots
    available_slots.short_description = _('Available Slots')

    def available_slots_display(self, obj):
        return obj.available_slots
    available_slots_display.short_description = _('Available Slots')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin for Subject model"""
    list_display = ['name', 'code', 'category', 'is_core', 'credit_hours', 'passing_score', 'teacher_count', 'student_count']
    list_filter = ['is_core', 'category']
    search_fields = ['name', 'code', 'description']
    filter_horizontal = ['grade_levels', 'prerequisites']
    readonly_fields = ['teacher_count_display', 'student_count_display', 'average_score_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'category', 'department')
        }),
        (_('Academic Configuration'), {
            'fields': ('is_core', 'credit_hours', 'passing_score', 'max_score', 'grade_levels', 'prerequisites')
        }),
        (_('Resources'), {
            'fields': ('syllabus',)
        }),
        (_('Statistics'), {
            'fields': ('teacher_count_display', 'student_count_display', 'average_score_display', 'created_at', 'updated_at')
        }),
    )

    def teacher_count(self, obj):
        return len(obj.get_teachers())
    teacher_count.short_description = _('Teachers')

    def teacher_count_display(self, obj):
        return len(obj.get_teachers())
    teacher_count_display.short_description = _('Teachers')

    def student_count(self, obj):
        return obj.get_student_count()
    student_count.short_description = _('Students')

    def student_count_display(self, obj):
        return obj.get_student_count()
    student_count_display.short_description = _('Students')

    def average_score_display(self, obj):
        return f"{obj.get_average_score():.2f}%"
    average_score_display.short_description = _('Average Score')


@admin.register(CompetencyArea)
class CompetencyAreaAdmin(admin.ModelAdmin):
    """Admin for CompetencyArea model"""
    list_display = ['name', 'code', 'curriculum', 'assessment_method', 'is_core', 'order']
    list_filter = ['curriculum', 'is_core', 'assessment_method']
    search_fields = ['name', 'code', 'description']
    filter_horizontal = ['grade_levels', 'subjects']
    readonly_fields = ['levels_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'curriculum')
        }),
        (_('Scope'), {
            'fields': ('grade_levels', 'subjects', 'parent_area')
        }),
        (_('Assessment'), {
            'fields': ('assessment_method', 'levels')
        }),
        (_('Status'), {
            'fields': ('is_core', 'order')
        }),
        (_('Competency Levels'), {
            'fields': ('levels_display',)
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def levels_display(self, obj):
        """Display levels in formatted way"""
        levels = obj.get_competency_levels()
        if not levels:
            return _('No levels defined')
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;">'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Level') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Name') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Min Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Max Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Description') + '</th>'
        html += '</tr>'
        
        for level in levels:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{level.get("level", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{level.get("name", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{level.get("min_score", 0)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{level.get("max_score", 100)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{level.get("description", "")}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    levels_display.short_description = _('Competency Levels')


@admin.register(CompetencyAssessment)
class CompetencyAssessmentAdmin(admin.ModelAdmin):
    """Admin for CompetencyAssessment model"""
    list_display = ['student', 'competency_area', 'academic_year', 'term', 'score', 'level', 'assessed_by', 'assessment_date']
    list_filter = ['academic_year', 'term', 'competency_area', 'is_verified']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'competency_area__name']
    readonly_fields = ['evidence_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['student', 'competency_area', 'grade_level', 'assessed_by', 'verified_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'competency_area', 'academic_year', 'term', 'grade_level')
        }),
        (_('Assessment Details'), {
            'fields': ('score', 'level', 'assessment_date', 'assessed_by')
        }),
        (_('Evidence & Comments'), {
            'fields': ('evidence', 'comments')
        }),
        (_('Verification'), {
            'fields': ('is_verified', 'verified_by', 'verified_date')
        }),
        (_('Evidence Display'), {
            'fields': ('evidence_display',)
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def evidence_display(self, obj):
        """Display evidence in formatted way"""
        if not obj.evidence:
            return _('No evidence provided')
        
        html = '<ul>'
        for item in obj.evidence:
            html += f'<li>{item}</li>'
        html += '</ul>'
        return format_html(html)
    evidence_display.short_description = _('Assessment Evidence')


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Admin for Classroom model"""
    list_display = ['room_number', 'name', 'building', 'floor', 'capacity', 'is_available', 'is_special', 'current_class_display']
    list_filter = ['building', 'floor', 'is_available', 'is_special']
    search_fields = ['room_number', 'name', 'building']
    readonly_fields = ['current_class_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('room_number', 'name', 'building', 'floor', 'description')
        }),
        (_('Capacity & Status'), {
            'fields': ('capacity', 'is_available', 'is_special', 'special_type')
        }),
        (_('Facilities'), {
            'fields': ('facilities',)
        }),
        (_('Current Status'), {
            'fields': ('current_class_display', 'created_at', 'updated_at')
        }),
    )

    def current_class_display(self, obj):
        current_class = obj.current_class
        if current_class:
            url = reverse('admin:academic_class_change', args=[current_class.id])
            return format_html('<a href="{}">{}</a>', url, current_class.name)
        return _('No class currently')
    current_class_display.short_description = _('Current Class')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin for Class model"""
    list_display = ['name', 'code', 'grade_level', 'academic_year', 'term', 'form_teacher', 'students_count', 'max_students', 'available_slots']
    list_filter = ['academic_year', 'term', 'grade_level']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['students_count_display', 'available_slots_display', 'performance_summary', 'attendance_summary', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'grade_level', 'description')
        }),
        (_('Academic Period'), {
            'fields': ('academic_year', 'term')
        }),
        (_('Staff Assignment'), {
            'fields': ('form_teacher', 'assistant_teacher', 'classroom')
        }),
        (_('Capacity'), {
            'fields': ('max_students', 'students_count_display', 'available_slots_display')
        }),
        (_('Statistics'), {
            'fields': ('performance_summary', 'attendance_summary', 'created_at', 'updated_at')
        }),
    )
    inlines = [TeacherAssignmentInline, ScheduleInline]
    # REMOVED: autocomplete_fields = ['grade_level', 'form_teacher', 'assistant_teacher', 'classroom']

    def students_count_display(self, obj):
        return obj.students_count
    students_count_display.short_description = _('Current Students')

    def available_slots_display(self, obj):
        return obj.available_slots
    available_slots_display.short_description = _('Available Slots')

    def performance_summary(self, obj):
        """Display performance summary"""
        performance = obj.get_average_performance()
        return format_html(
            _("""
            <div>
                <strong>Average Score:</strong> {average_score:.2f}<br>
                <strong>Highest Score:</strong> {highest_score:.2f}<br>
                <strong>Lowest Score:</strong> {lowest_score:.2f}<br>
                <strong>Total Students:</strong> {total_students}
            </div>
            """).format(**performance)
        )
    performance_summary.short_description = _('Performance Summary')

    def attendance_summary(self, obj):
        """Display attendance summary"""
        summary = obj.get_attendance_summary()
        return format_html(
            _("""
            <div>
                <strong>Present:</strong> {present_percentage:.1f}%<br>
                <strong>Absent:</strong> {absent_percentage:.1f}%<br>
                <strong>Late:</strong> {late_percentage:.1f}%<br>
                <strong>Total Records:</strong> {total_records}
            </div>
            """).format(**summary)
        )
    attendance_summary.short_description = _('Attendance Summary (Last 30 Days)')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin for Enrollment model"""
    list_display = ['student', 'class_assigned', 'academic_year', 'term', 'enrollment_date', 'status', 'academic_status', 'performance_link']
    list_filter = ['academic_year', 'term', 'status', 'academic_status', 'enrollment_type']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'enrollment_number', 'class_assigned__name']
    readonly_fields = ['enrollment_number', 'performance_summary', 'attendance_summary', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'class_assigned', 'academic_year', 'term')
        }),
        (_('Enrollment Details'), {
            'fields': ('enrollment_number', 'enrollment_date', 'enrollment_type', 'status', 'academic_status')
        }),
        (_('Management'), {
            'fields': ('remarks', 'created_by')
        }),
        (_('Statistics'), {
            'fields': ('performance_summary', 'attendance_summary', 'created_at', 'updated_at')
        }),
    )
    inlines = [SubjectEnrollmentInline]
    # REMOVED: autocomplete_fields = ['student', 'class_assigned', 'created_by']

    def performance_link(self, obj):
        """Link to performance summary"""
        url = reverse('admin:academic_enrollment_change', args=[obj.id])
        return format_html('<a href="{}#performance_summary">View</a>', url)
    performance_link.short_description = _('Performance')

    def performance_summary(self, obj):
        """Display performance summary"""
        performance = obj.get_academic_performance()
        return format_html(
            _("""
            <div>
                <strong>Average Score:</strong> {average_score:.2f}<br>
                <strong>Subjects:</strong> {passed_subjects}/{total_subjects} passed ({pass_percentage:.1f}%)<br>
                <strong>Highest Score:</strong> {highest_score:.2f}<br>
                <strong>Lowest Score:</strong> {lowest_score:.2f}
            </div>
            """).format(**performance)
        )
    performance_summary.short_description = _('Academic Performance')

    def attendance_summary(self, obj):
        """Display attendance summary"""
        summary = obj.get_attendance_summary()
        return format_html(
            _("""
            <div>
                <strong>Attendance:</strong> {attendance_percentage:.1f}%<br>
                <strong>Present:</strong> {present_days}<br>
                <strong>Absent:</strong> {absent_days}<br>
                <strong>Late:</strong> {late_days}<br>
                <strong>Excused:</strong> {excused_days}<br>
                <strong>Total Days:</strong> {total_days}
            </div>
            """).format(**summary)
        )
    attendance_summary.short_description = _('Attendance Summary')


@admin.register(SubjectEnrollment)
class SubjectEnrollmentAdmin(admin.ModelAdmin):
    """Admin for SubjectEnrollment model"""
    list_display = ['enrollment', 'subject', 'teacher', 'status', 'score', 'grade', 'credits_earned']
    list_filter = ['academic_year', 'term', 'status']
    search_fields = ['enrollment__student__username', 'subject__name', 'teacher__username']
    readonly_fields = ['assessment_grades_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('enrollment', 'subject', 'teacher', 'academic_year', 'term')
        }),
        (_('Status & Results'), {
            'fields': ('enrollment_date', 'status', 'score', 'grade', 'credits_earned', 'remarks')
        }),
        (_('Assessment Grades'), {
            'fields': ('assessment_grades_display',)
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    actions = ['calculate_final_grades']

    def assessment_grades_display(self, obj):
        """Display assessment grades"""
        grades = obj.get_assessment_grades()
        if not grades:
            return _('No assessment grades available')
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;">'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Assessment') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Type') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Grade') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Weight') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Date') + '</th>'
        html += '</tr>'
        
        for grade in grades:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("assessment", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("type", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("score", 0)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("grade", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("weight", 0)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade.get("date", "")}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    assessment_grades_display.short_description = _('Assessment Grades')

    def calculate_final_grades(self, request, queryset):
        """Calculate final grades for selected subject enrollments"""
        for enrollment in queryset:
            enrollment.calculate_final_grade()
        self.message_user(request, _('Final grades calculated successfully.'))
    calculate_final_grades.short_description = _('Calculate final grades')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin for Assessment model"""
    list_display = ['name', 'code', 'subject', 'class_assigned', 'assessment_type', 'date', 'total_marks', 'is_published', 'class_average']
    list_filter = ['academic_year', 'term', 'assessment_type', 'is_published', 'subject']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['class_average_display', 'pass_rate_display', 'top_performers_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['subject', 'class_assigned', 'created_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'subject', 'class_assigned', 'academic_year', 'term')
        }),
        (_('Assessment Details'), {
            'fields': ('assessment_type', 'date', 'start_time', 'end_time', 'description', 'instructions')
        }),
        (_('Grading'), {
            'fields': ('total_marks', 'passing_marks', 'weight')
        }),
        (_('Publication'), {
            'fields': ('is_published', 'published_date', 'created_by')
        }),
        (_('Statistics'), {
            'fields': ('class_average_display', 'pass_rate_display', 'top_performers_display', 'created_at', 'updated_at')
        }),
    )
    actions = ['publish_results']

    def class_average(self, obj):
        avg = obj.get_class_average()
        return f"{avg:.2f}" if avg else "0.00"
    class_average.short_description = _('Class Average')

    def class_average_display(self, obj):
        avg = obj.get_class_average()
        return f"{avg:.2f}" if avg else "0.00"
    class_average_display.short_description = _('Class Average')

    def pass_rate_display(self, obj):
        return f"{obj.get_pass_rate():.1f}%"
    pass_rate_display.short_description = _('Pass Rate')

    def top_performers_display(self, obj):
        """Display top performers"""
        performers = obj.get_top_performers(limit=5)
        if not performers:
            return _('No grades recorded yet')
        
        html = '<ol>'
        for performer in performers:
            html += f'<li>{performer.student.get_full_name()} - {performer.score:.2f}</li>'
        html += '</ol>'
        return format_html(html)
    top_performers_display.short_description = _('Top 5 Performers')

    def publish_results(self, request, queryset):
        """Publish results for selected assessments"""
        for assessment in queryset:
            assessment.publish_results()
        self.message_user(request, _('Selected assessment results have been published.'))
    publish_results.short_description = _('Publish results')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin for Grade model"""
    list_display = ['student', 'assessment', 'score', 'grade', 'percentage', 'is_passing', 'is_absent', 'graded_date']
    list_filter = ['assessment__academic_year', 'assessment__term', 'grade', 'is_absent', 'is_exempted']  # Fixed
    search_fields = ['student__username', 'assessment__name', 'subject__name']
    readonly_fields = ['grade_description_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'assessment', 'subject', 'class_assigned', 'enrollment')
        }),
        (_('Grade Details'), {
            'fields': ('score', 'grade', 'grade_point', 'percentage', 'is_absent', 'is_exempted')
        }),
        (_('Grading Information'), {
            'fields': ('graded_by', 'graded_date', 'remarks')
        }),
        (_('Additional Information'), {
            'fields': ('grade_description_display', 'created_at', 'updated_at')
        }),
    )

    def is_passing(self, obj):
        return obj.is_passing
    is_passing.boolean = True
    is_passing.short_description = _('Passing')

    def grade_description_display(self, obj):
        return obj.grade_description
    grade_description_display.short_description = _('Grade Description')

@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    """Admin for Transcript model"""
    list_display = ['student', 'academic_year', 'term', 'gpa', 'cgpa', 'class_rank', 'is_official', 'generated_date']
    list_filter = ['academic_year', 'term', 'is_official']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['student', 'generated_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'academic_year', 'term', 'is_official')
        }),
        (_('Academic Performance'), {
            'fields': ('gpa', 'cgpa', 'total_credits', 'credits_earned')
        }),
        (_('Rankings'), {
            'fields': ('class_rank', 'grade_level_rank', 'overall_rank')
        }),
        (_('Document'), {
            'fields': ('document', 'remarks')
        }),
        (_('Generation'), {
            'fields': ('generated_by', 'generated_date')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    actions = ['calculate_gpa', 'update_ranks']

    def calculate_gpa(self, request, queryset):
        """Calculate GPA for selected transcripts"""
        for transcript in queryset:
            transcript.gpa = transcript.calculate_gpa()
            transcript.cgpa = transcript.calculate_cgpa()
            transcript.save()
        self.message_user(request, _('GPA calculated successfully.'))
    calculate_gpa.short_description = _('Calculate GPA')

    def update_ranks(self, request, queryset):
        """Update ranks for selected transcripts"""
        for transcript in queryset:
            transcript.update_ranks()
        self.message_user(request, _('Ranks updated successfully.'))
    update_ranks.short_description = _('Update ranks')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin for Attendance model"""
    list_display = ['student', 'date', 'class_assigned', 'status', 'check_in_time', 'check_out_time', 'duration_display', 'is_late_display']
    list_filter = ['academic_year', 'term', 'status', 'date']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'class_assigned__name']
    readonly_fields = ['duration_display', 'is_late_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['student', 'enrollment', 'class_assigned', 'verified_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'enrollment', 'class_assigned', 'academic_year', 'term', 'date')
        }),
        (_('Attendance Details'), {
            'fields': ('status', 'check_in_time', 'check_out_time', 'reason')
        }),
        (_('Verification'), {
            'fields': ('verified_by', 'verified_date', 'medical_certificate', 'parent_note')
        }),
        (_('Additional Information'), {
            'fields': ('remarks', 'duration_display', 'is_late_display', 'created_at', 'updated_at')
        }),
    )
    actions = ['mark_as_present', 'mark_as_absent', 'mark_as_late']

    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "-"
    duration_display.short_description = _('Duration')

    def is_late_display(self, obj):
        return _('Yes') if obj.is_late else _('No')
    is_late_display.short_description = _('Late')

    def mark_as_present(self, request, queryset):
        """Mark selected attendance records as present"""
        queryset.update(status='present')
        self.message_user(request, _('Selected attendance records marked as present.'))
    mark_as_present.short_description = _('Mark as present')

    def mark_as_absent(self, request, queryset):
        """Mark selected attendance records as absent"""
        queryset.update(status='absent')
        self.message_user(request, _('Selected attendance records marked as absent.'))
    mark_as_absent.short_description = _('Mark as absent')

    def mark_as_late(self, request, queryset):
        """Mark selected attendance records as late"""
        queryset.update(status='late')
        self.message_user(request, _('Selected attendance records marked as late.'))
    mark_as_late.short_description = _('Mark as late')


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    """Admin for AttendanceReport model"""
    list_display = ['student', 'academic_year', 'term', 'period_start', 'period_end', 'attendance_percentage', 'is_at_risk', 'warning_level']
    list_filter = ['academic_year', 'term', 'is_at_risk', 'warning_level', 'parent_notified']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['student', 'enrollment', 'generated_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'enrollment', 'academic_year', 'term')
        }),
        (_('Period'), {
            'fields': ('period_start', 'period_end', 'total_school_days')
        }),
        (_('Statistics'), {
            'fields': ('days_present', 'days_absent', 'days_late', 'days_excused', 'attendance_percentage')
        }),
        (_('Patterns & Warnings'), {
            'fields': ('consecutive_absences', 'frequent_absence_pattern', 'is_at_risk', 'warning_level')
        }),
        (_('Notifications'), {
            'fields': ('parent_notified', 'last_notification_date')
        }),
        (_('Management'), {
            'fields': ('remarks', 'generated_by', 'generated_date')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    actions = ['update_statistics', 'detect_patterns']

    def update_statistics(self, request, queryset):
        """Update statistics for selected reports"""
        for report in queryset:
            report.update_statistics()
        self.message_user(request, _('Statistics updated successfully.'))
    update_statistics.short_description = _('Update statistics')

    def detect_patterns(self, request, queryset):
        """Detect patterns for selected reports"""
        for report in queryset:
            report.detect_patterns()
        self.message_user(request, _('Pattern detection completed.'))
    detect_patterns.short_description = _('Detect patterns')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Admin for Schedule model"""
    list_display = ['class_assigned', 'subject', 'teacher', 'day_of_week', 'start_time', 'end_time', 'duration', 'is_active', 'is_current_display']
    list_filter = ['academic_year', 'term', 'day_of_week', 'is_active', 'class_assigned']
    search_fields = ['subject__name', 'teacher__username', 'class_assigned__name']
    readonly_fields = ['duration_display', 'is_current_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['class_assigned', 'subject', 'teacher', 'classroom']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('class_assigned', 'subject', 'teacher', 'classroom')
        }),
        (_('Schedule Details'), {
            'fields': ('day_of_week', 'start_time', 'end_time', 'academic_year', 'term')
        }),
        (_('Recurrence'), {
            'fields': ('is_recurring', 'start_date', 'end_date')
        }),
        (_('Display'), {
            'fields': ('color_code', 'description')
        }),
        (_('Status'), {
            'fields': ('is_active', 'duration_display', 'is_current_display', 'created_at', 'updated_at')
        }),
    )

    def duration(self, obj):
        duration = obj.duration
        return f"{duration} min" if duration else "-"
    duration.short_description = _('Duration')

    def duration_display(self, obj):
        duration = obj.duration
        return f"{duration} minutes" if duration else "-"
    duration_display.short_description = _('Duration')

    def is_current_display(self, obj):
        return _('Yes') if obj.is_current else _('No')
    is_current_display.short_description = _('Currently Active')


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    """Admin for TeacherAssignment model"""
    list_display = ['teacher', 'subject', 'class_assigned', 'academic_year', 'term', 'is_class_teacher', 'assignment_type', 'is_active']
    list_filter = ['academic_year', 'term', 'is_class_teacher', 'assignment_type', 'is_active']
    search_fields = ['teacher__username', 'subject__name', 'class_assigned__name']
    readonly_fields = ['duration_display', 'teaching_hours_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['teacher', 'subject', 'class_assigned']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('teacher', 'subject', 'class_assigned', 'academic_year', 'term')
        }),
        (_('Assignment Details'), {
            'fields': ('is_class_teacher', 'assignment_type', 'hours_per_week')
        }),
        (_('Duration'), {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        (_('Statistics'), {
            'fields': ('duration_display', 'teaching_hours_display', 'created_at', 'updated_at')
        }),
        (_('Management'), {
            'fields': ('remarks',)
        }),
    )

    def duration_display(self, obj):
        duration = obj.duration
        if duration > 365:
            years = duration // 365
            return _('{} years').format(years)
        elif duration > 30:
            months = duration // 30
            return _('{} months').format(months)
        else:
            return _('{} days').format(duration)
    duration_display.short_description = _('Duration')

    def teaching_hours_display(self, obj):
        hours = obj.get_teaching_hours()
        return f"{hours:.1f} hours"
    teaching_hours_display.short_description = _('Teaching Hours')


@admin.register(AcademicReport)
class AcademicReportAdmin(admin.ModelAdmin):
    """Admin for AcademicReport model"""
    list_display = ['student', 'academic_year', 'term', 'overall_grade', 'gpa', 'class_rank', 'attendance_percentage', 'promotion_status', 'is_published']
    list_filter = ['academic_year', 'term', 'overall_grade', 'promotion_status', 'is_published']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']
    readonly_fields = ['subject_performance_display', 'strengths_display', 'weaknesses_display', 'created_at', 'updated_at']
    # REMOVED: autocomplete_fields = ['student', 'enrollment', 'generated_by']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'enrollment', 'academic_year', 'term')
        }),
        (_('Performance Metrics'), {
            'fields': ('overall_score', 'overall_grade', 'gpa', 'class_rank', 'grade_level_rank', 'attendance_percentage')
        }),
        (_('Detailed Performance'), {
            'fields': ('subject_performance_display', 'strengths_display', 'weaknesses_display')
        }),
        (_('Comments & Recommendations'), {
            'fields': ('form_teacher_comment', 'head_teacher_comment', 'recommendations')
        }),
        (_('Promotion Status'), {
            'fields': ('promotion_status',)
        }),
        (_('Publication'), {
            'fields': ('is_published', 'published_date', 'report_document')
        }),
        (_('Generation'), {
            'fields': ('generated_by', 'generated_date')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    actions = ['generate_reports', 'publish_reports']

    def subject_performance_display(self, obj):
        """Display subject performance in a formatted way"""
        if not obj.subject_performance:
            return _('No subject performance data available')
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;">'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Subject') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Grade') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Status') + '</th>'
        html += '</tr>'
        
        for subject in obj.subject_performance:
            status_color = '#4CAF50' if subject.get('is_passing', False) else '#F44336'
            status_text = _('Pass') if subject.get('is_passing', False) else _('Fail')
            
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{subject.get("subject_name", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{subject.get("percentage", 0):.1f}%</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{subject.get("grade", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd; color: {status_color};">{status_text}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    subject_performance_display.short_description = _('Subject Performance')

    def strengths_display(self, obj):
        """Display strengths"""
        if not obj.strengths:
            return _('No strengths identified')
        
        html = '<ul>'
        for strength in obj.strengths:
            html += f'<li>{strength.get("subject", "")}: {strength.get("score", 0):.1f}% ({strength.get("grade", "")})</li>'
        html += '</ul>'
        return format_html(html)
    strengths_display.short_description = _('Strengths')

    def weaknesses_display(self, obj):
        """Display weaknesses"""
        if not obj.weaknesses:
            return _('No areas for improvement identified')
        
        html = '<ul>'
        for weakness in obj.weaknesses:
            if 'subject' in weakness:
                html += f'<li>{weakness["subject"]}: {weakness.get("score", 0):.1f}% ({weakness.get("grade", "")}) - {weakness.get("recommendation", "")}</li>'
            else:
                html += f'<li>{weakness.get("area", "")}: {weakness.get("score", 0):.1f}% - {weakness.get("recommendation", "")}</li>'
        html += '</ul>'
        return format_html(html)
    weaknesses_display.short_description = _('Areas for Improvement')

    def generate_reports(self, request, queryset):
        """Generate reports for selected records"""
        for report in queryset:
            report.generate_report()
        self.message_user(request, _('Reports generated successfully.'))
    generate_reports.short_description = _('Generate reports')

    def publish_reports(self, request, queryset):
        """Publish selected reports"""
        for report in queryset:
            report.publish_report()
        self.message_user(request, _('Selected reports have been published.'))
    publish_reports.short_description = _('Publish reports')


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    """Admin for AcademicEvent model"""
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'academic_year', 'term', 'is_holiday', 'is_current_display']
    list_filter = ['event_type', 'academic_year', 'term', 'is_holiday', 'start_date']
    search_fields = ['title', 'description', 'location']
    filter_horizontal = ['participants', 'affected_classes']
    readonly_fields = ['duration_display', 'is_current_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'event_type', 'description')
        }),
        (_('Date & Time'), {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time')
        }),
        (_('Academic Period'), {
            'fields': ('academic_year', 'term')
        }),
        (_('Location & Organization'), {
            'fields': ('location', 'organizer')
        }),
        (_('Participants'), {
            'fields': ('participants', 'affected_classes')
        }),
        (_('Display'), {
            'fields': ('color_code', 'is_holiday')
        }),
        (_('Statistics'), {
            'fields': ('duration_display', 'is_current_display', 'created_at', 'updated_at')
        }),
    )

    def duration_display(self, obj):
        days = obj.duration_days
        if days == 1:
            return _('1 day')
        return _('{} days').format(days)
    duration_display.short_description = _('Duration')

    def is_current_display(self, obj):
        return _('Yes') if obj.is_current() else _('No')
    is_current_display.short_description = _('Currently Ongoing')


@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    """Admin for GradingScale model"""
    list_display = ['name', 'scale_type', 'academic_level', 'curriculum', 'is_default']
    list_filter = ['scale_type', 'academic_level', 'curriculum', 'is_default']
    search_fields = ['name', 'description']
    readonly_fields = ['grade_ranges_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'scale_type', 'academic_level', 'curriculum', 'description')
        }),
        (_('Default Status'), {
            'fields': ('is_default',)
        }),
        (_('Grade Ranges'), {
            'fields': ('grade_ranges', 'grade_ranges_display')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def grade_ranges_display(self, obj):
        """Display grade ranges in a formatted way"""
        if not obj.grade_ranges:
            return _('No grade ranges defined')
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;">'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Min Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Max Score') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Grade') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Points') + '</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd;">' + _('Description') + '</th>'
        html += '</tr>'
        
        for grade_range in obj.grade_ranges:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade_range.get("min_score", 0)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade_range.get("max_score", 100)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade_range.get("grade", "")}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade_range.get("points", 0)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{grade_range.get("description", "")}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    grade_ranges_display.short_description = _('Grade Ranges Preview')


@admin.register(AcademicConfiguration)
class AcademicConfigurationAdmin(admin.ModelAdmin):
    """Admin for AcademicConfiguration model"""
    list_display = ['current_academic_year', 'min_attendance_percentage', 'passing_grade_percentage', 'school_start_time', 'school_end_time']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Prevent adding new configurations"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting configuration"""
        return False
    
    fieldsets = (
        (_('Academic Settings'), {
            'fields': ('current_academic_year', 'default_grading_scale')
        }),
        (_('Attendance Settings'), {
            'fields': ('min_attendance_percentage', 'max_absent_days')
        }),
        (_('Grading Settings'), {
            'fields': ('passing_grade_percentage', 'min_promotion_score', 'max_failed_subjects')
        }),
        (_('School Timing'), {
            'fields': ('school_start_time', 'school_end_time',
                      'period_duration', 'break_duration', 'lunch_duration')
        }),
        (_('Assessment Weights'), {
            'fields': ('exam_weight', 'test_weight', 'assignment_weight', 'participation_weight')
        }),
        (_('Notification Settings'), {
            'fields': ('attendance_warning_threshold',
                      'send_attendance_alerts',
                      'send_performance_alerts',
                      'result_publication_delay')
        }),
        (_('System Features'), {
            'fields': ('enable_online_submission', 'enable_parent_portal')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    """Admin for Stream model"""
    list_display = ['name', 'code', 'current_student_count', 'capacity', 'available_slots', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['current_student_count_display', 'available_slots_display', 'created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'color_code')
        }),
        (_('Capacity'), {
            'fields': ('capacity', 'current_student_count_display', 'available_slots_display')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def current_student_count_display(self, obj):
        return obj.current_student_count
    current_student_count_display.short_description = _('Current Students')
    
    def available_slots_display(self, obj):
        return obj.available_slots
    available_slots_display.short_description = _('Available Slots')

# ============================================================================
# DASHBOARD CUSTOMIZATION
# ============================================================================

class AcademicAdminSite(admin.AdminSite):
    """Custom admin site for academic management"""
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request, app_label)
        
        # Custom ordering of academic models
        for app in app_list:
            if app['app_label'] == 'academic':
                app['models'].sort(key=lambda x: x['name'])
        
        return app_list