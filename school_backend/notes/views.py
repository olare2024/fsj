"""
Enhanced REST API Views for Notes and Learning Content Management System
Features:
1. Comprehensive CRUD operations for all models
2. Advanced filtering, search, and ordering
3. Progress tracking and analytics
4. Bulk operations and batch processing
5. Dashboard and summary views
6. Content discovery and recommendations
7. Advanced permissions and access control
"""

from rest_framework import viewsets, generics, status, permissions, filters, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum, F, Max, Min, Value
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.db import transaction, models
import datetime
import logging
from datetime import timedelta
import json
from collections import defaultdict

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

from .serializers import (
    # Core Serializers
    ContentCategorySerializer, ContentTagSerializer,
    
    # Content Serializers
    TextContentSerializer, VideoContentSerializer, AudioContentSerializer,
    PDFContentSerializer, PresentationContentSerializer,
    InteractiveContentSerializer, QuizContentSerializer,
    AssignmentContentSerializer, LinkContentSerializer,
    FileContentSerializer, LearningContentBaseSerializer,
    
    # Module Serializers
    LearningModuleSerializer, ModuleContentSerializer,
    
    # Enrollment Serializers
    EnrollmentSerializer, EnrollmentProgressSerializer,
    
    # Progress Tracking
    ContentProgressSerializer, ContentProgressUpdateSerializer, 
    
    # Assessment Serializers
    QuestionSerializer, QuestionChoiceSerializer,
    QuizAttemptSerializer, QuizAnswerSerializer,
    QuizSubmissionSerializer,
    
    # User Interaction Serializers
    ContentNoteSerializer, ContentAnnotationSerializer,
    ContentRatingSerializer, ContentReviewSerializer,
    
    # Analytics Serializers
    ContentAnalyticsSerializer, ModuleAnalyticsSerializer,
    
    # Statistics Serializers
    ContentStatisticsSerializer, ModuleStatisticsSerializer,
    StudentProgressStatisticsSerializer,
    
    # Bulk Operation Serializers
    BulkContentProgressSerializer, BulkEnrollmentSerializer,
    
    # Search Serializers
    ContentSearchSerializer,
    
    # Summary Serializers
    ContentSummarySerializer, ModuleSummarySerializer,
)

from accounts.models import User

logger = logging.getLogger(__name__)


# ==================== PAGINATION CLASSES ====================
class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for list views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Large pagination for content-heavy views"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """Small pagination for dashboard widgets"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ==================== PERMISSION CLASSES ====================
class IsSuperUser(permissions.BasePermission):
    """Permission for superusers only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminUser(permissions.BasePermission):
    """Permission for admin users only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'head_teacher']


class IsTeacherUser(permissions.BasePermission):
    """Permission for teacher users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'head_teacher']


class IsStudentUser(permissions.BasePermission):
    """Permission for student users only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class CanViewContent(permissions.BasePermission):
    """Permission to view content based on access level"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if hasattr(obj, 'is_public') and obj.is_public and obj.access_level == 'public':
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Check user role against access level
        if obj.access_level == 'authenticated':
            return True
        elif obj.access_level == 'students' and request.user.role == 'student':
            return True
        elif obj.access_level == 'teachers' and request.user.role in ['teacher', 'head_teacher']:
            return True
        elif obj.access_level == 'specific':
            return request.user in obj.allowed_users.all()
        
        # For unpublished content, check if user is author or admin
        if not obj.is_published:
            return request.user == obj.author or request.user.role in ['admin', 'head_teacher']
        
        return False


class CanEditContent(permissions.BasePermission):
    """Permission to edit content"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if request.user.role in ['admin', 'head_teacher']:
            return True
        
        if request.user == obj.author:
            return True
        
        return False


class CanPublishContent(permissions.BasePermission):
    """Permission to publish content"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if request.user.role in ['admin', 'head_teacher', 'curriculum_coordinator']:
            return True
        
        if request.user == obj.author and request.user.role == 'teacher':
            return True
        
        return False


# ==================== BASE VIEWSETS ====================
class BaseModelViewSet(viewsets.ModelViewSet):
    """Base viewset with common functionality"""
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Override to add filtering"""
        return super().get_queryset()
    
    def perform_create(self, serializer):
        """Set created_by on creation"""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Handle update logic"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Handle soft delete if available"""
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            instance.save()
        else:
            instance.delete()


