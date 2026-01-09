"""
Enhanced Notes and Learning Content Management System for Delvok Academy
Features:
1. Multiple content types (Text, Video, Audio, PDF, Interactive, etc.)
2. Learning modules and course organization
3. Student progress tracking
4. Content sequencing and prerequisites
5. Curriculum alignment
6. Analytics and reporting
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
import logging
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Count, Avg, Sum, Q
from django.core.cache import cache
from django.urls import reverse
import json
from django.db import transaction
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


# ==================== BASE MODELS ====================
class BaseNotesModel(models.Model):
    """Abstract base model for all notes and learning content models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_%(class)s_entries'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def get_absolute_url(self):
        """Override in child classes for detail view URLs"""
        return reverse(f'{self._meta.model_name}_detail', args=[str(self.id)])


# ==================== CONTENT CATEGORIES ====================
class ContentCategory(BaseNotesModel):
    """Categories for organizing learning content"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)
    
    # Curriculum alignment
    curriculum = models.CharField(max_length=20, blank=True, choices=[
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('ib', 'International Baccalaureate'),
    ])
    
    class Meta:
        verbose_name = _("Content Category")
        verbose_name_plural = _("Content Categories")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def content_count(self):
        """Count of content items in this category"""
        return self.contents.count()
    
    @property
    def tree_path(self):
        """Get hierarchical path for this category"""
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)


# ==================== TAGS ====================
class ContentTag(BaseNotesModel):
    """Tags for content organization and discovery"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _("Content Tag")
        verbose_name_plural = _("Content Tags")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


# ==================== CONTENT BASE MODEL ====================
class LearningContent(BaseNotesModel):
    """
    Base model for all learning content types
    Uses polymorphic approach for different content types
    """
    
    CONTENT_TYPES = [
        ('text', 'Text Content'),
        ('video', 'Video Lesson'),
        ('audio', 'Audio Lesson'),
        ('pdf', 'PDF Document'),
        ('presentation', 'Presentation'),
        ('interactive', 'Interactive Content'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('link', 'External Link'),
        ('file', 'File Resource'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='intermediate')
    
    # Academic Context
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_contents'
    )
    grade_level = models.CharField(max_length=20, blank=True)
    curriculum = models.CharField(max_length=20, blank=True, choices=[
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('ib', 'International Baccalaureate'),
    ])
    
    # Organization
    categories = models.ManyToManyField(ContentCategory, related_name='contents', blank=True)
    tags = models.ManyToManyField(ContentTag, related_name='contents', blank=True)
    
    # Learning Objectives
    learning_objectives = models.JSONField(default=list, blank=True)
    prerequisites = models.TextField(blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)
    
    # Timing
    estimated_duration = models.PositiveIntegerField(
        default=15,
        help_text="Estimated completion time in minutes"
    )
    publish_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Access Control
    is_public = models.BooleanField(default=True)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('authenticated', 'Authenticated Users'),
            ('students', 'Students Only'),
            ('teachers', 'Teachers Only'),
            ('premium', 'Premium Users'),
        ],
        default='students'
    )
    allowed_users = models.ManyToManyField(
        'accounts.User',
        related_name='allowed_contents',
        blank=True
    )
    password_protected = models.BooleanField(default=False)
    access_password = models.CharField(max_length=100, blank=True)
    
    # Resources
    resources = models.JSONField(default=list, blank=True, help_text="Additional resources")
    references = models.JSONField(default=list, blank=True)
    
    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # SEO & Metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_versions'
    )
    
    # Review Process
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_contents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Analytics
    last_accessed = models.DateTimeField(null=True, blank=True)
    completion_count = models.PositiveIntegerField(default=0)
    average_completion_time = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _("Learning Content")
        verbose_name_plural = _("Learning Contents")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'publish_date']),
            models.Index(fields=['content_type', 'subject']),
            models.Index(fields=['views_count']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Generate slug and handle publish logic"""
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set publish date when status changes to published
        if self.status == 'published' and not self.publish_date:
            self.publish_date = timezone.now()
        
        # Update version if parent version exists
        if self.parent_version and not self.version:
            self.version = self.parent_version.version + 1
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate content data"""
        if self.expiry_date and self.publish_date:
            if self.expiry_date <= self.publish_date:
                raise ValidationError(_("Expiry date must be after publish date"))
    
    @property
    def is_published(self):
        """Check if content is currently published"""
        now = timezone.now()
        return (
            self.status == 'published' and
            (not self.publish_date or self.publish_date <= now) and
            (not self.expiry_date or self.expiry_date > now)
        )
    
    @property
    def duration_formatted(self):
        """Format duration in human-readable format"""
        if self.estimated_duration < 60:
            return f"{self.estimated_duration} min"
        else:
            hours = self.estimated_duration // 60
            minutes = self.estimated_duration % 60
            if minutes:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
    
    @property
    def completion_rate(self):
        """Calculate completion rate"""
        if self.views_count > 0:
            return (self.completion_count / self.views_count) * 100
        return 0
    
    def increment_view(self):
        """Increment view count"""
        self.views_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['views_count', 'last_accessed'])
    
    def record_completion(self, duration):
        """Record content completion"""
        self.completion_count += 1
        
        # Update average completion time
        total_time = self.average_completion_time * (self.completion_count - 1)
        self.average_completion_time = (total_time + duration) / self.completion_count
        
        self.save(update_fields=['completion_count', 'average_completion_time'])
    
    def get_content_type_model(self):
        """Get the specific content type model"""
        content_type_map = {
            'text': TextContent,
            'video': VideoContent,
            'audio': AudioContent,
            'pdf': PDFContent,
            'presentation': PresentationContent,
            'interactive': InteractiveContent,
            'quiz': QuizContent,
            'assignment': AssignmentContent,
            'link': LinkContent,
            'file': FileContent,
        }
        return content_type_map.get(self.content_type)
    
    def get_specific_content(self):
        """Get the specific content object"""
        model = self.get_content_type_model()
        if model:
            return model.objects.filter(id=self.id).first()
        return None


