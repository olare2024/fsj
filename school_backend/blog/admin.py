# blog/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.text import Truncator
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django_object_actions import DjangoObjectActions

from .models import (
    BlogCategory, BlogPost, BlogComment, DiscussionThread, 
    DiscussionPost, StudyGroup, StudyGroupMembership, 
    PostLike, DiscussionVote, BlogNotification
)


class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin interface for BlogCategory model"""
    list_display = [
        'name', 'slug', 'parent', 'curriculum', 'education_level', 
        'post_count', 'discussion_count', 'is_active', 'order'
    ]
    list_filter = [
        'curriculum', 'education_level', 'is_active', 
        'accessible_to_students', 'accessible_to_teachers', 'accessible_to_parents'
    ]
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['post_count', 'discussion_count', 'created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'name', 'slug', 'description', 'parent', 'order',
                'color', 'icon'
            ]
        }),
        ('Access Control', {
            'fields': [
                'accessible_to_students', 'accessible_to_teachers', 'accessible_to_parents',
                'min_grade_level', 'max_grade_level'
            ]
        }),
        ('Curriculum Settings', {
            'fields': [
                'curriculum', 'education_level'
            ]
        }),
        ('Status', {
            'fields': [
                'is_active', 'created_at', 'updated_at'
            ]
        })
    ]
    actions = ['activate_categories', 'deactivate_categories']

    def post_count(self, obj):
        return obj.posts.filter(status='published').count()
    post_count.short_description = 'Published Posts'

    def discussion_count(self, obj):
        return obj.discussions.filter(is_active=True).count()
    discussion_count.short_description = 'Active Discussions'

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated successfully.')
    activate_categories.short_description = "Activate selected categories"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated successfully.')
    deactivate_categories.short_description = "Deactivate selected categories"


class BlogPostAdmin(DjangoObjectActions, admin.ModelAdmin):
    """Admin interface for BlogPost model"""
    list_display = [
        'title', 'author', 'category', 'content_type', 'status', 
        'published_date', 'views_count', 'likes_count', 'comments_count',
        'content_quality_score', 'is_featured_display', 'kicd_aligned'
    ]
    list_filter = [
        'status', 'content_type', 'category', 'curriculum', 
        'audience', 'kicd_aligned', 'competency_based', 'exam_related',
        'requires_approval', 'created_at'
    ]
    search_fields = ['title', 'content', 'excerpt', 'author__first_name', 'author__last_name']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = [
        'views_count', 'likes_count', 'comments_count', 'shares_count',
        'content_quality_score', 'created_at', 'updated_at', 
        'published_date', 'archive_date', 'approved_at'
    ]
    date_hierarchy = 'published_date'
    filter_horizontal = ['co_authors']
    raw_id_fields = ['author', 'approved_by', 'specific_class', 'subject']
    
    fieldsets = [
        ('Basic Content', {
            'fields': [
                'title', 'slug', 'content', 'excerpt', 'featured_image', 'image_caption'
            ]
        }),
        ('Categorization', {
            'fields': [
                'category', 'content_type', 'tags', 'reading_level'
            ]
        }),
        ('Authorship', {
            'fields': [
                'author', 'co_authors'
            ]
        }),
        ('Audience Targeting', {
            'fields': [
                'audience', 'specific_class', 'subject', 'curriculum', 'target_grade_level'
            ]
        }),
        ('Publishing', {
            'fields': [
                'status', 'published_date', 'scheduled_date', 'archive_date'
            ]
        }),
        ('SEO & Metadata', {
            'fields': [
                'meta_title', 'meta_description', 'keywords', 'canonical_url'
            ]
        }),
        ('Kenya Education Context', {
            'fields': [
                'kicd_aligned', 'competency_based', 'exam_related', 'learning_outcomes'
            ]
        }),
        ('Moderation', {
            'fields': [
                'requires_approval', 'approved_by', 'approved_at', 'review_notes'
            ]
        }),
        ('Engagement Metrics', {
            'fields': [
                'views_count', 'likes_count', 'comments_count', 'shares_count',
                'average_rating', 'content_quality_score'
            ]
        }),
        ('Attachments', {
            'fields': [
                'attachments'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at', 'updated_at'
            ]
        })
    ]

    actions = [
        'publish_posts', 'archive_posts', 'mark_as_draft', 
        'approve_posts', 'reject_posts', 'improve_content_quality'
    ]

    def is_featured_display(self, obj):
        return obj.is_featured
    is_featured_display.short_description = 'Featured'
    is_featured_display.boolean = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see their own posts
            qs = qs.filter(author=request.user)
        return qs

    def publish_posts(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} posts published successfully.')
    publish_posts.short_description = "Publish selected posts"

    def archive_posts(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} posts archived successfully.')
    archive_posts.short_description = "Archive selected posts"

    def mark_as_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts marked as draft.')
    mark_as_draft.short_description = "Mark selected posts as draft"

    def approve_posts(self, request, queryset):
        updated = queryset.update(
            requires_approval=False,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} posts approved successfully.')
    approve_posts.short_description = "Approve selected posts"

    def reject_posts(self, request, queryset):
        for post in queryset:
            post.requires_approval = True
            post.review_notes = "Post rejected by administrator."
            post.save()
        self.message_user(request, f'{queryset.count()} posts rejected.')
    reject_posts.short_description = "Reject selected posts"

    def improve_content_quality(self, request, queryset):
        for post in queryset:
            post.calculate_content_quality()
            post.save()
        self.message_user(request, f'Content quality scores updated for {queryset.count()} posts.')
    improve_content_quality.short_description = "Update content quality scores"

    @admin.action(description="Preview post")
    def preview_post(self, request, obj):
        """Preview the blog post"""
        return HttpResponseRedirect(reverse('blog:post_detail', kwargs={'slug': obj.slug}))

    @admin.action(description="View engagement analytics")
    def view_analytics(self, request, obj):
        """View detailed engagement analytics"""
        # This would redirect to a custom analytics view
        return HttpResponseRedirect(reverse('admin:blog_blogpost_analytics', args=[obj.pk]))

    change_actions = ['preview_post', 'view_analytics']


class BlogCommentAdmin(admin.ModelAdmin):
    """Admin interface for BlogComment model"""
    list_display = [
        'truncated_content', 'author', 'post', 'is_approved', 
        'likes_count', 'report_count', 'is_edited', 'created_at'
    ]
    list_filter = [
        'is_approved', 'user_role', 'created_at', 'post__category'
    ]
    search_fields = [
        'content', 'author__first_name', 'author__last_name', 
        'post__title'
    ]
    readonly_fields = [
        'likes_count', 'report_count', 'created_at', 'updated_at',
        'edited_at', 'last_edited_by', 'user_role', 'user_grade_level'
    ]
    raw_id_fields = ['author', 'post', 'parent', 'approved_by', 'last_edited_by']
    actions = ['approve_comments', 'reject_comments', 'mark_as_edited']

    def truncated_content(self, obj):
        return Truncator(obj.content).chars(50)
    truncated_content.short_description = 'Comment'

    def is_edited(self, obj):
        return obj.is_edited
    is_edited.short_description = 'Edited'
    is_edited.boolean = True

    def approve_comments(self, request, queryset):
        updated = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} comments approved successfully.')
    approve_comments.short_description = "Approve selected comments"

    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments rejected.')
    reject_comments.short_description = "Reject selected comments"

    def mark_as_edited(self, request, queryset):
        for comment in queryset:
            comment.mark_as_edited(request.user)
        self.message_user(request, f'{queryset.count()} comments marked as edited.')
    mark_as_edited.short_description = "Mark selected comments as edited"


class DiscussionThreadAdmin(admin.ModelAdmin):
    """Admin interface for DiscussionThread model"""
    list_display = [
        'title', 'created_by', 'discussion_type', 'category', 
        'privacy_level', 'reply_count', 'participant_count', 
        'views_count', 'is_pinned', 'is_locked', 'is_active_display',
        'last_activity'
    ]
    list_filter = [
        'discussion_type', 'privacy_level', 'category', 'curriculum',
        'is_pinned', 'is_locked', 'is_featured', 'exam_related',
        'created_at'
    ]
    search_fields = [
        'title', 'description', 'created_by__first_name', 
        'created_by__last_name', 'kicd_topic'
    ]
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = [
        'views_count', 'reply_count', 'participant_count', 
        'last_activity', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['moderators', 'invited_users']
    raw_id_fields = ['created_by', 'category', 'subject', 'classroom']
    
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'title', 'slug', 'description'
            ]
        }),
        ('Categorization', {
            'fields': [
                'category', 'discussion_type', 'subject', 'classroom', 'curriculum'
            ]
        }),
        ('Moderation & Access', {
            'fields': [
                'created_by', 'moderators', 'privacy_level', 'allowed_roles', 'invited_users'
            ]
        }),
        ('Status & Settings', {
            'fields': [
                'is_pinned', 'is_locked', 'is_anonymous', 'is_featured'
            ]
        }),
        ('Kenya Education Context', {
            'fields': [
                'exam_related', 'grade_level', 'kicd_topic'
            ]
        }),
        ('Engagement Metrics', {
            'fields': [
                'views_count', 'reply_count', 'participant_count', 'last_activity'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at', 'updated_at'
            ]
        })
    ]

    actions = [
        'pin_discussions', 'unpin_discussions', 'lock_discussions', 
        'unlock_discussions', 'feature_discussions', 'unfeature_discussions'
    ]

    def is_active_display(self, obj):
        return obj.is_active
    is_active_display.short_description = 'Active'
    is_active_display.boolean = True

    def pin_discussions(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} discussions pinned.')
    pin_discussions.short_description = "Pin selected discussions"

    def unpin_discussions(self, request, queryset):
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} discussions unpinned.')
    unpin_discussions.short_description = "Unpin selected discussions"

    def lock_discussions(self, request, queryset):
        updated = queryset.update(is_locked=True)
        self.message_user(request, f'{updated} discussions locked.')
    lock_discussions.short_description = "Lock selected discussions"

    def unlock_discussions(self, request, queryset):
        updated = queryset.update(is_locked=False)
        self.message_user(request, f'{updated} discussions unlocked.')
    unlock_discussions.short_description = "Unlock selected discussions"

    def feature_discussions(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} discussions featured.')
    feature_discussions.short_description = "Feature selected discussions"

    def unfeature_discussions(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} discussions unfeatured.')
    unfeature_discussions.short_description = "Unfeature selected discussions"


class DiscussionPostAdmin(admin.ModelAdmin):
    """Admin interface for DiscussionPost model"""
    list_display = [
        'truncated_content', 'author', 'discussion', 'is_approved',
        'is_answer', 'net_votes', 'reply_count', 'created_at'
    ]
    list_filter = [
        'is_approved', 'is_answer', 'user_role', 'discussion__discussion_type',
        'created_at'
    ]
    search_fields = [
        'content', 'author__first_name', 'author__last_name',
        'discussion__title', 'code_snippet'
    ]
    readonly_fields = [
        'upvotes', 'downvotes', 'net_votes', 'created_at', 'updated_at',
        'edited_at', 'user_role'
    ]
    raw_id_fields = ['author', 'discussion', 'parent', 'approved_by']
    
    fieldsets = [
        ('Content', {
            'fields': [
                'discussion', 'parent', 'author', 'content', 'content_html',
                'code_snippet'
            ]
        }),
        ('Attachments', {
            'fields': [
                'attachments'
            ]
        }),
        ('Moderation', {
            'fields': [
                'is_approved', 'approved_by', 'approved_at'
            ]
        }),
        ('Engagement', {
            'fields': [
                'upvotes', 'downvotes', 'net_votes', 'is_answer'
            ]
        }),
        ('User Context', {
            'fields': [
                'user_role'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at', 'updated_at', 'edited_at'
            ]
        })
    ]

    actions = ['approve_posts', 'reject_posts', 'mark_as_answers', 'unmark_as_answers']

    def truncated_content(self, obj):
        return Truncator(obj.content).chars(60)
    truncated_content.short_description = 'Content'

    def net_votes(self, obj):
        return obj.net_votes
    net_votes.short_description = 'Net Votes'

    def approve_posts(self, request, queryset):
        updated = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} discussion posts approved.')
    approve_posts.short_description = "Approve selected posts"

    def reject_posts(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} discussion posts rejected.')
    reject_posts.short_description = "Reject selected posts"

    def mark_as_answers(self, request, queryset):
        for post in queryset:
            post.mark_as_answer()
        self.message_user(request, f'{queryset.count()} posts marked as answers.')
    mark_as_answers.short_description = "Mark selected posts as answers"

    def unmark_as_answers(self, request, queryset):
        updated = queryset.update(is_answer=False)
        self.message_user(request, f'{updated} posts unmarked as answers.')
    unmark_as_answers.short_description = "Unmark selected posts as answers"


class StudyGroupMembershipInline(admin.TabularInline):
    """Inline admin for StudyGroupMembership"""
    model = StudyGroupMembership
    extra = 1
    raw_id_fields = ['user']
    readonly_fields = ['joined_at']


class StudyGroupAdmin(admin.ModelAdmin):
    """Admin interface for StudyGroup model"""
    list_display = [
        'name', 'subject', 'classroom', 'creator', 'member_count',
        'is_full', 'is_public', 'exam_prep_group', 'last_activity'
    ]
    list_filter = [
        'subject', 'curriculum', 'exam_prep_group', 'target_exam',
        'is_public', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'creator__first_name', 'creator__last_name',
        'join_code'
    ]
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = [
        'member_count', 'last_activity', 'join_code', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['moderators']
    raw_id_fields = ['creator', 'subject', 'classroom']
    inlines = [StudyGroupMembershipInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'name', 'slug', 'description'
            ]
        }),
        ('Organization', {
            'fields': [
                'subject', 'classroom', 'curriculum'
            ]
        }),
        ('Membership', {
            'fields': [
                'creator', 'moderators', 'max_members', 'is_public', 'join_code'
            ]
        }),
        ('Kenya Education Context', {
            'fields': [
                'exam_prep_group', 'target_exam'
            ]
        }),
        ('Activity & Schedule', {
            'fields': [
                'last_activity', 'meeting_schedule'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at', 'updated_at'
            ]
        })
    ]

    actions = ['generate_join_codes', 'make_public', 'make_private']

    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'

    def is_full(self, obj):
        return obj.is_full
    is_full.short_description = 'Full'
    is_full.boolean = True

    def generate_join_codes(self, request, queryset):
        for group in queryset:
            if not group.join_code:
                group.generate_join_code()
        self.message_user(request, f'Join codes generated for {queryset.count()} study groups.')
    generate_join_codes.short_description = "Generate join codes for selected groups"

    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} study groups made public.')
    make_public.short_description = "Make selected groups public"

    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} study groups made private.')
    make_private.short_description = "Make selected groups private"


class PostLikeAdmin(admin.ModelAdmin):
    """Admin interface for PostLike model"""
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'post__category']
    search_fields = [
        'user__first_name', 'user__last_name', 'post__title'
    ]
    raw_id_fields = ['user', 'post']
    readonly_fields = ['created_at']


class DiscussionVoteAdmin(admin.ModelAdmin):
    """Admin interface for DiscussionVote model"""
    list_display = ['user', 'post', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = [
        'user__first_name', 'user__last_name', 'post__content'
    ]
    raw_id_fields = ['user', 'post']
    readonly_fields = ['created_at']


class BlogNotificationAdmin(admin.ModelAdmin):
    """Admin interface for BlogNotification model"""
    list_display = [
        'user', 'notification_type', 'truncated_title', 
        'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'title', 'message'
    ]
    readonly_fields = ['created_at', 'read_at']
    raw_id_fields = ['user']
    actions = ['mark_as_read', 'mark_as_unread']

    def truncated_title(self, obj):
        return Truncator(obj.title).chars(40)
    truncated_title.short_description = 'Title'

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Custom Admin Views and Reports
class BlogAnalyticsAdmin(admin.ModelAdmin):
    """Custom admin view for blog analytics"""
    
    def changelist_view(self, request, extra_context=None):
        # Add analytics data to the context
        from django.utils import timezone
        from datetime import timedelta
        
        # Basic statistics
        total_posts = BlogPost.objects.count()
        published_posts = BlogPost.objects.filter(status='published').count()
        total_comments = BlogComment.objects.count()
        total_discussions = DiscussionThread.objects.count()
        
        # Recent activity
        last_week = timezone.now() - timedelta(days=7)
        recent_posts = BlogPost.objects.filter(created_at__gte=last_week).count()
        recent_comments = BlogComment.objects.filter(created_at__gte=last_week).count()
        
        # Popular content
        popular_posts = BlogPost.objects.filter(status='published').order_by('-views_count')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_posts': total_posts,
            'published_posts': published_posts,
            'total_comments': total_comments,
            'total_discussions': total_discussions,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'popular_posts': popular_posts,
            'title': 'Blog Analytics Dashboard'
        })
        
        return super().changelist_view(request, extra_context=extra_context)


# Register models with admin site
admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(DiscussionThread, DiscussionThreadAdmin)
admin.site.register(DiscussionPost, DiscussionPostAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupMembership)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(DiscussionVote, DiscussionVoteAdmin)
admin.site.register(BlogNotification, BlogNotificationAdmin)

# Add custom admin site titles
admin.site.site_header = "Delvok Academy Blog Administration"
admin.site.site_title = "Blog Admin Portal"
admin.site.index_title = "Welcome to Delvok Academy Blog Administration"

# Import timezone for the admin actions
