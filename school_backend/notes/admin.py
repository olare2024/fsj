"""
Enhanced Django Admin Configuration for Notes and Learning Content Management System
Features:
1. Custom admin interfaces for all models
2. Advanced filtering, search, and export options
3. Bulk actions for content management
4. Progress tracking views
5. Analytics dashboards
6. Content publishing workflow
FIXED VERSION with all issues resolved
"""

from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.db import transaction
from import_export.admin import ImportExportModelAdmin
from import_export import resources
import csv
import json
from datetime import timedelta

from .models import (
    ContentCategory, ContentTag, LearningContent,
    TextContent, VideoContent, AudioContent, PDFContent,
    PresentationContent, InteractiveContent, QuizContent,
    AssignmentContent, LinkContent, FileContent,
    LearningModule, ModuleContent, Enrollment,
    EnrollmentProgress, ContentProgress, Question,
    QuestionChoice, QuizAttempt, QuizAnswer,
    ContentNote, ContentAnnotation, ContentRating,
    ContentReview, ContentAnalytics, ModuleAnalytics
)


# ==================== RESOURCE CLASSES FOR IMPORT/EXPORT ====================
class ContentCategoryResource(resources.ModelResource):
    class Meta:
        model = ContentCategory
        fields = ('id', 'name', 'slug', 'description', 'parent', 'icon', 'color', 'order', 'curriculum')
        export_order = fields


class LearningContentResource(resources.ModelResource):
    class Meta:
        model = LearningContent
        fields = (
            'id', 'title', 'slug', 'content_type', 'status', 'difficulty_level',
            'subject', 'grade_level', 'curriculum',
            'estimated_duration', 'views_count', 'average_rating'
        )
        export_order = fields


class LearningModuleResource(resources.ModelResource):
    class Meta:
        model = LearningModule
        fields = ('id', 'name', 'slug', 'description', 'subject', 'grade_level', 
                 'curriculum', 'content_count', 'enrollments_count', 'completion_rate')
        export_order = fields