# ==================== SPECIFIC CONTENT TYPES ====================
class TextContent(LearningContent):
    """Text-based learning content"""
    content = models.TextField()
    word_count = models.PositiveIntegerField(default=0, editable=False)
    format = models.CharField(
        max_length=20,
        choices=[
            ('plain', 'Plain Text'),
            ('html', 'HTML'),
            ('markdown', 'Markdown'),
        ],
        default='html'
    )
    
    class Meta:
        verbose_name = _("Text Content")
        verbose_name_plural = _("Text Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'text'
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)


class VideoContent(LearningContent):
    """Video-based learning content"""
    video_url = models.URLField(blank=True)
    video_file = models.FileField(
        upload_to='learning_videos/%Y/%m/',
        blank=True,
        null=True
    )
    thumbnail = models.ImageField(
        upload_to='video_thumbnails/%Y/%m/',
        blank=True,
        null=True
    )
    duration_seconds = models.PositiveIntegerField(default=0)
    transcript = models.TextField(blank=True)
    captions_url = models.URLField(blank=True)
    quality_options = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = _("Video Content")
        verbose_name_plural = _("Video Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'video'
        super().save(*args, **kwargs)
    
    @property
    def duration_formatted(self):
        """Format video duration"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class AudioContent(LearningContent):
    """Audio-based learning content"""
    audio_file = models.FileField(upload_to='learning_audio/%Y/%m/')
    duration_seconds = models.PositiveIntegerField(default=0)
    transcript = models.TextField(blank=True)
    bitrate = models.PositiveIntegerField(default=128, help_text="Bitrate in kbps")
    
    class Meta:
        verbose_name = _("Audio Content")
        verbose_name_plural = _("Audio Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'audio'
        super().save(*args, **kwargs)


class PDFContent(LearningContent):
    """PDF-based learning content"""
    pdf_file = models.FileField(upload_to='learning_pdfs/%Y/%m/')
    page_count = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    allow_printing = models.BooleanField(default=True)
    allow_download = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("PDF Content")
        verbose_name_plural = _("PDF Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'pdf'
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class PresentationContent(LearningContent):
    """Presentation-based learning content"""
    presentation_file = models.FileField(
        upload_to='learning_presentations/%Y/%m/',
        blank=True,
        null=True
    )
    slide_count = models.PositiveIntegerField(default=0)
    speaker_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Presentation Content")
        verbose_name_plural = _("Presentation Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'presentation'
        super().save(*args, **kwargs)


class InteractiveContent(LearningContent):
    """Interactive learning content"""
    interactive_type = models.CharField(
        max_length=20,
        choices=[
            ('simulation', 'Simulation'),
            ('game', 'Educational Game'),
            ('quiz', 'Interactive Quiz'),
            ('vr', 'VR/AR Experience'),
            ('h5p', 'H5P Content'),
            ('scorm', 'SCORM Package'),
        ]
    )
    interactive_file = models.FileField(
        upload_to='interactive_content/%Y/%m/',
        blank=True,
        null=True
    )
    embed_code = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Interactive Content")
        verbose_name_plural = _("Interactive Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'interactive'
        super().save(*args, **kwargs)


class QuizContent(LearningContent):
    """Quiz content with questions"""
    total_questions = models.PositiveIntegerField(default=0)
    passing_score = models.PositiveIntegerField(default=70)
    time_limit = models.PositiveIntegerField(default=0, help_text="Time limit in minutes (0 = no limit)")
    shuffle_questions = models.BooleanField(default=True)
    show_results = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Quiz Content")
        verbose_name_plural = _("Quiz Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'quiz'
        super().save(*args, **kwargs)


class AssignmentContent(LearningContent):
    """Assignment content"""
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    submission_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('file', 'File Upload'),
            ('both', 'Both'),
        ],
        default='both'
    )
    allowed_file_types = models.JSONField(default=list, blank=True)
    max_file_size = models.PositiveIntegerField(default=10, help_text="Maximum file size in MB")
    
    class Meta:
        verbose_name = _("Assignment Content")
        verbose_name_plural = _("Assignment Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'assignment'
        super().save(*args, **kwargs)


class LinkContent(LearningContent):
    """External link content"""
    url = models.URLField()
    preview_image = models.URLField(blank=True)
    open_in_new_tab = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Link Content")
        verbose_name_plural = _("Link Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'link'
        super().save(*args, **kwargs)


class FileContent(LearningContent):
    """File resource content"""
    file = models.FileField(upload_to='learning_files/%Y/%m/')
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _("File Content")
        verbose_name_plural = _("File Contents")
    
    def save(self, *args, **kwargs):
        self.content_type = 'file'
        super().save(*args, **kwargs)


# ==================== LEARNING MODULES ====================
class LearningModule(BaseNotesModel):
    """Organized collection of learning content"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    
    # Academic context
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modules'
    )
    grade_level = models.CharField(max_length=20, blank=True)
    curriculum = models.CharField(max_length=20, blank=True)
    
    # Organization
    categories = models.ManyToManyField(ContentCategory, related_name='modules', blank=True)
    tags = models.ManyToManyField(ContentTag, related_name='modules', blank=True)
    cover_image = models.ImageField(upload_to='module_covers/%Y/%m/', blank=True, null=True)
    
    # Module configuration
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_sequential = models.BooleanField(default=True, help_text="Must complete content in order")
    completion_threshold = models.PositiveIntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage to complete module"
    )
    
    # Statistics
    total_duration = models.PositiveIntegerField(default=0, help_text="Total duration in minutes")
    content_count = models.PositiveIntegerField(default=0)
    enrollments_count = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    class Meta:
        verbose_name = _("Learning Module")
        verbose_name_plural = _("Learning Modules")
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['completion_rate']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def total_contents(self):
        """Get total number of content items"""
        return self.contents.count()
    
    @property
    def duration_formatted(self):
        """Format total duration"""
        if self.total_duration < 60:
            return f"{self.total_duration} min"
        else:
            hours = self.total_duration // 60
            minutes = self.total_duration % 60
            if minutes:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
    
    def update_statistics(self):
        """Update module statistics"""
        with transaction.atomic():
            contents = self.contents.select_related('content').all()
            
            # Calculate total duration
            total_duration = sum(
                content.content.estimated_duration 
                for content in contents 
                if content.content.estimated_duration
            )
            
            # Count content items
            content_count = contents.count()
            
            # Update completion rate (requires enrollment data)
            # This would be calculated from EnrollmentProgress
            
            self.total_duration = total_duration
            self.content_count = content_count
            self.save(update_fields=['total_duration', 'content_count'])