class ContentTypeViewSet(BaseModelViewSet):
    """Base viewset for all content types"""
    permission_classes = [permissions.IsAuthenticated, CanViewContent]
    search_fields = ['title', 'description', 'keywords']
    ordering_fields = ['title', 'created_at', 'updated_at', 'views_count', 'average_rating']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser:
            return queryset
        
        # Apply content-specific filters
        queryset = queryset.filter(is_active=True)
        
        # For non-admin users, filter by published content
        if not user.role in ['admin', 'head_teacher']:
            queryset = queryset.filter(is_published=True)
            
            # Check access levels
            access_filters = Q(is_public=True, access_level='public')
            
            if user.is_authenticated:
                access_filters |= Q(access_level='authenticated')
                
                if user.role == 'student':
                    access_filters |= Q(access_level='students')
                elif user.role in ['teacher', 'head_teacher']:
                    access_filters |= Q(access_level='teachers')
                    access_filters |= Q(author=user)  # Teachers can see their own content
                
                access_filters |= Q(allowed_users=user)
            
            queryset = queryset.filter(access_filters)
        
        return queryset.distinct()
    
    def get_permissions(self):
        """Override permissions for different actions"""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, CanEditContent]
        elif self.action in ['publish', 'unpublish']:
            permission_classes = [permissions.IsAuthenticated, CanPublishContent]
        else:
            permission_classes = [permissions.IsAuthenticated, CanViewContent]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish content"""
        instance = self.get_object()
        instance.status = 'published'
        instance.publish_date = timezone.now()
        instance.save()
        return Response({'status': 'published'})
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish content"""
        instance = self.get_object()
        instance.status = 'draft'
        instance.publish_date = None
        instance.save()
        return Response({'status': 'draft'})
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get content analytics"""
        instance = self.get_object()
        try:
            analytics = instance.analytics
            serializer = ContentAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except ContentAnalytics.DoesNotExist:
            return Response({'detail': 'Analytics not found'}, status=404)
    
    @action(detail=True, methods=['get'], permission_classes=[IsStudentUser])
    def progress(self, request, pk=None):
        """Get student progress for this content"""
        instance = self.get_object()
        
        # Find enrollment that includes this content
        enrollment = Enrollment.objects.filter(
            student=request.user,
            module__contents__content=instance
        ).first()
        
        if enrollment:
            progress = ContentProgress.objects.filter(
                enrollment=enrollment,
                content=instance
            ).first()
            
            if progress:
                serializer = ContentProgressSerializer(progress)
                return Response(serializer.data)
        
        return Response({
            'status': 'not_started',
            'message': 'Content not started'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsStudentUser])
    def update_progress(self, request, pk=None):
        """Update student progress for this content"""
        instance = self.get_object()
        
        # Find enrollment
        enrollment = Enrollment.objects.filter(
            student=request.user,
            module__contents__content=instance
        ).first()
        
        if not enrollment:
            return Response(
                {'error': 'Not enrolled in module containing this content'},
                status=400
            )
        
        # Get or create progress
        progress, created = ContentProgress.objects.get_or_create(
            enrollment=enrollment,
            content=instance,
            defaults={
                'status': 'started',
                'started_at': timezone.now()
            }
        )
        
        serializer = ContentProgressUpdateSerializer(progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)


# ==================== CONTENT TYPE VIEWSETS ====================
class TextContentViewSet(ContentTypeViewSet):
    """Viewset for text content"""
    queryset = TextContent.objects.all()
    serializer_class = TextContentSerializer
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class VideoContentViewSet(ContentTypeViewSet):
    """Viewset for video content"""
    queryset = VideoContent.objects.all()
    serializer_class = VideoContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class AudioContentViewSet(ContentTypeViewSet):
    """Viewset for audio content"""
    queryset = AudioContent.objects.all()
    serializer_class = AudioContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class PDFContentViewSet(ContentTypeViewSet):
    """Viewset for PDF content"""
    queryset = PDFContent.objects.all()
    serializer_class = PDFContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class PresentationContentViewSet(ContentTypeViewSet):
    """Viewset for presentation content"""
    queryset = PresentationContent.objects.all()
    serializer_class = PresentationContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class InteractiveContentViewSet(ContentTypeViewSet):
    """Viewset for interactive content"""
    queryset = InteractiveContent.objects.all()
    serializer_class = InteractiveContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level', 'interactive_type']


class QuizContentViewSet(ContentTypeViewSet):
    """Viewset for quiz content"""
    queryset = QuizContent.objects.all()
    serializer_class = QuizContentSerializer
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class AssignmentContentViewSet(ContentTypeViewSet):
    """Viewset for assignment content"""
    queryset = AssignmentContent.objects.all()
    serializer_class = AssignmentContentSerializer
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class LinkContentViewSet(ContentTypeViewSet):
    """Viewset for link content"""
    queryset = LinkContent.objects.all()
    serializer_class = LinkContentSerializer
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


class FileContentViewSet(ContentTypeViewSet):
    """Viewset for file content"""
    queryset = FileContent.objects.all()
    serializer_class = FileContentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'status', 'difficulty_level']


# ==================== CATEGORY AND TAG VIEWSETS ====================
class ContentCategoryViewSet(BaseModelViewSet):
    """Viewset for content categories"""
    queryset = ContentCategory.objects.all()
    serializer_class = ContentCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    search_fields = ['name', 'description']
    filterset_fields = ['parent', 'curriculum', 'is_active']
    
    @action(detail=True, methods=['get'])
    def contents(self, request, pk=None):
        """Get all contents in this category"""
        category = self.get_object()
        contents = []
        
        # Get contents from all content types
        for model in [
            TextContent, VideoContent, AudioContent, PDFContent,
            PresentationContent, InteractiveContent, QuizContent,
            AssignmentContent, LinkContent, FileContent
        ]:
            model_contents = model.objects.filter(categories=category, is_active=True)
            for content in model_contents:
                contents.append({
                    'id': content.id,
                    'title': content.title,
                    'content_type': content.content_type,
                    'description': content.description,
                    'created_at': content.created_at
                })
        
        return Response(contents)


class ContentTagViewSet(BaseModelViewSet):
    """Viewset for content tags"""
    queryset = ContentTag.objects.all()
    serializer_class = ContentTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']


# ==================== MODULE VIEWSETS ====================
class LearningModuleViewSet(BaseModelViewSet):
    """Viewset for learning modules"""
    queryset = LearningModule.objects.all()
    serializer_class = LearningModuleSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewContent]
    search_fields = ['name', 'description', 'short_description']
    filterset_fields = ['subject', 'grade_level', 'curriculum', 'is_public', 'is_featured', 'is_active']
    
    def get_queryset(self):
        """Filter modules based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser:
            return queryset
        
        queryset = queryset.filter(is_active=True)
        
        if not user.role in ['admin', 'head_teacher']:
            queryset = queryset.filter(is_public=True)
            
            # For students, filter by their grade level
            if user.role == 'student' and user.grade_level:
                queryset = queryset.filter(Q(grade_level='') | Q(grade_level=user.grade_level))
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for different actions"""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, CanEditContent]
        else:
            permission_classes = [permissions.IsAuthenticated, CanViewContent]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def contents(self, request, pk=None):
        """Get all contents in this module"""
        module = self.get_object()
        contents = ModuleContent.objects.filter(module=module, is_active=True).order_by('order')
        serializer = ModuleContentSerializer(contents, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get module analytics"""
        module = self.get_object()
        try:
            analytics = module.analytics
            serializer = ModuleAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except ModuleAnalytics.DoesNotExist:
            return Response({'detail': 'Analytics not found'}, status=404)
    
    @action(detail=True, methods=['get'], permission_classes=[IsStudentUser])
    def my_progress(self, request, pk=None):
        """Get student's progress in this module"""
        module = self.get_object()
        
        # Check if enrolled
        enrollment = Enrollment.objects.filter(
            student=request.user,
            module=module
        ).first()
        
        if not enrollment:
            return Response({
                'is_enrolled': False,
                'message': 'Not enrolled in this module'
            })
        
        progress = enrollment.progress
        if progress:
            serializer = EnrollmentProgressSerializer(progress)
            return Response(serializer.data)
        
        return Response({
            'is_enrolled': True,
            'progress': 0,
            'message': 'No progress data available'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsStudentUser])
    def enroll(self, request, pk=None):
        """Enroll student in this module"""
        module = self.get_object()
        user = request.user
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=user, module=module).exists():
            return Response({
                'message': 'Already enrolled in this module'
            }, status=400)
        
        # Check if module is open for enrollment
        if not module.is_public:
            return Response({
                'message': 'Module is not open for enrollment'
            }, status=400)
        
        with transaction.atomic():
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=user,
                module=module
            )
            
            # Create progress record
            EnrollmentProgress.objects.create(enrollment=enrollment)
            
            # Create content progress records
            module_contents = ModuleContent.objects.filter(module=module, is_active=True)
            for module_content in module_contents:
                if module_content.content:
                    ContentProgress.objects.create(
                        enrollment=enrollment,
                        content=module_content.content,
                        status='not_started'
                    )
        
        return Response({
            'message': 'Successfully enrolled in module',
            'enrollment_id': enrollment.id
        }, status=201)