# ==================== ADMIN ACTION MIXINS ====================
class PublishActionMixin:
    """Mixin for publish/unpublish actions"""
    
    @admin.action(description="📤 Publish selected items")
    def publish_selected(self, request, queryset):
        updated = queryset.update(status='published', publish_date=timezone.now())
        self.message_user(
            request,
            f"✅ Successfully published {updated} items.",
            messages.SUCCESS
        )
    
    @admin.action(description="📥 Unpublish selected items")
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(status='draft', publish_date=None)
        self.message_user(
            request,
            f"📥 Successfully unpublished {updated} items.",
            messages.WARNING
        )
    
    @admin.action(description="🗄️ Archive selected items")
    def archive_selected(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(
            request,
            f"🗄️ Successfully archived {updated} items.",
            messages.INFO
        )
    
    # Define actions as a property to avoid tuple/list concatenation issues
    @property
    def publish_actions(self):
        return ['publish_selected', 'unpublish_selected', 'archive_selected']


class ExportActionMixin:
    """Mixin for export actions"""
    
    @admin.action(description="📊 Export selected as CSV")
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        
        return response
    
    @admin.action(description="📁 Export selected as JSON")
    def export_as_json(self, request, queryset):
        data = list(queryset.values())
        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename={self.model._meta.verbose_name_plural}.json'
        return response
    
    # Define actions as a property
    @property
    def export_actions(self):
        return ['export_as_csv', 'export_as_json']


# ==================== INLINE ADMINS ====================
class ModuleContentInline(admin.TabularInline):
    """Inline for module contents"""
    model = ModuleContent
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['content']
    fields = ['content', 'order', 'is_required', 'unlock_after_previous']
    readonly_fields = ['get_content_type']
    
    def get_content_type(self, obj):
        if obj.content:
            return obj.content.get_content_type_display()
        return '-'
    get_content_type.short_description = 'Content Type'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    ordering = ['order']
    fields = ['text', 'question_type', 'points', 'difficulty']


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    can_delete = False

    readonly_fields = [
        'question_display',
        'choice_display',
        'answer_text',
        'is_correct',
        'points_earned'
    ]

    fields = readonly_fields

    def question_display(self, obj):
        return obj.question
    question_display.short_description = "Question"

    def choice_display(self, obj):
        return obj.choice
    choice_display.short_description = "Selected Choice"

    def has_add_permission(self, request, obj=None):
        return False




# ==================== BASE ADMIN CLASS ====================
class BaseNotesAdmin(admin.ModelAdmin):
    """Base admin class for all notes models"""
    
    def save_model(self, request, obj, form, change):
        if not change and hasattr(obj, 'created_by'):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and hasattr(obj, 'created_at'):
            readonly_fields.extend(['created_by', 'created_at', 'updated_at'])
        return readonly_fields
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter by created_by for non-superusers
            if hasattr(self.model, 'created_by'):
                qs = qs.filter(created_by=request.user)
        return qs


# ==================== CONTENT CATEGORY ADMIN ====================
@admin.register(ContentCategory)
class ContentCategoryAdmin(ImportExportModelAdmin, BaseNotesAdmin):
    """Admin for content categories"""
    resource_class = ContentCategoryResource
    list_display = ('name', 'parent', 'content_count', 'curriculum', 'order', 'is_active')
    list_filter = ('parent', 'curriculum', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ['name']}
    autocomplete_fields = ['parent']
    ordering = ['order', 'name']
    actions = ['activate_selected', 'deactivate_selected']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Display', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Curriculum Alignment', {
            'fields': ('curriculum',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    @admin.display(description='📊 Content Count')
    def content_count(self, obj):
        return obj.contents.count()
    
    @admin.action(description="✅ Activate selected categories")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ Activated {updated} categories.", messages.SUCCESS)
    
    @admin.action(description="⛔ Deactivate selected categories")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"⛔ Deactivated {updated} categories.", messages.WARNING)


# ==================== CONTENT TAG ADMIN ====================
@admin.register(ContentTag)
class ContentTagAdmin(BaseNotesAdmin):
    """Admin for content tags"""
    list_display = ('name', 'slug', 'usage_count', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ['name']}
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Usage', {
            'fields': ('usage_count',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    readonly_fields = ('usage_count', 'created_by', 'created_at', 'updated_at')


# ==================== GENERIC CONTENT ADMIN ====================
class LearningContentBaseAdmin(ImportExportModelAdmin, PublishActionMixin, ExportActionMixin, BaseNotesAdmin):
    """Base admin for learning content with mixins"""
    
    def get_actions(self, request):
        # Combine actions from all mixins
        actions = super().get_actions(request)
        
        # Add publish actions
        if hasattr(self, 'publish_actions'):
            for action_name in self.publish_actions:
                if hasattr(self, action_name):
                    actions[action_name] = (
                        getattr(self, action_name),
                        action_name,
                        getattr(getattr(self, action_name), 'short_description', action_name)
                    )
        
        # Add export actions
        if hasattr(self, 'export_actions'):
            for action_name in self.export_actions:
                if hasattr(self, action_name):
                    actions[action_name] = (
                        getattr(self, action_name),
                        action_name,
                        getattr(getattr(self, action_name), 'short_description', action_name)
                    )
        
        return actions


@admin.register(LearningContent)
class LearningContentAdmin(LearningContentBaseAdmin):
    """Base admin for learning content - REQUIRED for autocomplete_fields"""
    resource_class = LearningContentResource
    list_display = ('title', 'content_type', 'status_badge', 'subject', 'difficulty', 
                   'views_count', 'rating_stars', 'created_by', 'is_active')
    list_filter = ('content_type', 'status', 'difficulty_level', 'curriculum', 
                  'subject', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'slug', 'learning_objectives')
    prepopulated_fields = {'slug': ['title']}
    autocomplete_fields = ['subject', 'categories', 'tags', 'allowed_users', 'reviewed_by', 'parent_version']
    readonly_fields = ('views_count', 'average_rating', 'completion_count', 
                      'created_by', 'created_at', 'updated_at', 'last_accessed')
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    # Hide from admin index but keep accessible for autocomplete
    def get_model_perms(self, request):
        return {}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content_type', 'status')
        }),
        ('Academic Context', {
            'fields': ('subject', 'grade_level', 'curriculum', 'difficulty_level')
        }),
        ('Content Details', {
            'fields': ('estimated_duration', 'learning_objectives', 
                      'learning_outcomes', 'prerequisites')
        }),
        ('Organization', {
            'fields': ('categories', 'tags')
        }),
        ('Timing', {
            'fields': ('publish_date', 'expiry_date')
        }),
        ('Access Control', {
            'fields': ('is_public', 'access_level', 'allowed_users', 
                      'password_protected', 'access_password')
        }),
        ('Resources & References', {
            'fields': ('resources', 'references')
        }),
        ('Versioning', {
            'fields': ('version', 'parent_version')
        }),
        ('Review Process', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Analytics', {
            'fields': ('views_count', 'average_rating', 'completion_count', 
                      'average_completion_time', 'last_accessed')
        }),
        ('SEO & Metadata', {
            'fields': ('meta_title', 'meta_description', 'keywords')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    @admin.display(description='📊 Status')
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'review': 'orange',
            'published': 'green',
            'archived': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.display(description='⭐ Rating')
    def rating_stars(self, obj):
        if obj.average_rating:
            stars = '★' * int(obj.average_rating)
            return format_html(
                '<span style="color: #f5c518;">{}</span> <small>({:.1f})</small>',
                stars, obj.average_rating
            )
        return '-'
    
    @admin.display(description='📈 Difficulty')
    def difficulty(self, obj):
        colors = {
            'beginner': 'green',
            'intermediate': 'blue',
            'advanced': 'orange',
            'expert': 'red'
        }
        color = colors.get(obj.difficulty_level, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_difficulty_level_display()
        )


# ==================== SPECIFIC CONTENT TYPE ADMINS ====================
# All inherit from LearningContentBaseAdmin but show in admin

class SpecificContentAdmin(LearningContentBaseAdmin):
    """Base class for specific content types that should appear in admin"""
    
    def get_model_perms(self, request):
        # Show in admin index
        return super(BaseNotesAdmin, self).get_model_perms(request)


@admin.register(TextContent)
class TextContentAdmin(SpecificContentAdmin):
    """Admin for text content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Text Content', {
            'fields': ('content', 'format', 'word_count')
        }),
    )
    readonly_fields = LearningContentAdmin.readonly_fields + ('word_count',)


@admin.register(VideoContent)
class VideoContentAdmin(SpecificContentAdmin):
    """Admin for video content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Video Content', {
            'fields': ('video_url', 'video_file', 'thumbnail', 
                      'duration_seconds', 'transcript', 'captions_url', 'quality_options')
        }),
    )