class ModuleContent(BaseNotesModel):
    """Links content to modules with sequencing"""
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='contents')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='module_assignments')
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    unlock_after_previous = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['module', 'content']
        verbose_name = _("Module Content")
        verbose_name_plural = _("Module Contents")
    
    def __str__(self):
        return f"{self.module.name} - {self.content.title}"

    def clean(self):
        """Prevent circular dependencies"""
        if self.unlock_after_previous:
            # Check if this creates a circular dependency
            pass


# ==================== ENROLLMENTS AND PROGRESS ====================
class Enrollment(BaseNotesModel):
    """Student enrollment in learning modules"""
    student = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='enrollments_school',
        limit_choices_to={'role': 'student'}
    )
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped'),
            ('suspended', 'Suspended'),
        ],
        default='active'
    )
    grade = models.CharField(max_length=5, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'module']
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['module', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.module.name}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        try:
            progress = self.progress
            return progress.overall_progress if progress else 0
        except EnrollmentProgress.DoesNotExist:
            return 0
    
    @property
    def is_completed(self):
        """Check if enrollment is completed"""
        return self.status == 'completed' and self.completion_date is not None


class EnrollmentProgress(BaseNotesModel):
    """Tracks progress of enrollment"""
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    overall_progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completed_content = models.PositiveIntegerField(default=0)
    total_content = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    total_time_spent = models.PositiveIntegerField(default=0, help_text="Total time spent in minutes")
    
    class Meta:
        verbose_name = _("Enrollment Progress")
        verbose_name_plural = _("Enrollment Progress")
    
    def __str__(self):
        return f"Progress for {self.enrollment}"
    
    def update_progress(self):
        """Update progress statistics"""
        content_progress = ContentProgress.objects.filter(
            enrollment=self.enrollment,
            status='completed'
        ).count()
        
        total_content = self.enrollment.module.contents.count()
        
        if total_content > 0:
            self.completed_content = content_progress
            self.total_content = total_content
            self.overall_progress = int((content_progress / total_content) * 100)
            
            # Check if module is completed
            if self.overall_progress >= self.enrollment.module.completion_threshold:
                self.enrollment.status = 'completed'
                self.enrollment.completion_date = timezone.now()
                self.enrollment.save()
        
        self.save()


