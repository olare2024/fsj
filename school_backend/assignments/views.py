# assignments/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, FloatField
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import BasePermission
from datetime import timedelta
from django.core.exceptions import ValidationError
import logging

from .models import (
    Assignment, StudentAssignment, AssignmentCategory, AssignmentGradeScale,
    AssignmentGroup, GroupMembership, AssignmentComment, AssignmentAnalytics
)
from .serializers import (
    AssignmentCategorySerializer, AssignmentGradeScaleSerializer,
    AssignmentListSerializer, AssignmentDetailSerializer, AssignmentCreateSerializer,
    AssignmentUpdateSerializer, StudentAssignmentDetailSerializer,
    StudentAssignmentSubmitSerializer, StudentAssignmentGradeSerializer,
    StudentAssignmentMiniSerializer, AssignmentGroupSerializer,
    GroupMembershipSerializer, AssignmentCommentSerializer,
    AssignmentDashboardSerializer, TeacherAssignmentStatsSerializer
)

# Set up logger
logger = logging.getLogger(__name__)

# Import models with proper error handling
try:
    from academics.models import Student, Teacher
except ImportError:
    logger.warning("Could not import Student and Teacher from academics.models")
    # Create fallback classes
    class Student:
        pass
    
    class Teacher:
        pass

try:
    from accounts.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()


class IsTeacher(BasePermission):
    """
    Custom permission to only allow teachers to access the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check multiple ways user could be a teacher
        # 1. Check if user has is_teacher property
        if hasattr(request.user, 'is_teacher') and request.user.is_teacher:
            return True
        
        # 2. Check role directly
        if hasattr(request.user, 'role'):
            user_role = str(request.user.role).lower()
            teacher_roles = ['teacher', 'head_teacher', 'curriculum_coordinator', 'admin']
            if user_role in teacher_roles:
                return True
        
        # 3. Check if user is staff (admin/teacher)
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # 4. Check if user is superuser
        if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
            return True
        
        # 5. Check if user has teacher_profile attribute
        if hasattr(request.user, 'teacher_profile'):
            return True
        
        return False



class AssignmentCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment categories
    """
    permission_classes = [IsAuthenticated]
    queryset = AssignmentCategory.objects.all()
    serializer_class = AssignmentCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """
        Apply admin permissions for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Create category with error handling
        """
        try:
            serializer.save()
            logger.info(f"Assignment category created: {serializer.instance.name}")
        except Exception as e:
            logger.error(f"Error creating assignment category: {str(e)}")
            raise

    def perform_update(self, serializer):
        """
        Update category with error handling
        """
        try:
            serializer.save()
            logger.info(f"Assignment category updated: {serializer.instance.name}")
        except Exception as e:
            logger.error(f"Error updating assignment category: {str(e)}")
            raise


class AssignmentGradeScaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment grade scales
    """
    permission_classes = [IsAuthenticated]
    queryset = AssignmentGradeScale.objects.all()
    serializer_class = AssignmentGradeScaleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['grade', 'description']
    filterset_fields = ['curriculum', 'is_active']
    ordering_fields = ['curriculum', 'min_percentage']
    ordering = ['curriculum', 'min_percentage']
    
    def get_permissions(self):
        """
        Apply admin permissions for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def validate_grade_scale(self, data):
        """
        Validate grade scale data
        """
        min_percentage = data.get('min_percentage')
        max_percentage = data.get('max_percentage')
        
        if min_percentage and max_percentage and min_percentage >= max_percentage:
            raise ValidationError("Min percentage must be less than max percentage")
        
        return data

    def perform_create(self, serializer):
        """
        Create grade scale with validation
        """
        try:
            self.validate_grade_scale(serializer.validated_data)
            serializer.save()
            logger.info(f"Grade scale created: {serializer.instance.grade}")
        except Exception as e:
            logger.error(f"Error creating grade scale: {str(e)}")
            raise

    def perform_update(self, serializer):
        """
        Update grade scale with validation
        """
        try:
            self.validate_grade_scale(serializer.validated_data)
            serializer.save()
            logger.info(f"Grade scale updated: {serializer.instance.grade}")
        except Exception as e:
            logger.error(f"Error updating grade scale: {str(e)}")
            raise


