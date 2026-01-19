# blog/models.py
import uuid
import os
import logging
from datetime import timedelta
import random
import string

from django.conf import settings
from django.db import models
from django.db.models import Count, Q, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from accounts.models import User
# FIXED: Import Classroom from academics.models
from academics.models import Classroom, Subject

logger = logging.getLogger(__name__)


class BaseBlogModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


# File path functions
def blog_image_path(instance, filename):
    """Generate file path for blog images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('blog/images', str(instance.id), filename)


def discussion_attachment_path(instance, filename):
    """Generate file path for discussion attachments"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('blog/attachments', str(instance.discussion.id), filename)


class BlogCategory(BaseBlogModel):
    """Enhanced categories for organizing blog posts and discussions"""
    
    # Curriculum choices
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('all', 'All Curricula'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('pre_primary', 'Pre-Primary'),
        ('lower_primary', 'Lower Primary'),
        ('upper_primary', 'Upper Primary'),
        ('lower_secondary', 'Lower Secondary'),
        ('upper_secondary', 'Upper Secondary'),
        ('all', 'All Levels'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    order = models.PositiveIntegerField(default=0)
    
    # Access control
    accessible_to_students = models.BooleanField(default=True)
    accessible_to_teachers = models.BooleanField(default=True)
    accessible_to_parents = models.BooleanField(default=False)
    min_grade_level = models.CharField(max_length=20, blank=True, help_text="Minimum grade level required")
    max_grade_level = models.CharField(max_length=20, blank=True, help_text="Maximum grade level allowed")
    
    # Kenya curriculum alignment
    curriculum = models.CharField(
        max_length=10,
        choices=CURRICULUM_CHOICES,
        default='all'
    )
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVEL_CHOICES,
        default='all'
    )

    class Meta:
        verbose_name = _('Blog Category')
        verbose_name_plural = _('Blog Categories')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['curriculum', 'education_level']),
            models.Index(fields=['parent', 'order']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'slug': self.slug})
    
    @property
    def post_count(self):
        return self.posts.filter(status='published').count()
    
    @property
    def discussion_count(self):
        return self.discussions.filter(is_active=True).count()
    
    @property
    def all_subcategories(self):
        """Get all subcategories recursively"""
        subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.all_subcategories)
        return subcategories
    
    def can_access(self, user):
        """Check if user can access this category"""
        # Check role-based access
        if user.role == 'student' and not self.accessible_to_students:
            return False
        elif user.role == 'teacher' and not self.accessible_to_teachers:
            return False
        elif user.role == 'parent' and not self.accessible_to_parents:
            return False
        
        # Check curriculum match
        if self.curriculum != 'all' and hasattr(user, 'primary_curriculum'):
            if user.primary_curriculum != self.curriculum:
                return False
        
        # Check grade level if student
        if user.role == 'student' and user.grade_level:
            try:
                student_grade = user.grade_level
                if self.min_grade_level and student_grade < self.min_grade_level:
                    return False
                if self.max_grade_level and student_grade > self.max_grade_level:
                    return False
            except AttributeError:
                pass
        
        return True