class ContentProgress(BaseNotesModel):
    """Tracks student progress for individual content items"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='content_progress')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('started', 'Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('reviewed', 'Reviewed'),
        ],
        default='not_started'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent in seconds")
    completion_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_position = models.PositiveIntegerField(default=0, help_text="For video/audio content")
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['enrollment', 'content']
        verbose_name = _("Content Progress")
        verbose_name_plural = _("Content Progress")
        indexes = [
            models.Index(fields=['enrollment', 'status']),
            models.Index(fields=['content', 'status']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student.get_full_name()} - {self.content.title}"
    
    def start_content(self):
        """Mark content as started"""
        if self.status == 'not_started':
            self.status = 'started'
            self.started_at = timezone.now()
            self.save()
    
    def update_progress(self, percentage, time_spent=0):
        """Update progress percentage"""
        self.completion_percentage = min(100, max(0, percentage))
        self.time_spent += time_spent
        
        if self.completion_percentage >= 100:
            self.mark_completed()
        elif self.completion_percentage > 0:
            self.status = 'in_progress'
        
        self.save()
        
        # Update enrollment progress
        self.enrollment.progress.update_progress()
    
    def mark_completed(self, score=None):
        """Mark content as completed"""
        self.status = 'completed'
        self.completion_percentage = 100
        self.completed_at = timezone.now()
        
        if score is not None:
            self.score = score
        
        self.save()
        
        # Update enrollment progress
        self.enrollment.progress.update_progress()


# ==================== ASSESSMENTS AND QUIZZES ====================
class Question(BaseNotesModel):
    """Question for quizzes and assessments"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('matching', 'Matching'),
        ('fill_blank', 'Fill in the Blank'),
        ('ordering', 'Ordering'),
    ]
    
    content = models.ForeignKey(
        LearningContent,
        on_delete=models.CASCADE,
        related_name='questions',
        limit_choices_to={'content_type': 'quiz'}
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    text = models.TextField()
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(max_length=20, choices=LearningContent.DIFFICULTY_LEVELS, default='intermediate')
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:100]}..."


