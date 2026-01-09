from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    GradeScale, GradeScaleRule, Examination, StudentMark, 
    Result, SubjectResult
)


class GradeScaleRuleInline(admin.TabularInline):
    """Inline admin for GradeScaleRule"""
    model = GradeScaleRule
    extra = 1
    fields = ('min_grade', 'max_grade', 'letter_grade', 'numeric_scale', 'description', 'color')
    ordering = ['min_grade']


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'curriculum', 'is_default', 'is_active')
    list_filter = ('curriculum', 'is_default', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [GradeScaleRuleInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'curriculum', 'is_default')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GradeScaleRule)
class GradeScaleRuleAdmin(admin.ModelAdmin):
    list_display = ('grade_scale', 'min_grade', 'max_grade', 'letter_grade', 'numeric_scale', 'description')
    list_filter = ('grade_scale', 'grade_scale__curriculum')
    search_fields = ('letter_grade', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Grade Range'), {
            'fields': ('grade_scale', 'min_grade', 'max_grade')
        }),
        (_('Grade Conversions'), {
            'fields': ('letter_grade', 'numeric_scale', 'description', 'color')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StudentMarkInline(admin.TabularInline):
    """Inline admin for StudentMark"""
    model = StudentMark
    extra = 0
    fields = ('student', 'subject', 'points_scored', 'percentage', 'grade', 'is_absent')
    readonly_fields = ('percentage', 'grade')
    can_delete = True
    show_change_link = True


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'academic_year', 'term', 'start_date', 'end_date', 'status', 'total_students', 'is_active')
    list_filter = ('exam_type', 'status', 'academic_year', 'term')  # Removed 'is_active' from list_filter
    search_fields = ('name', 'instructions', 'venue')
    readonly_fields = ('status', 'total_students', 'is_active', 'days_remaining', 'created_on', 'updated_on')
    filter_horizontal = ('classes', 'subjects')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'exam_type', 'academic_year', 'term')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date', 'duration', 'venue')
        }),
        (_('Configuration'), {
            'fields': ('out_of', 'grade_scale', 'classes', 'subjects')
        }),
        (_('Details'), {
            'fields': ('instructions', 'comments')
        }),
        (_('Metadata'), {
            'fields': ('created_by',)
        }),
        (_('Statistics'), {
            'fields': ('status', 'total_students', 'days_remaining')
        }),
        (_('Timestamps'), {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'academic_year', 'term', 'grade_scale', 'created_by'
        )


@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'subject', 'points_scored', 'percentage', 'grade', 'is_absent', 'is_passing')
    list_filter = ('exam', 'subject', 'grade', 'is_absent', 'exam__academic_year')  # Removed 'is_active'
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'subject__name')
    readonly_fields = ('percentage', 'grade', 'points', 'remarks', 'is_passing', 'date_time', 'updated_at')
    fieldsets = (
        (_('Mark Details'), {
            'fields': ('exam', 'student', 'subject', 'points_scored')
        }),
        (_('Calculated Fields'), {
            'fields': ('percentage', 'grade', 'points', 'remarks', 'is_passing')
        }),
        (_('Status'), {
            'fields': ('is_absent', 'is_special', 'special_notes')
        }),
        (_('Verification'), {
            'fields': ('verified_by', 'verified_at')
        }),
        (_('Metadata'), {
            'fields': ('created_by',)
        }),
        (_('Timestamps'), {
            'fields': ('date_time', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'exam', 'student', 'subject', 'created_by', 'verified_by'
        )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'term', 'gpa', 'class_position', 'attendance_rate', 'is_published')
    list_filter = ('academic_year', 'term', 'is_published', 'conduct_grade')  # Removed 'is_active'
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('letter_grade', 'created_at', 'updated_at')
    fieldsets = (
        (_('Student Information'), {
            'fields': ('student', 'academic_year', 'term', 'grade_scale')
        }),
        (_('Academic Performance'), {
            'fields': ('gpa', 'cat_gpa', 'letter_grade')
        }),
        (_('Position Tracking'), {
            'fields': ('class_position', 'stream_position', 'overall_position', 'total_students')
        }),
        (_('Additional Metrics'), {
            'fields': ('attendance_rate', 'conduct_grade')
        }),
        (_('Comments'), {
            'fields': ('teacher_comments', 'principal_comments', 'improvement_areas')
        }),
        (_('Publication Status'), {
            'fields': ('is_published', 'published_at', 'parent_acknowledged', 'parent_acknowledged_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'academic_year', 'term', 'grade_scale'
        )


@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_year', 'term', 'average_score', 'grade', 'subject_position', 'is_passing')
    list_filter = ('academic_year', 'term', 'subject')  # Removed 'is_active'
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'subject__name')
    readonly_fields = ('total_score', 'average_score', 'grade', 'points', 'is_passing', 'created_at', 'updated_at')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('student', 'subject', 'academic_year', 'term')
        }),
        (_('Assessment Scores'), {
            'fields': ('cat1_score', 'cat2_score', 'cat3_score', 'end_term_score')
        }),
        (_('Calculated Scores'), {
            'fields': ('total_score', 'average_score', 'grade', 'points', 'is_passing')
        }),
        (_('Position'), {
            'fields': ('subject_position', 'total_in_subject')
        }),
        (_('Teacher Feedback'), {
            'fields': ('teacher_comments', 'strengths', 'improvement_areas')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'subject', 'academic_year', 'term'
        )


# Custom admin site header
admin.site.site_header = "Delvok Academy - Examination Management"
admin.site.site_title = "Delvok Academy Exam Admin"
admin.site.index_title = "Examination Management System"