@admin.register(AudioContent)
class AudioContentAdmin(SpecificContentAdmin):
    """Admin for audio content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Audio Content', {
            'fields': ('audio_file', 'duration_seconds', 'transcript', 'bitrate')
        }),
    )


@admin.register(PDFContent)
class PDFContentAdmin(SpecificContentAdmin):
    """Admin for PDF content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('PDF Content', {
            'fields': ('pdf_file', 'page_count', 'file_size', 
                      'allow_printing', 'allow_download')
        }),
    )


@admin.register(PresentationContent)
class PresentationContentAdmin(SpecificContentAdmin):
    """Admin for presentation content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Presentation Content', {
            'fields': ('presentation_file', 'slide_count', 'speaker_notes')
        }),
    )


@admin.register(InteractiveContent)
class InteractiveContentAdmin(SpecificContentAdmin):
    """Admin for interactive content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Interactive Content', {
            'fields': ('interactive_type', 'interactive_file', 'embed_code', 'parameters')
        }),
    )


@admin.register(QuizContent)
class QuizContentAdmin(SpecificContentAdmin):
    """Admin for quiz content"""
    inlines = [QuestionInline]
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Quiz Configuration', {
            'fields': ('total_questions', 'passing_score', 'time_limit', 
                      'shuffle_questions', 'show_results')
        }),
    )


@admin.register(AssignmentContent)
class AssignmentContentAdmin(SpecificContentAdmin):
    """Admin for assignment content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Assignment Configuration', {
            'fields': ('due_date', 'max_score', 'submission_type', 
                      'allowed_file_types', 'max_file_size')
        }),
    )


@admin.register(LinkContent)
class LinkContentAdmin(SpecificContentAdmin):
    """Admin for link content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('Link Content', {
            'fields': ('url', 'preview_image', 'open_in_new_tab')
        }),
    )


@admin.register(FileContent)
class FileContentAdmin(SpecificContentAdmin):
    """Admin for file content"""
    fieldsets = LearningContentAdmin.fieldsets + (
        ('File Content', {
            'fields': ('file', 'file_type', 'file_size')
        }),
    )