class QuestionChoice(BaseNotesModel):
    """Choices for multiple choice questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Question Choice")
        verbose_name_plural = _("Question Choices")
    
    def __str__(self):
        return f"Choice {self.order} for Q{self.question.order}"


class QuizAttempt(BaseNotesModel):
    """Student attempt at a quiz"""
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='quiz_attempts')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(default=0, help_text="Time taken in seconds")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = _("Quiz Attempt")
        verbose_name_plural = _("Quiz Attempts")
        indexes = [
            models.Index(fields=['student', 'content']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.content.title}"
    
    def calculate_score(self):
        """Calculate final score"""
        answers = self.answers.all()
        total_points = sum(answer.question.points for answer in answers)
        earned_points = sum(answer.points_earned for answer in answers)
        
        if total_points > 0:
            self.score = earned_points
            self.percentage = (earned_points / total_points) * 100
            self.is_passed = self.percentage >= self.content.quizcontent.passing_score
        
        self.save()


class QuizAnswer(BaseNotesModel):
    """Student's answer to a quiz question"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True)
    selected_choices = models.ManyToManyField(QuestionChoice, blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
        verbose_name = _("Quiz Answer")
        verbose_name_plural = _("Quiz Answers")
    
    def __str__(self):
        return f"Answer for Q{self.question.order} in {self.attempt}"


# ==================== NOTES AND ANNOTATIONS ====================
class ContentNote(BaseNotesModel):
    """Student notes on content"""
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='content_notes')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, blank=True)
    note = models.TextField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    position = models.JSONField(default=dict, blank=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Content Note")
        verbose_name_plural = _("Content Notes")
    
    def __str__(self):
        return f"Note by {self.student.get_full_name()} on {self.content.title}"


class ContentAnnotation(BaseNotesModel):
    """Annotations on content (highlights, comments, etc.)"""
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='annotations')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='annotations')
    annotation_type = models.CharField(
        max_length=20,
        choices=[
            ('highlight', 'Highlight'),
            ('comment', 'Comment'),
            ('bookmark', 'Bookmark'),
            ('question', 'Question'),
        ]
    )
    text = models.TextField(blank=True)
    position = models.JSONField(default=dict)
    color = models.CharField(max_length=7, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Content Annotation")
        verbose_name_plural = _("Content Annotations")
    
    def __str__(self):
        return f"{self.get_annotation_type_display()} by {self.student.get_full_name()}"


# ==================== RATINGS AND REVIEWS ====================
class ContentRating(BaseNotesModel):
    """User ratings for content"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='content_ratings')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'content']
        verbose_name = _("Content Rating")
        verbose_name_plural = _("Content Ratings")
    
    def __str__(self):
        return f"{self.rating}★ by {self.user.get_full_name()} for {self.content.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update content average rating
        self.content.update_average_rating()


class ContentReview(BaseNotesModel):
    """Detailed reviews for content"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='content_reviews')
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200)
    review = models.TextField()
    helpful_votes = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Content Review")
        verbose_name_plural = _("Content Reviews")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} on {self.content.title}"