class ModuleContentViewSet(BaseModelViewSet):
    """Viewset for module contents"""
    queryset = ModuleContent.objects.all()
    serializer_class = ModuleContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    filterset_fields = ['module', 'is_active']
    ordering_fields = ['order']
    ordering = ['order']


# ==================== ENROLLMENT VIEWSETS ====================
class EnrollmentViewSet(BaseModelViewSet):
    """Viewset for enrollments"""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    filterset_fields = ['student', 'module', 'status', 'is_active']
    
    def get_queryset(self):
        """Filter enrollments based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'head_teacher']:
            return queryset
        
        if user.role == 'teacher':
            # Teachers can see enrollments in their modules
            teacher_modules = LearningModule.objects.filter(author=user)
            return queryset.filter(module__in=teacher_modules)
        
        if user.role == 'student':
            # Students can only see their own enrollments
            return queryset.filter(student=user)
        
        return queryset.none()


# ==================== PROGRESS VIEWSETS ====================
class ContentProgressViewSet(BaseModelViewSet):
    """Viewset for content progress"""
    queryset = ContentProgress.objects.all()
    serializer_class = ContentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['enrollment', 'content', 'status', 'is_active']
    ordering_fields = ['started_at', 'completed_at', 'completion_percentage']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Filter progress based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'head_teacher']:
            return queryset
        
        if user.role == 'teacher':
            # Teachers can see progress in their modules
            teacher_modules = LearningModule.objects.filter(author=user)
            teacher_enrollments = Enrollment.objects.filter(module__in=teacher_modules)
            return queryset.filter(enrollment__in=teacher_enrollments)
        
        if user.role == 'student':
            # Students can only see their own progress
            student_enrollments = Enrollment.objects.filter(student=user)
            return queryset.filter(enrollment__in=student_enrollments)
        
        return queryset.none()
    
    @action(detail=False, methods=['post'], permission_classes=[IsStudentUser])
    def bulk_update(self, request):
        """Bulk update progress records"""
        serializer = BulkContentProgressSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                enrollment = serializer.validated_data['enrollment']
                results = []
                
                for update in serializer.validated_data['progress_updates']:
                    content_id = update.get('content_id')
                    
                    try:
                        content = LearningContent.objects.get(id=content_id)
                    except LearningContent.DoesNotExist:
                        continue
                    
                    # Get or create progress
                    progress, created = ContentProgress.objects.get_or_create(
                        enrollment=enrollment,
                        content=content,
                        defaults={
                            'status': 'started',
                            'started_at': timezone.now()
                        }
                    )
                    
                    # Update progress
                    if 'completion_percentage' in update:
                        progress.completion_percentage = update['completion_percentage']
                    
                    if 'time_spent' in update:
                        progress.time_spent += update['time_spent']
                    
                    if 'status' in update:
                        progress.status = update['status']
                    
                    if progress.completion_percentage >= 100:
                        progress.status = 'completed'
                        progress.completed_at = timezone.now()
                    
                    progress.save()
                    results.append(ContentProgressSerializer(progress).data)
                
                # Update enrollment progress
                enrollment.progress.update_progress()
                
                return Response(results, status=200)
        
        return Response(serializer.errors, status=400)


# ==================== ASSESSMENT VIEWSETS ====================
class QuestionViewSet(BaseModelViewSet):
    """Viewset for questions"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    filterset_fields = ['content', 'question_type', 'difficulty', 'is_active']