# ==================== LEARNING MODULE ADMIN ====================
@admin.register(LearningModule)
class LearningModuleAdmin(ImportExportModelAdmin, BaseNotesAdmin):
    """Admin for learning modules"""
    resource_class = LearningModuleResource
    list_display = ('name', 'subject', 'curriculum', 'content_count', 
                   'enrollments_count', 'completion_rate_badge', 'is_featured', 'is_active')
    list_filter = ('subject', 'curriculum', 'is_featured', 'is_public', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description', 'short_description')
    prepopulated_fields = {'slug': ['name']}
    autocomplete_fields = ['subject', 'categories', 'tags']
    readonly_fields = ('total_duration', 'content_count', 'enrollments_count', 
                      'completion_rate', 'average_rating', 'created_by')
    ordering = ['name']
    date_hierarchy = 'created_at'
    inlines = [ModuleContentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Academic Context', {
            'fields': ('subject', 'grade_level', 'curriculum')
        }),
        ('Organization', {
            'fields': ('categories', 'tags', 'cover_image')
        }),
        ('Module Configuration', {
            'fields': ('is_public', 'is_featured', 'is_sequential', 'completion_threshold')
        }),
        ('Statistics', {
            'fields': ('total_duration', 'content_count', 'enrollments_count', 
                      'completion_rate', 'average_rating')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    actions = ['feature_selected', 'unfeature_selected', 'update_statistics']
    
    @admin.display(description='📚 Content')
    def content_count(self, obj):
        return obj.contents.count()
    
    @admin.display(description='👥 Enrollments')
    def enrollments_count(self, obj):
        return obj.enrollments.count()
    
    @admin.display(description='📈 Completion Rate')
    def completion_rate_badge(self, obj):
        completion_rate = obj.completion_rate or 0
        if completion_rate > 80:
            color = 'green'
        elif completion_rate > 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}%</span>',
            color, completion_rate
        )
    
    @admin.action(description="⭐ Feature selected modules")
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"⭐ Featured {updated} modules.", messages.SUCCESS)
    
    @admin.action(description="⭐ Unfeature selected modules")
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"⭐ Unfeatured {updated} modules.", messages.WARNING)
    
    @admin.action(description="📊 Update statistics")
    def update_statistics(self, request, queryset):
        for module in queryset:
            module.update_statistics()
        self.message_user(request, f"📊 Updated statistics for {queryset.count()} modules.", messages.SUCCESS)


# ==================== MODULE CONTENT ADMIN ====================
@admin.register(ModuleContent)
class ModuleContentAdmin(BaseNotesAdmin):
    """Admin for module content relationships"""
    list_display = ('module', 'content', 'order', 'is_required', 'unlock_after_previous')
    list_filter = ('module', 'is_required', 'unlock_after_previous')
    search_fields = ('module__name', 'content__title')
    autocomplete_fields = ['module', 'content']
    ordering = ['module', 'order']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('module', 'content', 'order')
        }),
        ('Access Control', {
            'fields': ('is_required', 'unlock_after_previous')
        }),
    )


# ==================== QUESTION ADMIN ====================
@admin.register(Question)
class QuestionAdmin(BaseNotesAdmin):
    """Admin for questions"""
    list_display = ('content', 'question_type', 'text_preview', 'points', 'difficulty', 'order')
    list_filter = ('question_type', 'difficulty', 'content__content_type')
    search_fields = ('text', 'explanation', 'content__title')
    autocomplete_fields = ['content']
    ordering = ['content', 'order']
   
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('content', 'question_type', 'text', 'explanation')
        }),
        ('Scoring & Difficulty', {
            'fields': ('points', 'difficulty', 'order')
        }),
    )
    
    @admin.display(description='📝 Question')
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    
    @admin.display(description='📈 Difficulty')
    def difficulty(self, obj):
        colors = {
            'beginner': 'green',
            'intermediate': 'blue',
            'advanced': 'orange',
            'expert': 'red'
        }
        color = colors.get(obj.difficulty, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_difficulty_display()
        )