# ==================== ANALYTICS AND REPORTS ====================
class ContentAnalytics(BaseNotesModel):
    """Analytics for learning content"""
    content = models.OneToOneField(LearningContent, on_delete=models.CASCADE, related_name='analytics')
    total_views = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_time_spent = models.PositiveIntegerField(default=0)
    popular_times = models.JSONField(default=list, blank=True)
    drop_off_points = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = _("Content Analytics")
        verbose_name_plural = _("Content Analytics")
    
    def __str__(self):
        return f"Analytics for {self.content.title}"
    
    def update_analytics(self):
        """Update analytics data"""
        progress_records = ContentProgress.objects.filter(content=self.content)
        
        if progress_records.exists():
            self.total_views = progress_records.count()
            self.unique_viewers = progress_records.values('enrollment__student').distinct().count()
            
            completed = progress_records.filter(status='completed').count()
            self.completion_rate = (completed / self.total_views * 100) if self.total_views > 0 else 0
            
            avg_time = progress_records.aggregate(avg=Avg('time_spent'))['avg'] or 0
            self.average_time_spent = avg_time
        
        self.save()


class ModuleAnalytics(BaseNotesModel):
    """Analytics for learning modules"""
    module = models.OneToOneField(LearningModule, on_delete=models.CASCADE, related_name='analytics')
    total_enrollments = models.PositiveIntegerField(default=0)
    active_enrollments = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    popular_content = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = _("Module Analytics")
        verbose_name_plural = _("Module Analytics")
    
    def __str__(self):
        return f"Analytics for {self.module.name}"
    
    def update_analytics(self):
        """Update module analytics"""
        enrollments = self.module.enrollments.all()
        
        self.total_enrollments = enrollments.count()
        self.active_enrollments = enrollments.filter(status='active').count()
        
        completed = enrollments.filter(status='completed').count()
        self.completion_rate = (completed / self.total_enrollments * 100) if self.total_enrollments > 0 else 0
        
        # Calculate average grade
        grades = enrollments.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        self.average_grade = grades
        
        self.save()


# ==================== SIGNALS ====================
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

@receiver(post_save, sender=LearningContent)
def create_content_analytics(sender, instance, created, **kwargs):
    """Create analytics record for new content"""
    if created:
        ContentAnalytics.objects.create(content=instance)

@receiver(post_save, sender=LearningModule)
def create_module_analytics(sender, instance, created, **kwargs):
    """Create analytics record for new module"""
    if created:
        ModuleAnalytics.objects.create(module=instance)

@receiver(post_save, sender=ContentRating)
def update_content_rating(sender, instance, **kwargs):
    """Update content average rating when new rating is added"""
    ratings = instance.content.ratings.all()
    if ratings.exists():
        average = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        instance.content.average_rating = average
        instance.content.save(update_fields=['average_rating'])

@receiver(post_save, sender=Enrollment)
def create_enrollment_progress(sender, instance, created, **kwargs):
    """Create progress tracking for new enrollment"""
    if created:
        EnrollmentProgress.objects.create(enrollment=instance)

# FIXED VERSION - Replace the problematic signal:
# OLD (incorrect):
# @receiver(m2m_changed, sender=ModuleContent.through)
# def update_module_statistics(sender, instance, action, **kwargs):
#     """Update module statistics when content changes"""
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         if isinstance(instance, LearningModule):
#             instance.update_statistics()
#         elif isinstance(instance, LearningContent):
#             # Update all modules containing this content
#             for module in instance.module_assignments.all():
#                 module.module.update_statistics()

# NEW (corrected):
@receiver([post_save, post_delete], sender=ModuleContent)
def update_module_statistics(sender, instance, **kwargs):
    """Update module statistics when ModuleContent is saved or deleted"""
    try:
        # Update the specific module's statistics
        module = instance.module
        module.update_statistics()
    except AttributeError:
        pass  # In case instance doesn't have a module attribute