"""
Enhanced REST API Serializers for Notes and Learning Content Management System
Features:
1. Comprehensive serializers for all models
2. Nested relationships with optimization
3. Progress tracking serializers
4. Bulk operations support
5. Statistics and analytics
6. Permission-based serialization
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse
import uuid
import logging

from .models import (
    # Core Models
    ContentCategory, ContentTag, LearningContent,
    
    # Content Types
    TextContent, VideoContent, AudioContent, PDFContent,
    PresentationContent, InteractiveContent, QuizContent,
    AssignmentContent, LinkContent, FileContent,
    
    # Modules
    LearningModule, ModuleContent,
    
    # Progress Tracking
    Enrollment, EnrollmentProgress, ContentProgress,
    
    # Assessments
    Question, QuestionChoice, QuizAttempt, QuizAnswer,
    
    # User Interactions
    ContentNote, ContentAnnotation, ContentRating, ContentReview,
    
    # Analytics
    ContentAnalytics, ModuleAnalytics
)

User = get_user_model()
logger = logging.getLogger(__name__)


# ==================== UTILITY SERIALIZERS ====================
class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for related fields"""
    full_name = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'initials', 'profile_picture', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_initials(self, obj):
        return obj.get_initials()


class ContentCategorySerializer(serializers.ModelSerializer):
    """Serializer for content categories"""
    content_count = serializers.IntegerField(read_only=True)
    subcategory_count = serializers.IntegerField(read_only=True)
    tree_path = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContentCategory
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'icon', 'color',
            'order', 'curriculum', 'content_count', 'subcategory_count',
            'tree_path', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class ContentTagSerializer(serializers.ModelSerializer):
    """Serializer for content tags"""
    
    class Meta:
        model = ContentTag
        fields = ['id', 'name', 'slug', 'description', 'usage_count', 'is_active']
        read_only_fields = ['slug', 'usage_count']


