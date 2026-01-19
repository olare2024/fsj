# assignments/views.py
"""
Clean and organized views for the Assignments module.
All views follow RESTful conventions with proper error handling and logging.
"""

import logging
import csv
import json
from datetime import timedelta
from io import StringIO

from django.db import transaction
from django.db.models import Q, Count, Avg, Max, Min, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Assignment, StudentAssignment, AssignmentCategory,
    AssignmentGroup, AssignmentComment, AssignmentReminder
)
from .serializers import (
    AssignmentCategorySerializer, AssignmentListSerializer,
    AssignmentDetailSerializer, AssignmentCreateSerializer,
    AssignmentUpdateSerializer, StudentAssignmentDetailSerializer,
    StudentAssignmentMiniSerializer, StudentAssignmentSubmitSerializer,
    StudentAssignmentGradeSerializer, AssignmentGroupSerializer,
    AssignmentCommentSerializer, AssignmentReminderSerializer,
    AssignmentDashboardSerializer, TeacherAssignmentStatsSerializer,
    CalendarEventSerializer, BulkAssignmentCreateSerializer,
    BulkGradingSerializer, ImportGradesSerializer
)
from .permissions import IsTeacher, IsStudent
from .filters import AssignmentFilter, StudentAssignmentFilter

logger = logging.getLogger(__name__)
User = get_user_model()


# ==================== HELPER FUNCTIONS ====================

def _get_event_color(status, is_overdue):
    """Helper method to determine event color based on status."""
    color_map = {
        'draft': '#6c757d',  # Gray
        'published': '#0d6efd',  # Blue
        'in_progress': '#fd7e14',  # Orange
        'closed': '#6f42c1',  # Purple
        'graded': '#198754',  # Green
    }
    
    if is_overdue:
        return '#dc3545'  # Red for overdue
    
    return color_map.get(status, '#6c757d')  # Default gray