class BlogPost(BaseBlogModel):
    """Enhanced blog post model for educational content"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('scheduled', 'Scheduled'),
        ('pending_review', 'Pending Review'),
    ]
    
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('news', 'News'),
        ('announcement', 'Announcement'),
        ('tutorial', 'Tutorial'),
        ('resource', 'Learning Resource'),
        ('event', 'Event'),
        ('achievement', 'Achievement'),
        ('kenya_education', 'Kenya Education Update'),
        ('cbc_guide', 'CBC Guide'),
        ('exam_tips', 'Exam Tips'),
        ('career_advice', 'Career Advice'),
        ('student_spotlight', 'Student Spotlight'),
    ]
    
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
        ('specific_class', 'Specific Classroom'),
        ('specific_curriculum', 'Specific Curriculum'),
        ('specific_grade', 'Specific Grade Level'),
    ]
    
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('all', 'All Curricula'),
    ]
    
    READING_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # Basic content fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text="Brief summary of the post")
    
    # Categorization
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='article')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Author and ownership
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog_posts',
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher', 'curriculum_coordinator']}
    )
    co_authors = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='coauthored_posts',
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher', 'curriculum_coordinator']}
    )
    
    # Audience targeting
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    # FIXED: Changed ClassRoom to Classroom
    specific_class = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    curriculum = models.CharField(
        max_length=10,
        choices=CURRICULUM_CHOICES,
        default='all'
    )
    target_grade_level = models.CharField(max_length=20, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to=blog_image_path, blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True)
    attachments = models.JSONField(
        default=list, 
        blank=True, 
        help_text="JSON array of additional file URLs with metadata"
    )
    
    # Status and publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    archive_date = models.DateTimeField(null=True, blank=True)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    canonical_url = models.URLField(blank=True)
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # Moderation
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_blog_posts',
        limit_choices_to={'role__in': ['admin', 'head_teacher']}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Notes from moderators")
    
    # Kenya education specific
    kicd_aligned = models.BooleanField(default=False, help_text="Aligned with KICD curriculum")
    competency_based = models.BooleanField(default=False, help_text="Focuses on CBC competencies")
    exam_related = models.BooleanField(default=False, help_text="Related to national exams (KCPE/KCSE)")
    learning_outcomes = models.JSONField(
        default=list, 
        blank=True, 
        help_text="Specific learning outcomes for this content"
    )
    
    # Content quality
    reading_level = models.CharField(
        max_length=20,
        choices=READING_LEVEL_CHOICES,
        default='intermediate'
    )
    content_quality_score = models.PositiveIntegerField(default=0, help_text="Automated quality score 0-100")

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['curriculum', 'audience']),
            models.Index(fields=['content_type', 'published_date']),
            models.Index(fields=['kicd_aligned', 'exam_related']),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Enhanced validation for blog post data"""
        if self.status == 'scheduled' and not self.scheduled_date:
            raise ValidationError({'scheduled_date': 'Scheduled date is required for scheduled posts.'})
        
        if self.audience == 'specific_class' and not self.specific_class:
            raise ValidationError({'specific_class': 'Specific class is required when audience is set to specific class.'})
        
        if self.audience == 'specific_curriculum' and self.curriculum == 'all':
            raise ValidationError({'curriculum': 'Specific curriculum must be selected when audience is set to specific curriculum.'})
        
        if self.audience == 'specific_grade' and not self.target_grade_level:
            raise ValidationError({'target_grade_level': 'Target grade level is required when audience is set to specific grade.'})
        
        # Validate scheduled date is in future
        if self.scheduled_date and self.scheduled_date <= timezone.now():
            raise ValidationError({'scheduled_date': 'Scheduled date must be in the future.'})
        
        # Validate author has appropriate role
        if self.author.role not in ['teacher', 'admin', 'head_teacher', 'curriculum_coordinator']:
            raise ValidationError({'author': 'Only teachers, admins, and staff can create blog posts.'})
    
    def save(self, *args, **kwargs):
        """Enhanced save method with additional logic"""
        # Set published date when publishing
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        
        # Auto-publish scheduled posts
        if self.status == 'scheduled' and self.scheduled_date and self.scheduled_date <= timezone.now():
            self.status = 'published'
            self.published_date = timezone.now()
        
        # Auto-archive old posts
        if (self.status == 'published' and self.published_date and 
            self.published_date < timezone.now() - timedelta(days=365)):
            self.status = 'archived'
            self.archive_date = timezone.now()
        
        # Generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        
        # Calculate content quality score
        self.calculate_content_quality()
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Create notification when published
        if self.status == 'published':
            self.notify_audience()
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def is_featured(self):
        """Determine if post should be featured based on engagement"""
        return (self.views_count > 100 or 
                self.likes_count > 50 or 
                self.comments_count > 20 or
                self.average_rating >= 4.0)
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)  # Assuming 200 words per minute
    
    @property
    def tag_list(self):
        """Convert tags string to list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    @property
    def display_author(self):
        """Get display name for author"""
        return self.author.get_full_name() or self.author.username
    
    @property
    def co_author_names(self):
        """Get display names for co-authors"""
        return [co_author.get_full_name() or co_author.username 
                for co_author in self.co_authors.all()]
    
    def calculate_content_quality(self):
        """Calculate automated content quality score"""
        score = 0
        
        # Content length (max 30 points)
        word_count = len(self.content.split())
        if word_count >= 500:
            score += 30
        elif word_count >= 300:
            score += 20
        elif word_count >= 150:
            score += 10
        
        # Images and media (max 20 points)
        if self.featured_image:
            score += 10
        if self.attachments and len(self.attachments) > 0:
            score += 10
        
        # Structure and formatting (max 30 points)
        if len(self.excerpt) >= 100:
            score += 10
        if self.meta_description:
            score += 10
        if self.tags and len(self.tag_list) >= 3:
            score += 10
        
        # Educational value (max 20 points)
        if self.learning_outcomes and len(self.learning_outcomes) > 0:
            score += 10
        if self.kicd_aligned or self.competency_based:
            score += 10
        
        self.content_quality_score = min(score, 100)
    
    def can_view(self, user):
        """Enhanced access control for blog posts"""
        if not self.is_published:
            return False
        
        # Check category access
        if self.category and not self.category.can_access(user):
            return False
        
        # Audience-specific access control
        if self.audience == 'all':
            return True
        elif self.audience == 'students' and user.role == 'student':
            return True
        elif self.audience == 'teachers' and user.role in ['teacher', 'admin', 'head_teacher', 'curriculum_coordinator']:
            return True
        elif self.audience == 'parents' and user.role == 'parent':
            return True
        elif self.audience == 'specific_class' and user.role == 'student':
            # Check if student is in the specific class
            return user.current_class == self.specific_class.name if self.specific_class else False
        elif self.audience == 'specific_curriculum':
            return hasattr(user, 'primary_curriculum') and user.primary_curriculum == self.curriculum
        elif self.audience == 'specific_grade' and user.role == 'student':
            return user.grade_level == self.target_grade_level
        
        return False
    
    def increment_views(self):
        """Increment view count atomically"""
        BlogPost.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)
        self.refresh_from_db()
    
    def notify_audience(self):
        """Enhanced notification system for new posts"""
        # FIXED: Import from accounts instead of users
        from accounts.models import UserNotification
        
        users_to_notify = self.get_target_audience_users()
        
        for user in users_to_notify:
            try:
                UserNotification.objects.create(
                    user=user,
                    notification_type='academic',
                    priority='normal',
                    title=f'New {self.get_content_type_display()}: {self.title}',
                    message=f'{self.excerpt[:120]}...',
                    action_url=self.get_absolute_url(),
                    action_text='Read Now',
                    metadata={
                        'post_id': str(self.id),
                        'content_type': self.content_type,
                        'author': self.display_author
                    }
                )
            except Exception as e:
                logger.error(f"Failed to create notification for user {user.id}: {e}")
    
    def get_target_audience_users(self):
        """Get users who should receive notifications for this post"""
        from accounts.models import User
        
        base_query = User.objects.filter(is_active=True, is_verified=True)
        
        if self.audience == 'all':
            return base_query
        elif self.audience == 'students':
            return base_query.filter(role='student')
        elif self.audience == 'teachers':
            return base_query.filter(role__in=['teacher', 'admin', 'head_teacher', 'curriculum_coordinator'])
        elif self.audience == 'parents':
            return base_query.filter(role='parent')
        elif self.audience == 'specific_class' and self.specific_class:
            return base_query.filter(
                role='student',
                current_class=self.specific_class.name
            )
        elif self.audience == 'specific_curriculum' and self.curriculum != 'all':
            return base_query.filter(primary_curriculum=self.curriculum)
        elif self.audience == 'specific_grade' and self.target_grade_level:
            return base_query.filter(
                role='student',
                grade_level=self.target_grade_level
            )
        
        return User.objects.none()
    
    @classmethod
    def get_published_posts(cls):
        """Get all published posts"""
        return cls.objects.filter(status='published')
    
    @classmethod
    def get_featured_posts(cls, limit=5):
        """Get featured posts based on engagement"""
        return (cls.get_published_posts()
                .order_by('-views_count', '-likes_count', '-comments_count')
                [:limit])
    
    @classmethod
    def get_recent_posts(cls, days=7):
        """Get posts from recent days"""
        since_date = timezone.now() - timedelta(days=days)
        return cls.get_published_posts().filter(published_date__gte=since_date)
    
    @classmethod
    def get_posts_by_curriculum(cls, curriculum):
        """Get posts for specific curriculum"""
        return cls.get_published_posts().filter(
            Q(curriculum=curriculum) | Q(curriculum='all')
        )
    
    @classmethod
    def get_posts_for_user(cls, user):
        """Get posts visible to specific user"""
        posts = cls.get_published_posts()
        return [post for post in posts if post.can_view(user)]


class DiscussionThread(BaseBlogModel):
    """Enhanced discussion threads for educational interactions"""
    
    DISCUSSION_TYPES = [
        ('qna', 'Q&A Discussion'),
        ('project', 'Project Discussion'),
        ('study_group', 'Study Group'),
        ('general', 'General Discussion'),
        ('assignment_help', 'Assignment Help'),
        ('subject_discussion', 'Subject Discussion'),
        ('exam_prep', 'Exam Preparation'),
        ('career_guidance', 'Career Guidance'),
        ('kenya_education', 'Kenya Education Discussion'),
        ('teacher_collab', 'Teacher Collaboration'),
        ('parent_engagement', 'Parent Engagement'),
    ]
    
    PRIVACY_LEVELS = [
        ('public', 'Public - All users can view and participate'),
        ('class_only', 'Classroom Only - Only class members can participate'),
        ('private', 'Private - Only invited users can participate'),
        ('curriculum_specific', 'Curriculum Specific - Only users in same curriculum'),
        ('role_specific', 'Role Specific - Only users with specific roles'),
    ]
    
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('all', 'All Curricula'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Categorization
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    discussion_type = models.CharField(max_length=20, choices=DISCUSSION_TYPES, default='general')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    # FIXED: Changed ClassRoom to Classroom
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    curriculum = models.CharField(
        max_length=10,
        choices=CURRICULUM_CHOICES,
        default='all'
    )
    
    # Ownership and moderation
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_discussions'
    )
    moderators = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='moderated_discussions',
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher']}
    )
    
    # Privacy and access
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_LEVELS, default='public')
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of roles allowed to participate"
    )
    invited_users = models.ManyToManyField(User, blank=True, related_name='invited_discussions')
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Status
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False, help_text="Hide user identities in this discussion")
    is_featured = models.BooleanField(default=False)
    
    # Kenya education context
    exam_related = models.BooleanField(default=False, help_text="Related to national exams")
    grade_level = models.CharField(max_length=20, blank=True, help_text="Target grade level")
    kicd_topic = models.CharField(max_length=100, blank=True, help_text="Related KICD topic")

    class Meta:
        ordering = ['-is_pinned', '-is_featured', '-last_activity']
        verbose_name = _('Discussion Thread')
        verbose_name_plural = _('Discussion Threads')
        indexes = [
            models.Index(fields=['discussion_type', 'last_activity']),
            models.Index(fields=['classroom', 'last_activity']),
            models.Index(fields=['curriculum', 'subject']),
            models.Index(fields=['is_featured', 'created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:discussion_detail', kwargs={'slug': self.slug})
    
    @property
    def is_active(self):
        """Check if discussion is active (recent activity)"""
        return self.last_activity >= timezone.now() - timedelta(days=30)
    
    @property
    def is_very_active(self):
        """Check if discussion is very active"""
        return self.last_activity >= timezone.now() - timedelta(days=7)
    
    @property
    def first_post(self):
        """Get the first post in the discussion"""
        return self.posts.filter(parent__isnull=True).first()
    
    @property
    def recent_participants(self):
        """Get users who have posted recently"""
        recent_posts = self.posts.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        return User.objects.filter(
            id__in=recent_posts.values('author')
        ).distinct()
    
    @property
    def answer_count(self):
        """Count of marked answers (for Q&A discussions)"""
        return self.posts.filter(is_answer=True).count()
    
    def can_view(self, user):
        """Check if user can view this discussion"""
        return self.can_participate(user) or user.role in ['teacher', 'admin', 'head_teacher']
    
    def can_participate(self, user):
        """Enhanced participation check"""
        if self.is_locked:
            return False
        
        if self.privacy_level == 'public':
            return True
        elif self.privacy_level == 'class_only' and user.role == 'student':
            return user.current_class == self.classroom.name if self.classroom else False
        elif self.privacy_level == 'private':
            return user in self.invited_users.all() or user == self.created_by
        elif self.privacy_level == 'curriculum_specific':
            return hasattr(user, 'primary_curriculum') and (
                user.primary_curriculum == self.curriculum or self.curriculum == 'all'
            )
        elif self.privacy_level == 'role_specific':
            return user.role in self.allowed_roles
        
        return False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def add_moderator(self, user):
        """Add a moderator to the discussion"""
        if user.role in ['teacher', 'admin', 'head_teacher']:
            self.moderators.add(user)
            return True
        return False
    
    def get_engagement_stats(self):
        """Get detailed engagement statistics"""
        return {
            'total_posts': self.posts.count(),
            'total_participants': self.participant_count,
            'posts_last_week': self.posts.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'answer_rate': (self.answer_count / self.posts.count() * 100) if self.posts.count() > 0 else 0,
        }


class DiscussionPost(BaseBlogModel):
    """Individual posts within a discussion thread"""
    
    # Relationships
    discussion = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='posts')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Content
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_posts')
    content = models.TextField()
    content_html = models.TextField(blank=True, help_text="HTML formatted content")
    
    # Media and attachments
    attachments = models.JSONField(blank=True, null=True, help_text="JSON array of file attachments")
    code_snippet = models.TextField(blank=True, help_text="Code blocks with syntax highlighting")
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_discussion_posts',
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher']}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    is_answer = models.BooleanField(default=False, help_text="Marked as correct answer in Q&A")
    
    # Timestamps
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # User context
    user_role = models.CharField(max_length=20, blank=True, help_text="User's role when posting")

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Discussion Post')
        verbose_name_plural = _('Discussion Posts')
        indexes = [
            models.Index(fields=['discussion', 'parent', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['is_answer', 'created_at']),
        ]
    
    def __str__(self):
        return f"Post by {self.author} in {self.discussion.title}"
    
    def save(self, *args, **kwargs):
        """Override save to update discussion activity"""
        is_new = self._state.adding
        
        # Set user role for context
        if not self.user_role:
            self.user_role = self.author.role
        
        super().save(*args, **kwargs)
        
        if is_new:
            # Update discussion metrics
            self.discussion.reply_count = models.F('reply_count') + 1
            self.discussion.update_activity()
            
            # Update participant count if new participant
            if not self.discussion.posts.filter(author=self.author).exclude(pk=self.pk).exists():
                self.discussion.participant_count = models.F('participant_count') + 1
            
            self.discussion.save()
            
            # Notify discussion participants about new reply
            self.notify_participants()
    
    @property
    def net_votes(self):
        return self.upvotes - self.downvotes
    
    @property
    def is_root_post(self):
        return self.parent is None
    
    @property
    def reply_count(self):
        return self.replies.count()
    
    def mark_as_answer(self):
        """Mark this post as the answer (for Q&A discussions)"""
        if self.discussion.discussion_type == 'qna':
            # Unmark other answers in the same discussion
            DiscussionPost.objects.filter(
                discussion=self.discussion,
                is_answer=True
            ).update(is_answer=False)
            
            self.is_answer = True
            self.save()
    
    def notify_participants(self):
        """Notify discussion participants about new reply"""
        # FIXED: Import from accounts instead of users
        from accounts.models import UserNotification
        
        # Notify thread creator if it's a new reply
        if not self.is_root_post and self.parent:
            if self.parent.author != self.author:
                UserNotification.objects.create(
                    user=self.parent.author,
                    notification_type='academic',
                    priority='normal',
                    title=f'New Reply in {self.discussion.title}',
                    message=f'{self.author.get_full_name()} replied to your post in "{self.discussion.title}".',
                    action_url=f'/discussions/{self.discussion.slug}#post-{self.id}',
                    action_text='View Reply'
                )
        
        # Notify moderators about new posts in their discussions
        for moderator in self.discussion.moderators.all():
            if moderator != self.author:
                UserNotification.objects.create(
                    user=moderator,
                    notification_type='academic',
                    priority='low',
                    title=f'New Activity in {self.discussion.title}',
                    message=f'New post in discussion "{self.discussion.title}" that you moderate.',
                    action_url=f'/discussions/{self.discussion.slug}#post-{self.id}',
                    action_text='View Post'
                )


class BlogComment(BaseBlogModel):
    """Enhanced comments on blog posts with moderation features"""
    
    # Relationships
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Content
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog_comments'
    )
    content = models.TextField()
    content_html = models.TextField(blank=True, help_text="HTML formatted content")
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_blog_comments',
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher']}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True, help_text="Notes from moderators")
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    report_count = models.PositiveIntegerField(default=0, help_text="Number of times reported")
    
    # User context
    user_role = models.CharField(max_length=20, blank=True, help_text="User's role when commenting")
    user_grade_level = models.CharField(max_length=20, blank=True, help_text="User's grade level when commenting")
    
    # Timestamps
    edited_at = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='edited_comments'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Blog Comment')
        verbose_name_plural = _('Blog Comments')
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['is_approved', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
    
    @property
    def is_root_comment(self):
        return self.parent is None
    
    @property
    def reply_count(self):
        return self.replies.count()
    
    @property
    def net_likes(self):
        return self.likes_count
    
    @property
    def is_edited(self):
        return self.edited_at is not None
    
    def save(self, *args, **kwargs):
        """Update post comment count when comment is saved"""
        is_new = self._state.adding
        
        # Set user context
        if not self.user_role:
            self.user_role = self.author.role
        
        # Set grade level for students
        if not self.user_grade_level and self.author.role == 'student':
            self.user_grade_level = self.author.grade_level or ''
        
        super().save(*args, **kwargs)
        
        if is_new:
            # Update post comment count
            BlogPost.objects.filter(pk=self.post.pk).update(
                comments_count=F('comments_count') + 1
            )
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return user == self.author or user.role in ['teacher', 'admin', 'head_teacher']
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return (user == self.author or 
                user.role in ['teacher', 'admin', 'head_teacher'] or
                user == self.post.author)
    
    def mark_as_edited(self, user):
        """Mark comment as edited by user"""
        self.edited_at = timezone.now()
        self.last_edited_by = user
        self.save()
    
    def report(self, user, reason=""):
        """Report this comment"""
        # FIXED: Import from accounts instead of users
        from accounts.models import UserNotification
        
        self.report_count = F('report_count') + 1
        self.save()
        
        # Notify moderators
        moderators = User.objects.filter(role__in=['teacher', 'admin', 'head_teacher'])
        for moderator in moderators:
            UserNotification.objects.create(
                user=moderator,
                notification_type='moderation',
                priority='high',
                title='Comment Reported',
                message=f'Comment by {self.author} on "{self.post.title}" has been reported. Reason: {reason}',
                action_url=f'/admin/blog/blogcomment/{self.id}/change/',
                action_text='Review Comment'
            )


class PostLike(BaseBlogModel):
    """Track likes on blog posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    
    class Meta:
        unique_together = ['user', 'post']
        verbose_name = _('Post Like')
        verbose_name_plural = _('Post Likes')
    
    def __str__(self):
        return f"{self.user} likes {self.post.title}"
    
    def save(self, *args, **kwargs):
        """Update post like count"""
        is_new = self._state.adding
        
        super().save(*args, **kwargs)
        
        if is_new:
            self.post.likes_count = models.F('likes_count') + 1
            self.post.save(update_fields=['likes_count'])