# ==================== QUESTION CHOICE ADMIN ====================
@admin.register(QuestionChoice)
class QuestionChoiceAdmin(BaseNotesAdmin):
    """Admin for question choices"""
    list_display = ('question', 'text_preview', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__content')
    search_fields = ('text', 'feedback', 'question__text')
    autocomplete_fields = ['question']
    ordering = ['question', 'order']
    
    fieldsets = (
        ('Choice Information', {
            'fields': ('question', 'text', 'is_correct', 'order', 'feedback')
        }),
    )
    
    @admin.display(description='📝 Choice')
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


# ==================== ENROLLMENT ADMIN ====================
@admin.register(Enrollment)
class EnrollmentAdmin(BaseNotesAdmin):
    """Admin for enrollments"""
    list_display = ('student', 'module', 'status_badge', 'enrolled_at', 
                   'progress_bar', 'completion_date', 'grade', 'score')
    list_filter = ('status', 'module', 'enrolled_at', 'completion_date')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'module__name')
    autocomplete_fields = ['student', 'module']
    readonly_fields = ('enrolled_at', 'created_by', 'created_at', 'updated_at')
    ordering = ['-enrolled_at']
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'module', 'status', 'enrolled_at')
        }),
        ('Completion Details', {
            'fields': ('completion_date', 'grade', 'score', 'certificate_issued', 'certificate_issued_at')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    @admin.display(description='📊 Status')
    def status_badge(self, obj):
        colors = {
            'active': 'blue',
            'completed': 'green',
            'dropped': 'red',
            'suspended': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.display(description='📈 Progress')
    def progress_bar(self, obj):
        try:
            progress = obj.progress.overall_progress
        except EnrollmentProgress.DoesNotExist:
            progress = 0
        
        color = 'green' if progress >= 80 else 'orange' if progress >= 50 else 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px; height: 20px;">'
            '<div style="width: {}%; background-color: {}; height: 100%; border-radius: 3px; '
            'color: white; text-align: center; font-size: 12px; line-height: 20px;">{}%</div>'
            '</div>',
            progress, color, progress
        )
    
    actions = ['complete_selected', 'activate_selected', 'issue_certificates']
    
    @admin.action(description="✅ Mark as completed")
    def complete_selected(self, request, queryset):
        updated = queryset.update(
            status='completed',
            completion_date=timezone.now()
        )
        self.message_user(request, f"✅ Marked {updated} enrollments as completed.", messages.SUCCESS)
    
    @admin.action(description="🔄 Activate selected")
    def activate_selected(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"🔄 Activated {updated} enrollments.", messages.SUCCESS)
    
    @admin.action(description="🏆 Issue certificates")
    def issue_certificates(self, request, queryset):
        completed = queryset.filter(status='completed', certificate_issued=False)
        updated = completed.update(
            certificate_issued=True,
            certificate_issued_at=timezone.now()
        )
        self.message_user(
            request, 
            f"🏆 Issued certificates for {updated} enrollments.", 
            messages.SUCCESS
        )


# ==================== ENROLLMENT PROGRESS ADMIN ====================
@admin.register(EnrollmentProgress)
class EnrollmentProgressAdmin(BaseNotesAdmin):
    """Admin for enrollment progress"""
    list_display = ('enrollment', 'overall_progress_bar', 'completed_content', 
                   'total_content', 'total_time_spent_formatted')
    search_fields = ('enrollment__student__email', 'enrollment__module__name')
    autocomplete_fields = ['enrollment']
    readonly_fields = ('overall_progress', 'completed_content', 'total_content', 
                      'total_time_spent', 'last_accessed', 'created_at', 'updated_at')
    
    @admin.display(description='📈 Progress')
    def overall_progress_bar(self, obj):
        color = 'green' if obj.overall_progress >= 80 else 'orange' if obj.overall_progress >= 50 else 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px; height: 20px;">'
            '<div style="width: {}%; background-color: {}; height: 100%; border-radius: 3px; '
            'color: white; text-align: center; font-size: 12px; line-height: 20px;">{}%</div>'
            '</div>',
            obj.overall_progress, color, obj.overall_progress
        )
    
    @admin.display(description='⏱️ Total Time')
    def total_time_spent_formatted(self, obj):
        if obj.total_time_spent < 60:
            return f"{obj.total_time_spent} min"
        else:
            hours = obj.total_time_spent // 60
            minutes = obj.total_time_spent % 60
            return f"{hours}h {minutes}m"


# ==================== CONTENT PROGRESS ADMIN ====================
@admin.register(ContentProgress)
class ContentProgressAdmin(BaseNotesAdmin):
    """Admin for content progress"""
    list_display = ('enrollment', 'content', 'status_badge', 'completion_percentage_bar', 
                   'started_at', 'completed_at', 'time_spent_formatted')
    list_filter = ('status', 'content__content_type')
    search_fields = ('enrollment__student__email', 'content__title')
    autocomplete_fields = ['enrollment', 'content']
    readonly_fields = ('started_at', 'completed_at', 'time_spent', 'completion_percentage', 
                      'score', 'attempts', 'last_position', 'created_at', 'updated_at')
    ordering = ['-updated_at']
    
    @admin.display(description='📊 Status')
    def status_badge(self, obj):
        colors = {
            'not_started': 'gray',
            'started': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'reviewed': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.display(description='📈 Progress')
    def completion_percentage_bar(self, obj):
        color = 'green' if obj.completion_percentage >= 100 else 'orange' if obj.completion_percentage >= 50 else 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px; height: 20px;">'
            '<div style="width: {}%; background-color: {}; height: 100%; border-radius: 3px; '
            'color: white; text-align: center; font-size: 12px; line-height: 20px;">{}%</div>'
            '</div>',
            obj.completion_percentage, color, obj.completion_percentage
        )
    
    @admin.display(description='⏱️ Time')
    def time_spent_formatted(self, obj):
        if obj.time_spent < 60:
            return f"{obj.time_spent}s"
        else:
            minutes = obj.time_spent // 60
            seconds = obj.time_spent % 60
            return f"{minutes}m {seconds}s"


# ==================== QUIZ ATTEMPT ADMIN ====================
@admin.register(QuizAttempt)
class QuizAttemptAdmin(BaseNotesAdmin):
    """Admin for quiz attempts"""
    list_display = ('student', 'content', 'started_at', 'completed_at', 
                   'score', 'percentage_badge', 'is_passed', 'time_taken_formatted')
    list_filter = ('is_passed', 'content__content_type', 'started_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'content__title')
    autocomplete_fields = ['student', 'content']
    readonly_fields = ('started_at', 'created_by', 'created_at', 'updated_at')
    ordering = ['-started_at']
    date_hierarchy = 'started_at'
    inlines = [QuizAnswerInline]
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('student', 'content', 'started_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('score', 'percentage', 'is_passed', 'time_taken')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    @admin.display(description='📊 Score %')
    def percentage_badge(self, obj):
        if obj.percentage is None:
            return '-'
        
        if obj.percentage >= 80:
            color = 'green'
        elif obj.percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}%</span>',
            color, obj.percentage
        )
    
    @admin.display(description='⏱️ Time')
    def time_taken_formatted(self, obj):
        if obj.time_taken < 60:
            return f"{obj.time_taken}s"
        else:
            minutes = obj.time_taken // 60
            seconds = obj.time_taken % 60
            return f"{minutes}m {seconds}s"
    
    actions = ['regrade_selected']
    
    @admin.action(description="📝 Regrade selected attempts")
    def regrade_selected(self, request, queryset):
        for attempt in queryset:
            attempt.calculate_score()
        self.message_user(request, f"📝 Regraded {queryset.count()} attempts.", messages.SUCCESS)


# ==================== QUIZ ANSWER ADMIN ====================
@admin.register(QuizAnswer)
class QuizAnswerAdmin(BaseNotesAdmin):
    """Admin for quiz answers"""
    list_display = ('attempt', 'question_preview', 'is_correct', 'points_earned')
    list_filter = ('is_correct', 'attempt__content')
    search_fields = ('question__text', 'attempt__student__email')
    autocomplete_fields = ['attempt', 'question', 'selected_choices']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']
    
    @admin.display(description='❓ Question')
    def question_preview(self, obj):
        if obj.question:
            return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
        return 'N/A'
    
    def has_add_permission(self, request):
        return False


# ==================== CONTENT NOTE ADMIN ====================
@admin.register(ContentNote)
class ContentNoteAdmin(BaseNotesAdmin):
    """Admin for content notes"""
    list_display = ('student', 'content', 'title', 'created_at', 'is_public', 'is_active')
    list_filter = ('is_public', 'is_active', 'created_at')
    search_fields = ('student__email', 'content__title', 'title', 'note')
    autocomplete_fields = ['student', 'content']
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Note Information', {
            'fields': ('student', 'content', 'title', 'note')
        }),
        ('Location', {
            'fields': ('page_number', 'position')
        }),
        ('Visibility', {
            'fields': ('is_public',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )


# ==================== CONTENT ANNOTATION ADMIN ====================
@admin.register(ContentAnnotation)
class ContentAnnotationAdmin(BaseNotesAdmin):
    """Admin for content annotations"""
    list_display = ('student', 'content', 'annotation_type', 'created_at', 'is_active')
    list_filter = ('annotation_type', 'created_at')
    search_fields = ('student__email', 'content__title', 'text')
    autocomplete_fields = ['student', 'content']
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Annotation Information', {
            'fields': ('student', 'content', 'annotation_type', 'text')
        }),
        ('Location', {
            'fields': ('position', 'color')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )


# ==================== CONTENT RATING ADMIN ====================
@admin.register(ContentRating)
class ContentRatingAdmin(BaseNotesAdmin):
    """Admin for content ratings"""
    list_display = ('user', 'content', 'rating_stars', 'created_at', 'is_active')
    list_filter = ('rating', 'content__content_type', 'created_at')
    search_fields = ('user__email', 'content__title', 'comment')
    autocomplete_fields = ['user', 'content']
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'content', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    @admin.display(description='⭐ Rating')
    def rating_stars(self, obj):
        stars = '★' * obj.rating
        return format_html(
            '<span style="color: #f5c518; font-size: 16px;">{}</span>',
            stars
        )


# ==================== CONTENT REVIEW ADMIN ====================
@admin.register(ContentReview)
class ContentReviewAdmin(BaseNotesAdmin):
    """Admin for content reviews"""
    list_display = ('user', 'content', 'title', 'helpful_votes', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__email', 'content__title', 'title', 'review')
    autocomplete_fields = ['user', 'content']
    readonly_fields = ('helpful_votes', 'created_by', 'created_at', 'updated_at')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'content', 'title', 'review')
        }),
        ('Approval', {
            'fields': ('is_approved', 'helpful_votes')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    @admin.action(description="✅ Approve selected reviews")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"✅ Approved {updated} reviews.", messages.SUCCESS)
    
    @admin.action(description="⛔ Disapprove selected reviews")
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"⛔ Disapproved {updated} reviews.", messages.WARNING)