class QuizAttemptViewSet(BaseModelViewSet):
    """Viewset for quiz attempts"""
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'content', 'is_passed', 'is_active']
    
    def get_queryset(self):
        """Filter attempts based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'head_teacher']:
            return queryset
        
        if user.role == 'teacher':
            # Teachers can see attempts for their quizzes
            teacher_quizzes = QuizContent.objects.filter(author=user)
            return queryset.filter(content__in=teacher_quizzes)
        
        if user.role == 'student':
            # Students can only see their own attempts
            return queryset.filter(student=user)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        """Submit quiz answers"""
        attempt = self.get_object()
        
        # Check if quiz is already completed
        if attempt.completed_at:
            return Response({
                'error': 'Quiz already completed'
            }, status=400)
        
        serializer = QuizSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                answers = serializer.validated_data['answers']
                total_score = 0
                total_possible = 0
                
                # Process each answer
                for answer_data in answers:
                    question_id = answer_data.get('question_id')
                    answer_text = answer_data.get('answer_text', '')
                    selected_choices = answer_data.get('selected_choices', [])
                    
                    try:
                        question = Question.objects.get(id=question_id, content=attempt.content)
                    except Question.DoesNotExist:
                        continue
                    
                    # Create answer record
                    quiz_answer = QuizAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        answer_text=answer_text
                    )
                    
                    # Add selected choices
                    if selected_choices:
                        choices = QuestionChoice.objects.filter(id__in=selected_choices, question=question)
                        quiz_answer.selected_choices.set(choices)
                    
                    # Calculate score
                    if question.question_type == 'multiple_choice':
                        correct_choices = question.choices.filter(is_correct=True)
                        selected_correct = quiz_answer.selected_choices.filter(is_correct=True).count()
                        
                        if correct_choices.count() > 0:
                            score = (selected_correct / correct_choices.count()) * question.points
                            quiz_answer.points_earned = score
                            quiz_answer.is_correct = (selected_correct == correct_choices.count())
                    else:
                        # For other question types, manual grading required
                        quiz_answer.points_earned = 0
                    
                    quiz_answer.save()
                    total_score += quiz_answer.points_earned
                    total_possible += question.points
                
                # Update attempt
                attempt.completed_at = timezone.now()
                attempt.time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
                
                if total_possible > 0:
                    attempt.score = total_score
                    attempt.percentage = (total_score / total_possible) * 100
                    
                    # Check if passed
                    if hasattr(attempt.content, 'quizcontent'):
                        passing_score = attempt.content.quizcontent.passing_score
                        attempt.is_passed = attempt.percentage >= passing_score
                
                attempt.save()
                
                return Response(QuizAttemptSerializer(attempt).data)
        
        return Response(serializer.errors, status=400)


# ==================== USER INTERACTION VIEWSETS ====================
class ContentNoteViewSet(BaseModelViewSet):
    """Viewset for content notes"""
    queryset = ContentNote.objects.all()
    serializer_class = ContentNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'content', 'is_public', 'is_active']
    
    def get_queryset(self):
        """Filter notes based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'head_teacher']:
            return queryset
        
        # Users can see their own notes and public notes
        return queryset.filter(
            Q(student=user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        """Set student when creating note"""
        serializer.save(student=self.request.user)


class ContentRatingViewSet(BaseModelViewSet):
    """Viewset for content ratings"""
    queryset = ContentRating.objects.all()
    serializer_class = ContentRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'content', 'is_active']
    
    def get_queryset(self):
        """Filter ratings based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'head_teacher']:
            return queryset
        
        # Users can see all ratings (public information)
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating rating"""
        serializer.save(user=self.request.user)
        
        # Update content average rating
        content = serializer.validated_data['content']
        content.update_average_rating()


# ==================== DASHBOARD AND ANALYTICS VIEWS ====================
class StudentDashboardView(generics.RetrieveAPIView):
    """Student dashboard view"""
    permission_classes = [permissions.IsAuthenticated, IsStudentUser]
    
    def get(self, request, *args, **kwargs):
        """Get student dashboard data"""
        user = request.user
        
        # Get cache key
        cache_key = f'student_dashboard_{user.id}_{timezone.now().date()}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get enrollments and progress
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        total_modules = enrollments.count()
        
        # Calculate overall progress
        overall_stats = enrollments.aggregate(
            completed=Count('id', filter=Q(status='completed')),
            avg_progress=Avg('progress__overall_progress'),
            total_time=Sum('progress__total_time_spent')
        )
        
        # Get recent activity
        recent_progress = ContentProgress.objects.filter(
            enrollment__student=user
        ).select_related('content', 'enrollment__module').order_by('-updated_at')[:10]
        
        recent_activity = []
        for progress in recent_progress:
            recent_activity.append({
                'content_title': progress.content.title if progress.content else 'Unknown',
                'content_type': progress.content.content_type if progress.content else 'unknown',
                'module': progress.enrollment.module.name if progress.enrollment.module else 'Unknown',
                'status': progress.status,
                'progress': progress.completion_percentage,
                'updated_at': progress.updated_at
            })
        
        # Get upcoming deadlines
        upcoming_deadlines = []
        for enrollment in enrollments:
            assignments = AssignmentContent.objects.filter(
                module_content__module=enrollment.module,
                due_date__gt=timezone.now()
            ).order_by('due_date')[:5]
            
            for assignment in assignments:
                progress = ContentProgress.objects.filter(
                    enrollment=enrollment,
                    content=assignment
                ).first()
                
                upcoming_deadlines.append({
                    'title': assignment.title,
                    'due_date': assignment.due_date,
                    'module': enrollment.module.name,
                    'progress': progress.completion_percentage if progress else 0,
                    'days_remaining': (assignment.due_date - timezone.now()).days
                })
        
        # Get recommended content
        recommended_content = self.get_recommended_content(user)
        
        dashboard_data = {
            'student': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'grade_level': user.grade_level,
                'class': user.current_class
            },
            'overall_stats': {
                'total_modules': total_modules,
                'completed_modules': overall_stats['completed'] or 0,
                'average_progress': round(overall_stats['avg_progress'] or 0, 2),
                'total_time_spent': overall_stats['total_time'] or 0,
                'completion_rate': (overall_stats['completed'] / total_modules * 100) if total_modules > 0 else 0
            },
            'recent_activity': recent_activity,
            'upcoming_deadlines': sorted(upcoming_deadlines, key=lambda x: x['days_remaining'])[:10],
            'recommended_content': recommended_content,
            'last_updated': timezone.now()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, dashboard_data, 300)
        
        return Response(dashboard_data)
    
    def get_recommended_content(self, user):
        """Get recommended content for student"""
        recommended = []
        
        # Get content from enrolled modules not yet completed
        enrollments = Enrollment.objects.filter(student=user, status='active')
        
        for enrollment in enrollments:
            module = enrollment.module
            
            # Get not started or in-progress content
            module_contents = ModuleContent.objects.filter(
                module=module,
                is_active=True
            ).select_related('content').order_by('order')
            
            for module_content in module_contents:
                if module_content.content:
                    content_progress = ContentProgress.objects.filter(
                        enrollment=enrollment,
                        content=module_content.content
                    ).first()
                    
                    if not content_progress or content_progress.status != 'completed':
                        # Check if previous content is completed (if sequential)
                        if module_content.unlock_after_previous:
                            # Get previous content
                            previous_content = ModuleContent.objects.filter(
                                module=module,
                                order__lt=module_content.order
                            ).order_by('-order').first()
                            
                            if previous_content and previous_content.content:
                                prev_progress = ContentProgress.objects.filter(
                                    enrollment=enrollment,
                                    content=previous_content.content,
                                    status='completed'
                                ).exists()
                                
                                if not prev_progress:
                                    continue
                        
                        recommended.append({
                            'id': module_content.content.id,
                            'title': module_content.content.title,
                            'content_type': module_content.content.content_type,
                            'description': module_content.content.description[:100] + '...' if module_content.content.description else '',
                            'estimated_duration': module_content.content.estimated_duration,
                            'module': module.name,
                            'reason': 'Next in sequence' if module.is_sequential else 'Available content'
                        })
        
        return recommended[:10]


    def get(self, request, *args, **kwargs):
        """Get teacher dashboard data"""
        user = request.user
        
        # Cache key
        cache_key = f'teacher_dashboard_{user.id}_{timezone.now().date()}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get teacher's modules
        teacher_modules = LearningModule.objects.filter(author=user)
        total_modules = teacher_modules.count()
        
        # Get enrollment statistics
        module_enrollments = Enrollment.objects.filter(
            module__in=teacher_modules,
            is_active=True
        ).values('module__id', 'module__name').annotate(
            total_students=Count('student', distinct=True),
            active_students=Count('student', distinct=True, filter=Q(status='active')),
            completed_students=Count('student', distinct=True, filter=Q(status='completed'))
        )
        
        # Calculate overall module statistics
        module_stats = []
        total_students = 0
        total_completed = 0
        
        for me in module_enrollments:
            module_id = me['module__id']
            module = LearningModule.objects.get(id=module_id)
            
            # Get average progress
            avg_progress = EnrollmentProgress.objects.filter(
                enrollment__module_id=module_id
            ).aggregate(
                avg_progress=Avg('overall_progress')
            )['avg_progress'] or 0
            
            # Get recent submissions (assignments/quizzes)
            recent_submissions = QuizAttempt.objects.filter(
                content__module_content__module=module,
                completed_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            # Get pending grading
            pending_grading = QuizAttempt.objects.filter(
                content__module_content__module=module,
                completed_at__isnull=False,
                is_graded=False
            ).count()
            
            module_stats.append({
                'module_id': module_id,
                'module_name': me['module__name'],
                'total_students': me['total_students'],
                'active_students': me['active_students'],
                'completed_students': me['completed_students'],
                'average_progress': round(avg_progress, 2),
                'recent_submissions': recent_submissions,
                'pending_grading': pending_grading,
                'completion_rate': (me['completed_students'] / me['total_students'] * 100) if me['total_students'] > 0 else 0
            })
            
            total_students += me['total_students']
            total_completed += me['completed_students']
        
        # Get recent student activity
        recent_activity = []
        student_progress = ContentProgress.objects.filter(
            content__author=user,
            updated_at__gte=timezone.now() - timedelta(days=1)
        ).select_related('enrollment__student', 'content').order_by('-updated_at')[:20]
        
        for progress in student_progress:
            recent_activity.append({
                'student_name': progress.enrollment.student.get_full_name(),
                'student_id': progress.enrollment.student.id,
                'content_title': progress.content.title,
                'content_type': progress.content.content_type,
                'progress': progress.completion_percentage,
                'status': progress.status,
                'time_spent': progress.time_spent,
                'updated_at': progress.updated_at
            })
        
        # Get assignment submissions needing attention
        pending_assignments = []
        assignments = AssignmentContent.objects.filter(
            author=user,
            due_date__gt=timezone.now()
        )
        
        for assignment in assignments:
            submissions = QuizAttempt.objects.filter(
                content=assignment,
                completed_at__isnull=False
            )
            
            graded = submissions.filter(is_graded=True).count()
            total = submissions.count()
            
            if total > 0:
                pending_assignments.append({
                    'assignment_id': assignment.id,
                    'assignment_title': assignment.title,
                    'due_date': assignment.due_date,
                    'total_submissions': total,
                    'graded_submissions': graded,
                    'grading_progress': (graded / total * 100) if total > 0 else 0,
                    'days_until_due': (assignment.due_date - timezone.now()).days
                })
        
        # Get content performance metrics
        content_performance = []
        teacher_contents = LearningContent.objects.filter(author=user)
        
        for content in teacher_contents[:10]:  # Top 10
            analytics = ContentAnalytics.objects.filter(content=content).first()
            if analytics:
                completion_rate = (analytics.completed_count / analytics.started_count * 100) if analytics.started_count > 0 else 0
                
                content_performance.append({
                    'content_id': content.id,
                    'content_title': content.title,
                    'content_type': content.content_type,
                    'views': analytics.views_count,
                    'started': analytics.started_count,
                    'completed': analytics.completed_count,
                    'completion_rate': round(completion_rate, 2),
                    'average_rating': analytics.average_rating,
                    'rating_count': analytics.rating_count
                })
        
        # Get student performance overview
        student_performance = []
        student_enrollments = Enrollment.objects.filter(
            module__in=teacher_modules
        ).select_related('student').distinct('student')[:10]
        
        for enrollment in student_enrollments:
            student = enrollment.student
            
            # Get student's average progress across teacher's modules
            student_progress = EnrollmentProgress.objects.filter(
                enrollment__student=student,
                enrollment__module__in=teacher_modules
            ).aggregate(
                avg_progress=Avg('overall_progress')
            )['avg_progress'] or 0
            
            # Get recent quiz scores
            recent_quizzes = QuizAttempt.objects.filter(
                student=student,
                content__author=user,
                completed_at__isnull=False
            ).order_by('-completed_at')[:3]
            
            quiz_scores = [q.percentage for q in recent_quizzes]
            avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
            
            student_performance.append({
                'student_id': student.id,
                'student_name': student.get_full_name(),
                'grade_level': student.grade_level,
                'avg_progress': round(student_progress, 2),
                'avg_quiz_score': round(avg_quiz_score, 2),
                'active_modules': Enrollment.objects.filter(
                    student=student,
                    module__in=teacher_modules,
                    status='active'
                ).count(),
                'last_active': ContentProgress.objects.filter(
                    enrollment__student=student
                ).aggregate(last_active=Max('updated_at'))['last_active']
            })
        
        dashboard_data = {
            'teacher': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'overall_stats': {
                'total_modules': total_modules,
                'total_students': total_students,
                'total_completed': total_completed,
                'completion_rate': (total_completed / total_students * 100) if total_students > 0 else 0,
                'total_assignments': AssignmentContent.objects.filter(author=user).count(),
                'total_quizzes': QuizContent.objects.filter(author=user).count()
            },
            'module_statistics': module_stats,
            'recent_activity': recent_activity,
            'pending_assignments': sorted(pending_assignments, key=lambda x: x['days_until_due']),
            'content_performance': content_performance,
            'student_performance': student_performance,
            'alerts': self.get_teacher_alerts(user),
            'last_updated': timezone.now()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, dashboard_data, 300)
        
        return Response(dashboard_data)
    
    def get_teacher_alerts(self, user):
        """Get alerts for teacher"""
        alerts = []
        
        # Check for modules with low engagement
        teacher_modules = LearningModule.objects.filter(author=user)
        
        for module in teacher_modules:
            enrollments = Enrollment.objects.filter(module=module, is_active=True).count()
            
            if enrollments > 0:
                avg_progress = EnrollmentProgress.objects.filter(
                    enrollment__module=module
                ).aggregate(
                    avg_progress=Avg('overall_progress')
                )['avg_progress'] or 0
                
                if avg_progress < 30:
                    alerts.append({
                        'type': 'low_engagement',
                        'module_id': module.id,
                        'module_name': module.name,
                        'message': f'Low engagement in {module.name} ({avg_progress:.1f}% average progress)',
                        'priority': 'medium'
                    })
        
        # Check for assignments due soon
        assignments = AssignmentContent.objects.filter(
            author=user,
            due_date__range=[timezone.now(), timezone.now() + timedelta(days=2)]
        )
        
        for assignment in assignments:
            total_submissions = QuizAttempt.objects.filter(content=assignment).count()
            graded_submissions = QuizAttempt.objects.filter(content=assignment, is_graded=True).count()
            
            if graded_submissions < total_submissions:
                alerts.append({
                    'type': 'grading_pending',
                    'assignment_id': assignment.id,
                    'assignment_title': assignment.title,
                    'message': f'Grading pending for {assignment.title}',
                    'priority': 'high' if assignment.due_date.date() == timezone.now().date() else 'medium'
                })
        
        # Check for content needing review
        contents = LearningContent.objects.filter(
            author=user,
            status='needs_review'
        )
        
        for content in contents:
            alerts.append({
                'type': 'content_review',
                'content_id': content.id,
                'content_title': content.title,
                'message': f'Content "{content.title}" needs review',
                'priority': 'low'
            })
        
        return alerts[:10]  # Limit to 10 alerts



class AnalyticsView(generics.GenericAPIView):
    """Comprehensive analytics view"""
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    
    def get(self, request, *args, **kwargs):
        """Get detailed analytics"""
        # Time-based analytics
        date_range = request.GET.get('range', '7d')  # 7d, 30d, 90d, custom
        end_date = timezone.now()
        
        if date_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif date_range == '30d':
            start_date = end_date - timedelta(days=30)
        elif date_range == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            # Custom range
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            start_date = timezone.datetime.fromisoformat(start_date_str) if start_date_str else end_date - timedelta(days=7)
            end_date = timezone.datetime.fromisoformat(end_date_str) if end_date_str else timezone.now()
        
        # Get analytics data
        analytics_data = self.get_time_series_analytics(start_date, end_date)
        
        return Response(analytics_data)
    
    def get_time_series_analytics(self, start_date, end_date):
        """Get time series analytics data"""
        # Enrollment trends
        enrollments_by_day = Enrollment.objects.filter(
            enrolled_at__range=[start_date, end_date],
            module__author=self.request.user
        ).annotate(
            day=TruncDate('enrolled_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Content progress trends
        progress_by_day = ContentProgress.objects.filter(
            updated_at__range=[start_date, end_date],
            content__author=self.request.user,
            status='completed'
        ).annotate(
            day=TruncDate('updated_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Quiz performance trends
        quiz_performance = QuizAttempt.objects.filter(
            completed_at__range=[start_date, end_date],
            content__author=self.request.user
        ).annotate(
            day=TruncDate('completed_at')
        ).values('day').annotate(
            avg_score=Avg('percentage'),
            count=Count('id')
        ).order_by('day')
        
        return {
            'enrollment_trends': list(enrollments_by_day),
            'completion_trends': list(progress_by_day),
            'quiz_performance': list(quiz_performance),
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }


class ContentRecommendationView(generics.GenericAPIView):
    """Content recommendation view"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get personalized content recommendations"""
        user = request.user
        
        if user.role == 'student':
            recommendations = self.get_student_recommendations(user)
        else:
            recommendations = self.get_teacher_recommendations(user)
        
        return Response(recommendations)
    
    def get_student_recommendations(self, user):
        """Get recommendations for students based on learning patterns"""
        recommendations = []
        
        # Based on completed content
        completed_content = ContentProgress.objects.filter(
            enrollment__student=user,
            status='completed'
        ).select_related('content')
        
        # Find similar content
        for progress in completed_content[:5]:
            content = progress.content
            
            # Find content with same tags/categories
            similar = LearningContent.objects.filter(
                Q(categories__in=content.categories.all()) |
                Q(tags__in=content.tags.all()),
                is_published=True,
                is_active=True
            ).exclude(id=content.id).distinct()[:3]
            
            for sim in similar:
                recommendations.append({
                    'content_id': sim.id,
                    'title': sim.title,
                    'content_type': sim.content_type,
                    'description': sim.description[:150] + '...' if len(sim.description) > 150 else sim.description,
                    'reason': f'Similar to "{content.title}"',
                    'match_score': 85  # Could be calculated based on similarity
                })
        
        # Based on peer activity
        if user.current_class:
            classmates = User.objects.filter(
                current_class=user.current_class,
                role='student'
            ).exclude(id=user.id)
            
            class_completed = ContentProgress.objects.filter(
                enrollment__student__in=classmates,
                status='completed'
            ).values('content').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            for item in class_completed:
                content = LearningContent.objects.get(id=item['content'])
                
                # Check if student hasn't completed this
                if not ContentProgress.objects.filter(
                    enrollment__student=user,
                    content=content,
                    status='completed'
                ).exists():
                    recommendations.append({
                        'content_id': content.id,
                        'title': content.title,
                        'content_type': content.content_type,
                        'description': content.description[:150] + '...' if len(content.description) > 150 else content.description,
                        'reason': f'Popular with your classmates ({item["count"]} students completed)',
                        'match_score': 75
                    })
        
        # Remove duplicates
        seen_ids = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec['content_id'] not in seen_ids:
                seen_ids.add(rec['content_id'])
                unique_recommendations.append(rec)
        
        return sorted(unique_recommendations, key=lambda x: x['match_score'], reverse=True)[:10]



class BulkOperationsView(generics.GenericAPIView):
    """Bulk operations view"""
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]
    
    def post(self, request, *args, **kwargs):
        """Perform bulk operations"""
        operation = request.data.get('operation')
        
        if operation == 'enroll_students':
            return self.bulk_enroll_students(request.data)
        elif operation == 'update_progress':
            return self.bulk_update_progress(request.data)
        elif operation == 'create_contents':
            return self.bulk_create_contents(request.data)
        elif operation == 'import_from_csv':
            return self.import_from_csv(request)
        else:
            return Response({'error': 'Invalid operation'}, status=400)
    
    def bulk_enroll_students(self, data):
        """Bulk enroll students in modules"""
        serializer = BulkEnrollmentSerializer(data=data)
        
        if serializer.is_valid():
            with transaction.atomic():
                module_id = serializer.validated_data['module_id']
                student_ids = serializer.validated_data['student_ids']
                
                module = LearningModule.objects.get(id=module_id)
                results = []
                
                for student_id in student_ids:
                    try:
                        student = User.objects.get(id=student_id, role='student')
                        
                        # Check if already enrolled
                        if Enrollment.objects.filter(student=student, module=module).exists():
                            results.append({
                                'student_id': student_id,
                                'status': 'already_enrolled',
                                'message': f'{student.get_full_name()} is already enrolled'
                            })
                            continue
                        
                        # Create enrollment
                        enrollment = Enrollment.objects.create(
                            student=student,
                            module=module
                        )
                        
                        # Create progress records
                        EnrollmentProgress.objects.create(enrollment=enrollment)
                        
                        results.append({
                            'student_id': student_id,
                            'status': 'success',
                            'enrollment_id': enrollment.id,
                            'message': f'Successfully enrolled {student.get_full_name()}'
                        })
                        
                    except User.DoesNotExist:
                        results.append({
                            'student_id': student_id,
                            'status': 'error',
                            'message': f'Student with ID {student_id} not found'
                        })
                
                return Response(results, status=200)
        
        return Response(serializer.errors, status=400)

class AdvancedSearchView(generics.ListAPIView):
    """Advanced search with filtering"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ContentSearchSerializer
    
    def get_queryset(self):
        """Get filtered search results"""
        queryset = LearningContent.objects.filter(is_active=True, is_published=True)
        user = self.request.user
        
        # Apply permissions
        if not user.is_superuser and user.role not in ['admin', 'head_teacher']:
            access_filters = Q(is_public=True, access_level='public')
            
            if user.is_authenticated:
                access_filters |= Q(access_level='authenticated')
                
                if user.role == 'student':
                    access_filters |= Q(access_level='students')
                elif user.role in ['teacher', 'head_teacher']:
                    access_filters |= Q(access_level='teachers')
                    access_filters |= Q(author=user)
                
                access_filters |= Q(allowed_users=user)
            
            queryset = queryset.filter(access_filters)
        
        # Apply search filters
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(keywords__icontains=search_query) |
                Q(content_text__icontains=search_query)  # For text content
            )
        
        # Filter by content type
        content_types = self.request.GET.getlist('content_type')
        if content_types:
            queryset = queryset.filter(content_type__in=content_types)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Filter by grade level
        grade_level = self.request.GET.get('grade_level')
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by duration range
        min_duration = self.request.GET.get('min_duration')
        max_duration = self.request.GET.get('max_duration')
        
        if min_duration:
            queryset = queryset.filter(estimated_duration__gte=int(min_duration))
        if max_duration:
            queryset = queryset.filter(estimated_duration__lte=int(max_duration))
        
        # Filter by rating
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        # Filter by tags
        tags = self.request.GET.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        
        # Filter by categories
        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(categories__id__in=categories)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', 'relevance')
        if sort_by == 'relevance' and search_query:
            # Simple relevance scoring
            queryset = queryset.annotate(
                relevance=Count(
                    'id',
                    filter=Q(title__icontains=search_query) |
                          Q(description__icontains=search_query)
                )
            ).order_by('-relevance')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort_by == 'duration':
            queryset = queryset.order_by('estimated_duration')
        
        return queryset.distinct()
    
    def list(self, request, *args, **kwargs):
        """Override list to include aggregations"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get aggregations for filters
        aggregations = {
            'total_count': queryset.count(),
            'content_types': list(queryset.values('content_type').annotate(count=Count('id'))),
            'subjects': list(queryset.values('subject').annotate(count=Count('id')).filter(subject__isnull=False)),
            'difficulty_levels': list(queryset.values('difficulty_level').annotate(count=Count('id')).filter(difficulty_level__isnull=False)),
            'min_duration': queryset.aggregate(min=Min('estimated_duration'))['min'] or 0,
            'max_duration': queryset.aggregate(max=Max('estimated_duration'))['max'] or 0,
            'average_rating': queryset.aggregate(avg=Avg('average_rating'))['avg'] or 0
        }
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['aggregations'] = aggregations
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'aggregations': aggregations
        })




class AdvancedSearchView(generics.ListAPIView):
    """Advanced search with filtering"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ContentSearchSerializer
    
    def get_queryset(self):
        """Get filtered search results"""
        queryset = LearningContent.objects.filter(is_active=True, is_published=True)
        user = self.request.user
        
        # Apply permissions
        if not user.is_superuser and user.role not in ['admin', 'head_teacher']:
            access_filters = Q(is_public=True, access_level='public')
            
            if user.is_authenticated:
                access_filters |= Q(access_level='authenticated')
                
                if user.role == 'student':
                    access_filters |= Q(access_level='students')
                elif user.role in ['teacher', 'head_teacher']:
                    access_filters |= Q(access_level='teachers')
                    access_filters |= Q(author=user)
                
                access_filters |= Q(allowed_users=user)
            
            queryset = queryset.filter(access_filters)
        
        # Apply search filters
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(keywords__icontains=search_query) |
                Q(content_text__icontains=search_query)  # For text content
            )
        
        # Filter by content type
        content_types = self.request.GET.getlist('content_type')
        if content_types:
            queryset = queryset.filter(content_type__in=content_types)
        
        # Filter by subject
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Filter by grade level
        grade_level = self.request.GET.get('grade_level')
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by duration range
        min_duration = self.request.GET.get('min_duration')
        max_duration = self.request.GET.get('max_duration')
        
        if min_duration:
            queryset = queryset.filter(estimated_duration__gte=int(min_duration))
        if max_duration:
            queryset = queryset.filter(estimated_duration__lte=int(max_duration))
        
        # Filter by rating
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        # Filter by tags
        tags = self.request.GET.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        
        # Filter by categories
        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(categories__id__in=categories)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', 'relevance')
        if sort_by == 'relevance' and search_query:
            # Simple relevance scoring
            queryset = queryset.annotate(
                relevance=Count(
                    'id',
                    filter=Q(title__icontains=search_query) |
                          Q(description__icontains=search_query)
                )
            ).order_by('-relevance')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort_by == 'duration':
            queryset = queryset.order_by('estimated_duration')
        
        return queryset.distinct()
    
    def list(self, request, *args, **kwargs):
        """Override list to include aggregations"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get aggregations for filters
        aggregations = {
            'total_count': queryset.count(),
            'content_types': list(queryset.values('content_type').annotate(count=Count('id'))),
            'subjects': list(queryset.values('subject').annotate(count=Count('id')).filter(subject__isnull=False)),
            'difficulty_levels': list(queryset.values('difficulty_level').annotate(count=Count('id')).filter(difficulty_level__isnull=False)),
            'min_duration': queryset.aggregate(min=Min('estimated_duration'))['min'] or 0,
            'max_duration': queryset.aggregate(max=Max('estimated_duration'))['max'] or 0,
            'average_rating': queryset.aggregate(avg=Avg('average_rating'))['avg'] or 0
        }
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['aggregations'] = aggregations
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'aggregations': aggregations
        })


