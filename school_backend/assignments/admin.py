# assignments/admin.py - FIXED VERSION
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    AssignmentCategory, Assignment, StudentAssignment, 
    AssignmentGroup, GroupMembership, AssignmentComment,
    AssignmentAnalytics, AssignmentReminder
)

User = get_user_model()


class BaseAdmin(admin.ModelAdmin):
    """Base admin configuration for all models"""
    list_per_page = 50
    save_on_top = True
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssignmentCategory)
class AssignmentCategoryAdmin(BaseAdmin):
    """Admin interface for AssignmentCategory"""
    list_display = ['name', 'curriculum', 'education_level', 'color_display', 'is_active', 'assignment_count']
    list_filter = ['curriculum', 'education_level', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}
    ordering = ['name']
    actions = ['activate_categories', 'deactivate_categories']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'curriculum', 'education_level')
        }),
        (_('Display Options'), {
            'fields': ('color', 'icon'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(assignment_count=Count('assignment'))
    
    def assignment_count(self, obj):
        return obj.assignment_count
    assignment_count.short_description = _('Assignments')
    assignment_count.admin_order_field = 'assignment_count'
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = _('Color')
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _('{} categories activated successfully.').format(updated))
    activate_categories.short_description = _('Activate selected categories')
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('{} categories deactivated successfully.').format(updated))
    deactivate_categories.short_description = _('Deactivate selected categories')


class StudentAssignmentInline(admin.TabularInline):
    """Inline for student assignments in Assignment admin"""
    model = StudentAssignment
    fields = ['student', 'status', 'marks_obtained', 'submission_date', 'is_late']
    readonly_fields = ['student', 'status', 'submission_date', 'is_late']
    extra = 0
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


class AssignmentCommentInline(admin.TabularInline):
    """Inline for assignment comments"""
    model = AssignmentComment
    fields = ['author', 'content', 'is_private', 'created_at']
    readonly_fields = ['author', 'created_at']
    extra = 0
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser


class AssignmentGroupInline(admin.TabularInline):
    """Inline for assignment groups"""
    model = AssignmentGroup
    fields = ['name', 'leader', 'member_count', 'is_active']
    readonly_fields = ['member_count']
    extra = 0
    show_change_link = True


class IsOverdueFilter(admin.SimpleListFilter):
    """Filter assignments by overdue status"""
    title = _('overdue status')
    parameter_name = 'is_overdue'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', _('Overdue')),
            ('no', _('Not Overdue')),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'yes':
            return queryset.filter(
                due_date__lt=now,
                status__in=['published', 'in_progress']
            )
        if self.value() == 'no':
            return queryset.filter(
                Q(due_date__gte=now) | Q(status__in=['closed', 'graded', 'archived'])
            )
        return queryset


class SubmissionRateFilter(admin.SimpleListFilter):
    """Filter assignments by submission rate"""
    title = _('submission rate')
    parameter_name = 'submission_rate'
    
    def lookups(self, request, model_admin):
        return (
            ('high', _('High (> 80%)')),
            ('medium', _('Medium (50-80%)')),
            ('low', _('Low (< 50%)')),
            ('none', _('No submissions')),
        )
    
    def queryset(self, request, queryset):
        # Annotate queryset with submission rate
        queryset = queryset.annotate(
            total_students=Count('classroom__student_enrollments', 
                               filter=Q(classroom__student_enrollments__status='active')),
            submitted_count=Count('student_assignments',
                                filter=Q(student_assignments__status__in=['submitted', 'late', 'graded']))
        )
        
        # Apply filter based on submission rate
        if self.value() == 'high':
            return queryset.annotate(
                submission_rate=100.0 * F('submitted_count') / F('total_students')
            ).filter(submission_rate__gte=80)
        elif self.value() == 'medium':
            return queryset.annotate(
                submission_rate=100.0 * F('submitted_count') / F('total_students')
            ).filter(submission_rate__range=[50, 80])
        elif self.value() == 'low':
            return queryset.annotate(
                submission_rate=100.0 * F('submitted_count') / F('total_students')
            ).filter(submission_rate__lt=50)
        elif self.value() == 'none':
            return queryset.filter(student_assignments__status__in=['not_submitted']).distinct()
        return queryset


@admin.register(Assignment)
class AssignmentAdmin(BaseAdmin):
    """Admin interface for Assignment model"""
    
    # Display configuration
    list_display = [
        'title', 'teacher_name', 'subject', 'classroom', 
        'assignment_type', 'status_badge', 'due_date_display',
        'submission_stats', 'average_score_display', 'actions_links'
    ]
    
    list_filter = [
        'status', 'assignment_type', 'curriculum', 'difficulty_level',
        'academic_year', 'term', 'subject', 'classroom', 'stream',
        IsOverdueFilter, SubmissionRateFilter, 'is_active'
    ]
    
    search_fields = [
        'title', 'description', 'instructions', 
        'teacher__first_name', 'teacher__last_name',
        'subject__name', 'classroom__name'
    ]
    
    list_select_related = [
        'teacher', 'subject', 'classroom', 'stream', 
        'academic_year', 'term', 'category'
    ]
    
    readonly_fields = [
        'published_at', 'closed_at', 'approved_at',
        'views_count', 'average_score', 'completion_rate',
        'created_by', 'created_at', 'updated_at'
    ]
    
    autocomplete_fields = [
        'teacher', 'subject', 'classroom', 'stream',
        'academic_year', 'term', 'category', 'approved_by',
        'created_by'
    ]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'assignment_type', 'category')
        }),
        (_('Curriculum & Subject'), {
            'fields': ('curriculum', 'subject', 'classroom', 'stream')
        }),
        (_('Academic Context'), {
            'fields': ('academic_year', 'term', 'teacher')
        }),
        (_('Assignment Details'), {
            'fields': (
                'due_date', 'total_marks', 'passing_marks',
                'difficulty_level', 'estimated_completion_time'
            )
        }),
        (_('Content & Instructions'), {
            'fields': ('instructions', 'learning_objectives', 'resources'),
            'classes': ('wide',)
        }),
        (_('CBC Competencies'), {
            'fields': ('competencies', 'core_competencies'),
            'classes': ('collapse',)
        }),
        (_('Grading Rubric'), {
            'fields': ('rubric',),
            'classes': ('collapse',)
        }),
        (_('Submission Settings'), {
            'fields': (
                'allow_late_submission', 'late_submission_penalty',
                'allow_resubmission', 'max_resubmissions',
                'is_group_assignment', 'max_group_size'
            ),
            'classes': ('collapse',)
        }),
        (_('Attachments'), {
            'fields': ('attachment', 'additional_files'),
            'classes': ('collapse',)
        }),
        (_('Approval Workflow'), {
            'fields': ('require_approval', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('status', 'is_active')
        }),
        (_('Analytics'), {
            'fields': ('views_count', 'average_score', 'completion_rate'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': (
                'published_at', 'closed_at',
                'created_at', 'updated_at', 'created_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [
        StudentAssignmentInline,
        AssignmentGroupInline,
        AssignmentCommentInline,
    ]
    
    def get_actions(self, request):
        # Get the default actions
        actions = super().get_actions(request)
        
        # Add our custom actions
        if 'publish_assignments' not in actions:
            actions['publish_assignments'] = (
                self.publish_assignments,
                'publish_assignments',
                _('Publish selected assignments')
            )
        if 'close_assignments' not in actions:
            actions['close_assignments'] = (
                self.close_assignments,
                'close_assignments',
                _('Close selected assignments')
            )
        if 'archive_assignments' not in actions:
            actions['archive_assignments'] = (
                self.archive_assignments,
                'archive_assignments',
                _('Archive selected assignments')
            )
        if 'activate_assignments' not in actions:
            actions['activate_assignments'] = (
                self.activate_assignments,
                'activate_assignments',
                _('Activate selected assignments')
            )
        if 'deactivate_assignments' not in actions:
            actions['deactivate_assignments'] = (
                self.deactivate_assignments,
                'deactivate_assignments',
                _('Deactivate selected assignments')
            )
        
        return actions
    
    # Custom methods for list display
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.with_submission_stats()
    
    def teacher_name(self, obj):
        return obj.teacher.get_full_name()
    teacher_name.short_description = _('Teacher')
    teacher_name.admin_order_field = 'teacher__first_name'
    
    def status_badge(self, obj):
        status_colors = {
            'draft': 'gray',
            'published': 'green',
            'in_progress': 'blue',
            'closed': 'orange',
            'graded': 'purple',
            'archived': 'red'
        }
        
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'background-color: {}; color: white; border-radius: 10px; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def due_date_display(self, obj):
        now = timezone.now()
        if obj.due_date < now and obj.status in ['published', 'in_progress']:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} ⏰</span>',
                obj.due_date.strftime('%Y-%m-%d %H:%M')
            )
        elif obj.due_date > now:
            days_until = (obj.due_date - now).days
            if days_until <= 3:
                return format_html(
                    '<span style="color: #ffc107; font-weight: bold;">{} ({} days)</span>',
                    obj.due_date.strftime('%Y-%m-%d %H:%M'), days_until
                )
        return obj.due_date.strftime('%Y-%m-%d %H:%M')
    due_date_display.short_description = _('Due Date')
    due_date_display.admin_order_field = 'due_date'
    
    def submission_stats(self, obj):
        try:
            stats = obj.submission_stats
            return format_html(
                '{}<br><small style="color: #666;">{} submitted, {} graded</small>',
                format_html(
                    '<span style="font-weight: bold; color: {};">{:.1f}%</span>',
                    '#28a745' if stats['submission_rate'] >= 80 else 
                    '#ffc107' if stats['submission_rate'] >= 50 else '#dc3545',
                    stats['submission_rate']
                ),
                stats['submitted'],
                stats['graded']
            )
        except Exception:
            return '-'
    submission_stats.short_description = _('Submissions')
    
    def average_score_display(self, obj):
        if obj.average_score > 0:
            percentage = (obj.average_score / obj.total_marks * 100) if obj.total_marks > 0 else 0
            return format_html(
                '{}<br><small style="color: #666;">{:.1f}%</small>',
                format_html(
                    '<span style="font-weight: bold; color: {};">{:.1f}</span>',
                    '#28a745' if percentage >= 50 else 
                    '#ffc107' if percentage >= 40 else '#dc3545',
                    obj.average_score
                ),
                percentage
            )
        return '-'
    average_score_display.short_description = _('Avg Score')
    average_score_display.admin_order_field = 'average_score'
    
    def actions_links(self, obj):
        links = []
        
        # View submissions link
        submissions_url = reverse('admin:assignments_studentassignment_changelist')
        submissions_url += f'?assignment__id__exact={obj.id}'
        links.append(
            format_html(
                '<a href="{}" class="button" style="padding: 2px 8px; background: #007bff; '
                'color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">'
                '📋 Submissions</a>',
                submissions_url
            )
        )
        
        # Preview link (adjust URL to your actual view)
        try:
            preview_url = reverse('admin:assignments_assignment_preview', args=[obj.id])
            links.append(
                format_html(
                    '<a href="{}" class="button" style="padding: 2px 8px; background: #6c757d; '
                    'color: white; text-decoration: none; border-radius: 3px; font-size: 12px; '
                    'margin-left: 5px;" target="_blank">👁️ Preview</a>',
                    preview_url
                )
            )
        except:
            # If preview URL doesn't exist, create a simple view link
            preview_url = reverse('admin:assignments_assignment_change', args=[obj.id])
            links.append(
                format_html(
                    '<a href="{}" class="button" style="padding: 2px 8px; background: #6c757d; '
                    'color: white; text-decoration: none; border-radius: 3px; font-size: 12px; '
                    'margin-left: 5px;">📝 Edit</a>',
                    preview_url
                )
            )
        
        return format_html(' '.join(links))
    actions_links.short_description = _('Actions')
    
    # Custom actions
    
    def publish_assignments(self, request, queryset):
        """Publish selected assignments"""
        for assignment in queryset:
            if assignment.can_be_published:
                assignment.status = Assignment.StatusChoices.PUBLISHED
                assignment.published_at = timezone.now()
                assignment.save()
                self.message_user(
                    request, 
                    _('Assignment "{}" published successfully.').format(assignment.title)
                )
            else:
                self.message_user(
                    request,
                    _('Assignment "{}" cannot be published. Missing required fields.').format(assignment.title),
                    level='ERROR'
                )
    publish_assignments.short_description = _('Publish selected assignments')
    
    def close_assignments(self, request, queryset):
        """Close selected assignments"""
        updated = 0
        for assignment in queryset:
            assignment.status = Assignment.StatusChoices.CLOSED
            assignment.closed_at = timezone.now()
            assignment.save()
            updated += 1
        
        self.message_user(
            request, 
            _('{} assignments closed successfully.').format(updated)
        )
    close_assignments.short_description = _('Close selected assignments')
    
    def archive_assignments(self, request, queryset):
        """Archive selected assignments"""
        updated = 0
        for assignment in queryset:
            assignment.status = Assignment.StatusChoices.ARCHIVED
            assignment.is_active = False
            assignment.save()
            updated += 1
        
        self.message_user(
            request, 
            _('{} assignments archived successfully.').format(updated)
        )
    archive_assignments.short_description = _('Archive selected assignments')
    
    def activate_assignments(self, request, queryset):
        """Activate selected assignments"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            _('{} assignments activated successfully.').format(updated)
        )
    activate_assignments.short_description = _('Activate selected assignments')
    
    def deactivate_assignments(self, request, queryset):
        """Deactivate selected assignments"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            _('{} assignments deactivated successfully.').format(updated)
        )
    deactivate_assignments.short_description = _('Deactivate selected assignments')
    
    # Form handling
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Limit teacher choices to actual teachers
        if 'teacher' in form.base_fields:
            form.base_fields['teacher'].queryset = User.objects.filter(
                role='teacher', is_active=True
            )
        if 'approved_by' in form.base_fields:
            form.base_fields['approved_by'].queryset = User.objects.filter(
                role__in=['admin', 'head_teacher'], is_active=True
            )
        if 'created_by' in form.base_fields:
            form.base_fields['created_by'].initial = request.user
        return form
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(BaseAdmin):
    """Admin interface for StudentAssignment"""
    
    list_display = [
        'student_name', 'assignment_title', 'status_badge',
        'marks_obtained_display', 'percentage_display', 'grade_display',
        'submission_date_display', 'is_late_badge', 'graded_by_display'
    ]
    
    list_filter = [
        'status', 'is_late', 'assignment__assignment_type',
        'assignment__subject', 'assignment__classroom',
        'assignment__academic_year', 'assignment__term'
    ]
    
    search_fields = [
        'student__first_name', 'student__last_name',
        'assignment__title', 'feedback', 'comments'
    ]
    
    readonly_fields = [
        'submission_date', 'graded_at', 'last_resubmission_date',
        'days_late', 'percentage', 'grade', 'is_passing'
    ]
    
    list_select_related = ['student', 'assignment', 'graded_by', 'group']
    
    autocomplete_fields = ['student', 'assignment', 'graded_by', 'group']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('assignment', 'student', 'group')
        }),
        (_('Submission Details'), {
            'fields': (
                'submission_text', 'submission_file', 'attachments',
                'submission_date', 'status', 'resubmission_count',
                'last_resubmission_date'
            )
        }),
        (_('Grading'), {
            'fields': (
                'marks_obtained', 'final_marks', 'feedback', 'comments',
                'graded_by', 'graded_at'
            )
        }),
        (_('Late Submission'), {
            'fields': ('is_late', 'late_penalty_applied', 'days_late'),
            'classes': ('collapse',)
        }),
        (_('Calculated Fields'), {
            'fields': ('percentage', 'grade', 'is_passing'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        if 'mark_as_graded' not in actions:
            actions['mark_as_graded'] = (
                self.mark_as_graded,
                'mark_as_graded',
                _('Mark as graded')
            )
        if 'apply_late_penalty' not in actions:
            actions['apply_late_penalty'] = (
                self.apply_late_penalty,
                'apply_late_penalty',
                _('Apply late penalty')
            )
        if 'return_for_revision' not in actions:
            actions['return_for_revision'] = (
                self.return_for_revision,
                'return_for_revision',
                _('Return for revision')
            )
        
        return actions
    
    # Custom methods
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = _('Student')
    student_name.admin_order_field = 'student__first_name'
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = _('Assignment')
    assignment_title.admin_order_field = 'assignment__title'
    
    def status_badge(self, obj):
        status_colors = {
            'not_submitted': 'secondary',
            'submitted': 'info',
            'late': 'warning',
            'graded': 'success',
            'returned': 'danger',
            'resubmitted': 'primary'
        }
        
        color_map = {
            'secondary': '#6c757d',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'success': '#28a745',
            'danger': '#dc3545',
            'primary': '#007bff'
        }
        
        color = color_map.get(status_colors.get(obj.status, 'secondary'), '#6c757d')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'background-color: {}; color: white; border-radius: 10px; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def marks_obtained_display(self, obj):
        if obj.marks_obtained:
            return format_html(
                '<strong>{:.1f}</strong> / {:.1f}',
                obj.marks_obtained,
                obj.assignment.total_marks
            )
        return '-'
    marks_obtained_display.short_description = _('Marks')
    marks_obtained_display.admin_order_field = 'marks_obtained'
    
    def percentage_display(self, obj):
        if obj.percentage > 0:
            color = '#28a745' if obj.percentage >= 50 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, obj.percentage
            )
        return '-'
    percentage_display.short_description = _('Percentage')
    
    def grade_display(self, obj):
        grade_colors = {
            'A': '#28a745',
            'B': '#20c997',
            'C': '#ffc107',
            'D': '#fd7e14',
            'F': '#dc3545'
        }
        
        grade = obj.grade
        color = grade_colors.get(grade, '#6c757d')
        return format_html(
            '<span style="display: inline-block; width: 24px; height: 24px; '
            'background-color: {}; color: white; border-radius: 50%; '
            'text-align: center; line-height: 24px; font-weight: bold;">{}</span>',
            color, grade
        )
    grade_display.short_description = _('Grade')
    
    def submission_date_display(self, obj):
        if obj.submission_date:
            return obj.submission_date.strftime('%Y-%m-%d %H:%M')
        return '-'
    submission_date_display.short_description = _('Submitted')
    submission_date_display.admin_order_field = 'submission_date'
    
    def is_late_badge(self, obj):
        if obj.is_late:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⏰ Late</span>'
            )
        return '-'
    is_late_badge.short_description = _('Late')
    is_late_badge.admin_order_field = 'is_late'
    
    def graded_by_display(self, obj):
        if obj.graded_by:
            return obj.graded_by.get_full_name()
        return '-'
    graded_by_display.short_description = _('Graded By')
    
    # Custom actions
    
    def mark_as_graded(self, request, queryset):
        """Mark selected submissions as graded"""
        for submission in queryset:
            if not submission.marks_obtained:
                submission.marks_obtained = 0
            submission.status = 'graded'
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
        
        self.message_user(
            request,
            _('{} submissions marked as graded.').format(queryset.count())
        )
    mark_as_graded.short_description = _('Mark as graded')
    
    def apply_late_penalty(self, request, queryset):
        """Apply late submission penalty"""
        updated = 0
        for submission in queryset:
            if submission.is_late and not submission.late_penalty_applied:
                submission.is_late = True
                submission.save()
                updated += 1
        
        self.message_user(
            request,
            _('Late penalty applied to {} submissions.').format(updated)
        )
    apply_late_penalty.short_description = _('Apply late penalty')
    
    def return_for_revision(self, request, queryset):
        """Return submissions for revision"""
        updated = queryset.update(
            status='returned',
            feedback='Please revise and resubmit.'
        )
        self.message_user(
            request,
            _('{} submissions returned for revision.').format(updated)
        )
    return_for_revision.short_description = _('Return for revision')


class GroupMembershipInline(admin.TabularInline):
    """Inline for group members in AssignmentGroup admin"""
    model = GroupMembership
    fields = ['student', 'role', 'joined_at']
    readonly_fields = ['joined_at']
    extra = 1
    show_change_link = True
    autocomplete_fields = ['student']


@admin.register(AssignmentGroup)
class AssignmentGroupAdmin(BaseAdmin):
    """Admin interface for AssignmentGroup"""
    
    list_display = [
        'name', 'assignment_title', 'leader_name', 
        'member_count_display', 'is_active_badge'
    ]
    
    list_filter = ['is_active', 'assignment__subject', 'assignment__classroom']
    search_fields = ['name', 'description', 'assignment__title']
    readonly_fields = ['member_count']
    autocomplete_fields = ['assignment', 'leader']
    
    # FIXED: Removed filter_horizontal for 'members' since it's a ManyToManyField through GroupMembership
    # and added inline instead
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'assignment', 'leader', 'description')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [GroupMembershipInline]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(member_count=Count('members'))
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = _('Assignment')
    assignment_title.admin_order_field = 'assignment__title'
    
    def leader_name(self, obj):
        return obj.leader.get_full_name()
    leader_name.short_description = _('Leader')
    leader_name.admin_order_field = 'leader__first_name'
    
    def member_count_display(self, obj):
        total = obj.member_count
        return format_html(
            '<span style="font-weight: bold;">{}</span> '
            '<small style="color: #666;">members</small>',
            total
        )
    member_count_display.short_description = _('Members')
    member_count_display.admin_order_field = 'member_count'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Inactive</span>'
        )
    is_active_badge.short_description = _('Status')