# ==================== LEARNING CONTENT BASE SERIALIZER ====================
class LearningContentBaseSerializer(serializers.ModelSerializer):
    """Base serializer for all learning content types"""
    author_details = UserMinimalSerializer(source='author', read_only=True)
    reviewed_by_details = UserMinimalSerializer(source='reviewed_by', read_only=True)
    categories_details = ContentCategorySerializer(source='categories', many=True, read_only=True)
    tags_details = ContentTagSerializer(source='tags', many=True, read_only=True)
    
    # Content type specific
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    access_level_display = serializers.CharField(source='get_access_level_display', read_only=True)
    
    # Formatted fields
    duration_formatted = serializers.CharField(read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    # Progress tracking for authenticated users
    user_progress = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    can_access = serializers.SerializerMethodField()
    
    # Statistics
    average_rating_stars = serializers.SerializerMethodField()
    completion_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = LearningContent
        fields = [
            # Basic Info
            'id', 'title', 'slug', 'description', 'content_type', 'content_type_display',
            'status', 'status_display', 'difficulty_level', 'difficulty_display',
            
            # Academic Context
            'subject', 'subject_name', 'grade_level', 'curriculum',
            
            # Organization
            'categories', 'categories_details', 'tags', 'tags_details',
            
            # Learning Objectives
            'learning_objectives', 'prerequisites', 'learning_outcomes',
            
            # Timing
            'estimated_duration', 'duration_formatted', 'publish_date', 'expiry_date',
            
            # Access Control
            'is_public', 'access_level', 'access_level_display', 'allowed_users',
            'password_protected', 'access_password',
            
            # Resources
            'resources', 'references',
            
            # Author & Review
            'author', 'author_details', 'reviewed_by', 'reviewed_by_details',
            'reviewed_at', 'review_notes',
            
            # Engagement
            'views_count', 'likes_count', 'shares_count', 'average_rating',
            'average_rating_stars', 'completion_count', 'completion_rate',
            
            # SEO & Metadata
            'meta_title', 'meta_description', 'keywords',
            
            # Versioning
            'version', 'parent_version',
            
            # User-specific
            'user_progress', 'is_completed', 'can_access',
            
            # System
            'created_at', 'updated_at', 'last_accessed', 'is_active'
        ]
        read_only_fields = [
            'slug', 'views_count', 'likes_count', 'shares_count', 'average_rating',
            'completion_count', 'completion_rate', 'created_at', 'updated_at',
            'last_accessed'
        ]
    
    def get_user_progress(self, obj):
        """Get progress for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.filter(
                    student=request.user,
                    module__contents__content=obj
                ).first()
                
                if enrollment:
                    progress = ContentProgress.objects.filter(
                        enrollment=enrollment,
                        content=obj
                    ).first()
                    if progress:
                        return ContentProgressSerializer(progress, context=self.context).data
            except Exception as e:
                logger.error(f"Error getting user progress: {e}")
        return None
    
    def get_is_completed(self, obj):
        """Check if content is completed by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.filter(
                    student=request.user,
                    module__contents__content=obj
                ).first()
                
                if enrollment:
                    return ContentProgress.objects.filter(
                        enrollment=enrollment,
                        content=obj,
                        status='completed'
                    ).exists()
            except Exception as e:
                logger.error(f"Error checking completion: {e}")
        return False
    
    def get_can_access(self, obj):
        """Check if user can access this content"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.is_public and obj.access_level == 'public'
        
        user = request.user
        
        # Check if content is published
        if not obj.is_published:
            return False
        
        # Check access level
        if obj.access_level == 'public':
            return True
        elif obj.access_level == 'authenticated':
            return user.is_authenticated
        elif obj.access_level == 'students':
            return user.role == 'student'
        elif obj.access_level == 'teachers':
            return user.role in ['teacher', 'head_teacher']
        elif obj.access_level == 'premium':
            # Implement premium user check
            return False
        elif obj.access_level == 'specific':
            return user in obj.allowed_users.all()
        
        return False
    
    def get_average_rating_stars(self, obj):
        """Get star representation of average rating"""
        if obj.average_rating:
            full_stars = int(obj.average_rating)
            half_star = obj.average_rating - full_stars >= 0.5
            empty_stars = 5 - full_stars - (1 if half_star else 0)
            
            stars = '★' * full_stars
            if half_star:
                stars += '½'
            stars += '☆' * empty_stars
            
            return stars
        return '☆☆☆☆☆'
    
    def validate(self, data):
        """Validate content data"""
        if 'expiry_date' in data and 'publish_date' in data:
            if data['expiry_date'] <= data['publish_date']:
                raise serializers.ValidationError({
                    'expiry_date': 'Expiry date must be after publish date'
                })
        
        # Validate access password
        if data.get('password_protected') and not data.get('access_password'):
            raise serializers.ValidationError({
                'access_password': 'Password is required when content is password protected'
            })
        
        return data
    
    def create(self, validated_data):
        """Create content with author"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            validated_data['author'] = request.user
        
        # Handle categories and tags
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        
        with transaction.atomic():
            content = super().create(validated_data)
            content.categories.set(categories)
            content.tags.set(tags)
            
            # Create analytics record
            ContentAnalytics.objects.create(content=content)
            
            return content


# ==================== SPECIFIC CONTENT TYPE SERIALIZERS ====================
class TextContentSerializer(LearningContentBaseSerializer):
    """Serializer for text content"""
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = TextContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'content', 'format', 'word_count'
        ]


class VideoContentSerializer(LearningContentBaseSerializer):
    """Serializer for video content"""
    duration_formatted = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = VideoContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'video_url', 'video_file', 'thumbnail', 'thumbnail_url',
            'duration_seconds', 'transcript', 'captions_url', 'quality_options'
        ]
    
    def get_duration_formatted(self, obj):
        return obj.duration_formatted
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class AudioContentSerializer(LearningContentBaseSerializer):
    """Serializer for audio content"""
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = AudioContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'audio_file', 'duration_seconds', 'transcript', 'bitrate'
        ]
    
    def get_duration_formatted(self, obj):
        return obj.duration_formatted


class PDFContentSerializer(LearningContentBaseSerializer):
    """Serializer for PDF content"""
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = PDFContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'pdf_file', 'page_count', 'file_size', 'allow_printing', 'allow_download'
        ]
    
    def get_file_size_mb(self, obj):
        return obj.file_size_mb


class PresentationContentSerializer(LearningContentBaseSerializer):
    """Serializer for presentation content"""
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = PresentationContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'presentation_file', 'slide_count', 'speaker_notes'
        ]


class InteractiveContentSerializer(LearningContentBaseSerializer):
    """Serializer for interactive content"""
    interactive_type_display = serializers.CharField(source='get_interactive_type_display', read_only=True)
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = InteractiveContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'interactive_type', 'interactive_type_display',
            'interactive_file', 'embed_code', 'parameters'
        ]


class QuizContentSerializer(LearningContentBaseSerializer):
    """Serializer for quiz content"""
    question_count = serializers.IntegerField(read_only=True)
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = QuizContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'total_questions', 'passing_score', 'time_limit',
            'shuffle_questions', 'show_results', 'question_count'
        ]