class AuditableModelViewSet(BaseModelViewSet):
    """Base viewset with audit logging"""
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.log_audit('CREATE', serializer.instance)
    
    def perform_update(self, serializer):
        old_instance = self.get_object()
        super().perform_update(serializer)
        self.log_audit('UPDATE', serializer.instance, old_instance)
    
    def perform_destroy(self, instance):
        self.log_audit('DELETE', instance)
        super().perform_destroy(instance)
    
    def log_audit(self, action, instance, old_instance=None):
        from .models import AuditLog
        
        changes = {}
        if old_instance:
            # Track changes
            for field in instance._meta.fields:
                old_value = getattr(old_instance, field.name)
                new_value = getattr(instance, field.name)
                if old_value != new_value:
                    changes[field.name] = {'old': old_value, 'new': new_value}
        
        AuditLog.objects.create(
            user=self.request.user,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=instance.id,
            changes=changes,
            ip_address=self.get_client_ip()
        )


        # ==================== STUDENT PROGRESS VIEWSET ====================
class StudentProgressViewSet(BaseModelViewSet):
    """Viewset for student progress (alias for ContentProgressViewSet)"""
    queryset = ContentProgress.objects.all()
    serializer_class = ContentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['enrollment__student', 'content', 'status', 'is_active']


# ==================== MODULE PROGRESS VIEWSET ====================
class ModuleProgressViewSet(BaseModelViewSet):
    """Viewset for module progress"""
    queryset = EnrollmentProgress.objects.all()
    serializer_class = EnrollmentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['enrollment__module', 'enrollment__student']


