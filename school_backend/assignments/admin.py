# assignments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.contrib.admin import SimpleListFilter
from .models import (
    Assignment, StudentAssignment, AssignmentCategory, AssignmentGradeScale,
    AssignmentGroup, GroupMembership, AssignmentComment, AssignmentAnalytics
)


class AssignmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'assignment_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {};">■</span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def assignment_count(self, obj):
        return obj.assignment_set.count()
    assignment_count.short_description = 'Assignments'


class AssignmentGradeScaleAdmin(admin.ModelAdmin):
    list_display = ['grade', 'min_percentage', 'max_percentage', 'points', 'curriculum', 'is_active']
    list_filter = ['curriculum', 'is_active']
    search_fields = ['grade', 'description']
    ordering = ['curriculum', 'min_percentage']


class StudentAssignmentInline(admin.TabularInline):
    model = StudentAssignment
    extra = 0
    readonly_fields = ['submission_date', 'status', 'marks_obtained']
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False


class IsLateFilter(SimpleListFilter):
    title = 'is late'
    parameter_name = 'is_late'

    def lookups(self, request, model_admin):
        return [
            ('true', 'Late'),
            ('false', 'On Time'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(status='late')
        elif self.value() == 'false':
            return queryset.filter(status='submitted')
        return queryset


class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject', 'teacher', 'classroom', 'assignment_type', 
        'status', 'due_date', 'total_marks', 'submission_count', 
        'average_score_display', 'created_at'
    ]
    list_filter = [
        'status', 'assignment_type', 'subject', 'teacher', 'classroom', 
        'term', 'curriculum', 'created_at'
    ]
    search_fields = ['title', 'description', 'subject__name']
    readonly_fields = [
        'created_at', 'updated_at', 'published_at', 'closed_at',
        'views_count', 'average_score', 'completion_rate'
    ]
    date_hierarchy = 'created_at'
    inlines = [StudentAssignmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'description', 'assignment_type', 'category', 
                'subject', 'teacher', 'classroom', 'stream'
            )
        }),
        ('Academic Context', {
            'fields': (
                'academic_year', 'term', 'curriculum'
            )
        }),
        ('Assignment Details', {
            'fields': (
                'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
                'estimated_completion_time', 'instructions', 'learning_objectives',
                'resources', 'rubric'
            )
        }),
        ('Files and Attachments', {
            'fields': (
                'attachment', 'additional_files'
            )
        }),
        ('Settings', {
            'fields': (
                'allow_late_submission', 'late_submission_penalty',
                'allow_resubmission', 'max_resubmissions', 'require_approval',
                'is_group_assignment', 'max_group_size'
            )
        }),
        ('Status and Tracking', {
            'fields': (
                'status', 'published_at', 'closed_at'
            )
        }),
        ('Analytics', {
            'fields': (
                'views_count', 'average_score', 'completion_rate'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )
    
    def submission_count(self, obj):
        return obj.student_assignments.count()
    submission_count.short_description = 'Submissions'
    
    def average_score_display(self, obj):
        if obj.average_score:
            return f"{obj.average_score:.1f}"
        return "N/A"
    average_score_display.short_description = 'Avg Score'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            submission_count=Count('student_assignments')
        )


class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'assignment', 'student', 'status', 'submission_date', 
        'marks_obtained', 'final_marks', 'grade', 'is_late_display',
        'graded_at', 'created_at'
    ]
    list_filter = [
        'status', 'assignment__subject', 'assignment__teacher',
        'assignment__classroom', IsLateFilter, 'graded_at'  # Use custom filter instead of 'is_late'
    ]
    search_fields = [
        'assignment__title', 'student__first_name', 
        'student__last_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'graded_at', 'submission_date',
        'get_is_late', 'percentage', 'days_late'
    ]
    date_hierarchy = 'submission_date'
    
    fieldsets = (
        ('Assignment Information', {
            'fields': (
                'assignment', 'student'
            )
        }),
        ('Submission Details', {
            'fields': (
                'submission_text', 'submission_file', 'submission_files',
                'word_count', 'character_count', 'time_spent'
            )
        }),
        ('Grading', {
            'fields': (
                'marks_obtained', 'penalty_points', 'final_marks', 'grade',
                'grade_points', 'teacher_feedback', 'rubric_scores', 'audio_feedback'
            )
        }),
        ('Status', {
            'fields': (
                'status', 'graded_by', 'graded_at'
            )
        }),
        ('Tracking', {
            'fields': (
                'version', 'previous_version', 'last_accessed', 'draft_saved',
                'ip_address', 'user_agent'
            )
        }),
        ('Computed Fields', {
            'fields': (
                'get_is_late', 'percentage', 'days_late'
            )
        }),
    )
    
    def is_late_display(self, obj):
        if obj.is_late:
            return format_html('<span style="color: red;">● Late</span>')
        return format_html('<span style="color: green;">● On Time</span>')
    is_late_display.short_description = 'Status'
    
    def get_is_late(self, obj):
        return obj.is_late
    get_is_late.short_description = 'Is Late'
    get_is_late.boolean = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assignment', 'student', 'graded_by'
        )


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1


class AssignmentGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'assignment', 'leader', 'member_count', 'created_at']
    list_filter = ['assignment__subject', 'assignment__teacher']
    search_fields = ['name', 'assignment__title', 'leader__first_name']
    inlines = [GroupMembershipInline]
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


class AssignmentCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'assignment', 'content_preview', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at', 'assignment__subject']
    search_fields = ['content', 'author__first_name', 'assignment__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


class AssignmentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'total_views', 'unique_viewers', 'average_time_spent', 'get_last_updated']
    readonly_fields = ['get_last_updated', 'created_at', 'updated_at']
    
    def get_last_updated(self, obj):
        return obj.last_updated
    get_last_updated.short_description = 'Last Updated'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Register models
admin.site.register(AssignmentCategory, AssignmentCategoryAdmin)
admin.site.register(AssignmentGradeScale, AssignmentGradeScaleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(StudentAssignment, StudentAssignmentAdmin)
admin.site.register(AssignmentGroup, AssignmentGroupAdmin)
admin.site.register(GroupMembership)
admin.site.register(AssignmentComment, AssignmentCommentAdmin)
admin.site.register(AssignmentAnalytics, AssignmentAnalyticsAdmin)