@admin.register(GroupMembership)
class GroupMembershipAdmin(BaseAdmin):
    """Admin interface for GroupMembership"""
    
    list_display = ['group_name', 'student_name', 'role_badge', 'joined_at']
    list_filter = ['role', 'group__assignment', 'group']
    search_fields = ['group__name', 'student__first_name', 'student__last_name']
    autocomplete_fields = ['group', 'student']
    
    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = _('Group')
    group_name.admin_order_field = 'group__name'
    
    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = _('Student')
    student_name.admin_order_field = 'student__first_name'
    
    def role_badge(self, obj):
        role_colors = {
            'member': '#6c757d',
            'secretary': '#17a2b8',
            'treasurer': '#28a745'
        }
        
        color = role_colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'background-color: {}; color: white; border-radius: 10px; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = _('Role')


@admin.register(AssignmentComment)
class AssignmentCommentAdmin(BaseAdmin):
    """Admin interface for AssignmentComment"""
    
    list_display = [
        'author_name', 'assignment_title', 'content_preview',
        'is_private_badge', 'created_at_display'
    ]
    
    list_filter = ['is_private', 'assignment__subject', 'created_at']
    search_fields = [
        'author__first_name', 'author__last_name',
        'content', 'assignment__title'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['assignment', 'student_assignment', 'author', 'parent_comment']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('assignment', 'student_assignment', 'author')
        }),
        (_('Comment Content'), {
            'fields': ('content', 'attachments', 'is_private', 'parent_comment')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def author_name(self, obj):
        return obj.author.get_full_name()
    author_name.short_description = _('Author')
    author_name.admin_order_field = 'author__first_name'
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = _('Assignment')
    assignment_title.admin_order_field = 'assignment__title'
    
    def content_preview(self, obj):
        preview = obj.content[:100]
        if len(obj.content) > 100:
            preview += '...'
        return preview
    content_preview.short_description = _('Comment')
    
    def is_private_badge(self, obj):
        if obj.is_private:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🔒 Private</span>'
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">👥 Public</span>'
        )
    is_private_badge.short_description = _('Privacy')
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = _('Created')
    created_at_display.admin_order_field = 'created_at'


@admin.register(AssignmentAnalytics)
class AssignmentAnalyticsAdmin(BaseAdmin):
    """Admin interface for AssignmentAnalytics"""
    
    list_display = [
        'assignment_title', 'analytics_type_display',
        'period_range', 'generated_at_display'
    ]
    
    list_filter = ['analytics_type', 'generated_at']
    search_fields = ['assignment__title', 'analytics_type']
    readonly_fields = ['generated_at', 'created_at', 'updated_at']
    autocomplete_fields = ['assignment']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('assignment', 'analytics_type')
        }),
        (_('Analytics Data'), {
            'fields': ('data',),
            'classes': ('wide',)
        }),
        (_('Period'), {
            'fields': ('period_start', 'period_end')
        }),
        (_('Timestamps'), {
            'fields': ('generated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = _('Assignment')
    assignment_title.admin_order_field = 'assignment__title'
    
    def analytics_type_display(self, obj):
        type_display = dict(AssignmentAnalytics._meta.get_field('analytics_type').choices)
        return type_display.get(obj.analytics_type, obj.analytics_type)
    analytics_type_display.short_description = _('Analytics Type')
    
    def period_range(self, obj):
        return format_html(
            '{}<br><small style="color: #666;">to {}</small>',
            obj.period_start.strftime('%Y-%m-%d'),
            obj.period_end.strftime('%Y-%m-%d')
        )
    period_range.short_description = _('Period')
    
    def generated_at_display(self, obj):
        return obj.generated_at.strftime('%Y-%m-%d %H:%M')
    generated_at_display.short_description = _('Generated')
    generated_at_display.admin_order_field = 'generated_at'


@admin.register(AssignmentReminder)
class AssignmentReminderAdmin(BaseAdmin):
    """Admin interface for AssignmentReminder"""
    
    list_display = [
        'assignment_title', 'reminder_type_badge',
        'recipient_display', 'scheduled_for_display',
        'status_badge', 'delivery_method_display'
    ]
    
    list_filter = [
        'reminder_type', 'is_sent', 'delivery_method',
        'scheduled_for', 'sent_at'
    ]
    
    search_fields = [
        'assignment__title', 'message',
        'student__first_name', 'student__last_name',
        'classroom__name'
    ]
    
    readonly_fields = ['sent_at', 'is_sent', 'created_at', 'updated_at']
    autocomplete_fields = ['assignment', 'student', 'classroom', 'sent_by']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('assignment', 'reminder_type', 'message')
        }),
        (_('Recipient'), {
            'fields': ('student', 'classroom'),
            'description': _('Specify either a student or a classroom')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_for', 'delivery_method')
        }),
        (_('Status'), {
            'fields': ('is_sent', 'sent_at', 'sent_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        if 'send_reminders' not in actions:
            actions['send_reminders'] = (
                self.send_reminders,
                'send_reminders',
                _('Send selected reminders')
            )
        if 'mark_as_sent' not in actions:
            actions['mark_as_sent'] = (
                self.mark_as_sent,
                'mark_as_sent',
                _('Mark as sent')
            )
        
        return actions
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = _('Assignment')
    assignment_title.admin_order_field = 'assignment__title'
    
    def reminder_type_badge(self, obj):
        type_colors = {
            'submission': '#007bff',
            'grading': '#28a745',
            'upcoming': '#ffc107',
            'overdue': '#dc3545'
        }
        
        color = type_colors.get(obj.reminder_type, '#6c757d')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'background-color: {}; color: white; border-radius: 10px; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_reminder_type_display()
        )
    reminder_type_badge.short_description = _('Type')
    
    def recipient_display(self, obj):
        if obj.student:
            return obj.student.get_full_name()
        elif obj.classroom:
            return format_html(
                '{}<br><small style="color: #666;">Classroom</small>',
                obj.classroom.name
            )
        return '-'
    recipient_display.short_description = _('Recipient')
    
    def scheduled_for_display(self, obj):
        now = timezone.now()
        if obj.scheduled_for < now and not obj.is_sent:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} ⚠️ Overdue</span>',
                obj.scheduled_for.strftime('%Y-%m-%d %H:%M')
            )
        return obj.scheduled_for.strftime('%Y-%m-%d %H:%M')
    scheduled_for_display.short_description = _('Scheduled For')
    scheduled_for_display.admin_order_field = 'scheduled_for'
    
    def status_badge(self, obj):
        if obj.is_sent:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Sent</span>'
            )
        elif obj.scheduled_for < timezone.now():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ Overdue</span>'
            )
        else:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">⏰ Pending</span>'
            )
    status_badge.short_description = _('Status')
    
    def delivery_method_display(self, obj):
        method_icons = {
            'email': '📧',
            'sms': '📱',
            'push': '🔔',
            'in_app': '📲'
        }
        
        icon = method_icons.get(obj.delivery_method, '📧')
        return format_html(
            '{} {}',
            icon, obj.get_delivery_method_display()
        )
    delivery_method_display.short_description = _('Method')
    
    # Custom actions
    
    def send_reminders(self, request, queryset):
        """Send selected reminders"""
        sent_count = 0
        for reminder in queryset:
            if not reminder.is_sent:
                # In a real application, you would implement actual sending logic here
                reminder.mark_as_sent()
                reminder.sent_by = request.user
                reminder.save()
                sent_count += 1
        
        self.message_user(
            request,
            _('{} reminders sent successfully.').format(sent_count)
        )
    send_reminders.short_description = _('Send selected reminders')
    
    def mark_as_sent(self, request, queryset):
        """Mark reminders as sent without actually sending"""
        updated = queryset.update(
            is_sent=True,
            sent_at=timezone.now(),
            sent_by=request.user
        )
        self.message_user(
            request,
            _('{} reminders marked as sent.').format(updated)
        )
    mark_as_sent.short_description = _('Mark as sent')


# Customize admin site header
admin.site.site_header = _('Delvok Academy - Assignments Management')
admin.site.site_title = _('Assignments Admin')
admin.site.index_title = _('Assignment Management Dashboard')