class DiscussionVote(BaseBlogModel):
    """Track votes on discussion posts"""
    
    VOTE_TYPES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)
    
    class Meta:
        unique_together = ['user', 'post']
        verbose_name = _('Discussion Vote')
        verbose_name_plural = _('Discussion Votes')
    
    def __str__(self):
        return f"{self.user} {self.vote_type}voted {self.post}"
    
    def save(self, *args, **kwargs):
        """Update post vote counts"""
        is_new = self._state.adding
        
        # Delete existing vote if changing vote type
        if not is_new:
            old_instance = DiscussionVote.objects.get(pk=self.pk)
            if old_instance.vote_type != self.vote_type:
                # Remove old vote count
                if old_instance.vote_type == 'up':
                    self.post.upvotes = models.F('upvotes') - 1
                else:
                    self.post.downvotes = models.F('downvotes') - 1
                self.post.save()
        
        super().save(*args, **kwargs)
        
        if is_new or not is_new:
            # Add new vote count
            if self.vote_type == 'up':
                self.post.upvotes = models.F('upvotes') + 1
            else:
                self.post.downvotes = models.F('downvotes') + 1
            self.post.save()


class StudyGroup(BaseBlogModel):
    """Study groups for collaborative learning"""
    
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
    ]
    
    EXAM_CHOICES = [
        ('kcpe', 'KCPE'),
        ('kcse', 'KCSE'),
        ('igcse', 'IGCSE'),
    ]
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    # Organization
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # FIXED: Changed ClassRoom to Classroom
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True, related_name='study_groups')
    curriculum = models.CharField(
        max_length=10,
        choices=CURRICULUM_CHOICES,
        blank=True
    )
    
    # Membership
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_study_groups',
        limit_choices_to={'role': 'student'}
    )
    members = models.ManyToManyField(
        User, 
        through='StudyGroupMembership', 
        related_name='study_groups',
        limit_choices_to={'role': 'student'}
    )
    moderators = models.ManyToManyField(
        User, 
        related_name='moderated_study_groups', 
        blank=True,
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher']}
    )
    
    # Settings
    max_members = models.PositiveIntegerField(default=10)
    is_public = models.BooleanField(default=True)
    join_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    
    # Activity tracking
    last_activity = models.DateTimeField(auto_now=True)
    meeting_schedule = models.JSONField(blank=True, null=True, help_text="JSON schedule for group meetings")
    
    # Kenya education context
    exam_prep_group = models.BooleanField(default=False, help_text="Group focused on exam preparation")
    target_exam = models.CharField(
        max_length=20,
        choices=EXAM_CHOICES,
        blank=True
    )

    class Meta:
        verbose_name = _('Study Group')
        verbose_name_plural = _('Study Groups')
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['subject', 'classroom']),
            models.Index(fields=['curriculum', 'exam_prep_group']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members
    
    def generate_join_code(self):
        """Generate a unique join code for the study group"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not StudyGroup.objects.filter(join_code=code).exists():
                self.join_code = code
                self.save()
                break
    
    def can_join(self, user):
        """Check if user can join this study group"""
        if user.role != 'student':
            return False
        
        if self.is_full:
            return False
        
        if not self.is_public and not self.join_code:
            return False
        
        # Check curriculum match if specified
        if self.curriculum and user.primary_curriculum != self.curriculum:
            return False
        
        # Check classroom match if specified
        if self.classroom:
            return user.current_class == self.classroom.name
        
        return True


class StudyGroupMembership(BaseBlogModel):
    """Track study group membership with roles"""
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['group', 'user']
        verbose_name = _('Study Group Membership')
        verbose_name_plural = _('Study Group Memberships')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user} in {self.group}"


class BlogNotification(BaseBlogModel):
    """Notifications for blog and discussion activities"""
    
    NOTIFICATION_TYPES = [
        ('new_post', 'New Blog Post'),
        ('new_comment', 'New Comment'),
        ('new_discussion', 'New Discussion'),
        ('discussion_reply', 'Discussion Reply'),
        ('post_like', 'Post Liked'),
        ('comment_reply', 'Comment Reply'),
        ('mention', 'Mentioned'),
        ('study_group_invite', 'Study Group Invitation'),
        ('content_approved', 'Content Approved'),
        ('moderation_required', 'Moderation Required'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related object references
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Blog Notification')
        verbose_name_plural = _('Blog Notifications')
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user}: {self.title}"


# Signals
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver


@receiver(post_save, sender=BlogPost)
def handle_blog_post_publishing(sender, instance, created, **kwargs):
    """Enhanced blog post signal handling"""
    if instance.status == 'published' and created:
        # Update author's activity metrics
        try:
            from accounts.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=instance.author)
            # FIXED: Use proper field name
            profile.save()
        except Exception as e:
            logger.error(f"Failed to update user profile for {instance.author}: {e}")
        
        # Log publishing event
        logger.info(f"Blog post published: {instance.title} by {instance.author}")


@receiver(m2m_changed, sender=BlogPost.co_authors.through)
def handle_coauthor_addition(sender, instance, action, pk_set, **kwargs):
    """Handle co-author additions"""
    if action == "post_add":
        from accounts.models import UserNotification
        for user_id in pk_set:
            try:
                co_author = User.objects.get(pk=user_id)
                UserNotification.objects.create(
                    user=co_author,
                    notification_type='academic',
                    priority='normal',
                    title='Added as Co-Author',
                    message=f'You have been added as a co-author to "{instance.title}"',
                    action_url=instance.get_absolute_url(),
                    action_text='View Post'
                )
            except Exception as e:
                logger.error(f"Failed to notify co-author {user_id}: {e}")


@receiver(post_save, sender=StudyGroup)
def handle_study_group_creation(sender, instance, created, **kwargs):
    """Handle study group creation"""
    if created:
        instance.generate_join_code()
        
        # Auto-add creator as admin
        StudyGroupMembership.objects.create(
            group=instance,
            user=instance.creator,
            role='admin'
        )


@receiver(post_delete, sender=PostLike)
def update_post_like_count_on_delete(sender, instance, **kwargs):
    """Update like count when a like is deleted"""
    instance.post.likes_count = models.F('likes_count') - 1
    instance.post.save()


@receiver(post_delete, sender=BlogComment)
def update_post_comment_count_on_delete(sender, instance, **kwargs):
    """Update comment count when a comment is deleted"""
    instance.post.comments_count = models.F('comments_count') - 1
    instance.post.save()


# Utility functions
def get_trending_posts(days=7, limit=10):
    """Get trending posts based on recent engagement"""
    since_date = timezone.now() - timedelta(days=days)
    return (BlogPost.objects
            .filter(
                status='published',
                published_date__gte=since_date
            )
            .annotate(
                engagement_score=(
                    F('views_count') * 0.3 + 
                    F('likes_count') * 0.4 + 
                    F('comments_count') * 0.3
                )
            )
            .order_by('-engagement_score')[:limit])


def get_user_contribution_stats(user):
    """Get comprehensive contribution statistics for a user"""
    return {
        'blog_posts': user.blog_posts.filter(status='published').count(),
        'discussions_created': user.created_discussions.count(),
        'discussion_posts': user.discussion_posts.count(),
        'comments': user.blog_comments.count(),
        'total_likes_received': user.blog_posts.aggregate(
            total_likes=Count('likes')
        )['total_likes'] or 0,
        'study_groups_created': user.created_study_groups.count(),
    }