class AssignmentContentSerializer(LearningContentBaseSerializer):
    """Serializer for assignment content"""
    is_submission_open = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = AssignmentContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'due_date', 'max_score', 'submission_type', 'submission_type_display',
            'allowed_file_types', 'max_file_size', 'is_submission_open', 'days_until_due'
        ]
    
    def get_is_submission_open(self, obj):
        if not obj.due_date:
            return True
        return timezone.now() <= obj.due_date
    
    def get_days_until_due(self, obj):
        if obj.due_date:
            delta = obj.due_date - timezone.now()
            return max(0, delta.days)
        return None


class LinkContentSerializer(LearningContentBaseSerializer):
    """Serializer for link content"""
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = LinkContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'url', 'preview_image', 'open_in_new_tab'
        ]


class FileContentSerializer(LearningContentBaseSerializer):
    """Serializer for file content"""
    file_size_mb = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta(LearningContentBaseSerializer.Meta):
        model = FileContent
        fields = LearningContentBaseSerializer.Meta.fields + [
            'file', 'file_url', 'file_type', 'file_size', 'file_size_mb'
        ]
    
    def get_file_size_mb(self, obj):
        return obj.file_size_mb
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


# ==================== MODULE SERIALIZERS ====================
class ModuleContentSerializer(serializers.ModelSerializer):
    """Serializer for module contents"""
    content_details = serializers.SerializerMethodField()
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleContent
        fields = [
            'id', 'module', 'content', 'order', 'is_required',
            'unlock_after_previous', 'content_details', 'content_type_display',
            'is_unlocked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_content_details(self, obj):
        """Get the actual content object"""
        if obj.content:
            serializer_class = self.get_content_serializer(obj.content)
            if serializer_class:
                return serializer_class(obj.content, context=self.context).data
        return None
    
    def get_content_serializer(self, content):
        """Get appropriate serializer for content type"""
        serializer_map = {
            'textcontent': TextContentSerializer,
            'videocontent': VideoContentSerializer,
            'audiocontent': AudioContentSerializer,
            'pdfcontent': PDFContentSerializer,
            'presentationcontent': PresentationContentSerializer,
            'interactivecontent': InteractiveContentSerializer,
            'quizcontent': QuizContentSerializer,
            'assignmentcontent': AssignmentContentSerializer,
            'linkcontent': LinkContentSerializer,
            'filecontent': FileContentSerializer,
        }
        return serializer_map.get(content._meta.model_name.lower())
    
    def get_is_unlocked(self, obj):
        """Check if content is unlocked for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # For now, return True. Implement proper unlocking logic
            return True
        return False


class LearningModuleSerializer(serializers.ModelSerializer):
    """Serializer for learning modules"""
    author_details = UserMinimalSerializer(source='author', read_only=True)
    categories_details = ContentCategorySerializer(source='categories', many=True, read_only=True)
    tags_details = ContentTagSerializer(source='tags', many=True, read_only=True)
    
    # Formatted fields
    duration_formatted = serializers.CharField(read_only=True)
    completion_rate_formatted = serializers.CharField(read_only=True)
    
    # Contents
    contents = ModuleContentSerializer(many=True, read_only=True, source='module_content')
    
    # Student progress
    student_enrollment = serializers.SerializerMethodField()
    student_progress = serializers.SerializerMethodField()
    next_content = serializers.SerializerMethodField()
    
    # Statistics
    enrollment_count = serializers.IntegerField(read_only=True)
    completion_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LearningModule
        fields = [
            # Basic Info
            'id', 'name', 'slug', 'description', 'short_description',
            
            # Academic Context
            'subject', 'subject_name', 'grade_level', 'curriculum',
            
            # Organization
            'categories', 'categories_details', 'tags', 'tags_details',
            'cover_image', 'cover_image_url',
            
            # Configuration
            'is_public', 'is_featured', 'is_sequential', 'completion_threshold',
            
            # Statistics
            'total_duration', 'duration_formatted', 'content_count',
            'enrollments_count', 'completion_rate', 'completion_rate_formatted',
            'average_rating', 'enrollment_count', 'completion_count',
            
            # Contents
            'contents',
            
            # Student-specific
            'student_enrollment', 'student_progress', 'next_content',
            
            # Author
            'author', 'author_details',
            
            # System
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'slug', 'total_duration', 'content_count', 'enrollments_count',
            'completion_rate', 'average_rating', 'created_at', 'updated_at'
        ]
    
    def get_student_enrollment(self, obj):
        """Get student's enrollment in this module"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            try:
                enrollment = Enrollment.objects.get(
                    student=request.user,
                    module=obj
                )
                return EnrollmentSerializer(enrollment, context=self.context).data
            except Enrollment.DoesNotExist:
                return None
        return None
    
    def get_student_progress(self, obj):
        """Get student's progress in this module"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            try:
                progress = EnrollmentProgress.objects.get(
                    enrollment__student=request.user,
                    enrollment__module=obj
                )
                return EnrollmentProgressSerializer(progress, context=self.context).data
            except EnrollmentProgress.DoesNotExist:
                return None
        return None
    
    def get_next_content(self, obj):
        """Get next content for student"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            try:
                enrollment = Enrollment.objects.get(
                    student=request.user,
                    module=obj
                )
                
                # Get completed content IDs
                completed_ids = ContentProgress.objects.filter(
                    enrollment=enrollment,
                    status='completed'
                ).values_list('content_id', flat=True)
                
                # Find next content
                next_content = ModuleContent.objects.filter(
                    module=obj,
                    content_id__isnull=False
                ).exclude(
                    content_id__in=completed_ids
                ).order_by('order').first()
                
                if next_content:
                    return ModuleContentSerializer(next_content, context=self.context).data
            except (Enrollment.DoesNotExist, Exception) as e:
                logger.error(f"Error getting next content: {e}")
        return None
    
    def validate(self, data):
        """Validate module data"""
        if data.get('completion_threshold', 0) > 100:
            raise serializers.ValidationError({
                'completion_threshold': 'Completion threshold cannot exceed 100%'
            })
        return data
    
    def create(self, validated_data):
        """Create module with author"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            validated_data['author'] = request.user
        
        # Handle categories and tags
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        
        with transaction.atomic():
            module = super().create(validated_data)
            module.categories.set(categories)
            module.tags.set(tags)
            
            # Create analytics record
            ModuleAnalytics.objects.create(module=module)
            
            return module


# ==================== ENROLLMENT SERIALIZERS ====================
class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments"""
    student_details = UserMinimalSerializer(source='student', read_only=True)
    module_details = LearningModuleSerializer(source='module', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_details', 'module', 'module_details',
            'enrolled_at', 'completion_date', 'status', 'status_display',
            'grade', 'score', 'certificate_issued', 'certificate_issued_at',
            'days_enrolled', 'progress_percentage',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['enrolled_at', 'created_at', 'updated_at']
    
    def get_days_enrolled(self, obj):
        """Calculate days since enrollment"""
        if obj.enrolled_at:
            delta = timezone.now() - obj.enrolled_at
            return delta.days
        return 0
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        try:
            return obj.progress.overall_progress
        except EnrollmentProgress.DoesNotExist:
            return 0
    
    def validate(self, data):
        """Validate enrollment data"""
        student = data.get('student')
        module = data.get('module')
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=student, module=module).exists():
            raise serializers.ValidationError({
                'student': 'Student is already enrolled in this module'
            })
        
        return data
    
    def create(self, validated_data):
        """Create enrollment with progress tracking"""
        with transaction.atomic():
            enrollment = super().create(validated_data)
            
            # Create progress record
            EnrollmentProgress.objects.create(enrollment=enrollment)
            
            # Create content progress records
            module_contents = ModuleContent.objects.filter(module=enrollment.module)
            for module_content in module_contents:
                ContentProgress.objects.create(
                    enrollment=enrollment,
                    content=module_content.content,
                    status='not_started'
                )
            
            # Update module enrollment count
            enrollment.module.enrollments_count = Enrollment.objects.filter(
                module=enrollment.module
            ).count()
            enrollment.module.save()
            
            return enrollment


class EnrollmentProgressSerializer(serializers.ModelSerializer):
    """Serializer for enrollment progress"""
    enrollment_details = EnrollmentSerializer(source='enrollment', read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    time_spent_formatted = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = EnrollmentProgress
        fields = [
            'id', 'enrollment', 'enrollment_details', 'overall_progress',
            'completed_content', 'total_content', 'progress_percentage',
            'last_accessed', 'total_time_spent', 'time_spent_formatted',
            'completion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_time_spent_formatted(self, obj):
        """Format total time spent"""
        if obj.total_time_spent < 60:
            return f"{obj.total_time_spent} min"
        else:
            hours = obj.total_time_spent // 60
            minutes = obj.total_time_spent % 60
            if minutes:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
    
    def get_completion_rate(self, obj):
        """Calculate completion rate"""
        if obj.total_content > 0:
            return (obj.completed_content / obj.total_content) * 100
        return 0


# ==================== PROGRESS TRACKING SERIALIZERS ===================class ContentProgressUpdateSerializer(serializers.Serializer):
    """Serializer for updating content progress"""
    completion_percentage = serializers.IntegerField(
        min_value=0, 
        max_value=100, 
        required=False,
        help_text="Completion percentage (0-100)"
    )
    time_spent = serializers.IntegerField(
        min_value=0, 
        required=False,
        help_text="Time spent in seconds"
    )
    
    # FIXED: Replace ContentProgress.STATUS_CHOICES with direct choices
    status = serializers.ChoiceField(
        choices=[
            ('not_started', 'Not Started'),
            ('started', 'Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('reviewed', 'Reviewed'),
        ],
        required=False,
        help_text="Progress status"
    )
    
    notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Optional notes"
    )
    last_position = serializers.IntegerField(
        min_value=0, 
        required=False,
        help_text="Last position (for video/audio content)"
    )
    score = serializers.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        required=False,
        min_value=0,
        help_text="Score if applicable"
    )
    
    def update(self, instance, validated_data):
        """Update content progress instance"""
        # Update completion percentage
        if 'completion_percentage' in validated_data:
            instance.completion_percentage = validated_data['completion_percentage']
        
        # Update time spent
        if 'time_spent' in validated_data:
            instance.time_spent += validated_data['time_spent']
        
        # Update status
        if 'status' in validated_data:
            instance.status = validated_data['status']
            
            # Set timestamps based on status
            if validated_data['status'] == 'started' and not instance.started_at:
                instance.started_at = timezone.now()
            elif validated_data['status'] == 'completed' and not instance.completed_at:
                instance.completed_at = timezone.now()
        
        # Update other fields
        if 'notes' in validated_data:
            instance.notes = validated_data['notes']
        
        if 'last_position' in validated_data:
            instance.last_position = validated_data['last_position']
        
        if 'score' in validated_data:
            instance.score = validated_data['score']
        
        # Save the instance
        instance.save()
        
        # Update enrollment progress
        instance.enrollment.progress.update_progress()
        
        return instance
    
    def validate(self, data):
        """Validate the data"""
        # Ensure completion percentage doesn't exceed 100
        if 'completion_percentage' in data and data['completion_percentage'] > 100:
            raise serializers.ValidationError({
                'completion_percentage': 'Cannot exceed 100%'
            })
        
        # If marking as completed, ensure percentage is 100
        if data.get('status') == 'completed' and 'completion_percentage' in data:
            if data['completion_percentage'] < 100:
                data['completion_percentage'] = 100
        
        return data

class ContentProgressSerializer(serializers.ModelSerializer):
    """Serializer for content progress"""
    enrollment_details = EnrollmentSerializer(source='enrollment', read_only=True)
    content_details = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_spent_formatted = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentProgress
        fields = [
            'id', 'enrollment', 'enrollment_details', 'content', 'content_details',
            'status', 'status_display', 'started_at', 'completed_at',
            'time_spent', 'time_spent_formatted', 'completion_percentage',
            'score', 'attempts', 'last_position', 'notes', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['started_at', 'completed_at', 'created_at', 'updated_at']
    
    def get_content_details(self, obj):
        """Get content details"""
        if obj.content:
            serializer_class = self.get_content_serializer(obj.content)
            if serializer_class:
                return serializer_class(obj.content, context=self.context).data
        return None
    
    def get_content_serializer(self, content):
        """Get appropriate serializer for content type"""
        serializer_map = {
            'textcontent': TextContentSerializer,
            'videocontent': VideoContentSerializer,
            'audiocontent': AudioContentSerializer,
            'pdfcontent': PDFContentSerializer,
            'presentationcontent': PresentationContentSerializer,
            'interactivecontent': InteractiveContentSerializer,
            'quizcontent': QuizContentSerializer,
            'assignmentcontent': AssignmentContentSerializer,
            'linkcontent': LinkContentSerializer,
            'filecontent': FileContentSerializer,
        }
        return serializer_map.get(content._meta.model_name.lower())
    
    def get_time_spent_formatted(self, obj):
        """Format time spent"""
        if obj.time_spent < 60:
            return f"{obj.time_spent}s"
        else:
            minutes = obj.time_spent // 60
            seconds = obj.time_spent % 60
            return f"{minutes}m {seconds}s"
    
    def get_is_overdue(self, obj):
        """Check if assignment is overdue"""
        if hasattr(obj.content, 'assignmentcontent'):
            assignment = obj.content.assignmentcontent
            if assignment.due_date and timezone.now() > assignment.due_date:
                return True
        return False


class ContentProgressUpdateSerializer(serializers.Serializer):
    """Serializer for updating content progress"""
    completion_percentage = serializers.IntegerField(
        min_value=0, 
        max_value=100, 
        required=False,
        help_text="Completion percentage (0-100)"
    )
    time_spent = serializers.IntegerField(
        min_value=0, 
        required=False,
        help_text="Time spent in seconds"
    )
    
    # FIXED: Use direct choices
    status = serializers.ChoiceField(
        choices=[
            ('not_started', 'Not Started'),
            ('started', 'Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('reviewed', 'Reviewed'),
        ],
        required=False,
        help_text="Progress status"
    )
    
    notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Optional notes"
    )
    last_position = serializers.IntegerField(
        min_value=0, 
        required=False,
        help_text="Last position (for video/audio content)"
    )
    score = serializers.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        required=False,
        min_value=0,
        help_text="Score if applicable"
    )
    
    def update(self, instance, validated_data):
        """Update content progress instance"""
        # Update completion percentage
        if 'completion_percentage' in validated_data:
            instance.completion_percentage = validated_data['completion_percentage']
        
        # Update time spent
        if 'time_spent' in validated_data:
            instance.time_spent += validated_data['time_spent']
        
        # Update status
        if 'status' in validated_data:
            instance.status = validated_data['status']
            
            # Set timestamps based on status
            if validated_data['status'] == 'started' and not instance.started_at:
                instance.started_at = timezone.now()
            elif validated_data['status'] == 'completed' and not instance.completed_at:
                instance.completed_at = timezone.now()
        
        # Update other fields
        if 'notes' in validated_data:
            instance.notes = validated_data['notes']
        
        if 'last_position' in validated_data:
            instance.last_position = validated_data['last_position']
        
        if 'score' in validated_data:
            instance.score = validated_data['score']
        
        # Save the instance
        instance.save()
        
        # Update enrollment progress
        if hasattr(instance.enrollment, 'progress'):
            instance.enrollment.progress.update_progress()
        
        return instance
    
    def validate(self, data):
        """Validate the data"""
        # Ensure completion percentage doesn't exceed 100
        if 'completion_percentage' in data and data['completion_percentage'] > 100:
            raise serializers.ValidationError({
                'completion_percentage': 'Cannot exceed 100%'
            })
        
        # If marking as completed, ensure percentage is 100
        if data.get('status') == 'completed' and 'completion_percentage' in data:
            if data['completion_percentage'] < 100:
                data['completion_percentage'] = 100
        
        return data



# ==================== ASSESSMENT SERIALIZERS ====================
class QuestionChoiceSerializer(serializers.ModelSerializer):
    """Serializer for question choices"""
    
    class Meta:
        model = QuestionChoice
        fields = ['id', 'question', 'text', 'is_correct', 'order', 'feedback']
        read_only_fields = ['question']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions"""
    choices = QuestionChoiceSerializer(many=True, read_only=True)
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'content', 'question_type', 'question_type_display',
            'text', 'explanation', 'points', 'order', 'difficulty',
            'difficulty_display', 'choices'
        ]


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for quiz answers"""
    question_details = QuestionSerializer(source='question', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'attempt', 'question', 'question_details',
            'answer_text', 'selected_choices', 'is_correct',
            'points_earned', 'feedback'
        ]
        read_only_fields = ['attempt', 'is_correct', 'points_earned']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts"""
    student_details = UserMinimalSerializer(source='student', read_only=True)
    content_details = QuizContentSerializer(source='content', read_only=True)
    answers = QuizAnswerSerializer(many=True, read_only=True)
    time_taken_formatted = serializers.SerializerMethodField()
    passing_score = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'student_details', 'content', 'content_details',
            'started_at', 'completed_at', 'score', 'percentage', 'is_passed',
            'time_taken', 'time_taken_formatted', 'passing_score', 'answers',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['started_at', 'created_at', 'updated_at']
    
    def get_time_taken_formatted(self, obj):
        """Format time taken"""
        if obj.time_taken < 60:
            return f"{obj.time_taken}s"
        else:
            minutes = obj.time_taken // 60
            seconds = obj.time_taken % 60
            return f"{minutes}m {seconds}s"
    
    def get_passing_score(self, obj):
        """Get passing score for this quiz"""
        if hasattr(obj.content, 'quizcontent'):
            return obj.content.quizcontent.passing_score
        return 70  # Default passing score
    
    def validate(self, data):
        """Validate quiz attempt"""
        # Check if quiz has time limit
        if hasattr(data['content'], 'quizcontent'):
            quiz = data['content'].quizcontent
            if quiz.time_limit > 0:
                # Check if time has expired
                pass  # Implement time check logic
        
        return data
    
    def create(self, validated_data):
        """Create quiz attempt"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['student'] = request.user
        
        with transaction.atomic():
            attempt = super().create(validated_data)
            
            # Auto-calculate score if answers are provided
            if 'answers' in self.initial_data:
                attempt.calculate_score()
            
            return attempt


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submissions"""
    answers = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    
    def validate(self, data):
        """Validate quiz submission"""
        if not data.get('answers'):
            raise serializers.ValidationError({
                'answers': 'At least one answer is required'
            })
        
        # Validate each answer
        for answer in data['answers']:
            if 'question_id' not in answer:
                raise serializers.ValidationError({
                    'answers': 'Each answer must have a question_id'
                })
        
        return data


# ==================== USER INTERACTION SERIALIZERS ====================
class ContentNoteSerializer(serializers.ModelSerializer):
    """Serializer for content notes"""
    student_details = UserMinimalSerializer(source='student', read_only=True)
    content_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentNote
        fields = [
            'id', 'student', 'student_details', 'content', 'content_details',
            'title', 'note', 'page_number', 'position', 'is_public',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at']
    
    def get_content_details(self, obj):
        """Get content details"""
        if obj.content:
            return {
                'id': str(obj.content.id),
                'title': obj.content.title,
                'content_type': obj.content.content_type
            }
        return None
    
    def create(self, validated_data):
        """Create note with student"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['student'] = request.user
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class ContentAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for content annotations"""
    student_details = UserMinimalSerializer(source='student', read_only=True)
    annotation_type_display = serializers.CharField(source='get_annotation_type_display', read_only=True)
    
    class Meta:
        model = ContentAnnotation
        fields = [
            'id', 'student', 'student_details', 'content',
            'annotation_type', 'annotation_type_display',
            'text', 'position', 'color',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at']


class ContentRatingSerializer(serializers.ModelSerializer):
    """Serializer for content ratings"""
    user_details = UserMinimalSerializer(source='user', read_only=True)
    rating_stars = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentRating
        fields = [
            'id', 'user', 'user_details', 'content',
            'rating', 'rating_stars', 'comment',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_rating_stars(self, obj):
        """Get star representation of rating"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return stars
    
    def validate(self, data):
        """Validate rating"""
        if 'rating' in data and (data['rating'] < 1 or data['rating'] > 5):
            raise serializers.ValidationError({
                'rating': 'Rating must be between 1 and 5'
            })
        
        return data
    
    def create(self, validated_data):
        """Create rating with user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            validated_data['created_by'] = request.user
        
        # Check if user already rated this content
        existing = ContentRating.objects.filter(
            user=validated_data['user'],
            content=validated_data['content']
        ).first()
        
        if existing:
            # Update existing rating
            for attr, value in validated_data.items():
                setattr(existing, attr, value)
            existing.save()
            return existing
        
        return super().create(validated_data)


class ContentReviewSerializer(serializers.ModelSerializer):
    """Serializer for content reviews"""
    user_details = UserMinimalSerializer(source='user', read_only=True)
    content_details = serializers.SerializerMethodField()
    helpful_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentReview
        fields = [
            'id', 'user', 'user_details', 'content', 'content_details',
            'title', 'review', 'helpful_votes', 'helpful_percentage',
            'is_approved', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['user', 'helpful_votes', 'created_at', 'updated_at']
    
    def get_content_details(self, obj):
        """Get content details"""
        if obj.content:
            return {
                'id': str(obj.content.id),
                'title': obj.content.title,
                'content_type': obj.content.content_type
            }
        return None
    
    def get_helpful_percentage(self, obj):
        """Calculate helpful percentage"""
        # This would normally be based on total votes
        return 0
    
    def create(self, validated_data):
        """Create review with user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


# ==================== ANALYTICS SERIALIZERS ====================
class ContentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for content analytics"""
    content_details = LearningContentBaseSerializer(source='content', read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    average_time_spent_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentAnalytics
        fields = [
            'id', 'content', 'content_details', 'total_views', 'unique_viewers',
            'completion_rate', 'average_time_spent', 'average_time_spent_formatted',
            'popular_times', 'drop_off_points', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_average_time_spent_formatted(self, obj):
        """Format average time spent"""
        if obj.average_time_spent < 60:
            return f"{obj.average_time_spent}s"
        else:
            minutes = obj.average_time_spent // 60
            seconds = obj.average_time_spent % 60
            return f"{minutes}m {seconds}s"


class ModuleAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for module analytics"""
    module_details = LearningModuleSerializer(source='module', read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    popular_content = serializers.JSONField(read_only=True)
    
    class Meta:
        model = ModuleAnalytics
        fields = [
            'id', 'module', 'module_details', 'total_enrollments',
            'active_enrollments', 'completion_rate', 'average_grade',
            'popular_content', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


# ==================== STATISTICS SERIALIZERS ====================
class ContentStatisticsSerializer(serializers.Serializer):
    """Serializer for content statistics"""
    content_type = serializers.CharField()
    total_count = serializers.IntegerField()
    published_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_views = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class ModuleStatisticsSerializer(serializers.Serializer):
    """Serializer for module statistics"""
    module_id = serializers.UUIDField()
    module_name = serializers.CharField()
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_grade = serializers.FloatField()
    total_time_spent = serializers.IntegerField()


class StudentProgressStatisticsSerializer(serializers.Serializer):
    """Serializer for student progress statistics"""
    student_id = serializers.UUIDField()
    student_name = serializers.CharField()
    enrolled_modules = serializers.IntegerField()
    completed_modules = serializers.IntegerField()
    average_progress = serializers.FloatField()
    total_time_spent = serializers.IntegerField()
    favorite_content_type = serializers.CharField()


# ==================== BULK OPERATION SERIALIZERS ====================
class BulkContentProgressSerializer(serializers.Serializer):
    """Serializer for bulk progress updates"""
    enrollment_id = serializers.UUIDField()
    progress_updates = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    
    def validate(self, data):
        """Validate bulk progress data"""
        enrollment_id = data.get('enrollment_id')
        
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
            data['enrollment'] = enrollment
        except Enrollment.DoesNotExist:
            raise serializers.ValidationError({
                'enrollment_id': 'Enrollment does not exist'
            })
        
        # Validate each progress update
        for update in data.get('progress_updates', []):
            if 'content_id' not in update:
                raise serializers.ValidationError({
                    'progress_updates': 'Each update must have a content_id'
                })
        
        return data


class BulkEnrollmentSerializer(serializers.Serializer):
    """Serializer for bulk enrollments"""
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True
    )
    module_id = serializers.UUIDField(required=True)
    
    def validate(self, data):
        """Validate bulk enrollment data"""
        module_id = data.get('module_id')
        
        try:
            module = LearningModule.objects.get(id=module_id)
            data['module'] = module
        except LearningModule.DoesNotExist:
            raise serializers.ValidationError({
                'module_id': 'Module does not exist'
            })
        
        # Validate students exist
        student_ids = data.get('student_ids', [])
        students = User.objects.filter(id__in=student_ids, role='student')
        
        if len(students) != len(student_ids):
            raise serializers.ValidationError({
                'student_ids': 'One or more students do not exist'
            })
        
        data['students'] = students
        return data


# ==================== SEARCH SERIALIZERS ====================
class ContentSearchSerializer(serializers.Serializer):
    """Serializer for content search"""
    query = serializers.CharField(required=True)
    content_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    categories = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    difficulty_levels = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    min_duration = serializers.IntegerField(min_value=0, required=False)
    max_duration = serializers.IntegerField(min_value=0, required=False)
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('newest', 'Newest'),
            ('oldest', 'Oldest'),
            ('popular', 'Most Popular'),
            ('rating', 'Highest Rated'),
        ],
        default='relevance'
    )


# ==================== PERMISSION SERIALIZERS ====================
class ContentPermissionSerializer(serializers.Serializer):
    """Serializer for content permissions"""
    can_view = serializers.BooleanField()
    can_edit = serializers.BooleanField()
    can_delete = serializers.BooleanField()
    can_publish = serializers.BooleanField()
    can_review = serializers.BooleanField()
    can_manage_access = serializers.BooleanField()


# ==================== SUMMARY SERIALIZERS ====================
class ContentSummarySerializer(serializers.Serializer):
    """Serializer for content summary"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    content_type = serializers.CharField()
    description = serializers.CharField()
    thumbnail_url = serializers.CharField(allow_null=True)
    duration_formatted = serializers.CharField()
    average_rating = serializers.FloatField()
    views_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class ModuleSummarySerializer(serializers.Serializer):
    """Serializer for module summary"""
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    cover_image_url = serializers.CharField(allow_null=True)
    total_duration_formatted = serializers.CharField()
    content_count = serializers.IntegerField()
    enrollment_count = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    created_at = serializers.DateTimeField()