# ==================== CONTENT ANNOTATION VIEWSET ====================
class ContentAnnotationViewSet(BaseModelViewSet):
    """Viewset for content annotations"""
    queryset = ContentAnnotation.objects.all()
    serializer_class = ContentAnnotationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'content', 'annotation_type']


# ==================== ANALYTICS VIEWSETS ====================
class ContentAnalyticsViewSet(BaseModelViewSet):
    """Viewset for content analytics"""
    queryset = ContentAnalytics.objects.all()
    serializer_class = ContentAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]


class ModuleAnalyticsViewSet(BaseModelViewSet):
    """Viewset for module analytics"""
    queryset = ModuleAnalytics.objects.all()
    serializer_class = ModuleAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]


# Add these to your views.py file if they don't exist:

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def learning_health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'service': 'Learning Management System'
    })


@api_view(['GET'])
def learning_404_handler(request, exception):
    """Custom 404 handler"""
    return Response({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }, status=404)


@api_view(['GET'])
def learning_500_handler(request):
    """Custom 500 handler"""
    return Response({
        'error': 'Server error',
        'message': 'An internal server error occurred',
        'status_code': 500
    }, status=500)


# Simple view classes for missing endpoints
class ContentSearchView(generics.ListAPIView):
    """Simple content search view"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContentSearchSerializer
    
    def get_queryset(self):
        return LearningContent.objects.filter(is_active=True, is_published=True)


class LearningSummaryView(generics.RetrieveAPIView):
    """Learning summary view"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        # Simple summary logic
        return Response({
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'role': user.role
            },
            'summary': 'Learning summary will be implemented here'
        })


# Admin views placeholder
class AdminDashboardView(generics.RetrieveAPIView):
    """Admin dashboard view"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Admin dashboard will be implemented here'
        })