def _calculate_median(queryset):
    """Helper method to calculate median."""
    values = list(queryset.values_list('marks_obtained', flat=True).order_by('marks_obtained'))
    n = len(values)
    if n == 0:
        return 0
    if n % 2 == 1:
        return values[n // 2]
    else:
        return (values[n // 2 - 1] + values[n // 2]) / 2


# ==================== ASSIGNMENT CATEGORY VIEWSET ====================

class AssignmentCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment categories.
    Categories organize assignments by type, curriculum, and education level.
    """
    queryset = AssignmentCategory.objects.all()
    serializer_class = AssignmentCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['curriculum', 'education_level', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        """
        Restrict write operations to admin users only.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Create assignment category with logging.
        """
        try:
            category = serializer.save()
            logger.info(f"Assignment category created: {category.name}")
        except Exception as e:
            logger.error(f"Error creating assignment category: {str(e)}")
            raise

    def perform_update(self, serializer):
        """
        Update assignment category with logging.
        """
        try:
            category = serializer.save()
            logger.info(f"Assignment category updated: {category.name}")
        except Exception as e:
            logger.error(f"Error updating assignment category: {str(e)}")
            raise

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignments.
    
    Features:
    - CRUD operations with proper permissions
    - Publishing workflow
    - Bulk operations
    - Statistics and analytics
    - Export functionality
    
    Permissions:
    - Teachers can create, update, delete their own assignments
    - Students can view assignments for their class
    - Admins can manage all assignments
    """
    
    queryset = Assignment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AssignmentFilter
    search_fields = ['title', 'description', 'subject__name']
    ordering_fields = ['created_at', 'due_date', 'total_marks', 'average_score']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # ====================
    # SERIALIZER METHODS
    # ====================
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        serializer_map = {
            'list': AssignmentListSerializer,
            'retrieve': AssignmentDetailSerializer,
            'create': AssignmentCreateSerializer,
            'update': AssignmentUpdateSerializer,
            'partial_update': AssignmentUpdateSerializer,
            'bulk_create': BulkAssignmentCreateSerializer,
            'bulk_grade': BulkGradingSerializer,
        }
        return serializer_map.get(self.action, AssignmentDetailSerializer)
    
    def get_serializer_context(self):
        """
        Add request context to serializer.
        """
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'user': self.request.user,
        })
        return context
    
    # ====================
    # PERMISSION METHODS
    # ====================
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == 'create':
            return [IsAuthenticated(), IsTeacher()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanModifyAssignment()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), CanViewAssignmentDetails()]
        elif self.action in ['publish', 'close', 'duplicate']:
            return [IsAuthenticated(), CanModifyAssignment()]
        elif self.action in ['bulk_create', 'bulk_grade']:
            return [IsAuthenticated(), IsTeacher()]
        else:
            return [IsAuthenticated()]
    
    # ====================
    # QUERYSET METHODS
    # ====================
    
    def get_queryset(self):
        """
        Filter assignments based on user role and permissions.
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'subject', 'teacher', 'classroom', 'category',
            'academic_year', 'term'
        ).prefetch_related(
            'student_assignments', 'prerequisites'
        )
        
        # Apply role-based filtering
        return self._filter_queryset_by_role(queryset, user)
    
    def _filter_queryset_by_role(self, queryset, user):
        """
        Apply role-specific filters to queryset.
        """
        if user.is_superuser or user.role == 'admin':
            # Admins can see everything
            return queryset
        
        if user.role == 'teacher':
            # Teachers can see their own assignments
            return queryset.filter(teacher=user)
        
        if user.role == 'student':
            # Students can see assignments for their class
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                current_class = user.student_profile.current_class
                return queryset.filter(
                    Q(classroom=current_class) | Q(classroom__isnull=True),
                    status__in=['published', 'in_progress', 'closed', 'graded']
                ).distinct()
            else:
                return queryset.none()
        
        # Default: return only published assignments
        return queryset.filter(status='published')
    
    # ====================
    # CRUD OPERATIONS
    # ====================
    
    def create(self, request, *args, **kwargs):
        """
        Create a new assignment.
        
        Required fields:
        - title
        - subject
        - teacher (auto-set to current user)
        - total_marks
        """
        # Debug logging
        self._log_create_request(request)
        
        # Check teacher permissions
        if not self._user_can_create_assignment(request.user):
            return self._permission_denied_response()
        
        try:
            # Prepare data and validate
            data = request.data.copy()
            data['teacher'] = str(request.user.id)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # Create assignment
            assignment = self._create_assignment_with_transaction(serializer)
            
            # Create student assignments if published
            if assignment.status == 'published' and assignment.classroom:
                self._create_student_assignments(assignment)
            
            logger.info(f"Assignment created: {assignment.title} by {request.user.email}")
            
            # Return response with assignment details
            return Response(
                AssignmentDetailSerializer(assignment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            logger.error(f"Validation error creating assignment: {str(e)}")
            return Response(
                {
                    'error': 'Validation failed',
                    'details': str(e),
                    'validation_errors': e.detail if hasattr(e, 'detail') else {}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating assignment: {str(e)}")
            return Response(
                {
                    'error': 'Failed to create assignment',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve assignment with view count increment.
        """
        try:
            assignment = self.get_object()
            
            # Increment views for published assignments
            if assignment.status == 'published':
                self._increment_views(assignment)
            
            serializer = self.get_serializer(assignment)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving assignment: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update an assignment.
        """
        try:
            assignment = self.get_object()
            partial = kwargs.pop('partial', False)
            
            serializer = self.get_serializer(assignment, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                updated_assignment = serializer.save()
                logger.info(f"Assignment updated: {updated_assignment.title}")
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error updating assignment: {str(e)}")
            return Response(
                {'error': 'Failed to update assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete an assignment (set is_active to False).
        """
        try:
            assignment = self.get_object()
            assignment.is_active = False
            assignment.save(update_fields=['is_active'])
            
            logger.info(f"Assignment soft deleted: {assignment.title}")
            
            return Response(
                {'message': 'Assignment deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            logger.error(f"Error deleting assignment: {str(e)}")
            return Response(
                {'error': 'Failed to delete assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ====================
    # WORKFLOW ACTIONS
    # ====================
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a draft assignment.
        """
        try:
            assignment = self.get_object()
            
            # Validate assignment can be published
            if not assignment.can_be_published:
                return Response(
                    {'error': 'Assignment cannot be published. Check required fields.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Update assignment
                assignment.status = 'published'
                assignment.published_at = timezone.now()
                assignment.save()
                
                # Create student assignments
                created_count, existing_count = assignment.create_student_assignments()
                
                logger.info(f"Assignment published: {assignment.title}")
                
                return Response({
                    'message': 'Assignment published successfully',
                    'assignment_id': str(assignment.id),
                    'student_assignments_created': created_count,
                    'data': AssignmentDetailSerializer(assignment).data
                })
                
        except Exception as e:
            logger.error(f"Error publishing assignment: {str(e)}")
            return Response(
                {'error': 'Failed to publish assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close an assignment for submissions.
        """
        try:
            assignment = self.get_object()
            
            # Validate assignment can be closed
            if assignment.status not in ['published', 'in_progress']:
                return Response(
                    {'error': 'Only published or in-progress assignments can be closed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update assignment
            assignment.status = 'closed'
            assignment.closed_at = timezone.now()
            assignment.save()
            
            logger.info(f"Assignment closed: {assignment.title}")
            
            return Response({
                'message': 'Assignment closed successfully',
                'assignment_id': str(assignment.id),
                'data': AssignmentDetailSerializer(assignment).data
            })
            
        except Exception as e:
            logger.error(f"Error closing assignment: {str(e)}")
            return Response(
                {'error': 'Failed to close assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate an existing assignment.
        """
        try:
            original_assignment = self.get_object()
            
            # Prepare duplicate data
            duplicate_data = self._prepare_duplicate_data(original_assignment, request)
            
            # Create duplicate
            serializer = AssignmentCreateSerializer(
                data=duplicate_data, 
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            duplicate_assignment = serializer.save()
            logger.info(f"Assignment duplicated: {original_assignment.title} -> {duplicate_assignment.title}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error duplicating assignment: {str(e)}")
            return Response(
                {'error': 'Failed to duplicate assignment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ====================
    # ANALYTICS ACTIONS
    # ====================
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get detailed statistics for an assignment.
        """
        try:
            assignment = self.get_object()
            
            # Calculate statistics
            stats = {
                'assignment_id': str(assignment.id),
                'assignment_title': assignment.title,
                'total_students': assignment.total_students,
                'submission_stats': assignment.submission_stats,
                'grade_summary': assignment.grade_summary,
                'average_score': float(assignment.average_score),
                'completion_rate': float(assignment.completion_rate),
                'views_count': assignment.views_count,
                'is_overdue': assignment.is_overdue,
                'days_until_due': assignment.days_until_due,
                'generated_at': timezone.now().isoformat()
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
        Get all submissions for this assignment.
        """
        try:
            assignment = self.get_object()
            
            # Get submissions with filtering
            submissions = assignment.student_assignments.all().select_related(
                'student', 'graded_by'
            )
            
            # Apply filters from query params
            submissions = self._filter_submissions(submissions, request)
            
            serializer = StudentAssignmentDetailSerializer(submissions, many=True)
            
            return Response({
                'assignment_id': str(assignment.id),
                'assignment_title': assignment.title,
                'total_submissions': submissions.count(),
                'submissions': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve submissions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ====================
    # BULK OPERATIONS
    # ====================
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create assignments from JSON data.
        """
        try:
            serializer = BulkAssignmentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            assignments_data = serializer.validated_data['assignments']
            created_assignments = []
            errors = []
            
            for idx, assignment_data in enumerate(assignments_data):
                try:
                    # Add teacher to each assignment
                    assignment_data['teacher'] = request.user.id
                    
                    assignment_serializer = AssignmentCreateSerializer(
                        data=assignment_data,
                        context={'request': request}
                    )
                    
                    if assignment_serializer.is_valid():
                        assignment = assignment_serializer.save()
                        created_assignments.append({
                            'id': str(assignment.id),
                            'title': assignment.title
                        })
                    else:
                        errors.append({
                            'index': idx,
                            'errors': assignment_serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'index': idx,
                        'error': str(e)
                    })
            
            response_data = {
                'created_count': len(created_assignments),
                'error_count': len(errors),
                'created_assignments': created_assignments,
                'errors': errors
            }
            
            if errors:
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in bulk create: {str(e)}")
            return Response(
                {'error': 'Failed to bulk create assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def bulk_grade(self, request, pk=None):
        """
        Bulk grade submissions for an assignment.
        """
        try:
            assignment = get_object_or_404(Assignment, id=pk)
            
            # Check permissions
            if not self._can_grade_assignment(request.user, assignment):
                return Response(
                    {'error': 'You do not have permission to grade this assignment'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = BulkGradingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            grades_data = serializer.validated_data['grades']
            graded_count = 0
            errors = []
            
            with transaction.atomic():
                for grade_data in grades_data:
                    result = self._grade_single_submission(assignment, grade_data, request.user)
                    if result['success']:
                        graded_count += 1
                    else:
                        errors.append(result['error'])
            
            response_data = {
                'assignment_id': str(assignment.id),
                'assignment_title': assignment.title,
                'graded_count': graded_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            if errors:
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            # Update assignment statistics
            assignment.update_statistics()
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error in bulk grading: {str(e)}")
            return Response(
                {'error': 'Failed to bulk grade assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ====================
    # HELPER METHODS
    # ====================
    
    def _user_can_create_assignment(self, user):
        """Check if user can create assignments."""
        # Teachers can create assignments
        if hasattr(user, 'role') and user.role == 'teacher':
            return True
        
        # Staff and admins can create assignments
        if user.is_staff or user.is_superuser:
            return True
        
        # Check is_teacher property
        if getattr(user, 'is_teacher', False):
            return True
        
        return False
    
    def _permission_denied_response(self):
        """Return a permission denied response."""
        return Response(
            {
                'error': 'Permission denied',
                'message': 'Only teachers can create assignments',
                'required_role': 'teacher'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    def _log_create_request(self, request):
        """Log create request details."""
        logger.info(f"Create assignment request from {request.user.email}")
        logger.debug(f"Request data: {request.data}")
    
    def _prepare_create_data(self, data, user):
        """Prepare data for assignment creation."""
        data = data.copy()
        
        # Ensure teacher is set to current user
        if 'teacher' not in data or not data['teacher']:
            data['teacher'] = str(user.id)
        
        # Set created_by if not set
        if 'created_by' not in data or not data['created_by']:
            data['created_by'] = str(user.id)
        
        return data
    
    def _create_assignment_with_transaction(self, serializer):
        """Create assignment within a transaction."""
        with transaction.atomic():
            assignment = serializer.save()
            logger.info(f"Assignment created: {assignment.id} - {assignment.title}")
            return assignment
    
    def _create_student_assignments(self, assignment):
        """Create student assignments for a published assignment."""
        if assignment.status == 'published' and assignment.classroom:
            created_count, existing_count = assignment.create_student_assignments()
            logger.info(f"Created {created_count} student assignments for {assignment.title}")
    
    def _increment_views(self, assignment):
        """Increment assignment views."""
        assignment.views_count += 1
        assignment.save(update_fields=['views_count'])
    
    def _prepare_duplicate_data(self, original_assignment, request):
        """Prepare data for duplicating an assignment."""
        duplicate_data = {
            'title': request.data.get('title', f"Copy of {original_assignment.title}"),
            'description': original_assignment.description,
            'assignment_type': original_assignment.assignment_type,
            'category': original_assignment.category.id if original_assignment.category else None,
            'subject': original_assignment.subject.id,
            'teacher': request.user.id,
            'classroom': original_assignment.classroom.id if original_assignment.classroom else None,
            'academic_year': original_assignment.academic_year.id if original_assignment.academic_year else None,
            'term': original_assignment.term.id if original_assignment.term else None,
            'due_date': request.data.get('due_date', original_assignment.due_date),
            'total_marks': original_assignment.total_marks,
            'passing_marks': original_assignment.passing_marks,
            'difficulty_level': original_assignment.difficulty_level,
            'instructions': original_assignment.instructions,
            'status': 'draft'
        }
        
        return duplicate_data
    
    def _filter_submissions(self, submissions, request):
        """Filter submissions based on query parameters."""
        status_filter = request.query_params.get('status')
        if status_filter:
            submissions = submissions.filter(status=status_filter)
        
        graded_filter = request.query_params.get('graded')
        if graded_filter:
            if graded_filter.lower() == 'true':
                submissions = submissions.filter(status='graded')
            elif graded_filter.lower() == 'false':
                submissions = submissions.exclude(status='graded')
        
        return submissions
    
    def _can_grade_assignment(self, user, assignment):
        """Check if user can grade an assignment."""
        # Admins can grade any assignment
        if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
            return True
        
        # Teachers can grade their own assignments
        if hasattr(user, 'role') and user.role == 'teacher':
            return assignment.teacher == user
        
        return False
    
    def _grade_single_submission(self, assignment, grade_data, grader):
        """Grade a single student submission."""
        try:
            student_id = grade_data.get('student_id')
            marks_obtained = grade_data.get('marks_obtained')
            feedback = grade_data.get('feedback', '')
            
            # Get student assignment
            try:
                student_assignment = StudentAssignment.objects.get(
                    assignment=assignment,
                    student_id=student_id
                )
            except StudentAssignment.DoesNotExist:
                return {
                    'success': False,
                    'error': {
                        'student_id': student_id,
                        'error': 'Student assignment not found'
                    }
                }
            
            # Validate marks
            if marks_obtained > assignment.total_marks:
                return {
                    'success': False,
                    'error': {
                        'student_id': student_id,
                        'error': f'Marks obtained ({marks_obtained}) exceeds total marks ({assignment.total_marks})'
                    }
                }
            
            # Grade the assignment
            student_assignment.marks_obtained = marks_obtained
            student_assignment.final_marks = marks_obtained
            student_assignment.feedback = feedback
            student_assignment.status = 'graded'
            student_assignment.graded_by = grader
            student_assignment.graded_at = timezone.now()
            student_assignment.save()
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'student_id': grade_data.get('student_id', 'unknown'),
                    'error': str(e)
                }
            }
    
    # ====================
    # LIST AND PAGINATION
    # ====================
    
    def list(self, request, *args, **kwargs):
        """
        List assignments with pagination and filtering.
        
        Query parameters:
        - search: Search in title, description, subject name
        - status: Filter by assignment status
        - subject: Filter by subject ID
        - classroom: Filter by classroom ID
        - page: Page number for pagination
        - page_size: Number of items per page
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Paginate
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error listing assignments: {str(e)}")
            return Response(
                {'error': 'Failed to list assignments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# ==================== STUDENT ASSIGNMENT VIEWSET ====================

class StudentAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student assignments and submissions.
    """
    queryset = StudentAssignment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentAssignmentFilter
    search_fields = [
        'assignment__title', 'student__first_name',
        'student__last_name', 'student__admission_number'
    ]
    ordering_fields = ['submission_date', 'graded_at', 'marks_obtained', 'created_at']
    ordering = ['-submission_date']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Filter student assignments based on user role.
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'student', 'graded_by', 'group'
        ).prefetch_related('assignment__subject')

        # Apply role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(student=user)
        elif user.role == 'teacher':
            queryset = queryset.filter(assignment__teacher=user)

        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        serializer_map = {
            'list': StudentAssignmentMiniSerializer,
            'retrieve': StudentAssignmentDetailSerializer,
            'submit': StudentAssignmentSubmitSerializer,
            'grade': StudentAssignmentGradeSerializer,
            'upload_attachment': StudentAssignmentSubmitSerializer,
        }
        return serializer_map.get(self.action, StudentAssignmentDetailSerializer)

    # ==================== CUSTOM ACTIONS ====================

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit an assignment.
        """
        try:
            student_assignment = self.get_object()
            
            # Validate ownership
            if student_assignment.student != request.user:
                return Response(
                    {'error': 'You can only submit your own assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate assignment is open for submission
            if student_assignment.assignment.status not in ['published', 'in_progress']:
                return Response(
                    {'error': 'Assignment is not open for submission.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(student_assignment, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                updated_assignment = serializer.save()
                logger.info(f"Assignment submitted: {student_assignment.assignment.title}")
            
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error submitting assignment: {str(e)}")
            return Response(
                {'error': 'Failed to submit assignment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """
        Grade a student assignment (teachers only).
        """
        try:
            student_assignment = self.get_object()
            
            # Validate teacher permissions
            if not (request.user.role == 'teacher' and student_assignment.assignment.teacher == request.user):
                return Response(
                    {'error': 'You can only grade assignments that belong to you.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(student_assignment, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                updated_assignment = serializer.save()
                logger.info(f"Assignment graded: {student_assignment.assignment.title}")
            
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error grading assignment: {str(e)}")
            return Response(
                {'error': 'Failed to grade assignment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """
        Get current user's submissions.
        """
        try:
            submissions = self.get_queryset().filter(student=request.user)
            serializer = self.get_serializer(submissions, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve submissions.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== ASSIGNMENT GROUP VIEWSET ====================

class AssignmentGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment groups for collaborative work.
    """
    queryset = AssignmentGroup.objects.all()
    serializer_class = AssignmentGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['assignment']
    search_fields = ['name', 'assignment__title']

    def get_queryset(self):
        """
        Filter groups based on user role.
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'leader'
        ).prefetch_related('members')

        if user.role == 'student':
            queryset = queryset.filter(
                Q(leader=user) | Q(members=user)
            ).distinct()
        elif user.role == 'teacher':
            queryset = queryset.filter(assignment__teacher=user)

        return queryset

    def perform_create(self, serializer):
        """
        Set leader when creating group.
        """
        if self.request.user.role == 'student':
            serializer.save(leader=self.request.user)
        else:
            serializer.save()


# ==================== ASSIGNMENT COMMENT VIEWSET ====================

class AssignmentCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment comments and discussions.
    """
    queryset = AssignmentComment.objects.all()
    serializer_class = AssignmentCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['assignment', 'student_assignment', 'is_private']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        """
        Filter comments based on privacy settings.
        """
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'assignment', 'student_assignment', 'author'
        )

        # Students can only see non-private comments or their own
        if user.role == 'student':
            queryset = queryset.filter(
                Q(is_private=False) | Q(author=user)
            )

        return queryset

    def perform_create(self, serializer):
        """
        Set author when creating comment.
        """
        serializer.save(author=self.request.user)


# ==================== API VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_dashboard(request):
    """
    Get assignment dashboard data for current user.
    """
    try:
        user = request.user
        
        if user.role == 'student':
            # Student dashboard
            total_assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress']
            ).count()
            
            student_assignments = StudentAssignment.objects.filter(student=user)
            pending_assignments = student_assignments.filter(status='not_submitted').count()
            submitted_assignments = student_assignments.filter(status__in=['submitted', 'late']).count()
            graded_assignments = student_assignments.filter(status='graded').count()
            
            overdue_assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__lt=timezone.now()
            ).exclude(
                student_assignments__student=user,
                student_assignments__status__in=['submitted', 'late', 'graded']
            ).count()
            
            average_score = student_assignments.filter(status='graded').aggregate(
                avg=Avg('final_marks')
            )['avg'] or 0
            
            recent_assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress']
            ).order_by('-created_at')[:5]
            
            upcoming_deadlines = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__gte=timezone.now()
            ).order_by('due_date')[:5]
            
        elif user.role == 'teacher':
            # Teacher dashboard
            total_assignments = Assignment.objects.filter(teacher=user).count()
            pending_assignments = Assignment.objects.filter(
                teacher=user,
                status='draft'
            ).count()
            
            student_assignments = StudentAssignment.objects.filter(assignment__teacher=user)
            submitted_assignments = student_assignments.filter(
                status__in=['submitted', 'late']
            ).count()
            graded_assignments = student_assignments.filter(status='graded').count()
            
            overdue_assignments = Assignment.objects.filter(
                teacher=user,
                status__in=['published', 'in_progress'],
                due_date__lt=timezone.now()
            ).count()
            
            average_score = student_assignments.filter(status='graded').aggregate(
                avg=Avg('final_marks')
            )['avg'] or 0
            
            recent_assignments = Assignment.objects.filter(teacher=user).order_by('-created_at')[:5]
            upcoming_deadlines = Assignment.objects.filter(
                teacher=user,
                due_date__gte=timezone.now()
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
            {'error': 'Failed to generate dashboard.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def teacher_assignment_stats(request):
    """
    Get detailed statistics for teacher assignments.
    """
    try:
        teacher = request.user
        
        # Get assignments created by this teacher
        assignments = Assignment.objects.filter(teacher=teacher)
        
        # Calculate statistics
        total_created = assignments.count()
        published_count = assignments.filter(status='published').count()
        
        # Get graded assignments count
        graded_count = StudentAssignment.objects.filter(
            assignment__teacher=teacher,
            status='graded'
        ).count()
        
        # Calculate completion stats
        published_assignments = assignments.filter(status__in=['published', 'closed', 'graded'])
        
        avg_completion = 0
        avg_score = 0
        
        if published_assignments.exists():
            completion_sum = 0
            score_sum = 0
            
            for assignment in published_assignments:
                completion_sum += assignment.completion_rate
                score_sum += assignment.average_score
            
            avg_completion = completion_sum / published_assignments.count()
            avg_score = score_sum / published_assignments.count()
        
        pending_grading = StudentAssignment.objects.filter(
            assignment__teacher=teacher,
            status__in=['submitted', 'late']
        ).count()
        
        # Subject breakdown
        subject_breakdown = assignments.values(
            'subject__name'
        ).annotate(
            count=Count('id'),
            avg_completion=Avg('completion_rate'),
            avg_score=Avg('average_score')
        )
        
        data = {
            'teacher': {
                'id': str(teacher.id),
                'name': teacher.get_full_name(),
                'email': teacher.email
            },
            'statistics': {
                'total_created': total_created,
                'published_count': published_count,
                'graded_count': graded_count,
                'average_completion_rate': round(avg_completion, 2),
                'average_score': round(avg_score, 2),
                'pending_grading': pending_grading,
            },
            'subject_breakdown': list(subject_breakdown)
        }
        
        serializer = TeacherAssignmentStatsSerializer(data)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error generating teacher stats: {str(e)}")
        return Response(
            {'error': 'Failed to generate teacher statistics.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_deadlines(request):
    """
    Get upcoming assignment deadlines.
    """
    try:
        user = request.user
        days = int(request.query_params.get('days', 7))
        
        # Calculate date range
        today = timezone.now().date()
        deadline_date = today + timedelta(days=days)
        
        # Get assignments based on user role
        if user.role == 'student':
            assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        elif user.role == 'teacher':
            assignments = Assignment.objects.filter(
                teacher=user,
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        else:
            assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__date__range=[today, deadline_date]
            ).order_by('due_date')
        
        # Format response
        deadlines = []
        for assignment in assignments:
            days_left = (assignment.due_date.date() - today).days
            
            deadlines.append({
                'id': str(assignment.id),
                'title': assignment.title,
                'subject': assignment.subject.name if assignment.subject else '',
                'due_date': assignment.due_date.isoformat(),
                'days_left': days_left,
                'total_marks': str(assignment.total_marks),
                'status': assignment.status,
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
            {'error': 'Failed to retrieve upcoming deadlines.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_calendar(request):
    """
    Get assignments in calendar format.
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
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not end_date_str:
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        else:
            try:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get assignments based on user role
        if user.role == 'student':
            # Get student's current class
            current_class = None
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                current_class = user.student_profile.current_class
            
            if current_class:
                assignments = Assignment.objects.filter(
                    classroom=current_class,
                    status__in=['published', 'in_progress', 'closed', 'graded'],
                    due_date__date__range=[start_date, end_date]
                ).order_by('due_date')
            else:
                assignments = Assignment.objects.none()
                
        elif user.role == 'teacher':
            assignments = Assignment.objects.filter(
                teacher=user,
                status__in=['published', 'in_progress', 'closed', 'graded'],
                due_date__date__range=[start_date, end_date]
            ).order_by('due_date')
        else:
            assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__date__range=[start_date, end_date]
            ).order_by('due_date')
        
        # Format calendar events
        events = []
        for assignment in assignments:
            event = {
                'id': str(assignment.id),
                'title': f"{assignment.title} ({assignment.subject.name if assignment.subject else 'No Subject'})",
                'start': assignment.due_date.isoformat(),
                'end': (assignment.due_date + timedelta(hours=1)).isoformat(),
                'allDay': False,
                'color': _get_event_color(assignment.status, assignment.is_overdue),
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': 'assignment',
                    'status': assignment.status,
                    'is_overdue': assignment.is_overdue,
                    'total_marks': str(assignment.total_marks),
                    'subject': assignment.subject.name if assignment.subject else '',
                    'classroom': assignment.classroom.name if assignment.classroom else '',
                    'url': f'/assignments/{assignment.id}/'
                }
            }
            events.append(event)
        
        serializer = CalendarEventSerializer(events, many=True)
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'events': serializer.data,
            'event_count': len(events)
        })

    except Exception as e:
        logger.error(f"Error retrieving calendar events: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve calendar events.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def bulk_grade(request, assignment_id):
    """
    Bulk grade assignments for a specific assignment.
    """
    try:
        # Get the assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only grade your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkGradingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        grades_data = serializer.validated_data['grades']
        graded_count = 0
        errors = []
        
        with transaction.atomic():
            for grade_data in grades_data:
                try:
                    student_id = grade_data.get('student_id')
                    marks_obtained = grade_data.get('marks_obtained')
                    feedback = grade_data.get('feedback', '')
                    
                    # Get student assignment
                    try:
                        student_assignment = StudentAssignment.objects.get(
                            assignment=assignment,
                            student_id=student_id
                        )
                    except StudentAssignment.DoesNotExist:
                        errors.append({
                            'student_id': student_id,
                            'error': 'Student assignment not found'
                        })
                        continue
                    
                    # Validate marks
                    if marks_obtained > assignment.total_marks:
                        errors.append({
                            'student_id': student_id,
                            'error': f'Marks obtained ({marks_obtained}) exceeds total marks ({assignment.total_marks})'
                        })
                        continue
                    
                    # Grade the assignment
                    student_assignment.marks_obtained = marks_obtained
                    student_assignment.final_marks = marks_obtained
                    student_assignment.feedback = feedback
                    student_assignment.status = 'graded'
                    student_assignment.graded_by = request.user
                    student_assignment.graded_at = timezone.now()
                    student_assignment.save()
                    
                    graded_count += 1
                    
                except Exception as e:
                    errors.append({
                        'student_id': student_id,
                        'error': str(e)
                    })
            
            # Update assignment stats
            assignment.update_statistics()
        
        response_data = {
            'assignment_id': str(assignment.id),
            'assignment_title': assignment.title,
            'graded_count': graded_count,
            'error_count': len(errors),
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in bulk grading: {str(e)}")
        return Response(
            {'error': 'Failed to bulk grade assignments.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def import_grades(request, assignment_id):
    """
    Import grades from CSV file.
    """
    try:
        # Get the assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only import grades for your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ImportGradesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_file = serializer.validated_data['csv_file']
        file_data = csv_file.read().decode('utf-8')
        
        # Parse CSV
        csv_data = []
        reader = csv.DictReader(StringIO(file_data))
        for row in reader:
            csv_data.append(row)
        
        if not csv_data:
            return Response(
                {'error': 'CSV file is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Required columns
        required_columns = ['student_id', 'admission_number', 'marks_obtained']
        actual_columns = list(csv_data[0].keys())
        
        missing_columns = [col for col in required_columns if col not in actual_columns]
        if missing_columns:
            return Response(
                {'error': f'Missing columns in CSV: {", ".join(missing_columns)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        imported_count = 0
        errors = []
        
        with transaction.atomic():
            for idx, row in enumerate(csv_data, start=2):  # Start at 2 to account for header
                try:
                    student_id = row.get('student_id')
                    admission_number = row.get('admission_number')
                    
                    # Find student
                    try:
                        if student_id:
                            student = User.objects.get(id=student_id, role='student')
                        elif admission_number:
                            student = User.objects.get(admission_number=admission_number, role='student')
                        else:
                            errors.append({
                                'row': idx,
                                'error': 'Either student_id or admission_number must be provided'
                            })
                            continue
                    except User.DoesNotExist:
                        errors.append({
                            'row': idx,
                            'error': f'Student not found: {student_id or admission_number}'
                        })
                        continue
                    
                    # Get student assignment
                    try:
                        student_assignment = StudentAssignment.objects.get(
                            assignment=assignment,
                            student=student
                        )
                    except StudentAssignment.DoesNotExist:
                        errors.append({
                            'row': idx,
                            'error': f'No assignment found for student: {student.get_full_name()}'
                        })
                        continue
                    
                    # Get marks
                    try:
                        marks_obtained = float(row['marks_obtained'])
                    except ValueError:
                        errors.append({
                            'row': idx,
                            'error': f'Invalid marks: {row["marks_obtained"]}'
                        })
                        continue
                    
                    # Validate marks
                    if marks_obtained > assignment.total_marks:
                        errors.append({
                            'row': idx,
                            'error': f'Marks ({marks_obtained}) exceeds total marks ({assignment.total_marks})'
                        })
                        continue
                    
                    # Update grade
                    student_assignment.marks_obtained = marks_obtained
                    student_assignment.final_marks = marks_obtained
                    student_assignment.feedback = row.get('feedback', '')
                    student_assignment.status = 'graded'
                    student_assignment.graded_by = request.user
                    student_assignment.graded_at = timezone.now()
                    student_assignment.save()
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append({
                        'row': idx,
                        'error': str(e)
                    })
            
            # Update assignment stats
            assignment.update_statistics()
        
        response_data = {
            'assignment_id': str(assignment.id),
            'assignment_title': assignment.title,
            'imported_count': imported_count,
            'error_count': len(errors),
            'total_rows': len(csv_data),
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error importing grades: {str(e)}")
        return Response(
            {'error': 'Failed to import grades.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def export_grades(request, assignment_id):
    """
    Export grades for an assignment.
    """
    try:
        # Get the assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only export grades for your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student assignments
        student_assignments = StudentAssignment.objects.filter(
            assignment=assignment
        ).select_related('student').order_by('student__first_name')
        
        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="grades_{assignment.title}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Student ID',
            'Admission Number',
            'First Name',
            'Last Name',
            'Email',
            'Class',
            'Submission Status',
            'Submission Date',
            'Marks Obtained',
            'Total Marks',
            'Percentage',
            'Grade',
            'Feedback',
            'Graded By',
            'Graded At'
        ])
        
        # Write data
        for student_assignment in student_assignments:
            percentage = (student_assignment.marks_obtained / assignment.total_marks * 100) if assignment.total_marks > 0 else 0
            
            writer.writerow([
                str(student_assignment.student.id),
                student_assignment.student.admission_number if hasattr(student_assignment.student, 'admission_number') else '',
                student_assignment.student.first_name,
                student_assignment.student.last_name,
                student_assignment.student.email,
                student_assignment.student.student_profile.current_class.name if hasattr(student_assignment.student, 'student_profile') and student_assignment.student.student_profile.current_class else '',
                student_assignment.get_status_display(),
                student_assignment.submission_date.strftime('%Y-%m-%d %H:%M:%S') if student_assignment.submission_date else '',
                student_assignment.marks_obtained if student_assignment.marks_obtained is not None else '',
                assignment.total_marks,
                f"{percentage:.2f}%",
                student_assignment.grade if hasattr(student_assignment, 'grade') else '',
                student_assignment.feedback,
                student_assignment.graded_by.get_full_name() if student_assignment.graded_by else '',
                student_assignment.graded_at.strftime('%Y-%m-%d %H:%M:%S') if student_assignment.graded_at else ''
            ])
        
        return response

    except Exception as e:
        logger.error(f"Error exporting grades: {str(e)}")
        return Response(
            {'error': 'Failed to export grades.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== ANALYTICS AND REPORTING VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def assignment_analytics(request, assignment_id):
    """
    Get detailed analytics for an assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only view analytics for your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all student assignments
        student_assignments = assignment.student_assignments.all()
        
        # Calculate detailed statistics
        total_students = assignment.total_students
        submitted_count = student_assignments.filter(status__in=['submitted', 'late', 'graded']).count()
        graded_count = student_assignments.filter(status='graded').count()
        
        # Score distribution
        score_bins = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for sa in student_assignments.filter(status='graded'):
            if sa.marks_obtained is not None:
                percentage = (sa.marks_obtained / assignment.total_marks) * 100
                if percentage >= 80:
                    score_bins['A'] += 1
                elif percentage >= 70:
                    score_bins['B'] += 1
                elif percentage >= 60:
                    score_bins['C'] += 1
                elif percentage >= 50:
                    score_bins['D'] += 1
                else:
                    score_bins['F'] += 1
        
        # Time analysis (submission times relative to deadline)
        on_time = 0
        late = 0
        for sa in student_assignments.filter(submission_date__isnull=False):
            if sa.submission_date and assignment.due_date:
                if sa.submission_date <= assignment.due_date:
                    on_time += 1
                else:
                    late += 1
        
        # Performance by gender (if available)
        performance_by_gender = []
        try:
            # This assumes User model has a gender field
            genders = User.objects.filter(
                student_assignments__assignment=assignment
            ).values('gender').annotate(
                count=Count('id'),
                avg_score=Avg('student_assignments__marks_obtained')
            )
            performance_by_gender = list(genders)
        except:
            pass
        
        analytics_data = {
            'assignment': {
                'id': str(assignment.id),
                'title': assignment.title,
                'total_marks': assignment.total_marks,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None
            },
            'statistics': {
                'total_students': total_students,
                'submitted_count': submitted_count,
                'submission_rate': round((submitted_count / total_students * 100) if total_students > 0 else 0, 2),
                'graded_count': graded_count,
                'grading_completion': round((graded_count / submitted_count * 100) if submitted_count > 0 else 0, 2),
                'average_score': round(float(assignment.average_score), 2),
                'highest_score': student_assignments.aggregate(max=Max('marks_obtained'))['max'] or 0,
                'lowest_score': student_assignments.aggregate(min=Min('marks_obtained'))['min'] or 0,
                'median_score': _calculate_median(student_assignments.filter(marks_obtained__isnull=False))
            },
            'score_distribution': score_bins,
            'submission_analysis': {
                'on_time': on_time,
                'late': late,
                'not_submitted': total_students - submitted_count
            },
            'performance_by_gender': performance_by_gender,
            'generated_at': timezone.now().isoformat()
        }
        
        serializer = AssignmentAnalyticsSerializer(analytics_data)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        return Response(
            {'error': 'Failed to generate analytics.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




# Add these to your views.py file

# ==================== STUDENT PROGRESS AND REPORTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_progress_report(request, student_id=None):
    """
    Get progress report for a student.
    """
    try:
        user = request.user
        
        # If student_id is provided, check permissions
        if student_id:
            if user.role not in ['teacher', 'admin', 'head_teacher', 'deputy_principal']:
                return Response(
                    {'error': 'You are not authorized to view other students\' reports.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            student = get_object_or_404(User, id=student_id, role='student')
        else:
            # Get current user's progress
            if user.role != 'student':
                return Response(
                    {'error': 'This endpoint is for students only.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            student = user
        
        # Get student assignments
        student_assignments = StudentAssignment.objects.filter(
            student=student
        ).select_related(
            'assignment', 'assignment__subject'
        ).order_by('assignment__due_date')
        
        # Calculate overall statistics
        total_assignments = student_assignments.count()
        submitted_assignments = student_assignments.filter(status__in=['submitted', 'late', 'graded']).count()
        graded_assignments = student_assignments.filter(status='graded').count()
        
        # Calculate average score
        graded_scores = student_assignments.filter(status='graded', marks_obtained__isnull=False)
        average_score = graded_scores.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        # Calculate performance by subject
        subject_performance = []
        subjects = student_assignments.values(
            'assignment__subject__id',
            'assignment__subject__name'
        ).distinct()
        
        for subject_data in subjects:
            subject_assignments = student_assignments.filter(
                assignment__subject__id=subject_data['assignment__subject__id']
            )
            subject_graded = subject_assignments.filter(status='graded')
            subject_avg = subject_graded.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
            subject_total = subject_assignments.count()
            subject_submitted = subject_assignments.filter(status__in=['submitted', 'late', 'graded']).count()
            
            subject_performance.append({
                'subject_id': subject_data['assignment__subject__id'],
                'subject_name': subject_data['assignment__subject__name'],
                'total_assignments': subject_total,
                'submitted_assignments': subject_submitted,
                'completion_rate': round((subject_submitted / subject_total * 100) if subject_total > 0 else 0, 2),
                'average_score': round(float(subject_avg), 2)
            })
        
        # Get recent assignments
        recent_assignments = student_assignments.order_by('-assignment__due_date')[:10]
        
        # Calculate trends (last month vs previous month)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        
        recent_graded = student_assignments.filter(
            status='graded',
            graded_at__gte=thirty_days_ago
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        previous_graded = student_assignments.filter(
            status='graded',
            graded_at__gte=sixty_days_ago,
            graded_at__lt=thirty_days_ago
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        trend = 'improving' if recent_graded > previous_graded else 'declining' if recent_graded < previous_graded else 'stable'
        
        # Prepare response
        report = {
            'student': {
                'id': str(student.id),
                'full_name': student.get_full_name(),
                'admission_number': student.admission_number if hasattr(student, 'admission_number') else '',
                'class': student.student_profile.current_class.name if hasattr(student, 'student_profile') else '',
                'email': student.email
            },
            'overall_statistics': {
                'total_assignments': total_assignments,
                'submitted_assignments': submitted_assignments,
                'submission_rate': round((submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0, 2),
                'graded_assignments': graded_assignments,
                'average_score': round(float(average_score), 2),
                'performance_trend': trend
            },
            'subject_performance': subject_performance,
            'recent_assignments': StudentAssignmentMiniSerializer(recent_assignments, many=True).data,
            'recommendations': _generate_student_recommendations(student_assignments)
        }
        
        return Response(report)
        
    except Exception as e:
        logger.error(f"Error generating student progress report: {str(e)}")
        return Response(
            {'error': 'Failed to generate progress report.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== ASSIGNMENT TIMELINE ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_timeline(request):
    """
    Get assignment timeline view with important dates.
    """
    try:
        user = request.user
        
        # Get date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Default to next 30 days
        today = timezone.now().date()
        if not start_date_str:
            start_date = today
        else:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not end_date_str:
            end_date = today + timedelta(days=30)
        else:
            try:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get assignments based on user role
        if user.role == 'student':
            # Get student's current class
            current_class = None
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                current_class = user.student_profile.current_class
            
            if current_class:
                assignments = Assignment.objects.filter(
                    classroom=current_class,
                    status__in=['published', 'in_progress'],
                    due_date__date__range=[start_date, end_date]
                ).order_by('due_date')
            else:
                assignments = Assignment.objects.none()
                
        elif user.role == 'teacher':
            assignments = Assignment.objects.filter(
                teacher=user,
                status__in=['published', 'in_progress'],
                due_date__date__range=[start_date, end_date]
            ).order_by('due_date')
        else:
            assignments = Assignment.objects.filter(
                status__in=['published', 'in_progress'],
                due_date__date__range=[start_date, end_date]
            ).order_by('due_date')
        
        # Group assignments by date
        timeline_events = {}
        for assignment in assignments:
            date_key = assignment.due_date.date().isoformat()
            if date_key not in timeline_events:
                timeline_events[date_key] = []
            
            # Get student status if applicable
            student_status = None
            if user.role == 'student':
                try:
                    student_assignment = StudentAssignment.objects.get(
                        assignment=assignment,
                        student=user
                    )
                    student_status = student_assignment.status
                except StudentAssignment.DoesNotExist:
                    student_status = 'not_started'
            
            timeline_events[date_key].append({
                'assignment_id': str(assignment.id),
                'title': assignment.title,
                'subject': assignment.subject.name if assignment.subject else '',
                'due_time': assignment.due_date.strftime('%H:%M'),
                'total_marks': assignment.total_marks,
                'status': assignment.status,
                'student_status': student_status,
                'is_overdue': assignment.is_overdue,
                'days_until_due': assignment.days_until_due,
                'priority': 'high' if assignment.days_until_due <= 1 else 'medium' if assignment.days_until_due <= 3 else 'low'
            })
        
        # Convert to list format
        timeline = []
        for date_str, events in timeline_events.items():
            timeline.append({
                'date': date_str,
                'events': events,
                'event_count': len(events)
            })
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_days': (end_date - start_date).days,
            'total_events': sum(len(events) for events in timeline_events.values()),
            'timeline': timeline
        })
        
    except Exception as e:
        logger.error(f"Error retrieving assignment timeline: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve assignment timeline.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== BATCH OPERATIONS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def batch_update_assignment_status(request):
    """
    Batch update assignment statuses.
    """
    try:
        serializer = BatchUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        assignment_ids = serializer.validated_data['assignment_ids']
        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')
        
        # Validate status transition
        valid_transitions = {
            'draft': ['published'],
            'published': ['in_progress', 'closed'],
            'in_progress': ['closed'],
            'closed': ['graded'],
            'graded': []  # Final state
        }
        
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for assignment_id in assignment_ids:
                try:
                    assignment = Assignment.objects.get(id=assignment_id, teacher=request.user)
                    
                    # Check if transition is valid
                    if new_status not in valid_transitions.get(assignment.status, []):
                        errors.append({
                            'assignment_id': str(assignment_id),
                            'error': f'Cannot transition from {assignment.status} to {new_status}'
                        })
                        continue
                    
                    # Update assignment
                    if new_status == 'published':
                        assignment.status = 'published'
                        assignment.published_at = timezone.now()
                        # Create student assignments
                        assignment.create_student_assignments()
                    elif new_status == 'closed':
                        assignment.status = 'closed'
                        assignment.closed_at = timezone.now()
                    elif new_status == 'graded':
                        assignment.status = 'graded'
                    else:
                        assignment.status = new_status
                    
                    assignment.save()
                    updated_count += 1
                    
                except Assignment.DoesNotExist:
                    errors.append({
                        'assignment_id': str(assignment_id),
                        'error': 'Assignment not found or you do not have permission'
                    })
                except Exception as e:
                    errors.append({
                        'assignment_id': str(assignment_id),
                        'error': str(e)
                    })
        
        response_data = {
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        return Response(
            {'error': 'Failed to batch update assignment statuses.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== SEARCH ENDPOINT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_search(request):
    """
    Advanced search for assignments.
    """
    try:
        user = request.user
        
        # Get search parameters
        query = request.query_params.get('q', '')
        status_filter = request.query_params.get('status', '')
        subject_id = request.query_params.get('subject_id', '')
        classroom_id = request.query_params.get('classroom_id', '')
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')
        sort_by = request.query_params.get('sort_by', 'relevance')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Build queryset based on user role
        if user.role == 'student':
            # Get student's current class
            current_class = None
            if hasattr(user, 'student_profile') and user.student_profile.current_class:
                current_class = user.student_profile.current_class
            
            if current_class:
                queryset = Assignment.objects.filter(
                    classroom=current_class,
                    status__in=['published', 'in_progress', 'closed', 'graded']
                )
            else:
                queryset = Assignment.objects.none()
                
        elif user.role == 'teacher':
            queryset = Assignment.objects.filter(teacher=user)
        else:
            queryset = Assignment.objects.filter(status='published')
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(subject__name__icontains=query)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        
        if date_from:
            try:
                date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Apply sorting
        if sort_by == 'relevance' and query:
            # Simple relevance sorting based on query matches
            queryset = queryset.annotate(
                relevance=Count(
                    Case(
                        When(title__icontains=query, then=Value(3)),
                        When(description__icontains=query, then=Value(2)),
                        When(subject__name__icontains=query, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                )
            ).order_by('-relevance', '-created_at')
        elif sort_by == 'date_asc':
            queryset = queryset.order_by('due_date')
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-due_date')
        elif sort_by == 'marks_asc':
            queryset = queryset.order_by('total_marks')
        elif sort_by == 'marks_desc':
            queryset = queryset.order_by('-total_marks')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        assignments = queryset[start_index:end_index]
        
        # Get student status for each assignment if user is student
        assignment_data = []
        for assignment in assignments:
            assignment_dict = {
                'id': str(assignment.id),
                'title': assignment.title,
                'description': assignment.description[:200] + '...' if assignment.description and len(assignment.description) > 200 else assignment.description,
                'subject': assignment.subject.name if assignment.subject else '',
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'total_marks': assignment.total_marks,
                'status': assignment.status,
                'is_overdue': assignment.is_overdue,
                'views_count': assignment.views_count,
                'average_score': assignment.average_score
            }
            
            if user.role == 'student':
                try:
                    student_assignment = StudentAssignment.objects.get(
                        assignment=assignment,
                        student=user
                    )
                    assignment_dict['student_status'] = student_assignment.status
                    assignment_dict['submitted_at'] = student_assignment.submission_date.isoformat() if student_assignment.submission_date else None
                    assignment_dict['marks_obtained'] = student_assignment.marks_obtained
                except StudentAssignment.DoesNotExist:
                    assignment_dict['student_status'] = 'not_started'
            
            assignment_data.append(assignment_dict)
        
        return Response({
            'query': query,
            'filters': {
                'status': status_filter,
                'subject_id': subject_id,
                'classroom_id': classroom_id,
                'date_from': date_from,
                'date_to': date_to
            },
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'results': assignment_data
        })
        
    except Exception as e:
        logger.error(f"Error in assignment search: {str(e)}")
        return Response(
            {'error': 'Failed to search assignments.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== TEMPLATE EXPORT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def export_assignment_template(request):
    """
    Export assignment template for bulk creation.
    """
    try:
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assignment_template.csv"'
        
        writer = csv.writer(response)
        
        # Write header with descriptions
        writer.writerow(['# Assignment Import Template'])
        writer.writerow(['# Fill in the values below, then import using the bulk create endpoint'])
        writer.writerow([])
        
        # Write column headers with examples
        writer.writerow([
            'title', 'description', 'assignment_type', 'subject_id',
            'classroom_id', 'due_date', 'total_marks', 'passing_marks',
            'difficulty_level', 'estimated_completion_time', 'instructions',
            'learning_objectives', 'resources', 'allow_late_submission',
            'late_submission_penalty', 'require_approval'
        ])
        
        # Write example row
        writer.writerow([
            'Math Homework 1', 'Solve quadratic equations', 'homework',
            'subject-uuid-here', 'classroom-uuid-here', '2024-12-31 23:59:59',
            '100', '40', 'medium', '60', 'Show all working',
            '1. Solve quadratic equations\n2. Understand discriminant', 
            'Textbook chapter 5', 'true', '10', 'false'
        ])
        
        # Write instructions
        writer.writerow([])
        writer.writerow(['# Instructions:'])
        writer.writerow(['# - Keep the header row as is'])
        writer.writerow(['# - Fill in actual values in the rows below'])
        writer.writerow(['# - assignment_type can be: homework, project, quiz, exam, presentation'])
        writer.writerow(['# - difficulty_level can be: easy, medium, hard, advanced'])
        writer.writerow(['# - Boolean fields: true/false'])
        writer.writerow(['# - IDs must be valid UUIDs from your system'])
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting template: {str(e)}")
        return Response(
            {'error': 'Failed to export template.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== DATA MANAGEMENT ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def fix_student_assignments(request, assignment_id):
    """
    Fix missing student assignments for a published assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check if assignment is published and has a classroom
        if assignment.status != 'published' or not assignment.classroom:
            return Response(
                {'error': 'Assignment must be published and assigned to a classroom.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all students in the classroom
        students = User.objects.filter(
            role='student',
            student_profile__current_class=assignment.classroom
        )
        
        created_count = 0
        existing_count = StudentAssignment.objects.filter(assignment=assignment).count()
        
        with transaction.atomic():
            for student in students:
                # Create student assignment if it doesn't exist
                student_assignment, created = StudentAssignment.objects.get_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={
                        'status': 'not_submitted',
                        'created_by': request.user
                    }
                )
                
                if created:
                    created_count += 1
        
        return Response({
            'assignment_id': str(assignment.id),
            'assignment_title': assignment.title,
            'classroom': assignment.classroom.name if assignment.classroom else '',
            'total_students_in_class': students.count(),
            'existing_assignments': existing_count,
            'new_assignments_created': created_count,
            'total_assignments_now': existing_count + created_count
        })
        
    except Exception as e:
        logger.error(f"Error fixing student assignments: {str(e)}")
        return Response(
            {'error': 'Failed to fix student assignments.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def recalculate_assignment_statistics(request):
    """
    Recalculate statistics for all assignments.
    """
    try:
        # Get filter parameters
        assignment_id = request.data.get('assignment_id')
        teacher_id = request.data.get('teacher_id')
        
        # Build queryset
        if assignment_id:
            assignments = Assignment.objects.filter(id=assignment_id)
        elif teacher_id:
            assignments = Assignment.objects.filter(teacher_id=teacher_id)
        else:
            assignments = Assignment.objects.all()
        
        updated_count = 0
        errors = []
        
        for assignment in assignments:
            try:
                assignment.update_statistics()
                updated_count += 1
            except Exception as e:
                errors.append({
                    'assignment_id': str(assignment.id),
                    'error': str(e)
                })
        
        return Response({
            'total_processed': assignments.count(),
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error recalculating statistics: {str(e)}")
        return Response(
            {'error': 'Failed to recalculate statistics.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== HELPER FUNCTIONS ====================

def _generate_student_recommendations(student_assignments):
    """
    Generate personalized recommendations for a student.
    """
    recommendations = []
    
    # Get overdue assignments
    overdue = student_assignments.filter(
        assignment__due_date__lt=timezone.now(),
        status='not_submitted'
    )
    
    if overdue.exists():
        recommendations.append({
            'type': 'urgent',
            'message': f'You have {overdue.count()} overdue assignment(s). Submit them as soon as possible.',
            'action': 'submit_overdue'
        })
    
    # Check for upcoming deadlines (within 2 days)
    two_days_from_now = timezone.now() + timedelta(days=2)
    upcoming = student_assignments.filter(
        assignment__due_date__lte=two_days_from_now,
        assignment__due_date__gt=timezone.now(),
        status='not_submitted'
    )
    
    if upcoming.exists():
        recommendations.append({
            'type': 'warning',
            'message': f'You have {upcoming.count()} assignment(s) due within 2 days.',
            'action': 'plan_submissions'
        })
    
    # Check performance in graded assignments
    graded_assignments = student_assignments.filter(status='graded', marks_obtained__isnull=False)
    
    if graded_assignments.count() >= 3:
        avg_score = graded_assignments.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        # Find assignments with low scores
        low_scoring = graded_assignments.filter(
            marks_obtained__lt=F('assignment__passing_marks')
        )
        
        if low_scoring.exists():
            recommendations.append({
                'type': 'improvement',
                'message': f'You scored below passing marks in {low_scoring.count()} assignment(s). Consider reviewing the material.',
                'action': 'review_low_scores'
            })
        
        # Check for improvement trend
        if graded_assignments.count() >= 5:
            recent_avg = graded_assignments.order_by('-assignment__due_date')[:3].aggregate(
                avg=Avg('marks_obtained')
            )['avg'] or 0
            
            older_avg = graded_assignments.order_by('-assignment__due_date')[3:5].aggregate(
                avg=Avg('marks_obtained')
            )['avg'] or 0
            
            if recent_avg > older_avg:
                recommendations.append({
                    'type': 'positive',
                    'message': 'Your grades are improving! Keep up the good work.',
                    'action': 'continue_good_habits'
                })
    
    # Check submission habits
    late_submissions = student_assignments.filter(status='late').count()
    total_submitted = student_assignments.filter(status__in=['submitted', 'late', 'graded']).count()
    
    if total_submitted > 0:
        late_percentage = (late_submissions / total_submitted) * 100
        if late_percentage > 50:
            recommendations.append({
                'type': 'habit',
                'message': 'You frequently submit assignments late. Try to work on time management.',
                'action': 'improve_time_management'
            })
    
    return recommendations

# Add these missing functions to your views.py file

# ==================== NOTIFICATIONS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    """
    Get assignment-related notifications for the current user.
    """
    try:
        user = request.user
        
        # Get query parameters
        notification_type = request.query_params.get('type', 'all')
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        limit = int(request.query_params.get('limit', 50))
        
        # Base queryset (in a real app, you'd have a Notification model)
        # For now, we'll generate notifications dynamically
        
        notifications_list = []
        
        if user.role == 'student':
            # Student notifications
            notifications_list.extend(_get_student_notifications(user, notification_type, unread_only))
        elif user.role == 'teacher':
            # Teacher notifications
            notifications_list.extend(_get_teacher_notifications(user, notification_type, unread_only))
        
        # Sort by priority and date
        notifications_list.sort(key=lambda x: (x['priority'], x['timestamp']), reverse=True)
        
        # Apply limit
        notifications_list = notifications_list[:limit]
        
        # Count unread
        unread_count = sum(1 for n in notifications_list if not n.get('read', False))
        
        return Response({
            'unread_count': unread_count,
            'total_count': len(notifications_list),
            'notifications': notifications_list
        })
        
    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve notifications.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_student_notifications(user, notification_type, unread_only):
    """Get notifications for a student."""
    notifications = []
    
    # Get overdue assignments
    if notification_type in ['all', 'overdue', 'urgent']:
        overdue_assignments = StudentAssignment.objects.filter(
            student=user,
            status='not_submitted',
            assignment__due_date__lt=timezone.now()
        ).select_related('assignment')
        
        for sa in overdue_assignments:
            notifications.append({
                'id': f"overdue_{sa.id}",
                'type': 'overdue',
                'title': 'Assignment Overdue',
                'message': f"Your assignment '{sa.assignment.title}' is overdue.",
                'timestamp': sa.assignment.due_date.isoformat(),
                'priority': 'high',
                'data': {
                    'assignment_id': str(sa.assignment.id),
                    'assignment_title': sa.assignment.title,
                    'days_overdue': (timezone.now() - sa.assignment.due_date).days
                },
                'actions': ['submit', 'request_extension'],
                'read': False
            })
    
    # Get assignments due soon (within 24 hours)
    if notification_type in ['all', 'upcoming', 'warning']:
        tomorrow = timezone.now() + timedelta(days=1)
        due_soon = StudentAssignment.objects.filter(
            student=user,
            status='not_submitted',
            assignment__due_date__range=[timezone.now(), tomorrow]
        ).select_related('assignment')
        
        for sa in due_soon:
            hours_left = (sa.assignment.due_date - timezone.now()).total_seconds() / 3600
            notifications.append({
                'id': f"due_soon_{sa.id}",
                'type': 'upcoming',
                'title': 'Assignment Due Soon',
                'message': f"Assignment '{sa.assignment.title}' is due in {int(hours_left)} hours.",
                'timestamp': sa.assignment.due_date.isoformat(),
                'priority': 'medium',
                'data': {
                    'assignment_id': str(sa.assignment.id),
                    'assignment_title': sa.assignment.title,
                    'hours_left': hours_left
                },
                'actions': ['submit', 'view_assignment'],
                'read': False
            })
    
    # Get graded assignments (recently graded)
    if notification_type in ['all', 'graded', 'info']:
        recent_graded = StudentAssignment.objects.filter(
            student=user,
            status='graded',
            graded_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('assignment')
        
        for sa in recent_graded:
            notifications.append({
                'id': f"graded_{sa.id}",
                'type': 'graded',
                'title': 'Assignment Graded',
                'message': f"Your assignment '{sa.assignment.title}' has been graded. Score: {sa.marks_obtained}/{sa.assignment.total_marks}",
                'timestamp': sa.graded_at.isoformat() if sa.graded_at else timezone.now().isoformat(),
                'priority': 'info',
                'data': {
                    'assignment_id': str(sa.assignment.id),
                    'assignment_title': sa.assignment.title,
                    'marks_obtained': sa.marks_obtained,
                    'total_marks': sa.assignment.total_marks,
                    'percentage': (sa.marks_obtained / sa.assignment.total_marks * 100) if sa.assignment.total_marks > 0 else 0
                },
                'actions': ['view_feedback', 'view_assignment'],
                'read': False
            })
    
    # Get new assignments
    if notification_type in ['all', 'new']:
        recent_assignments = Assignment.objects.filter(
            classroom=user.student_profile.current_class if hasattr(user, 'student_profile') else None,
            status='published',
            published_at__gte=timezone.now() - timedelta(days=3)
        )
        
        for assignment in recent_assignments:
            notifications.append({
                'id': f"new_{assignment.id}",
                'type': 'new_assignment',
                'title': 'New Assignment',
                'message': f"New assignment published: '{assignment.title}'",
                'timestamp': assignment.published_at.isoformat() if assignment.published_at else assignment.created_at.isoformat(),
                'priority': 'info',
                'data': {
                    'assignment_id': str(assignment.id),
                    'assignment_title': assignment.title,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None
                },
                'actions': ['view_assignment', 'start_working'],
                'read': False
            })
    
    return notifications


def _get_teacher_notifications(user, notification_type, unread_only):
    """Get notifications for a teacher."""
    notifications = []
    
    # Get assignments with submissions to grade
    if notification_type in ['all', 'grading', 'urgent']:
        assignments_to_grade = Assignment.objects.filter(
            teacher=user,
            status__in=['published', 'closed']
        ).annotate(
            ungraded_count=Count(
                'student_assignments',
                filter=Q(student_assignments__status__in=['submitted', 'late'])
            )
        ).filter(ungraded_count__gt=0)
        
        for assignment in assignments_to_grade:
            notifications.append({
                'id': f"grading_{assignment.id}",
                'type': 'grading',
                'title': 'Submissions to Grade',
                'message': f"You have {assignment.ungraded_count} submission(s) to grade for '{assignment.title}'",
                'timestamp': assignment.due_date.isoformat() if assignment.due_date else assignment.created_at.isoformat(),
                'priority': 'medium',
                'data': {
                    'assignment_id': str(assignment.id),
                    'assignment_title': assignment.title,
                    'ungraded_count': assignment.ungraded_count
                },
                'actions': ['grade_submissions', 'view_assignment'],
                'read': False
            })
    
    # Get assignments closing soon (for grading)
    if notification_type in ['all', 'closing', 'warning']:
        tomorrow = timezone.now() + timedelta(days=1)
        closing_soon = Assignment.objects.filter(
            teacher=user,
            status='published',
            due_date__range=[timezone.now(), tomorrow]
        )
        
        for assignment in closing_soon:
            hours_left = (assignment.due_date - timezone.now()).total_seconds() / 3600
            notifications.append({
                'id': f"closing_{assignment.id}",
                'type': 'closing',
                'title': 'Assignment Closing Soon',
                'message': f"Assignment '{assignment.title}' is closing in {int(hours_left)} hours.",
                'timestamp': assignment.due_date.isoformat(),
                'priority': 'medium',
                'data': {
                    'assignment_id': str(assignment.id),
                    'assignment_title': assignment.title,
                    'hours_left': hours_left
                },
                'actions': ['view_submissions', 'close_assignment'],
                'read': False
            })
    
    # Get late submissions
    if notification_type in ['all', 'late', 'info']:
        late_submissions = StudentAssignment.objects.filter(
            assignment__teacher=user,
            status='late',
            submission_date__gte=timezone.now() - timedelta(days=2)
        ).select_related('assignment', 'student')
        
        for submission in late_submissions:
            notifications.append({
                'id': f"late_{submission.id}",
                'type': 'late_submission',
                'title': 'Late Submission',
                'message': f"{submission.student.get_full_name()} submitted '{submission.assignment.title}' late",
                'timestamp': submission.submission_date.isoformat() if submission.submission_date else timezone.now().isoformat(),
                'priority': 'info',
                'data': {
                    'assignment_id': str(submission.assignment.id),
                    'assignment_title': submission.assignment.title,
                    'student_id': str(submission.student.id),
                    'student_name': submission.student.get_full_name(),
                    'submission_date': submission.submission_date.isoformat() if submission.submission_date else None
                },
                'actions': ['view_submission', 'apply_penalty'],
                'read': False
            })
    
    return notifications


# ==================== CLASS PERFORMANCE REPORT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacher])
def class_performance_report(request, classroom_id=None):
    """
    Get performance report for a class.
    """
    try:
        teacher = request.user
        
        # If classroom_id is provided, use it
        if classroom_id:
            classroom = get_object_or_404(Classroom, id=classroom_id)
        else:
            # Get teacher's default classroom or first classroom
            classrooms = Classroom.objects.filter(teacher=teacher)
            if not classrooms.exists():
                return Response(
                    {'error': 'No classrooms assigned to this teacher.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            classroom = classrooms.first()
        
        # Get all assignments for this classroom
        assignments = Assignment.objects.filter(
            teacher=teacher,
            classroom=classroom,
            status__in=['closed', 'graded']
        ).order_by('-due_date')
        
        # Get all students in the classroom
        students = User.objects.filter(
            role='student',
            student_profile__current_class=classroom
        )
        
        # Calculate class statistics
        total_assignments = assignments.count()
        total_students = students.count()
        
        # Calculate overall class average
        class_assignments = []
        for assignment in assignments:
            student_assignments = assignment.student_assignments.filter(status='graded')
            graded_count = student_assignments.count()
            average_score = student_assignments.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
            
            class_assignments.append({
                'assignment_id': str(assignment.id),
                'title': assignment.title,
                'subject': assignment.subject.name if assignment.subject else '',
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'total_marks': assignment.total_marks,
                'graded_count': graded_count,
                'average_score': round(float(average_score), 2),
                'completion_rate': round((graded_count / total_students * 100), 2) if total_students > 0 else 0
            })
        
        # Calculate student performance
        student_performance = []
        for student in students:
            student_assignments = StudentAssignment.objects.filter(
                student=student,
                assignment__in=assignments,
                status='graded'
            )
            
            total_graded = student_assignments.count()
            if total_graded == 0:
                continue
            
            average_score = student_assignments.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
            total_possible = sum(sa.assignment.total_marks for sa in student_assignments)
            overall_percentage = (sum(sa.marks_obtained for sa in student_assignments) / total_possible * 100) if total_possible > 0 else 0
            
            # Get performance trend
            recent_assignments = student_assignments.order_by('-assignment__due_date')[:3]
            older_assignments = student_assignments.order_by('-assignment__due_date')[3:6]
            
            recent_avg = recent_assignments.aggregate(avg=Avg('marks_obtained'))['avg'] or 0 if recent_assignments.exists() else 0
            older_avg = older_assignments.aggregate(avg=Avg('marks_obtained'))['avg'] or 0 if older_assignments.exists() else 0
            
            trend = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
            
            student_performance.append({
                'student_id': str(student.id),
                'full_name': student.get_full_name(),
                'admission_number': student.admission_number if hasattr(student, 'admission_number') else '',
                'total_assignments_graded': total_graded,
                'average_score': round(float(average_score), 2),
                'overall_percentage': round(float(overall_percentage), 2),
                'performance_trend': trend,
                'attendance_rate': 95.0,  # This would come from attendance module
                'participation_score': 85.0  # This would come from classroom interaction
            })
        
        # Calculate class averages
        class_average = sum(item['average_score'] for item in class_assignments) / len(class_assignments) if class_assignments else 0
        completion_rate = sum(item['completion_rate'] for item in class_assignments) / len(class_assignments) if class_assignments else 0
        
        # Subject-wise performance
        subject_performance = []
        subjects = assignments.values('subject__id', 'subject__name').distinct()
        
        for subject_data in subjects:
            subject_assignments = assignments.filter(subject__id=subject_data['subject__id'])
            subject_avg = sum(a.student_assignments.filter(status='graded').aggregate(
                avg=Avg('marks_obtained')
            )['avg'] or 0 for a in subject_assignments) / subject_assignments.count() if subject_assignments.exists() else 0
            
            subject_performance.append({
                'subject_id': subject_data['subject__id'],
                'subject_name': subject_data['subject__name'],
                'assignment_count': subject_assignments.count(),
                'average_score': round(float(subject_avg), 2)
            })
        
        report = {
            'classroom': {
                'id': str(classroom.id),
                'name': classroom.name,
                'grade_level': classroom.grade_level,
                'academic_year': classroom.academic_year.name if classroom.academic_year else '',
                'total_students': total_students
            },
            'summary': {
                'total_assignments': total_assignments,
                'class_average_score': round(float(class_average), 2),
                'average_completion_rate': round(float(completion_rate), 2),
                'top_performer': max(student_performance, key=lambda x: x['average_score'])['full_name'] if student_performance else '',
                'most_improved': max(student_performance, key=lambda x: 1 if x['performance_trend'] == 'improving' else 0)['full_name'] if student_performance else ''
            },
            'assignments': class_assignments,
            'student_performance': sorted(student_performance, key=lambda x: x['average_score'], reverse=True),
            'subject_performance': subject_performance,
            'recommendations': _generate_class_recommendations(assignments, student_performance),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(report)
        
    except Exception as e:
        logger.error(f"Error generating class performance report: {str(e)}")
        return Response(
            {'error': 'Failed to generate class performance report.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== SEND REMINDERS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def send_assignment_reminders(request, assignment_id):
    """
    Send reminders to students about an assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only send reminders for your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SendRemindersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reminder_type = serializer.validated_data['reminder_type']
        custom_message = serializer.validated_data.get('custom_message', '')
        target_students = serializer.validated_data.get('target_students', 'all')
        
        # Get students who haven't submitted
        student_assignments = assignment.student_assignments.all()
        
        if target_students == 'not_submitted':
            target_students_list = student_assignments.filter(status='not_submitted')
        elif target_students == 'late':
            target_students_list = student_assignments.filter(status='late')
        elif target_students == 'all':
            target_students_list = student_assignments
        else:
            # Specific student IDs
            target_students_list = student_assignments.filter(student_id__in=target_students)
        
        # In a real app, you would send actual notifications/emails here
        # For now, we'll just log and return a summary
        
        reminder_count = target_students_list.count()
        
        # Create reminder records
        reminders_created = []
        for student_assignment in target_students_list:
            reminder = AssignmentReminder.objects.create(
                assignment=assignment,
                student=student_assignment.student,
                reminder_type=reminder_type,
                message=custom_message or _get_default_reminder_message(assignment, reminder_type),
                sent_by=request.user,
                status='sent'
            )
            reminders_created.append({
                'student_id': str(student_assignment.student.id),
                'student_name': student_assignment.student.get_full_name(),
                'reminder_id': str(reminder.id)
            })
        
        logger.info(f"Reminders sent for assignment {assignment.title}: {reminder_count} reminders")
        
        return Response({
            'assignment_id': str(assignment.id),
            'assignment_title': assignment.title,
            'reminder_type': reminder_type,
            'reminders_sent': reminder_count,
            'target_students': target_students,
            'reminders': reminders_created
        })
        
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        return Response(
            {'error': 'Failed to send reminders.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== SYSTEM HEALTH AND STATS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assignments_health_check(request):
    """
    Perform system health check for assignments module.
    """
    try:
        checks = []
        
        # Check 1: Database connectivity
        try:
            assignment_count = Assignment.objects.count()
            checks.append({
                'check': 'database_connectivity',
                'status': 'pass',
                'message': f'Database connected successfully. Found {assignment_count} assignments.',
                'details': {'assignment_count': assignment_count}
            })
        except Exception as e:
            checks.append({
                'check': 'database_connectivity',
                'status': 'fail',
                'message': f'Database connection failed: {str(e)}',
                'details': {'error': str(e)}
            })
        
        # Check 2: Orphaned student assignments
        try:
            orphaned_count = StudentAssignment.objects.filter(
                assignment__isnull=True
            ).count()
            
            if orphaned_count == 0:
                checks.append({
                    'check': 'orphaned_assignments',
                    'status': 'pass',
                    'message': 'No orphaned student assignments found.',
                    'details': {'orphaned_count': 0}
                })
            else:
                checks.append({
                    'check': 'orphaned_assignments',
                    'status': 'warning',
                    'message': f'Found {orphaned_count} orphaned student assignments.',
                    'details': {'orphaned_count': orphaned_count}
                })
        except Exception as e:
            checks.append({
                'check': 'orphaned_assignments',
                'status': 'fail',
                'message': f'Failed to check orphaned assignments: {str(e)}',
                'details': {'error': str(e)}
            })
        
        # Check 3: Overdue assignments without proper status
        try:
            overdue_without_status = Assignment.objects.filter(
                due_date__lt=timezone.now(),
                status__in=['published', 'in_progress']
            ).count()
            
            if overdue_without_status == 0:
                checks.append({
                    'check': 'overdue_assignments',
                    'status': 'pass',
                    'message': 'No overdue assignments with incorrect status.',
                    'details': {'overdue_count': 0}
                })
            else:
                checks.append({
                    'check': 'overdue_assignments',
                    'status': 'warning',
                    'message': f'Found {overdue_without_status} overdue assignments that should be closed.',
                    'details': {'overdue_count': overdue_without_status}
                })
        except Exception as e:
            checks.append({
                'check': 'overdue_assignments',
                'status': 'fail',
                'message': f'Failed to check overdue assignments: {str(e)}',
                'details': {'error': str(e)}
            })
        
        # Check 4: Storage space (simulated)
        try:
            # In a real app, you would check actual storage
            checks.append({
                'check': 'storage_space',
                'status': 'pass',
                'message': 'Storage space is sufficient.',
                'details': {'estimated_usage': '2.5 GB', 'available': '47.5 GB'}
            })
        except Exception as e:
            checks.append({
                'check': 'storage_space',
                'status': 'fail',
                'message': f'Failed to check storage: {str(e)}',
                'details': {'error': str(e)}
            })
        
        # Calculate overall status
        all_passed = all(check['status'] == 'pass' for check in checks)
        has_failures = any(check['status'] == 'fail' for check in checks)
        has_warnings = any(check['status'] == 'warning' for check in checks)
        
        overall_status = 'healthy' if all_passed else 'degraded' if has_warnings and not has_failures else 'unhealthy'
        
        return Response({
            'service': 'assignments_module',
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'checks': checks,
            'summary': {
                'total_checks': len(checks),
                'passed': sum(1 for check in checks if check['status'] == 'pass'),
                'warnings': sum(1 for check in checks if check['status'] == 'warning'),
                'failures': sum(1 for check in checks if check['status'] == 'fail')
            }
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return Response(
            {'error': 'Health check failed.', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_stats(request):
    """
    Get system statistics for assignments module.
    """
    try:
        # Calculate various statistics
        stats = {
            'assignments': {
                'total': Assignment.objects.count(),
                'published': Assignment.objects.filter(status='published').count(),
                'draft': Assignment.objects.filter(status='draft').count(),
                'closed': Assignment.objects.filter(status='closed').count(),
                'graded': Assignment.objects.filter(status='graded').count(),
                'overdue': Assignment.objects.filter(
                    due_date__lt=timezone.now(),
                    status__in=['published', 'in_progress']
                ).count()
            },
            'student_assignments': {
                'total': StudentAssignment.objects.count(),
                'not_submitted': StudentAssignment.objects.filter(status='not_submitted').count(),
                'submitted': StudentAssignment.objects.filter(status='submitted').count(),
                'late': StudentAssignment.objects.filter(status='late').count(),
                'graded': StudentAssignment.objects.filter(status='graded').count(),
                'average_score': StudentAssignment.objects.filter(
                    status='graded'
                ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0
            },
            'users': {
                'total_teachers': User.objects.filter(role='teacher').count(),
                'total_students': User.objects.filter(role='student').count(),
                'active_teachers': User.objects.filter(
                    role='teacher',
                    last_login__gte=timezone.now() - timedelta(days=30)
                ).count(),
                'active_students': User.objects.filter(
                    role='student',
                    last_login__gte=timezone.now() - timedelta(days=30)
                ).count()
            },
            'storage': {
                'total_attachments': StudentAssignment.objects.exclude(
                    Q(attachments='') | Q(attachments__isnull=True)
                ).count(),
                # In a real app, you would calculate actual file sizes
                'estimated_size': '2.3 GB'
            },
            'activity': {
                'submissions_today': StudentAssignment.objects.filter(
                    submission_date__date=timezone.now().date()
                ).count(),
                'submissions_week': StudentAssignment.objects.filter(
                    submission_date__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'grading_today': StudentAssignment.objects.filter(
                    graded_at__date=timezone.now().date()
                ).count(),
                'new_assignments_today': Assignment.objects.filter(
                    created_at__date=timezone.now().date()
                ).count()
            }
        }
        
        # Calculate growth rates (compared to last month)
        last_month = timezone.now() - timedelta(days=30)
        
        stats['growth'] = {
            'assignments': {
                'current': stats['assignments']['total'],
                'previous': Assignment.objects.filter(
                    created_at__lt=last_month
                ).count(),
                'growth_rate': _calculate_growth_rate(
                    stats['assignments']['total'],
                    Assignment.objects.filter(created_at__lt=last_month).count()
                )
            },
            'submissions': {
                'current': stats['activity']['submissions_week'],
                'previous': StudentAssignment.objects.filter(
                    submission_date__range=[last_month - timedelta(days=7), last_month]
                ).count(),
                'growth_rate': _calculate_growth_rate(
                    stats['activity']['submissions_week'],
                    StudentAssignment.objects.filter(
                        submission_date__range=[last_month - timedelta(days=7), last_month]
                    ).count()
                )
            }
        }
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'stats': stats,
            'generated_by': request.user.email
        })
        
    except Exception as e:
        logger.error(f"Error generating system stats: {str(e)}")
        return Response(
            {'error': 'Failed to generate system statistics.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== HELPER FUNCTIONS ====================

def _get_default_reminder_message(assignment, reminder_type):
    """Get default reminder message based on type."""
    messages = {
        'due_soon': f"Reminder: Assignment '{assignment.title}' is due on {assignment.due_date.strftime('%B %d, %Y at %I:%M %p')}. Don't forget to submit!",
        'overdue': f"Urgent: Assignment '{assignment.title}' is now overdue. Please submit as soon as possible.",
        'general': f"Reminder about assignment '{assignment.title}'. Due date: {assignment.due_date.strftime('%B %d, %Y')}",
        'grading': f"Reminder: Assignment '{assignment.title}' needs to be graded. Please complete grading soon."
    }
    return messages.get(reminder_type, messages['general'])


def _calculate_growth_rate(current, previous):
    """Calculate growth rate percentage."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def _generate_class_recommendations(assignments, student_performance):
    """Generate recommendations for a class."""
    recommendations = []
    
    # Check for low-performing assignments
    for assignment in assignments:
        avg_score = assignment.average_score
        if avg_score < (assignment.total_marks * 0.6):  # Less than 60%
            recommendations.append({
                'type': 'assignment_review',
                'message': f"Assignment '{assignment.title}' had low average score ({avg_score}/{assignment.total_marks}). Consider reviewing the material or adjusting the difficulty.",
                'action': 'review_assignment_difficulty'
            })
    
    # Check for students needing attention
    low_performers = [s for s in student_performance if s['average_score'] < 50]
    if low_performers:
        recommendations.append({
            'type': 'student_support',
            'message': f"{len(low_performers)} student(s) are performing below 50% average. Consider providing additional support.",
            'action': 'provide_extra_help',
            'students': [s['full_name'] for s in low_performers[:3]]  # Top 3 lowest performers
        })
    
    # Check completion rates
    completion_rates = [a.completion_rate for a in assignments]
    avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    if avg_completion < 70:
        recommendations.append({
            'type': 'completion_rate',
            'message': f"Class completion rate is {avg_completion:.1f}%. Consider sending reminders or adjusting assignment deadlines.",
            'action': 'send_reminders'
        })
    
    return recommendations

# Add these functions to views.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assignment_comment(request, assignment_id):
    """
    Create a comment on an assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        data = {
            'assignment': assignment.id,
            'author': request.user.id,
            'content': request.data.get('content'),
            'is_private': request.data.get('is_private', False)
        }
        
        serializer = AssignmentCommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        return Response(
            {'error': 'Failed to create comment.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def create_assignment_reminder(request, assignment_id):
    """
    Create a reminder for an assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if assignment.teacher != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only create reminders for your own assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = {
            'assignment': assignment.id,
            'reminder_type': request.data.get('reminder_type', 'general'),
            'reminder_date': request.data.get('reminder_date'),
            'message': request.data.get('message'),
            'created_by': request.user.id
        }
        
        serializer = AssignmentReminderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        reminder = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating reminder: {str(e)}")
        return Response(
            {'error': 'Failed to create reminder.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assignment_groups(request, assignment_id):
    """
    Get all groups for an assignment.
    """
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check permissions
        if request.user.role == 'student':
            # Students can only see groups they're in
            groups = AssignmentGroup.objects.filter(
                assignment=assignment,
                members=request.user
            )
        elif request.user.role == 'teacher':
            # Teachers can see all groups for their assignments
            if assignment.teacher != request.user:
                return Response(
                    {'error': 'You can only view groups for your own assignments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            groups = AssignmentGroup.objects.filter(assignment=assignment)
        else:
            groups = AssignmentGroup.objects.filter(assignment=assignment)
        
        serializer = AssignmentGroupSerializer(groups, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error retrieving groups: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve groups.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_assignment_group(request, group_id):
    """
    Join an assignment group.
    """
    try:
        group = get_object_or_404(AssignmentGroup, id=group_id)
        
        # Check if user is a student
        if request.user.role != 'student':
            return Response(
                {'error': 'Only students can join groups.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if group is full
        if group.members.count() >= group.assignment.max_group_size:
            return Response(
                {'error': 'Group is full.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add user to group
        group.members.add(request.user)
        group.save()
        
        serializer = AssignmentGroupSerializer(group)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error joining group: {str(e)}")
        return Response(
            {'error': 'Failed to join group.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_assignment_group(request, group_id):
    """
    Leave an assignment group.
    """
    try:
        group = get_object_or_404(AssignmentGroup, id=group_id)
        
        # Check if user is a member
        if not group.members.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the leader
        if group.leader == request.user:
            return Response(
                {'error': 'Leader cannot leave group. Transfer leadership first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove user from group
        group.members.remove(request.user)
        group.save()
        
        serializer = AssignmentGroupSerializer(group)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error leaving group: {str(e)}")
        return Response(
            {'error': 'Failed to leave group.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_group_leadership(request, group_id):
    """
    Transfer leadership of a group.
    """
    try:
        group = get_object_or_404(AssignmentGroup, id=group_id)
        
        # Check if user is the current leader
        if group.leader != request.user:
            return Response(
                {'error': 'Only the current leader can transfer leadership.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_leader_id = request.data.get('new_leader_id')
        if not new_leader_id:
            return Response(
                {'error': 'new_leader_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new leader is a member
        new_leader = get_object_or_404(User, id=new_leader_id)
        if not group.members.filter(id=new_leader_id).exists():
            return Response(
                {'error': 'New leader must be a member of the group.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Transfer leadership
        group.leader = new_leader
        group.save()
        
        serializer = AssignmentGroupSerializer(group)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error transferring leadership: {str(e)}")
        return Response(
            {'error': 'Failed to transfer leadership.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# assignments/views.py - Add this function

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_create_assignment(request):
    """
    Debug endpoint to test assignment creation.
    """
    print("\n=== DEBUG CREATE ASSIGNMENT ===")
    print("Request method:", request.method)
    print("Request path:", request.path)
    print("Request user:", request.user.id, request.user.email)
    print("User role:", getattr(request.user, 'role', 'None'))
    print("User is teacher:", request.user.role == 'teacher' if hasattr(request.user, 'role') else False)
    print("Is authenticated:", request.user.is_authenticated)
    print("Request data:", request.data)
    
    # Check if user is teacher
    if not (request.user.role == 'teacher' or request.user.is_staff):
        return Response({
            'error': 'Only teachers can create assignments',
            'user_role': getattr(request.user, 'role', 'None')
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Return success response
    return Response({
        'message': 'Debug endpoint working!',
        'user': {
            'id': str(request.user.id),
            'email': request.user.email,
            'role': request.user.role
        },
        'data_received': request.data,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)


# assignments/views.py - Add this at the top
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.urls import get_resolver

class DebugURLsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Debug all registered URLs"""
        resolver = get_resolver()
        url_patterns = []
        
        def extract_urls(patterns, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    # It's an include
                    extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                else:
                    # It's a pattern
                    url_patterns.append({
                        'pattern': prefix + str(pattern.pattern),
                        'callback': str(pattern.callback),
                        'name': pattern.name,
                    })
        
        extract_urls(resolver.url_patterns)
        
        # Filter for assignments URLs
        assignment_urls = [url for url in url_patterns if 'assignment' in url['pattern'].lower()]
        
        return Response({
            'all_urls': url_patterns,
            'assignment_urls': assignment_urls,
            'router_urls': [
                {'pattern': str(url.pattern), 'name': url.name}
                for url in router.urls
            ] if 'router' in locals() else []
        })