# In assignments/views.py - Complete AssignmentViewSet with all endpoints

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Complete ViewSet for managing assignments with all frontend endpoints
    """
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'subject__name']
    filterset_fields = [
        'assignment_type', 'subject', 'teacher', 'classroom', 'stream',
        'academic_year', 'term', 'curriculum', 'status', 'difficulty_level',
        'category', 'is_group_assignment'
    ]
    ordering_fields = [
        'created_at', 'due_date', 'total_marks', 'average_score', 'views_count'
    ]
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """
        Filter assignments based on user role and permissions
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'subject', 'teacher', 'classroom', 'stream', 
            'academic_year', 'term', 'category', 'created_by'
        ).prefetch_related('student_assignments')
        
        try:
            # Filter based on user role
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                # Get assignments for student's classroom
                if hasattr(student, 'classroom') and student.classroom:
                    queryset = queryset.filter(
                        Q(classroom=student.classroom) | Q(classroom__isnull=True),
                        status__in=['published', 'in_progress', 'closed', 'graded']
                    )
                else:
                    queryset = queryset.none()
                    
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                queryset = queryset.filter(teacher=teacher)
                
            elif user.is_staff or user.is_superuser:
                # Admin users can see all assignments
                pass
                
            else:
                # Other users see only published assignments
                queryset = queryset.filter(status='published')
        except Exception as e:
            logger.error(f"Error filtering assignments: {str(e)}")
            queryset = Assignment.objects.none()
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return AssignmentListSerializer
        elif self.action == 'retrieve':
            return AssignmentDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            if self.action == 'create':
                return AssignmentCreateSerializer
            return AssignmentUpdateSerializer
        return AssignmentDetailSerializer
    
    def get_serializer_context(self):
        """
        Add request context to serializer
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Override create to provide better error responses
        """
        try:
            logger.info(f"Creating assignment with data: {request.data}")
            
            # Check if user can create assignments
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can create assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate required fields before serializer
            required_fields = ['title', 'subject', 'academic_year', 'term', 'due_date']
            missing_fields = []
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return Response({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Proceed with normal creation
            return super().create(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error creating assignment: {str(e)}")
            return Response(
                {'error': f'Failed to create assignment: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """
        Set created_by to current user when creating assignment
        """
        try:
            with transaction.atomic():
                assignment = serializer.save()
                
                # Create student assignments for all students in the classroom
                if assignment.classroom and assignment.status == 'published':
                    assignment.create_student_assignments()
                
                logger.info(f"Assignment created successfully: {assignment.title} by {self.request.user}")
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise
    
    def retrieve(self, request, *args, **kwargs):
        """
        Increment views count when assignment is viewed
        """
        try:
            instance = self.get_object()
            
            # Increment views count for published assignments
            if instance.status == 'published':
                instance.views_count = F('views_count') + 1
                instance.save(update_fields=['views_count'])
                instance.refresh_from_db()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving assignment: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==================== CUSTOM ACTIONS ====================
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish an assignment
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can publish assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if assignment.status != 'draft':
                return Response(
                    {'error': 'Only draft assignments can be published.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assignment.status = 'published'
            assignment.published_at = timezone.now()
            assignment.save()
            
            # Create student assignments when published
            assignment.create_student_assignments()
            
            logger.info(f"Assignment published: {assignment.title}")
            
            serializer = self.get_serializer(assignment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error publishing assignment: {str(e)}")
            return Response(
                {'error': 'Failed to publish assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """
        Unpublish an assignment
        """
        try:
            assignment = self.get_object()
            
            if assignment.status != 'published':
                return Response(
                    {'error': 'Only published assignments can be unpublished.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assignment.status = 'draft'
            assignment.save()
            logger.info(f"Assignment unpublished: {assignment.title}")
            
            serializer = self.get_serializer(assignment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error unpublishing assignment: {str(e)}")
            return Response(
                {'error': 'Failed to unpublish assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close an assignment for submissions
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can close assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if assignment.status not in ['published', 'in_progress']:
                return Response(
                    {'error': 'Only published or in-progress assignments can be closed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assignment.status = 'closed'
            assignment.closed_at = timezone.now()
            assignment.save()
            
            logger.info(f"Assignment closed: {assignment.title}")
            
            serializer = self.get_serializer(assignment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error closing assignment: {str(e)}")
            return Response(
                {'error': 'Failed to close assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate an assignment
        """
        try:
            original_assignment = self.get_object()
            
            # Create a copy of the assignment data
            assignment_data = {
                'title': request.data.get('title', f"Copy of {original_assignment.title}"),
                'description': original_assignment.description,
                'assignment_type': original_assignment.assignment_type,
                'category': original_assignment.category.id if original_assignment.category else None,
                'subject': original_assignment.subject.id,
                'teacher': original_assignment.teacher.id,
                'classroom': original_assignment.classroom.id if original_assignment.classroom else None,
                'stream': original_assignment.stream.id if original_assignment.stream else None,
                'academic_year': original_assignment.academic_year.id,
                'term': original_assignment.term.id,
                'curriculum': original_assignment.curriculum,
                'due_date': request.data.get('due_date', original_assignment.due_date),
                'total_marks': original_assignment.total_marks,
                'passing_marks': original_assignment.passing_marks,
                'difficulty_level': original_assignment.difficulty_level,
                'estimated_completion_time': original_assignment.estimated_completion_time,
                'instructions': original_assignment.instructions,
                'learning_objectives': original_assignment.learning_objectives,
                'resources': original_assignment.resources,
                'rubric': original_assignment.rubric,
                'allow_late_submission': original_assignment.allow_late_submission,
                'late_submission_penalty': original_assignment.late_submission_penalty,
                'allow_resubmission': original_assignment.allow_resubmission,
                'max_resubmissions': original_assignment.max_resubmissions,
                'require_approval': original_assignment.require_approval,
                'is_group_assignment': original_assignment.is_group_assignment,
                'max_group_size': original_assignment.max_group_size,
                'status': 'draft'
            }
            
            # Create the duplicate
            serializer = AssignmentCreateSerializer(data=assignment_data, context={'request': request})
            
            if serializer.is_valid():
                duplicate_assignment = serializer.save()
                logger.info(f"Assignment duplicated: {original_assignment.title} -> {duplicate_assignment.title}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error duplicating assignment: {str(e)}")
            return Response(
                {'error': 'Failed to duplicate assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get detailed statistics for an assignment
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can view assignment statistics.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Calculate statistics
            student_assignments = assignment.student_assignments.all()
            total_students = assignment.total_students
            
            # Grade distribution
            grade_distribution = student_assignments.filter(status='graded').values('grade').annotate(
                count=Count('id'),
                percentage=Count('id') * 100 / total_students if total_students > 0 else 0
            )
            
            stats = {
                'total_students': total_students,
                'total_submissions': student_assignments.filter(
                    status__in=['submitted', 'late', 'graded']
                ).count(),
                'graded_submissions': student_assignments.filter(status='graded').count(),
                'pending_grading': student_assignments.filter(status__in=['submitted', 'late']).count(),
                'not_submitted': student_assignments.filter(status='not_submitted').count(),
                'late_submissions': student_assignments.filter(status='late').count(),
                'average_score': float(assignment.average_score),
                'completion_rate': float(assignment.completion_rate),
                'high_score': float(student_assignments.filter(status='graded').aggregate(
                    max_score=Max('marks_obtained')
                )['max_score'] or 0),
                'low_score': float(student_assignments.filter(status='graded').aggregate(
                    min_score=Min('marks_obtained')
                )['min_score'] or 0),
                'grade_distribution': list(grade_distribution),
                'submission_timeline': self._get_submission_timeline(assignment)
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting assignment stats: {str(e)}")
            return Response(
                {'error': 'Failed to get assignment statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """
        Get all submissions for this assignment
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can view all submissions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            submissions = assignment.student_assignments.all().select_related(
                'student', 'graded_by'
            )
            
            # Filter based on query parameters
            status_filter = request.query_params.get('status')
            if status_filter:
                submissions = submissions.filter(status=status_filter)
            
            serializer = StudentAssignmentMiniSerializer(submissions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve submissions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Get assignment analytics and statistics
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can view analytics.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get or create analytics
            analytics, created = AssignmentAnalytics.objects.get_or_create(assignment=assignment)
            
            # Update analytics data
            analytics.update_analytics()
            
            return Response({
                'submission_stats': assignment.submission_stats,
                'average_score': assignment.average_score,
                'completion_rate': assignment.completion_rate,
                'views_count': assignment.views_count,
                'analytics': {
                    'total_views': analytics.total_views,
                    'unique_viewers': analytics.unique_viewers,
                    'average_time_spent': analytics.average_time_spent,
                    'common_issues': analytics.common_issues,
                    'plagiarism_cases': analytics.plagiarism_cases
                }
            })
        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get comments for this assignment
        """
        try:
            assignment = self.get_object()
            
            comments = assignment.comments.all().select_related(
                'author', 'student_assignment'
            ).order_by('created_at')
            
            serializer = AssignmentCommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving comments: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve comments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_attachment(self, request, pk=None):
        """
        Upload attachment for assignment
        """
        try:
            assignment = self.get_object()
            
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can upload attachments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            attachment_file = request.FILES.get('file')
            if not attachment_file:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save attachment
            assignment.attachment = attachment_file
            assignment.save()
            
            return Response({
                'success': True,
                'message': 'Attachment uploaded successfully',
                'attachment_url': assignment.attachment.url if assignment.attachment else None
            })
        except Exception as e:
            logger.error(f"Error uploading attachment: {str(e)}")
            return Response(
                {'error': 'Failed to upload attachment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==================== COLLECTION ACTIONS ====================
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """
        Get assignments relevant to current user with submission status
        """
        try:
            user = request.user
            queryset = self.get_queryset()
            
            if user.is_student and hasattr(user, 'student_profile'):
                # Student: show assignments with submission status
                student = user.student_profile
                assignments = queryset.filter(status__in=['published', 'in_progress'])
                
                # Get student's submissions to determine status
                student_submissions = StudentAssignment.objects.filter(
                    student=student,
                    assignment__in=assignments
                ).select_related('assignment')
                
                # Create a mapping of assignment ID to submission status
                submission_status_map = {
                    sub.assignment_id: sub.status for sub in student_submissions
                }
                
                # Add submission status to each assignment
                assignment_list = []
                for assignment in assignments:
                    assignment_data = AssignmentListSerializer(
                        assignment, 
                        context={'request': request}
                    ).data
                    assignment_data['my_submission_status'] = submission_status_map.get(
                        assignment.id, 'not_started'
                    )
                    assignment_list.append(assignment_data)
                
                return Response(assignment_list)
                
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                # Teacher: show their own assignments
                teacher = user.teacher_profile
                assignments = queryset.filter(teacher=teacher)
                
                page = self.paginate_queryset(assignments)
                if page is not None:
                    serializer = AssignmentListSerializer(
                        page, many=True, context={'request': request}
                    )
                    return self.get_paginated_response(serializer.data)
                
                serializer = AssignmentListSerializer(
                    assignments, many=True, context={'request': request}
                )
                return Response(serializer.data)
            
            else:
                return Response(
                    {'error': 'This endpoint is only available for students and teachers.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error retrieving my assignments: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get assignments with upcoming deadlines
        """
        try:
            user = request.user
            queryset = self.get_queryset()
            
            # Get days parameter
            days = int(request.query_params.get('days', 7))
            next_deadline = timezone.now() + timedelta(days=days)
            
            # Filter for upcoming deadlines
            upcoming = queryset.filter(
                due_date__gte=timezone.now().date(),
                due_date__lte=next_deadline.date(),
                status__in=['published', 'in_progress']
            ).order_by('due_date')
            
            if user.is_student and hasattr(user, 'student_profile'):
                # For students, only show assignments for their classroom
                student = user.student_profile
                if hasattr(student, 'classroom') and student.classroom:
                    upcoming = upcoming.filter(classroom=student.classroom)
                else:
                    upcoming = upcoming.none()
            
            page = self.paginate_queryset(upcoming)
            if page is not None:
                serializer = AssignmentListSerializer(
                    page, many=True, context={'request': request}
                )
                return self.get_paginated_response(serializer.data)
            
            serializer = AssignmentListSerializer(
                upcoming, many=True, context={'request': request}
            )
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving upcoming deadlines: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve upcoming deadlines'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue assignments
        """
        try:
            user = request.user
            queryset = self.get_queryset()
            
            overdue = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['published', 'in_progress']
            ).order_by('due_date')
            
            if user.is_student and hasattr(user, 'student_profile'):
                # For students, only show assignments for their classroom
                student = user.student_profile
                if hasattr(student, 'classroom') and student.classroom:
                    overdue = overdue.filter(classroom=student.classroom)
                else:
                    overdue = overdue.none()
            
            page = self.paginate_queryset(overdue)
            if page is not None:
                serializer = AssignmentListSerializer(
                    page, many=True, context={'request': request}
                )
                return self.get_paginated_response(serializer.data)
            
            serializer = AssignmentListSerializer(
                overdue, many=True, context={'request': request}
            )
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving overdue assignments: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve overdue assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """
        Get assignment notifications for current user
        """
        try:
            user = request.user
            
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                
                # Get assignments with upcoming deadlines (next 3 days)
                upcoming_cutoff = timezone.now() + timedelta(days=3)
                upcoming_assignments = self.get_queryset().filter(
                    classroom=student.classroom,
                    due_date__gte=timezone.now().date(),
                    due_date__lte=upcoming_cutoff.date(),
                    status__in=['published', 'in_progress']
                )
                
                # Get overdue assignments
                overdue_assignments = self.get_queryset().filter(
                    classroom=student.classroom,
                    due_date__lt=timezone.now().date(),
                    status__in=['published', 'in_progress']
                )
                
                notifications = []
                
                # Upcoming deadline notifications
                for assignment in upcoming_assignments:
                    days_left = (assignment.due_date.date() - timezone.now().date()).days
                    notifications.append({
                        'type': 'upcoming_deadline',
                        'assignment_id': assignment.id,
                        'assignment_title': assignment.title,
                        'due_date': assignment.due_date,
                        'days_left': days_left,
                        'message': f'Assignment "{assignment.title}" due in {days_left} day(s)',
                        'priority': 'high' if days_left <= 1 else 'medium'
                    })
                
                # Overdue notifications
                for assignment in overdue_assignments:
                    days_overdue = (timezone.now().date() - assignment.due_date.date()).days
                    notifications.append({
                        'type': 'overdue',
                        'assignment_id': assignment.id,
                        'assignment_title': assignment.title,
                        'due_date': assignment.due_date,
                        'days_overdue': days_overdue,
                        'message': f'Assignment "{assignment.title}" is {days_overdue} day(s) overdue',
                        'priority': 'critical'
                    })
                
                return Response(notifications)
            
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                
                # Teacher notifications
                notifications = []
                
                # Assignments pending grading
                pending_grading = StudentAssignment.objects.filter(
                    assignment__teacher=teacher,
                    status__in=['submitted', 'late']
                ).count()
                
                if pending_grading > 0:
                    notifications.append({
                        'type': 'pending_grading',
                        'count': pending_grading,
                        'message': f'You have {pending_grading} assignment(s) pending grading',
                        'priority': 'medium'
                    })
                
                # Assignments with upcoming deadlines
                upcoming_cutoff = timezone.now() + timedelta(days=3)
                upcoming_assignments = self.get_queryset().filter(
                    teacher=teacher,
                    due_date__gte=timezone.now().date(),
                    due_date__lte=upcoming_cutoff.date(),
                    status__in=['published', 'in_progress']
                ).count()
                
                if upcoming_assignments > 0:
                    notifications.append({
                        'type': 'upcoming_deadline_teacher',
                        'count': upcoming_assignments,
                        'message': f'You have {upcoming_assignments} assignment(s) with upcoming deadlines',
                        'priority': 'medium'
                    })
                
                return Response(notifications)
            
            return Response([])
        except Exception as e:
            logger.error(f"Error retrieving notifications: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve notifications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create assignments from JSON data
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can bulk create assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            assignments_data = request.data.get('assignments', [])
            
            if not assignments_data or not isinstance(assignments_data, list):
                return Response(
                    {'error': 'Invalid data format. Expected list of assignments.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_assignments = []
            errors = []
            
            for idx, assignment_data in enumerate(assignments_data):
                try:
                    serializer = AssignmentCreateSerializer(
                        data=assignment_data,
                        context={'request': request}
                    )
                    
                    if serializer.is_valid():
                        assignment = serializer.save()
                        created_assignments.append(assignment.id)
                    else:
                        errors.append({
                            'index': idx,
                            'errors': serializer.errors,
                            'data': assignment_data
                        })
                except Exception as e:
                    errors.append({
                        'index': idx,
                        'error': str(e),
                        'data': assignment_data
                    })
            
            return Response({
                'success': len(errors) == 0,
                'created_count': len(created_assignments),
                'error_count': len(errors),
                'created_assignments': created_assignments,
                'errors': errors
            })
        except Exception as e:
            logger.error(f"Error in bulk create: {str(e)}")
            return Response(
                {'error': 'Failed to bulk create assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update assignments
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can bulk update assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            updates_data = request.data.get('updates', [])
            
            if not updates_data or not isinstance(updates_data, list):
                return Response(
                    {'error': 'Invalid data format. Expected list of updates.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            updated_assignments = []
            errors = []
            
            for update_data in updates_data:
                assignment_id = update_data.get('assignment_id')
                update_fields = update_data.get('fields', {})
                
                if not assignment_id or not update_fields:
                    errors.append({
                        'assignment_id': assignment_id,
                        'error': 'Missing assignment_id or fields'
                    })
                    continue
                
                try:
                    assignment = Assignment.objects.get(id=assignment_id)
                    
                    # Check if user can update this assignment
                    if not (request.user.is_staff or request.user.is_superuser or 
                           (request.user.is_teacher and assignment.teacher.user == request.user)):
                        errors.append({
                            'assignment_id': assignment_id,
                            'error': 'Permission denied'
                        })
                        continue
                    
                    # Update assignment
                    for field, value in update_fields.items():
                        if hasattr(assignment, field):
                            setattr(assignment, field, value)
                    
                    assignment.save()
                    updated_assignments.append(assignment_id)
                    
                except Assignment.DoesNotExist:
                    errors.append({
                        'assignment_id': assignment_id,
                        'error': 'Assignment not found'
                    })
                except Exception as e:
                    errors.append({
                        'assignment_id': assignment_id,
                        'error': str(e)
                    })
            
            return Response({
                'success': len(errors) == 0,
                'updated_count': len(updated_assignments),
                'error_count': len(errors),
                'updated_assignments': updated_assignments,
                'errors': errors
            })
        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            return Response(
                {'error': 'Failed to bulk update assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export assignments to CSV or Excel
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can export assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            format_type = request.query_params.get('format', 'csv').lower()
            
            if format_type not in ['csv', 'excel']:
                return Response(
                    {'error': 'Invalid format. Supported formats: csv, excel'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            queryset = self.filter_queryset(self.get_queryset())
            
            # Prepare data for export
            assignments_data = []
            for assignment in queryset:
                assignments_data.append({
                    'ID': str(assignment.id),
                    'Title': assignment.title,
                    'Subject': assignment.subject.name if assignment.subject else '',
                    'Teacher': assignment.teacher.get_full_name() if assignment.teacher else '',
                    'Class': assignment.classroom.name if assignment.classroom else '',
                    'Due Date': assignment.due_date.strftime('%Y-%m-%d %H:%M') if assignment.due_date else '',
                    'Total Marks': str(assignment.total_marks),
                    'Passing Marks': str(assignment.passing_marks),
                    'Status': assignment.status,
                    'Type': assignment.assignment_type,
                    'Created At': assignment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Published At': assignment.published_at.strftime('%Y-%m-%d %H:%M') if assignment.published_at else '',
                    'Average Score': str(assignment.average_score),
                    'Completion Rate': str(assignment.completion_rate) + '%'
                })
            
            if format_type == 'csv':
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="assignments_export.csv"'
                
                writer = csv.DictWriter(response, fieldnames=assignments_data[0].keys() if assignments_data else [])
                writer.writeheader()
                writer.writerows(assignments_data)
                
                return response
            else:
                # For Excel export, you'll need to implement or use a library like openpyxl
                return Response(
                    {'error': 'Excel export not implemented yet. Use CSV format.'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
            
        except Exception as e:
            logger.error(f"Error exporting assignments: {str(e)}")
            return Response(
                {'error': 'Failed to export assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==================== HELPER METHODS ====================
    
    def _get_submission_timeline(self, assignment):
        """
        Get submission timeline data for charting
        """
        submissions = assignment.student_assignments.filter(
            submission_date__isnull=False
        ).values('submission_date__date').annotate(
            count=Count('id')
        ).order_by('submission_date__date')
        
        timeline = []
        for item in submissions:
            timeline.append({
                'date': item['submission_date__date'].strftime('%Y-%m-%d'),
                'count': item['count']
            })
        
        return timeline
    
    def _get_grade_distribution(self, assignment):
        """
        Calculate grade distribution
        """
        from django.db.models import Count
        
        distribution = StudentAssignment.objects.filter(
            assignment=assignment,
            status='graded',
            grade__isnull=False
        ).values('grade').annotate(
            count=Count('id')
        ).order_by('grade')
        
        total_graded = assignment.student_assignments.filter(status='graded').count()
        
        result = []
        for item in distribution:
            percentage = (item['count'] / total_graded * 100) if total_graded > 0 else 0
            result.append({
                'grade': item['grade'],
                'count': item['count'],
                'percentage': round(percentage, 2)
            })
        
        return result

# In assignments/views.py - Complete StudentAssignmentViewSet with all endpoints

class StudentAssignmentViewSet(viewsets.ModelViewSet):
    """
    Complete ViewSet for managing student assignments and submissions
    """
    permission_classes = [IsAuthenticated]
    queryset = StudentAssignment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'assignment__title', 'student__user__first_name', 
        'student__user__last_name', 'student__admission_number'
    ]
    filterset_fields = ['status', 'assignment__subject', 'assignment__teacher', 'is_late']
    ordering_fields = ['submission_date', 'graded_at', 'marks_obtained', 'created_at']
    ordering = ['-submission_date']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """
        Filter student assignments based on user role
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'student', 'graded_by', 'group'
        ).prefetch_related('assignment__subject')
        
        try:
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                queryset = queryset.filter(student=student)
                
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                queryset = queryset.filter(assignment__teacher=teacher)
                
            elif user.is_staff or user.is_superuser:
                # Admin users can see all submissions
                pass
                
            else:
                queryset = queryset.none()
        except Exception as e:
            logger.error(f"Error filtering student assignments: {str(e)}")
            queryset = StudentAssignment.objects.none()
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return StudentAssignmentMiniSerializer
        elif self.action == 'retrieve':
            return StudentAssignmentDetailSerializer
        elif self.action == 'submit':
            return StudentAssignmentSubmitSerializer
        elif self.action == 'grade':
            return StudentAssignmentGradeSerializer
        elif self.action == 'upload_attachment':
            return StudentAssignmentSubmitSerializer  # Reuse for file uploads
        return StudentAssignmentDetailSerializer
    
    def get_serializer_context(self):
        """
        Add request context to serializer
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Override create to handle student assignment creation
        """
        # Students should not be able to create student assignments directly
        if request.user.is_student:
            return Response(
                {'error': 'Students cannot create assignments directly. Use the submit action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
    
    # ==================== CUSTOM ACTIONS ====================
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit an assignment
        """
        try:
            student_assignment = self.get_object()
            
            # Check if user owns this assignment
            if (request.user.is_student and hasattr(request.user, 'student_profile') and 
                student_assignment.student != request.user.student_profile):
                return Response(
                    {'error': 'You can only submit your own assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if assignment is closed
            if student_assignment.assignment.status in ['closed', 'graded']:
                return Response(
                    {'error': 'Cannot submit. Assignment is closed or graded.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(student_assignment, data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    updated_assignment = serializer.save()
                    logger.info(f"Assignment submitted by student: {student_assignment.student}")
                
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error submitting assignment: {str(e)}")
            return Response(
                {'error': 'Failed to submit assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """
        Grade an assignment (teachers only)
        """
        try:
            student_assignment = self.get_object()
            
            # Check if user is a teacher and owns this assignment
            if not (request.user.is_teacher and hasattr(request.user, 'teacher_profile')):
                return Response(
                    {'error': 'Only teachers can grade assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if student_assignment.assignment.teacher != request.user.teacher_profile:
                return Response(
                    {'error': 'You can only grade assignments that belong to you.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(student_assignment, data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    updated_assignment = serializer.save()
                    logger.info(f"Assignment graded by teacher: {request.user.teacher_profile}")
                
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error grading assignment: {str(e)}")
            return Response(
                {'error': 'Failed to grade assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def allow_resubmission(self, request, pk=None):
        """
        Allow student to resubmit assignment
        """
        try:
            student_assignment = self.get_object()
            
            # Check if user is a teacher and owns this assignment
            if not (request.user.is_teacher and hasattr(request.user, 'teacher_profile')):
                return Response(
                    {'error': 'Only teachers can allow resubmissions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if student_assignment.assignment.teacher != request.user.teacher_profile:
                return Response(
                    {'error': 'You can only modify assignments that belong to you.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if resubmission is already allowed
            if student_assignment.status == 'returned':
                return Response(
                    {'error': 'Assignment already returned for revision.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to allow resubmission
            student_assignment.status = 'returned'
            student_assignment.teacher_feedback = request.data.get('feedback', 'Please resubmit your assignment.')
            student_assignment.save()
            
            logger.info(f"Resubmission allowed for assignment: {student_assignment.id}")
            
            serializer = self.get_serializer(student_assignment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error allowing resubmission: {str(e)}")
            return Response(
                {'error': 'Failed to allow resubmission'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def return_for_revision(self, request, pk=None):
        """
        Return assignment for revision (teachers only)
        """
        try:
            student_assignment = self.get_object()
            
            # Check if user is a teacher and owns this assignment
            if not (request.user.is_teacher and hasattr(request.user, 'teacher_profile')):
                return Response(
                    {'error': 'Only teachers can return assignments for revision.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if student_assignment.assignment.teacher != request.user.teacher_profile:
                return Response(
                    {'error': 'You can only return assignments that belong to you.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            feedback = request.data.get('feedback', 'Please revise your assignment.')
            
            # Set status to returned for revision
            student_assignment.status = 'returned'
            student_assignment.teacher_feedback = feedback
            student_assignment.save()
            
            logger.info(f"Assignment returned for revision: {student_assignment.id}")
            
            serializer = self.get_serializer(student_assignment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error returning assignment for revision: {str(e)}")
            return Response(
                {'error': 'Failed to return assignment for revision'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def submission_history(self, request, pk=None):
        """
        Get submission history for a student assignment
        """
        try:
            student_assignment = self.get_object()
            
            # Check permissions
            if (request.user.is_student and hasattr(request.user, 'student_profile') and 
                student_assignment.student != request.user.student_profile):
                return Response(
                    {'error': 'You can only view your own submission history.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get all versions of this assignment (including current)
            history = StudentAssignment.objects.filter(
                Q(id=student_assignment.id) | 
                Q(previous_version=student_assignment) |
                Q(previous_version__previous_version=student_assignment)
            ).order_by('version')
            
            serializer = StudentAssignmentMiniSerializer(history, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving submission history: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve submission history'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_attachment(self, request, pk=None):
        """
        Upload submission attachment
        """
        try:
            student_assignment = self.get_object()
            
            # Check if user owns this assignment
            if (request.user.is_student and hasattr(request.user, 'student_profile') and 
                student_assignment.student != request.user.student_profile):
                return Response(
                    {'error': 'You can only upload attachments to your own assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            attachment_file = request.FILES.get('file')
            if not attachment_file:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle single file upload (submission_file)
            if 'submission_file' in request.FILES:
                student_assignment.submission_file = attachment_file
            else:
                # Handle multiple files (submission_files as JSON)
                current_files = student_assignment.submission_files or []
                if not isinstance(current_files, list):
                    current_files = []
                
                # Create a new file entry
                file_entry = {
                    'id': str(uuid.uuid4()),
                    'name': attachment_file.name,
                    'size': attachment_file.size,
                    'type': attachment_file.content_type,
                    'url': '',  # Will be set by FileField
                    'uploaded_at': timezone.now().isoformat()
                }
                
                # Save the file to a temporary location
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment_file.name)[1]) as tmp:
                    for chunk in attachment_file.chunks():
                        tmp.write(chunk)
                    
                    # You'll need to implement proper file storage
                    # For now, we'll just save the reference
                    file_entry['temp_path'] = tmp.name
                
                current_files.append(file_entry)
                student_assignment.submission_files = current_files
            
            student_assignment.save()
            
            return Response({
                'success': True,
                'message': 'Attachment uploaded successfully',
                'file_url': student_assignment.submission_file.url if student_assignment.submission_file else None,
                'files': student_assignment.submission_files
            })
        except Exception as e:
            logger.error(f"Error uploading submission attachment: {str(e)}")
            return Response(
                {'error': 'Failed to upload attachment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==================== COLLECTION ACTIONS ====================
    
    @action(detail=False, methods=['get'])
    def pending_grading(self, request):
        """
        Get assignments pending grading (for teachers)
        """
        try:
            if not hasattr(request.user, 'teacher_profile'):
                return Response(
                    {'error': 'Only teachers can access this endpoint.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            teacher = request.user.teacher_profile
            pending = self.get_queryset().filter(
                assignment__teacher=teacher,
                status__in=['submitted', 'late']
            ).order_by('submission_date')
            
            page = self.paginate_queryset(pending)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(pending, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving pending grading: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve pending assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """
        Get current user's submissions (for students)
        """
        try:
            if not hasattr(request.user, 'student_profile'):
                return Response(
                    {'error': 'Only students can access this endpoint.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            student = request.user.student_profile
            submissions = self.get_queryset().filter(student=student).order_by('-submission_date')
            
            page = self.paginate_queryset(submissions)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(submissions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving my submissions: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve submissions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_grade(self, request):
        """
        Bulk grade student assignments
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can bulk grade assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            grading_data = request.data.get('grading', [])
            
            if not grading_data or not isinstance(grading_data, list):
                return Response(
                    {'error': 'Invalid data format. Expected list of grading data.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            graded_assignments = []
            errors = []
            
            for grade_data in grading_data:
                student_assignment_id = grade_data.get('student_assignment_id')
                marks_obtained = grade_data.get('marks_obtained')
                feedback = grade_data.get('feedback', '')
                
                if not student_assignment_id or marks_obtained is None:
                    errors.append({
                        'student_assignment_id': student_assignment_id,
                        'error': 'Missing student_assignment_id or marks_obtained'
                    })
                    continue
                
                try:
                    student_assignment = StudentAssignment.objects.get(id=student_assignment_id)
                    
                    # Check if user can grade this assignment
                    if not (request.user.is_staff or request.user.is_superuser or 
                           (request.user.is_teacher and student_assignment.assignment.teacher.user == request.user)):
                        errors.append({
                            'student_assignment_id': student_assignment_id,
                            'error': 'Permission denied'
                        })
                        continue
                    
                    # Grade the assignment
                    student_assignment.marks_obtained = marks_obtained
                    student_assignment.teacher_feedback = feedback
                    student_assignment.status = 'graded'
                    student_assignment.graded_at = timezone.now()
                    
                    if hasattr(request.user, 'teacher_profile'):
                        student_assignment.graded_by = request.user.teacher_profile
                    
                    student_assignment.save()
                    graded_assignments.append(student_assignment_id)
                    
                except StudentAssignment.DoesNotExist:
                    errors.append({
                        'student_assignment_id': student_assignment_id,
                        'error': 'Student assignment not found'
                    })
                except Exception as e:
                    errors.append({
                        'student_assignment_id': student_assignment_id,
                        'error': str(e)
                    })
            
            return Response({
                'success': len(errors) == 0,
                'graded_count': len(graded_assignments),
                'error_count': len(errors),
                'graded_assignments': graded_assignments,
                'errors': errors
            })
        except Exception as e:
            logger.error(f"Error in bulk grade: {str(e)}")
            return Response(
                {'error': 'Failed to bulk grade assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_grades(self, request):
        """
        Export grades to CSV or Excel
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can export grades.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            format_type = request.query_params.get('format', 'csv').lower()
            
            if format_type not in ['csv', 'excel']:
                return Response(
                    {'error': 'Invalid format. Supported formats: csv, excel'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            queryset = self.filter_queryset(self.get_queryset())
            
            # If teacher, only show their assignments
            if hasattr(request.user, 'teacher_profile'):
                teacher = request.user.teacher_profile
                queryset = queryset.filter(assignment__teacher=teacher)
            
            # Prepare data for export
            grades_data = []
            for student_assignment in queryset:
                grades_data.append({
                    'Student ID': str(student_assignment.student.id) if student_assignment.student else '',
                    'Student Name': student_assignment.student.get_full_name() if student_assignment.student else '',
                    'Admission Number': student_assignment.student.admission_number if hasattr(student_assignment.student, 'admission_number') else '',
                    'Assignment ID': str(student_assignment.assignment.id),
                    'Assignment Title': student_assignment.assignment.title,
                    'Subject': student_assignment.assignment.subject.name if student_assignment.assignment.subject else '',
                    'Total Marks': str(student_assignment.assignment.total_marks),
                    'Marks Obtained': str(student_assignment.marks_obtained) if student_assignment.marks_obtained else '',
                    'Percentage': str(student_assignment.percentage) + '%' if student_assignment.marks_obtained else '',
                    'Grade': student_assignment.grade or '',
                    'Status': student_assignment.status,
                    'Submission Date': student_assignment.submission_date.strftime('%Y-%m-%d %H:%M') if student_assignment.submission_date else '',
                    'Graded At': student_assignment.graded_at.strftime('%Y-%m-%d %H:%M') if student_assignment.graded_at else '',
                    'Graded By': student_assignment.graded_by.get_full_name() if student_assignment.graded_by else '',
                    'Feedback': student_assignment.teacher_feedback or '',
                    'Late Submission': 'Yes' if student_assignment.is_late else 'No'
                })
            
            if format_type == 'csv':
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="grades_export.csv"'
                
                if grades_data:
                    writer = csv.DictWriter(response, fieldnames=grades_data[0].keys())
                    writer.writeheader()
                    writer.writerows(grades_data)
                
                return response
            else:
                # For Excel export
                return Response(
                    {'error': 'Excel export not implemented yet. Use CSV format.'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
            
        except Exception as e:
            logger.error(f"Error exporting grades: {str(e)}")
            return Response(
                {'error': 'Failed to export grades'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def import_grades(self, request):
        """
        Import grades from CSV file
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can import grades.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            import_file = request.FILES.get('file')
            if not import_file:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check file type
            if not import_file.name.endswith('.csv'):
                return Response(
                    {'error': 'Only CSV files are supported'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            import csv
            import io
            
            # Read CSV file
            file_content = import_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # start=2 to account for header
                try:
                    student_assignment_id = row.get('Student Assignment ID')
                    marks_obtained = row.get('Marks Obtained')
                    
                    if not student_assignment_id or not marks_obtained:
                        errors.append({
                            'row': row_num,
                            'error': 'Missing required fields',
                            'data': row
                        })
                        continue
                    
                    student_assignment = StudentAssignment.objects.get(id=student_assignment_id)
                    
                    # Check permissions
                    if not (request.user.is_staff or request.user.is_superuser or 
                           (request.user.is_teacher and student_assignment.assignment.teacher.user == request.user)):
                        errors.append({
                            'row': row_num,
                            'error': 'Permission denied',
                            'data': row
                        })
                        continue
                    
                    # Update grade
                    student_assignment.marks_obtained = float(marks_obtained)
                    student_assignment.status = 'graded'
                    student_assignment.graded_at = timezone.now()
                    
                    if hasattr(request.user, 'teacher_profile'):
                        student_assignment.graded_by = request.user.teacher_profile
                    
                    student_assignment.save()
                    imported_count += 1
                    
                except StudentAssignment.DoesNotExist:
                    errors.append({
                        'row': row_num,
                        'error': 'Student assignment not found',
                        'data': row
                    })
                except ValueError:
                    errors.append({
                        'row': row_num,
                        'error': 'Invalid marks format',
                        'data': row
                    })
                except Exception as e:
                    errors.append({
                        'row': row_num,
                        'error': str(e),
                        'data': row
                    })
            
            return Response({
                'success': len(errors) == 0,
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors
            })
        except Exception as e:
            logger.error(f"Error importing grades: {str(e)}")
            return Response(
                {'error': 'Failed to import grades'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==================== FILTER ENDPOINTS ====================
    
    @action(detail=False, methods=['get'])
    def by_assignment(self, request):
        """
        Get student assignments by assignment ID
        """
        try:
            assignment_id = request.query_params.get('assignment_id')
            if not assignment_id:
                return Response(
                    {'error': 'assignment_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if assignment exists
            try:
                assignment = Assignment.objects.get(id=assignment_id)
            except Assignment.DoesNotExist:
                return Response(
                    {'error': 'Assignment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions
            if request.user.is_student:
                # Students can only see their own assignments
                if hasattr(request.user, 'student_profile'):
                    student = request.user.student_profile
                    queryset = self.get_queryset().filter(
                        assignment=assignment,
                        student=student
                    )
                else:
                    queryset = StudentAssignment.objects.none()
            elif request.user.is_teacher:
                # Teachers can see all submissions for their assignments
                if hasattr(request.user, 'teacher_profile'):
                    teacher = request.user.teacher_profile
                    if assignment.teacher != teacher:
                        return Response(
                            {'error': 'You can only view submissions for your own assignments'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                    queryset = self.get_queryset().filter(assignment=assignment)
                else:
                    queryset = StudentAssignment.objects.none()
            else:
                # Admin can see all
                queryset = self.get_queryset().filter(assignment=assignment)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving assignments by assignment: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve student assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """
        Get student assignments by student ID
        """
        try:
            student_id = request.query_params.get('student_id')
            if not student_id:
                return Response(
                    {'error': 'student_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            if request.user.is_student:
                # Students can only see their own assignments
                if hasattr(request.user, 'student_profile'):
                    if str(request.user.student_profile.id) != student_id:
                        return Response(
                            {'error': 'You can only view your own assignments'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                else:
                    queryset = StudentAssignment.objects.none()
            
            # Get student assignments
            queryset = self.get_queryset().filter(student__id=student_id)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving assignments by student: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve student assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get student assignments by status
        """
        try:
            status_filter = request.query_params.get('status')
            if not status_filter:
                return Response(
                    {'error': 'status parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            queryset = self.get_queryset().filter(status=status_filter)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving assignments by status: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve student assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def late_submissions(self, request):
        """
        Get late submissions
        """
        try:
            # Check permissions
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                return Response(
                    {'error': 'Only teachers and administrators can view late submissions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            queryset = self.get_queryset().filter(status='late')
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = StudentAssignmentMiniSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StudentAssignmentMiniSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving late submissions: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve late submissions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssignmentGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment groups
    """
    permission_classes = [IsAuthenticated]
    queryset = AssignmentGroup.objects.all()
    serializer_class = AssignmentGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'assignment__title']
    filterset_fields = ['assignment']
    
    def get_queryset(self):
        """
        Filter groups based on user role
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'leader'
        ).prefetch_related('members')
        
        try:
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                # Show groups where student is a member or leader
                queryset = queryset.filter(
                    Q(leader=student) | Q(members=student)
                ).distinct()
                
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                queryset = queryset.filter(assignment__teacher=teacher)
        except Exception as e:
            logger.error(f"Error filtering groups: {str(e)}")
            queryset = AssignmentGroup.objects.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set leader to current student when creating group
        """
        try:
            if self.request.user.is_student and hasattr(self.request.user, 'student_profile'):
                serializer.save(leader=self.request.user.student_profile)
            else:
                serializer.save()
            logger.info(f"Assignment group created: {serializer.instance.name}")
        except Exception as e:
            logger.error(f"Error creating assignment group: {str(e)}")
            raise


class AssignmentCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment comments
    """
    permission_classes = [IsAuthenticated]
    queryset = AssignmentComment.objects.all()
    serializer_class = AssignmentCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['assignment', 'student_assignment', 'is_private']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        """
        Filter comments based on user role and privacy
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'student_assignment', 'author', 'parent_comment'
        )
        
        try:
            # Students can only see non-private comments or their own private comments
            if user.is_student:
                queryset = queryset.filter(
                    Q(is_private=False) | Q(author=user)
                )
        except Exception as e:
            logger.error(f"Error filtering comments: {str(e)}")
            queryset = AssignmentComment.objects.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set author to current user when creating comment
        """
        try:
            serializer.save(author=self.request.user)
            logger.info(f"Comment created by user: {self.request.user}")
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise


class GroupMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing group memberships
    """
    permission_classes = [IsAuthenticated]
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
    
    def get_queryset(self):
        """
        Filter memberships based on user role
        """
        user = self.request.user
        queryset = super().get_queryset().select_related('group', 'student')
        
        try:
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                queryset = queryset.filter(
                    Q(group__leader=student) | Q(student=student)
                )
                
            elif user.is_teacher and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                queryset = queryset.filter(group__assignment__teacher=teacher)
        except Exception as e:
            logger.error(f"Error filtering group memberships: {str(e)}")
            queryset = GroupMembership.objects.none()
        
        return queryset


# Dashboard and Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_dashboard(request):
    """
    Get assignment dashboard data for current user
    """
    try:
        user = request.user
        
        if user.is_student and hasattr(user, 'student_profile'):
            student = user.student_profile
            
            # Student dashboard
            total_assignments = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress']
            ).count()
            
            student_assignments = StudentAssignment.objects.filter(student=student)
            pending_assignments = student_assignments.filter(status='not_started').count()
            submitted_assignments = student_assignments.filter(status__in=['submitted', 'late']).count()
            graded_assignments = student_assignments.filter(status='graded').count()
            
            # Calculate overdue assignments
            overdue_assignments = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress'],
                due_date__lt=timezone.now().date()
            ).exclude(
                student_assignments__student=student,
                student_assignments__status__in=['submitted', 'late', 'graded']
            ).count()
            
            average_score = student_assignments.filter(status='graded').aggregate(
                avg=Avg('final_marks')
            )['avg'] or 0
            
            recent_assignments = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress']
            ).order_by('-created_at')[:5]
            
            upcoming_deadlines = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress'],
                due_date__gte=timezone.now().date()
            ).order_by('due_date')[:5]
            
        elif user.is_teacher and hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            
            # Teacher dashboard
            total_assignments = Assignment.objects.filter(teacher=teacher).count()
            pending_assignments = Assignment.objects.filter(
                teacher=teacher,
                status='draft'
            ).count()
            
            student_assignments = StudentAssignment.objects.filter(assignment__teacher=teacher)
            submitted_assignments = student_assignments.filter(
                status__in=['submitted', 'late']
            ).count()
            graded_assignments = student_assignments.filter(status='graded').count()
            
            overdue_assignments = Assignment.objects.filter(
                teacher=teacher,
                status__in=['published', 'in_progress'],
                due_date__lt=timezone.now().date()
            ).count()
            
            average_score = student_assignments.filter(status='graded').aggregate(
                avg=Avg('final_marks')
            )['avg'] or 0
            
            recent_assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')[:5]
            upcoming_deadlines = Assignment.objects.filter(
                teacher=teacher,
                due_date__gte=timezone.now().date()
            ).order_by('due_date')[:5]
            
        else:
            return Response(
                {'error': 'Dashboard not available for this user type.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'total_assignments': total_assignments,
            'pending_assignments': pending_assignments,
            'submitted_assignments': submitted_assignments,
            'graded_assignments': graded_assignments,
            'overdue_assignments': overdue_assignments,
            'average_score': float(average_score),
            'recent_assignments': AssignmentListSerializer(
                recent_assignments, many=True, context={'request': request}
            ).data,
            'upcoming_deadlines': AssignmentListSerializer(
                upcoming_deadlines, many=True, context={'request': request}
            ).data,
        }
        
        serializer = AssignmentDashboardSerializer(data)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        return Response(
            {'error': 'Failed to generate dashboard'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_assignment_stats(request):
    """
    Get detailed statistics for teacher assignments
    """
    try:
        # FIXED: Check if user is a teacher using the IsTeacher permission logic
        permission_checker = IsTeacher()
        
        if not permission_checker.has_permission(request, None):
            return Response(
                {'error': 'Only teachers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get teacher object - handle both cases
        teacher = None
        
        # Try to get teacher profile first
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
        else:
            # Fallback: use User object as teacher
            teacher = request.user
        
        # Debug logging
        logger.info(f"Teacher stats requested by user: {request.user.email}, teacher: {teacher.email}")
        
        # Get statistics with proper teacher filtering
        # For assignments where teacher is User object
        assignments_by_user = Assignment.objects.filter(teacher__user=teacher)
        
        # For assignments where teacher is TeacherProfile object
        assignments_by_profile = Assignment.objects.filter(teacher=teacher)
        
        # Combine both querysets
        all_assignments = assignments_by_user | assignments_by_profile
        total_created = all_assignments.count()
        
        published_count = all_assignments.filter(status='published').count()
        
        # Get graded assignments count
        graded_count = StudentAssignment.objects.filter(
            Q(assignment__teacher__user=teacher) | Q(assignment__teacher=teacher),
            status='graded'
        ).count()
        
        # Calculate completion stats
        published_assignments = all_assignments.filter(status__in=['published', 'closed', 'graded'])
        
        avg_completion = 0
        avg_score = 0
        
        if published_assignments.exists():
            # We need to calculate these manually since they might be properties
            completion_sum = 0
            score_sum = 0
            count = 0
            
            for assignment in published_assignments:
                completion_sum += assignment.completion_rate
                score_sum += assignment.average_score
                count += 1
            
            avg_completion = completion_sum / count if count > 0 else 0
            avg_score = score_sum / count if count > 0 else 0
        
        pending_grading = StudentAssignment.objects.filter(
            Q(assignment__teacher__user=teacher) | Q(assignment__teacher=teacher),
            status__in=['submitted', 'late']
        ).count()
        
        # Subject breakdown
        subject_breakdown = all_assignments.values(
            'subject__name'
        ).annotate(
            count=Count('id')
        )
        
        # Add average completion and score for each subject
        subject_data = []
        for subject in subject_breakdown:
            subject_assignments = all_assignments.filter(
                subject__name=subject['subject__name']
            )
            
            subject_completion_sum = 0
            subject_score_sum = 0
            subject_count = 0
            
            for assignment in subject_assignments:
                subject_completion_sum += assignment.completion_rate
                subject_score_sum += assignment.average_score
                subject_count += 1
            
            avg_subject_completion = subject_completion_sum / subject_count if subject_count > 0 else 0
            avg_subject_score = subject_score_sum / subject_count if subject_count > 0 else 0
            
            subject_data.append({
                'subject_name': subject['subject__name'],
                'count': subject['count'],
                'average_completion_rate': avg_subject_completion,
                'average_score': avg_subject_score
            })
        
        data = {
            'total_created': total_created,
            'published_count': published_count,
            'graded_count': graded_count,
            'average_completion_rate': avg_completion,
            'average_score': avg_score,
            'pending_grading': pending_grading,
            'subject_breakdown': subject_data
        }
        
        serializer = TeacherAssignmentStatsSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating teacher stats: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to generate teacher statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_progress_report(request, student_id=None):
    """
    Get progress report for a student (teachers and admins only)
    """
    try:
        if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only teachers and administrators can view student progress reports.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student object
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return Response(
                    {'error': 'Student not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif request.user.is_student:
            student = request.user.student_profile
        else:
            return Response(
                {'error': 'Student ID is required for teachers and administrators.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all assignments for the student
        student_assignments = StudentAssignment.objects.filter(
            student=student
        ).select_related('assignment', 'assignment__subject')
        
        # Calculate statistics
        total_assignments = student_assignments.count()
        submitted_assignments = student_assignments.filter(
            status__in=['submitted', 'late', 'graded']
        ).count()
        graded_assignments = student_assignments.filter(status='graded').count()
        
        # Average score
        average_score = student_assignments.filter(status='graded').aggregate(
            avg=Avg('final_marks')
        )['avg'] or 0
        
        # Subject-wise performance
        subject_performance = student_assignments.filter(
            status='graded'
        ).values(
            'assignment__subject__name'
        ).annotate(
            avg_score=Avg('final_marks'),
            total_assignments=Count('id'),
            completed_assignments=Count('id', filter=Q(status='graded'))
        )
        
        # Recent activity
        recent_submissions = student_assignments.order_by('-submission_date')[:10]
        
        data = {
            'student': {
                'id': student.id,
                'name': student.get_full_name(),
                'admission_number': student.admission_number,
                'classroom': student.classroom.name if hasattr(student, 'classroom') and student.classroom else 'N/A'
            },
            'overall_stats': {
                'total_assignments': total_assignments,
                'submitted_assignments': submitted_assignments,
                'graded_assignments': graded_assignments,
                'submission_rate': (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0,
                'average_score': float(average_score)
            },
            'subject_performance': list(subject_performance),
            'recent_submissions': StudentAssignmentMiniSerializer(recent_submissions, many=True).data
        }
        
        return Response(data)
    except Exception as e:
        logger.error(f"Error generating student progress report: {str(e)}")
        return Response(
            {'error': 'Failed to generate progress report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




# Add these to your assignments/views.py

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_create_assignments(request):
    """
    Bulk create assignments from CSV or JSON data
    """
    # Implementation for bulk assignment creation
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes([IsTeacher])
def bulk_grade_assignments(request):
    """
    Bulk grade student assignments
    """
    # Implementation for bulk grading
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_assignments(request):
    """
    Export assignments to Excel or PDF
    """
    # Implementation for assignment export
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_grades(request):
    """
    Export grades to Excel or PDF
    """
    # Implementation for grade export
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_calendar(request):
    """
    Get assignments in calendar format
    """
    # Implementation for calendar view
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_deadlines(request):
    """
    Get upcoming deadlines with filters
    """
    # Implementation for deadlines view
    pass





# Add these imports at the top of the file if not already present
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.db.models import Q, Count, Max, Min
from rest_framework.decorators import api_view, permission_classes
import json

# ==================== MISSING VIEW FUNCTIONS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_assignments(request):
    """
    Bulk create assignments from CSV or JSON data
    """
    try:
        # Check permissions - only teachers and admins
        if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only teachers and administrators can bulk create assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if file is uploaded
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded. Please upload a CSV or JSON file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name.lower()
        
        created_assignments = []
        errors = []
        
        # Process CSV file
        if file_name.endswith('.csv'):
            import io
            import csv as csv_module
            
            # Read CSV file
            file_content = uploaded_file.read().decode('utf-8')
            csv_data = csv_module.DictReader(io.StringIO(file_content))
            
            for row_num, row in enumerate(csv_data, start=2):  # start=2 for header
                try:
                    # Convert row data to assignment format
                    assignment_data = {
                        'title': row.get('title', '').strip(),
                        'description': row.get('description', '').strip(),
                        'assignment_type': row.get('assignment_type', 'homework').strip(),
                        'subject': row.get('subject_id'),
                        'classroom': row.get('classroom_id'),
                        'due_date': row.get('due_date'),
                        'total_marks': row.get('total_marks', 100),
                        'status': 'draft'
                    }
                    
                    # Create serializer instance
                    serializer = AssignmentCreateSerializer(
                        data=assignment_data,
                        context={'request': request}
                    )
                    
                    if serializer.is_valid():
                        assignment = serializer.save()
                        created_assignments.append({
                            'id': str(assignment.id),
                            'title': assignment.title,
                            'status': assignment.status
                        })
                    else:
                        errors.append({
                            'row': row_num,
                            'errors': serializer.errors,
                            'data': assignment_data
                        })
                        
                except Exception as e:
                    errors.append({
                        'row': row_num,
                        'error': str(e),
                        'data': row
                    })
        
        # Process JSON file
        elif file_name.endswith('.json'):
            try:
                json_data = json.loads(uploaded_file.read().decode('utf-8'))
                
                if not isinstance(json_data, list):
                    return Response(
                        {'error': 'JSON file must contain an array of assignments.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                for idx, assignment_data in enumerate(json_data):
                    try:
                        serializer = AssignmentCreateSerializer(
                            data=assignment_data,
                            context={'request': request}
                        )
                        
                        if serializer.is_valid():
                            assignment = serializer.save()
                            created_assignments.append({
                                'id': str(assignment.id),
                                'title': assignment.title,
                                'status': assignment.status
                            })
                        else:
                            errors.append({
                                'index': idx,
                                'errors': serializer.errors,
                                'data': assignment_data
                            })
                            
                    except Exception as e:
                        errors.append({
                            'index': idx,
                            'error': str(e),
                            'data': assignment_data
                        })
                        
            except json.JSONDecodeError as e:
                return Response(
                    {'error': f'Invalid JSON file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        else:
            return Response(
                {'error': 'Unsupported file format. Please upload CSV or JSON.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'success': len(errors) == 0,
            'message': f'Successfully processed {len(created_assignments)} assignments.',
            'created_count': len(created_assignments),
            'error_count': len(errors),
            'created_assignments': created_assignments,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk create assignments: {str(e)}")
        return Response(
            {'error': f'Failed to bulk create assignments: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_grade_assignments(request):
    """
    Bulk grade student assignments
    """
    try:
        # Check permissions - only teachers and admins
        if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only teachers and administrators can bulk grade assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        grading_data = request.data.get('grading', [])
        
        if not isinstance(grading_data, list):
            return Response(
                {'error': 'Invalid data format. Expected list of grading data.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not grading_data:
            return Response(
                {'error': 'No grading data provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        graded_assignments = []
        errors = []
        
        for grade_item in grading_data:
            try:
                student_assignment_id = grade_item.get('student_assignment_id')
                marks_obtained = grade_item.get('marks_obtained')
                feedback = grade_item.get('feedback', '')
                
                if not student_assignment_id or marks_obtained is None:
                    errors.append({
                        'item': grade_item,
                        'error': 'Missing student_assignment_id or marks_obtained'
                    })
                    continue
                
                # Get student assignment
                student_assignment = StudentAssignment.objects.get(id=student_assignment_id)
                
                # Check if user can grade this assignment
                if not (request.user.is_staff or request.user.is_superuser or 
                       (request.user.is_teacher and student_assignment.assignment.teacher.user == request.user)):
                    errors.append({
                        'student_assignment_id': student_assignment_id,
                        'error': 'Permission denied to grade this assignment'
                    })
                    continue
                
                # Validate marks
                if float(marks_obtained) > student_assignment.assignment.total_marks:
                    errors.append({
                        'student_assignment_id': student_assignment_id,
                        'error': f'Marks obtained ({marks_obtained}) exceeds total marks ({student_assignment.assignment.total_marks})'
                    })
                    continue
                
                # Grade the assignment
                student_assignment.marks_obtained = float(marks_obtained)
                student_assignment.teacher_feedback = feedback
                student_assignment.status = 'graded'
                student_assignment.graded_at = timezone.now()
                
                if hasattr(request.user, 'teacher_profile'):
                    student_assignment.graded_by = request.user.teacher_profile
                
                student_assignment.save()
                graded_assignments.append(student_assignment_id)
                
            except StudentAssignment.DoesNotExist:
                errors.append({
                    'student_assignment_id': grade_item.get('student_assignment_id'),
                    'error': 'Student assignment not found'
                })
            except Exception as e:
                errors.append({
                    'item': grade_item,
                    'error': str(e)
                })
        
        return Response({
            'success': len(errors) == 0,
            'message': f'Successfully graded {len(graded_assignments)} assignments.',
            'graded_count': len(graded_assignments),
            'error_count': len(errors),
            'graded_assignments': graded_assignments,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk grade assignments: {str(e)}")
        return Response(
            {'error': f'Failed to bulk grade assignments: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_assignments(request):
    """
    Export assignments to CSV
    """
    try:
        # Check permissions - only teachers and admins
        if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only teachers and administrators can export assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type not in ['csv']:
            return Response(
                {'error': 'Only CSV format is supported for export.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get filtered assignments
        assignments = Assignment.objects.all()
        
        # Apply teacher filter if user is teacher
        if request.user.is_teacher and hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            assignments = assignments.filter(teacher=teacher)
        
        # Apply additional filters
        status_filter = request.query_params.get('status')
        if status_filter:
            assignments = assignments.filter(status=status_filter)
        
        subject_filter = request.query_params.get('subject')
        if subject_filter:
            assignments = assignments.filter(subject_id=subject_filter)
        
        classroom_filter = request.query_params.get('classroom')
        if classroom_filter:
            assignments = assignments.filter(classroom_id=classroom_filter)
        
        # Prepare CSV data
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assignments_export.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Type', 'Subject', 'Teacher',
            'Classroom', 'Due Date', 'Total Marks', 'Passing Marks',
            'Difficulty', 'Status', 'Created At', 'Published At',
            'Completion Rate', 'Average Score'
        ])
        
        # Write data rows
        for assignment in assignments:
            writer.writerow([
                assignment.id,
                assignment.title,
                assignment.description[:100],  # Limit description length
                assignment.assignment_type,
                assignment.subject.name if assignment.subject else '',
                assignment.teacher.get_full_name() if assignment.teacher else '',
                assignment.classroom.name if assignment.classroom else '',
                assignment.due_date.strftime('%Y-%m-%d %H:%M') if assignment.due_date else '',
                assignment.total_marks,
                assignment.passing_marks,
                assignment.difficulty_level,
                assignment.status,
                assignment.created_at.strftime('%Y-%m-%d %H:%M'),
                assignment.published_at.strftime('%Y-%m-%d %H:%M') if assignment.published_at else '',
                f"{assignment.completion_rate:.2f}%",
                f"{assignment.average_score:.2f}"
            ])
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting assignments: {str(e)}")
        return Response(
            {'error': f'Failed to export assignments: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_grades(request):
    """
    Export grades to CSV
    """
    try:
        # Check permissions - only teachers and admins
        if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only teachers and administrators can export grades.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type not in ['csv']:
            return Response(
                {'error': 'Only CSV format is supported for export.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get filtered student assignments
        student_assignments = StudentAssignment.objects.all()
        
        # Apply teacher filter if user is teacher
        if request.user.is_teacher and hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            student_assignments = student_assignments.filter(assignment__teacher=teacher)
        
        # Apply additional filters
        assignment_filter = request.query_params.get('assignment')
        if assignment_filter:
            student_assignments = student_assignments.filter(assignment_id=assignment_filter)
        
        student_filter = request.query_params.get('student')
        if student_filter:
            student_assignments = student_assignments.filter(student_id=student_filter)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            student_assignments = student_assignments.filter(status=status_filter)
        
        # Prepare CSV data
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="grades_export.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Student ID', 'Student Name', 'Admission Number',
            'Assignment ID', 'Assignment Title', 'Subject',
            'Total Marks', 'Marks Obtained', 'Percentage',
            'Grade', 'Status', 'Submission Date', 'Graded At',
            'Graded By', 'Feedback', 'Late Submission'
        ])
        
        # Write data rows
        for sa in student_assignments.select_related('student', 'assignment', 'assignment__subject', 'graded_by'):
            student = sa.student
            assignment = sa.assignment
            
            # Calculate percentage
            percentage = (sa.marks_obtained / assignment.total_marks * 100) if sa.marks_obtained and assignment.total_marks else 0
            
            writer.writerow([
                student.id if student else '',
                student.get_full_name() if student else '',
                student.admission_number if hasattr(student, 'admission_number') else '',
                assignment.id,
                assignment.title,
                assignment.subject.name if assignment.subject else '',
                assignment.total_marks,
                sa.marks_obtained if sa.marks_obtained else '',
                f"{percentage:.2f}%",
                sa.grade or '',
                sa.status,
                sa.submission_date.strftime('%Y-%m-%d %H:%M') if sa.submission_date else '',
                sa.graded_at.strftime('%Y-%m-%d %H:%M') if sa.graded_at else '',
                sa.graded_by.get_full_name() if sa.graded_by else '',
                sa.teacher_feedback[:200] if sa.teacher_feedback else '',  # Limit feedback length
                'Yes' if sa.is_late else 'No'
            ])
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting grades: {str(e)}")
        return Response(
            {'error': f'Failed to export grades: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_calendar(request):
    """
    Get assignments in calendar format
    """
    try:
        user = request.user
        
        # Get date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Default to current month
        today = timezone.now().date()
        if not start_date_str:
            start_date = today.replace(day=1)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if not end_date_str:
            # Default to end of current month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Get assignments based on user role
        if user.is_student and hasattr(user, 'student_profile'):
            student = user.student_profile
            assignments = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress'],
                due_date__date__range=[start_date, end_date]
            )
        elif user.is_teacher and hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            assignments = Assignment.objects.filter(
                teacher=teacher,
                due_date__date__range=[start_date, end_date]
            )
        elif user.is_staff or user.is_superuser:
            assignments = Assignment.objects.filter(
                due_date__date__range=[start_date, end_date]
            )
        else:
            assignments = Assignment.objects.none()
        
        # Format for calendar
        calendar_events = []
        for assignment in assignments:
            event_color = {
                'homework': '#3498db',
                'quiz': '#e74c3c',
                'test': '#9b59b6',
                'exam': '#e67e22',
                'project': '#2ecc71',
                'classwork': '#1abc9c',
                'essay': '#f39c12',
                'presentation': '#8e44ad',
                'research': '#16a085',
                'lab': '#27ae60'
            }.get(assignment.assignment_type, '#95a5a6')
            
            calendar_events.append({
                'id': str(assignment.id),
                'title': assignment.title,
                'start': assignment.due_date.isoformat(),
                'end': assignment.due_date.isoformat(),
                'allDay': True,
                'color': event_color,
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': assignment.assignment_type,
                    'subject': assignment.subject.name if assignment.subject else '',
                    'classroom': assignment.classroom.name if assignment.classroom else '',
                    'total_marks': str(assignment.total_marks),
                    'status': assignment.status,
                    'is_overdue': assignment.is_overdue
                }
            })
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'events': calendar_events
        })
        
    except Exception as e:
        logger.error(f"Error generating calendar: {str(e)}")
        return Response(
            {'error': f'Failed to generate calendar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_deadlines(request):
    """
    Get upcoming deadlines with filters
    """
    try:
        user = request.user
        
        # Get days parameter
        days = int(request.query_params.get('days', 7))
        
        # Calculate date range
        today = timezone.now().date()
        deadline_date = today + timedelta(days=days)
        
        # Get assignments based on user role
        if user.is_student and hasattr(user, 'student_profile'):
            student = user.student_profile
            assignments = Assignment.objects.filter(
                classroom=student.classroom,
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        elif user.is_teacher and hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            assignments = Assignment.objects.filter(
                teacher=teacher,
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        elif user.is_staff or user.is_superuser:
            assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        else:
            assignments = Assignment.objects.none()
        
        # Format response
        deadlines = []
        for assignment in assignments:
            days_left = (assignment.due_date.date() - today).days
            
            # Get submission stats for students
            submission_status = None
            if user.is_student and hasattr(user, 'student_profile'):
                student = user.student_profile
                try:
                    student_assignment = StudentAssignment.objects.get(
                        assignment=assignment,
                        student=student
                    )
                    submission_status = student_assignment.status
                except StudentAssignment.DoesNotExist:
                    submission_status = 'not_started'
            
            deadlines.append({
                'id': str(assignment.id),
                'title': assignment.title,
                'subject': assignment.subject.name if assignment.subject else '',
                'due_date': assignment.due_date.isoformat(),
                'days_left': days_left,
                'total_marks': str(assignment.total_marks),
                'status': assignment.status,
                'submission_status': submission_status,
                'is_overdue': assignment.is_overdue,
                'urgency': 'high' if days_left <= 1 else 'medium' if days_left <= 3 else 'low'
            })
        
        return Response({
            'days': days,
            'deadline_date': deadline_date.isoformat(),
            'total_count': len(deadlines),
            'deadlines': deadlines
        })
        
    except Exception as e:
        logger.error(f"Error retrieving upcoming deadlines: {str(e)}")
        return Response(
            {'error': f'Failed to retrieve upcoming deadlines: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