# ==================== ANALYTICS ADMINS ====================
@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(BaseNotesAdmin):
    """Admin for content analytics"""
    list_display = ('content', 'total_views', 'unique_viewers', 
                   'completion_rate_badge', 'average_time_spent_formatted')
    list_filter = ('content__content_type', 'content__subject')
    search_fields = ('content__title',)
    autocomplete_fields = ['content']
    readonly_fields = ('total_views', 'unique_viewers', 'completion_rate', 
                      'average_time_spent', 'popular_times', 'drop_off_points',
                      'created_at', 'updated_at')
    ordering = ['-total_views']
    
    @admin.display(description='📊 Completion Rate')
    def completion_rate_badge(self, obj):
        completion_rate = obj.completion_rate or 0
        if completion_rate > 80:
            color = 'green'
        elif completion_rate > 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}%</span>',
            color, completion_rate
        )
    
    @admin.display(description='⏱️ Avg Time')
    def average_time_spent_formatted(self, obj):
        avg_time = obj.average_time_spent or 0
        if avg_time < 60:
            return f"{avg_time}s"
        else:
            minutes = avg_time // 60
            seconds = avg_time % 60
            return f"{minutes}m {seconds}s"


@admin.register(ModuleAnalytics)
class ModuleAnalyticsAdmin(BaseNotesAdmin):
    """Admin for module analytics"""
    list_display = ('module', 'total_enrollments', 'active_enrollments', 
                   'completion_rate_badge', 'average_grade')
    search_fields = ('module__name',)
    autocomplete_fields = ['module']
    readonly_fields = ('total_enrollments', 'active_enrollments', 'completion_rate', 
                      'average_grade', 'popular_content', 'created_at', 'updated_at')
    ordering = ['-total_enrollments']
    
    @admin.display(description='📊 Completion Rate')
    def completion_rate_badge(self, obj):
        completion_rate = obj.completion_rate or 0
        if completion_rate > 80:
            color = 'green'
        elif completion_rate > 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}%</span>',
            color, completion_rate
        )


# ==================== ADMIN SITE CONFIGURATION ====================
# Customize the default admin site
admin.site.site_header = "Delvok Academy - Learning Content Management"
admin.site.site_title = "Notes & Content Admin"
admin.site.index_title = "Learning Content Dashboard"

# Unregister Group if not needed
admin.site.unregister(Group)