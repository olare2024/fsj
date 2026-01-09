"""
Views for student models and enrollment management.
"""

import json
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import (
    Q, Count, Avg, Sum, F, Value, Case, When, Max, Min, FloatField
)
from django.db.models.functions import Coalesce, Concat, TruncMonth, ExtractYear
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import (
    viewsets, generics, status, filters, mixins
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser, AllowAny, BasePermission
)
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from accounts.permissions import IsStudent, IsParent, IsTeacher, IsAdmin

from .models import (
    StudentProfile, StudentEnrollment,
    STUDENT_STATUS, ENROLLMENT_STATUS, TRANSPORT_CHOICES, GENDER_CHOICES, BLOOD_GROUP_CHOICES
)
from .serializers import (
    StudentProfileCreateSerializer, StudentProfileUpdateSerializer,
    StudentProfileListSerializer, StudentProfileDetailSerializer,
    StudentProfileSimpleSerializer,
    StudentEnrollmentCreateSerializer, StudentEnrollmentUpdateSerializer,
    StudentEnrollmentListSerializer, StudentEnrollmentDetailSerializer,
    StudentEnrollmentBulkCreateSerializer,
    StudentAcademicUpdateSerializer, StudentBehavioralUpdateSerializer,
    StudentHealthUpdateSerializer, StudentExtracurricularUpdateSerializer,
    StudentFeeUpdateSerializer,
    StudentBulkUpdateSerializer, StudentPromotionSerializer,
    StudentImportSerializer, StudentSearchSerializer,
    StudentStatisticsSerializer, StudentReportSerializer
)

logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM PERMISSIONS
# ============================================================================

class CanManageStudents(BasePermission):
    """
    Custom permission to allow only admin, teachers, and parents to manage students.
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if user.role in [User.Role.ADMIN, User.Role.HEAD_TEACHER, User.Role.TEACHER]:
            return True
        
        # Parents can only view/update their own children
        if user.role == User.Role.PARENT and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role in [User.Role.ADMIN, User.Role.HEAD_TEACHER, User.Role.TEACHER]:
            return True
        
        if user.role == User.Role.PARENT:
            # Check if this student is a child of the parent
            return obj.user.parent_set.filter(user=user).exists()
        
        if user.role == User.Role.STUDENT:
            return obj.user == user
        
        return False


class CanManageEnrollments(BasePermission):
    """
    Custom permission for enrollment management.
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if user.role in [User.Role.ADMIN, User.Role.HEAD_TEACHER]:
            return True
        
        if user.role == User.Role.TEACHER and request.method in ['GET', 'POST']:
            return True
        
        return False


# ============================================================================
# CUSTOM PAGINATION
# ============================================================================

class StudentResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


# ============================================================================
# FILTERSETS
# ============================================================================

class StudentProfileFilter(django_filters.FilterSet):
    """Filter for StudentProfile"""
    
    admission_number = django_filters.CharFilter(lookup_expr='icontains')
    full_name = django_filters.CharFilter(method='filter_full_name')
    gender = django_filters.ChoiceFilter(
        field_name='user__gender', choices=GENDER_CHOICES
    )
    blood_group = django_filters.ChoiceFilter(
        field_name='user__blood_group', choices=BLOOD_GROUP_CHOICES
    )
    cbc_pathway = django_filters.CharFilter(lookup_expr='icontains')
    student_status = django_filters.ChoiceFilter(choices=STUDENT_STATUS)
    fee_status = django_filters.CharFilter(lookup_expr='icontains')
    transport_mode = django_filters.ChoiceFilter(choices=TRANSPORT_CHOICES)
    current_class = django_filters.NumberFilter()
    current_academic_year = django_filters.NumberFilter()
    created_at_gte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte'
    )
    created_at_lte = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte'
    )
    gpa_gte = django_filters.NumberFilter(field_name='gpa', lookup_expr='gte')
    gpa_lte = django_filters.NumberFilter(field_name='gpa', lookup_expr='lte')
    attendance_gte = django_filters.NumberFilter(
        field_name='attendance_percentage', lookup_expr='gte'
    )
    attendance_lte = django_filters.NumberFilter(
        field_name='attendance_percentage', lookup_expr='lte'
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'admission_number', 'gender', 'student_status', 'cbc_pathway',
            'fee_status', 'transport_mode', 'current_class', 'current_academic_year',
            'is_active'
        ]
    
    def filter_full_name(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        )


class StudentEnrollmentFilter(django_filters.FilterSet):
    """Filter for StudentEnrollment"""
    
    student_name = django_filters.CharFilter(method='filter_student_name')
    class_name = django_filters.CharFilter(
        field_name='class_enrolled__display_name', lookup_expr='icontains'
    )
    academic_year_name = django_filters.CharFilter(
        field_name='academic_year__name', lookup_expr='icontains'
    )
    enrollment_date_gte = django_filters.DateFilter(
        field_name='enrollment_date', lookup_expr='gte'
    )
    enrollment_date_lte = django_filters.DateFilter(
        field_name='enrollment_date', lookup_expr='lte'
    )
    status = django_filters.ChoiceFilter(choices=ENROLLMENT_STATUS)
    house = django_filters.CharFilter(lookup_expr='icontains')
    cbc_pathway_selection = django_filters.CharFilter(lookup_expr='icontains')
    fee_status = django_filters.CharFilter(lookup_expr='icontains')
    is_current = django_filters.BooleanFilter(method='filter_is_current')
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'student_profile', 'class_enrolled', 'academic_year', 'status',
            'house', 'cbc_pathway_selection', 'senior_track_selection',
            'fee_status', 'is_active'
        ]
    
    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student_profile__user__first_name__icontains=value) |
            Q(student_profile__user__last_name__icontains=value)
        )
    
    def filter_is_current(self, queryset, name, value):
        if value:
            return queryset.filter(
                status='active',
                academic_year__is_current=True
            )
        return queryset


# ============================================================================
# VIEWSETS
# ============================================================================

class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing StudentProfile objects.
    """
    
    queryset = StudentProfile.objects.all().select_related(
        'user', 'current_class', 'current_academic_year'
    ).prefetch_related('friends')
    
    permission_classes = [IsAuthenticated, CanManageStudents]
    pagination_class = StudentResultsSetPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_class = StudentProfileFilter
    search_fields = [
        'admission_number',
        'upi_number',
        'nemis_number',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]
    ordering_fields = [
        'admission_number',
        'user__first_name',
        'user__last_name',
        'gpa',
        'attendance_percentage',
        'created_at',
        'updated_at',
    ]
    ordering = ['admission_number']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        action_serializers = {
            'create': StudentProfileCreateSerializer,
            'update': StudentProfileUpdateSerializer,
            'partial_update': StudentProfileUpdateSerializer,
            'list': StudentProfileListSerializer,
            'retrieve': StudentProfileDetailSerializer,
        }
        return action_serializers.get(
            self.action, StudentProfileDetailSerializer
        )
    
    def get_queryset(self):
        """Filter queryset based on user role and permissions."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role in [User.Role.ADMIN, User.Role.HEAD_TEACHER]:
            return queryset
        
        elif user.role == User.Role.TEACHER:
            from academics.models import Class
            taught_classes = Class.objects.filter(
                Q(class_teacher=user) | Q(subject_teachers=user)
            ).distinct()
            
            student_ids = queryset.filter(
                current_class__in=taught_classes
            ).values_list('id', flat=True)
            
            return queryset.filter(id__in=student_ids)
        
        elif user.role == User.Role.PARENT:
            children = User.objects.filter(
                parent_set__user=user
            ).values_list('id', flat=True)
            
            return queryset.filter(user_id__in=children)
        
        elif user.role == User.Role.STUDENT:
            return queryset.filter(user=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Set created_by user."""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by user."""
        serializer.save(updated_by=self.request.user)
    
    # ====================
    # CUSTOM ACTIONS
    # ====================
    
    @action(detail=True, methods=['GET'])
    def enrollments(self, request, pk=None):
        """Get all enrollments for a student."""
        student = self.get_object()
        enrollments = student.enrollments.all().order_by(
            '-academic_year__start_date'
        )
        
        paginator = StudentResultsSetPagination()
        page = paginator.paginate_queryset(enrollments, request)
        
        if page is not None:
            serializer = StudentEnrollmentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = StudentEnrollmentListSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def academic_info(self, request, pk=None):
        """Get academic information."""
        student = self.get_object()
        return Response(student.academic_info)
    
    @action(detail=True, methods=['GET'])
    def contact_info(self, request, pk=None):
        """Get contact information."""
        student = self.get_object()
        return Response(student.contact_info)
    
    @action(detail=True, methods=['GET'])
    def parent_info(self, request, pk=None):
        """Get parent information."""
        student = self.get_object()
        return Response(student.parent_info)
    
    @action(detail=True, methods=['GET'])
    def medical_info(self, request, pk=None):
        """Get medical information."""
        student = self.get_object()
        return Response(student.medical_info)
    
    @action(detail=True, methods=['GET'])
    def generate_report(self, request, pk=None):
        """Generate comprehensive student report."""
        student = self.get_object()
        report = student.generate_student_report()
        return Response(report)
    
    @action(detail=True, methods=['POST'])
    def update_academic(self, request, pk=None):
        """Update academic information only."""
        student = self.get_object()
        serializer = StudentAcademicUpdateSerializer(
            student, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def update_behavioral(self, request, pk=None):
        """Update behavioral information only."""
        student = self.get_object()
        serializer = StudentBehavioralUpdateSerializer(
            student, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def update_health(self, request, pk=None):
        """Update health information only."""
        student = self.get_object()
        serializer = StudentHealthUpdateSerializer(
            student, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def update_extracurricular(self, request, pk=None):
        """Update extracurricular information only."""
        student = self.get_object()
        serializer = StudentExtracurricularUpdateSerializer(
            student, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def update_fee_info(self, request, pk=None):
        """Update fee information only."""
        student = self.get_object()
        serializer = StudentFeeUpdateSerializer(
            student, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def add_community_service(self, request, pk=None):
        """Add community service hours."""
        student = self.get_object()
        hours = request.data.get('hours', 0)
        activity_description = request.data.get('activity_description')
        verified_by = request.user
        
        if hours <= 0:
            return Response(
                {'error': 'Hours must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = student.add_community_service_hours(
            hours, activity_description, verified_by
        )
        
        if success:
            return Response({
                'message': f'Added {hours} community service hours',
                'total_hours': student.community_service_hours_completed
            })
        
        return Response(
            {'error': 'Failed to add community service hours'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def add_test_score(self, request, pk=None):
        """Add a test score."""
        student = self.get_object()
        
        required_fields = [
            'test_name', 'subject', 'score', 'max_score', 'date_taken'
        ]
        missing_fields = [
            field for field in required_fields 
            if not request.data.get(field)
        ]
        
        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            score = float(request.data['score'])
            max_score = float(request.data['max_score'])
            date_taken = datetime.strptime(
                request.data['date_taken'], '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid data format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = student.add_test_score(
            request.data['test_name'],
            request.data['subject'],
            score,
            max_score,
            date_taken
        )
        
        if success:
            return Response({
                'message': f'Test score added for {request.data["test_name"]}',
                'percentage': (score / max_score) * 100
            })
        
        return Response(
            {'error': 'Failed to add test score'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def promote(self, request, pk=None):
        """Promote student to next class."""
        student = self.get_object()
        next_academic_year_id = request.data.get('next_academic_year')
        
        if not next_academic_year_id:
            return Response(
                {'error': 'next_academic_year is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from academics.models import AcademicYear
            next_academic_year = AcademicYear.objects.get(
                id=next_academic_year_id
            )
        except AcademicYear.DoesNotExist:
            return Response(
                {'error': 'Academic year not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_enrollment = student.promote_to_next_class(next_academic_year)
        
        if new_enrollment:
            return Response({
                'message': 'Student promoted successfully',
                'new_class': str(new_enrollment.class_enrolled),
                'new_academic_year': str(new_enrollment.academic_year)
            })
        
        return Response(
            {'error': 'Failed to promote student'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['POST'])
    def bulk_update(self, request):
        """Bulk update students."""
        serializer = StudentBulkUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            student_ids = serializer.validated_data['student_ids']
            update_fields = serializer.validated_data['update_fields']
            
            updated_count = StudentProfile.objects.filter(
                id__in=student_ids
            ).update(**update_fields)
            
            return Response({
                'message': f'Updated {updated_count} student(s)',
                'updated_count': updated_count
            })
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['POST'])
    def import_students(self, request):
        """Import students from file."""
        serializer = StudentImportSerializer(data=request.data)
        
        if serializer.is_valid():
            # TODO: Implement file parsing and import logic
            return Response({
                'message': 'Import functionality to be implemented',
                'data': serializer.validated_data
            })
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing StudentEnrollment objects.
    """
    
    queryset = StudentEnrollment.objects.all().select_related(
        'student_profile', 'student_profile__user',
        'class_enrolled', 'academic_year'
    )
    
    permission_classes = [IsAuthenticated, CanManageEnrollments]
    pagination_class = StudentResultsSetPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_class = StudentEnrollmentFilter
    search_fields = [
        'enrollment_number',
        'student_profile__admission_number',
        'student_profile__user__first_name',
        'student_profile__user__last_name',
        'student_profile__user__email',
    ]
    ordering_fields = [
        'enrollment_number',
        'enrollment_date',
        'roll_number',
        'created_at',
        'updated_at',
    ]
    ordering = ['-enrollment_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        action_serializers = {
            'create': StudentEnrollmentCreateSerializer,
            'update': StudentEnrollmentUpdateSerializer,
            'partial_update': StudentEnrollmentUpdateSerializer,
            'list': StudentEnrollmentListSerializer,
            'retrieve': StudentEnrollmentDetailSerializer,
        }
        return action_serializers.get(
            self.action, StudentEnrollmentDetailSerializer
        )
    
    def get_queryset(self):
        """Filter queryset based on user role and permissions."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role in [User.Role.ADMIN, User.Role.HEAD_TEACHER]:
            return queryset
        
        elif user.role == User.Role.TEACHER:
            from academics.models import Class
            taught_classes = Class.objects.filter(
                Q(class_teacher=user) | Q(subject_teachers=user)
            ).distinct()
            
            return queryset.filter(class_enrolled__in=taught_classes)
        
        elif user.role == User.Role.PARENT:
            children = User.objects.filter(
                parent_set__user=user
            ).values_list('id', flat=True)
            
            return queryset.filter(student_profile__user_id__in=children)
        
        elif user.role == User.Role.STUDENT:
            return queryset.filter(student_profile__user=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Set created_by user."""
        serializer.save()
    
    def perform_update(self, serializer):
        """Set updated_by user."""
        serializer.save()
    
    # ====================
    # CUSTOM ACTIONS
    # ====================
    
    @action(detail=False, methods=['POST'])
    def bulk_create(self, request):
        """Bulk create enrollments."""
        serializer = StudentEnrollmentBulkCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            enrollments = serializer.save()
            
            return Response({
                'message': f'Created {len(enrollments)} enrollment(s)',
                'enrollments': StudentEnrollmentListSerializer(
                    enrollments, many=True
                ).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        """Update enrollment status."""
        enrollment = self.get_object()
        
        new_status = request.data.get('status')
        reason = request.data.get('reason')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in ENROLLMENT_STATUS]
        if new_status not in valid_statuses:
            return Response(
                {
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = new_status
        enrollment.status_reason = reason
        enrollment.status_changed_date = timezone.now().date()
        enrollment.save()
        
        # Update student profile status if needed
        if new_status in ['transferred', 'graduated', 'withdrawn', 'suspended']:
            enrollment.student_profile.student_status = new_status
            enrollment.student_profile.save()
        
        return Response({
            'message': f'Enrollment status updated to {new_status}',
            'enrollment': StudentEnrollmentDetailSerializer(enrollment).data
        })
    
    @action(detail=False, methods=['GET'])
    def current_enrollments(self, request):
        """Get current academic year enrollments."""
        try:
            from academics.models import AcademicYear
            current_year = AcademicYear.objects.get(is_current=True)
            
            enrollments = self.get_queryset().filter(
                academic_year=current_year,
                status='active'
            )
            
            paginator = StudentResultsSetPagination()
            page = paginator.paginate_queryset(enrollments, request)
            
            if page is not None:
                serializer = StudentEnrollmentListSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = StudentEnrollmentListSerializer(enrollments, many=True)
            return Response(serializer.data)
        
        except AcademicYear.DoesNotExist:
            return Response(
                {'error': 'No current academic year found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['GET'])
    def by_class(self, request):
        """Get enrollments by class."""
        class_id = request.query_params.get('class_id')
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollments = self.get_queryset().filter(class_enrolled_id=class_id)
        
        academic_year_id = request.query_params.get('academic_year_id')
        if academic_year_id:
            enrollments = enrollments.filter(academic_year_id=academic_year_id)
        
        enrollments = enrollments.order_by('roll_number')
        
        paginator = StudentResultsSetPagination()
        page = paginator.paginate_queryset(enrollments, request)
        
        if page is not None:
            serializer = StudentEnrollmentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = StudentEnrollmentListSerializer(enrollments, many=True)
        return Response(serializer.data)


# ============================================================================
# API VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """
    Get student dashboard data.
    """
    user = request.user
    
    if user.role != User.Role.STUDENT:
        return Response(
            {'error': 'Only students can access this dashboard'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = StudentProfile.objects.get(user=user)
        
        current_enrollment = profile.enrollments.filter(
            status='active',
            academic_year__is_current=True
        ).first()
        
        dashboard_data = {
            'student': {
                'full_name': profile.full_name,
                'admission_number': profile.admission_number,
                'email': user.email,
                'phone_number': user.phone_number,
                'gender': user.get_gender_display(),
                'date_of_birth': user.date_of_birth,
                'age': profile.age,
            },
            'academic': {
                'current_class': str(profile.current_class) if profile.current_class else None,
                'current_academic_year': str(profile.current_academic_year) if profile.current_academic_year else None,
                'gpa': float(profile.gpa),
                'overall_grade': profile.overall_grade,
                'attendance_percentage': float(profile.attendance_percentage),
                'rank_in_class': profile.rank_in_class,
            },
            'cbc_info': {},
            'attendance_summary': {},
            'fee_summary': {},
            'recent_grades': [],
            'upcoming_events': [],
            'todays_schedule': [],
            'recent_announcements': [],
        }
        
        if profile.is_cbc_student:
            dashboard_data['cbc_info'] = {
                'pathway': profile.get_cbc_pathway_display(),
                'portfolio_status': profile.get_portfolio_status_display(),
                'community_service_hours': profile.community_service_hours_completed,
            }
        
        # Get attendance data
        try:
            from attendance.models import Attendance
            today = timezone.now().date()
            attendance_data = Attendance.objects.filter(
                student=user,
                date__month=today.month,
                date__year=today.year
            )
            
            present_count = attendance_data.filter(status='present').count()
            absent_count = attendance_data.filter(status='absent').count()
            late_count = attendance_data.filter(status='late').count()
            total_days = present_count + absent_count + late_count
            
            dashboard_data['attendance_summary'] = {
                'present': present_count,
                'absent': absent_count,
                'late': late_count,
                'percentage': (present_count / total_days * 100) if total_days > 0 else 0,
                'total_days': total_days,
            }
        except ImportError:
            pass
        
        # Get fee data
        try:
            from finance.models import StudentFee
            current_year_fees = StudentFee.objects.filter(
                student=user,
                academic_year__is_current=True
            ).aggregate(
                total_fees=Sum('amount'),
                paid=Sum('paid_amount'),
                balance=Sum('balance')
            )
            
            dashboard_data['fee_summary'] = {
                'total_fees': current_year_fees['total_fees'] or 0,
                'paid': current_year_fees['paid'] or 0,
                'balance': current_year_fees['balance'] or 0,
            }
        except ImportError:
            pass
        
        # Get recent grades
        try:
            from grading.models import Grade
            recent_grades = Grade.objects.filter(
                student=user
            ).select_related('subject').order_by('-date_graded')[:10]
            
            grades_list = []
            for grade in recent_grades:
                grades_list.append({
                    'subject': grade.subject.name if grade.subject else 'N/A',
                    'score': grade.score,
                    'grade': grade.grade,
                    'date': grade.date_graded,
                })
            
            dashboard_data['recent_grades'] = grades_list
        except ImportError:
            pass
        
        # Get upcoming events
        try:
            from events.models import Event
            upcoming_events = Event.objects.filter(
                is_active=True,
                start_date__gte=timezone.now().date()
            ).order_by('start_date')[:5]
            
            events_list = []
            for event in upcoming_events:
                events_list.append({
                    'title': event.title,
                    'description': event.description,
                    'start_date': event.start_date,
                    'end_date': event.end_date,
                    'venue': event.venue,
                })
            
            dashboard_data['upcoming_events'] = events_list
        except ImportError:
            pass
        
        # Get today's schedule
        try:
            from academics.models import Timetable
            today = timezone.now().date()
            todays_schedule = Timetable.objects.filter(
                class_name=profile.current_class,
                day_of_week=today.weekday()
            ).order_by('start_time')
            
            schedule_list = []
            for period in todays_schedule:
                schedule_list.append({
                    'subject': period.subject.name if period.subject else 'Free',
                    'teacher': period.teacher.get_full_name() if period.teacher else 'N/A',
                    'start_time': period.start_time,
                    'end_time': period.end_time,
                    'room': period.room,
                })
            
            dashboard_data['todays_schedule'] = schedule_list
        except ImportError:
            pass
        
        # Get recent announcements
        try:
            from announcements.models import Announcement
            recent_announcements = Announcement.objects.filter(
                is_active=True,
                target_groups__contains=['students']
            ).order_by('-created_at')[:5]
            
            announcements_list = []
            for announcement in recent_announcements:
                content = announcement.content
                if len(content) > 100:
                    content = content[:100] + '...'
                
                announcements_list.append({
                    'title': announcement.title,
                    'content': content,
                    'created_at': announcement.created_at,
                    'priority': announcement.priority,
                })
            
            dashboard_data['recent_announcements'] = announcements_list
        except ImportError:
            pass
        
        return Response(dashboard_data)
    
    except StudentProfile.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting student dashboard: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_students(request):
    """
    Search for students.
    """
    serializer = StudentSearchSerializer(data=request.query_params)
    
    if serializer.is_valid():
        search_params = serializer.validated_data
        queryset = StudentProfile.objects.all().select_related('user')
        
        # Apply filters
        if search_params.get('query'):
            query = search_params['query']
            queryset = queryset.filter(
                Q(admission_number__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(upi_number__icontains=query) |
                Q(nemis_number__icontains=query)
            )
        
        if search_params.get('admission_number'):
            queryset = queryset.filter(
                admission_number__icontains=search_params['admission_number']
            )
        
        if search_params.get('name'):
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_params['name']) |
                Q(user__last_name__icontains=search_params['name'])
            )
        
        if search_params.get('class_id'):
            queryset = queryset.filter(current_class_id=search_params['class_id'])
        
        if search_params.get('academic_year_id'):
            queryset = queryset.filter(
                current_academic_year_id=search_params['academic_year_id']
            )
        
        if search_params.get('status'):
            queryset = queryset.filter(student_status=search_params['status'])
        
        if search_params.get('gender'):
            queryset = queryset.filter(user__gender=search_params['gender'])
        
        if search_params.get('cbc_pathway'):
            queryset = queryset.filter(cbc_pathway=search_params['cbc_pathway'])
        
        if search_params.get('fee_status'):
            queryset = queryset.filter(fee_status=search_params['fee_status'])
        
        # Apply ordering
        order_by = search_params.get('order_by', 'admission_number')
        order_direction = search_params.get('order_direction', 'asc')
        
        if order_direction == 'desc':
            order_by = f'-{order_by}'
        
        queryset = queryset.order_by(order_by)
        
        # Pagination
        page = search_params.get('page', 1)
        page_size = search_params.get('page_size', 20)
        
        paginator = StudentResultsSetPagination()
        paginator.page_size = page_size
        
        page_obj = paginator.paginate_queryset(queryset, request)
        
        if page_obj is not None:
            serializer = StudentProfileListSerializer(page_obj, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = StudentProfileListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def student_statistics(request):
    """
    Get student statistics.
    """
    try:
        total_students = StudentProfile.objects.filter(is_active=True).count()
        active_students = StudentProfile.objects.filter(
            is_active=True,
            student_status='active'
        ).count()
        
        # Gender distribution
        gender_stats = StudentProfile.objects.filter(
            is_active=True
        ).values('user__gender').annotate(count=Count('id'))
        
        gender_distribution = {}
        for stat in gender_stats:
            gender_display = dict(GENDER_CHOICES).get(
                stat['user__gender'], stat['user__gender']
            )
            gender_distribution[gender_display] = stat['count']
        
        # Status distribution
        status_stats = StudentProfile.objects.filter(
            is_active=True
        ).values('student_status').annotate(count=Count('id'))
        
        status_distribution = {}
        for stat in status_stats:
            status_display = dict(STUDENT_STATUS).get(
                stat['student_status'], stat['student_status']
            )
            status_distribution[status_display] = stat['count']
        
        # Class distribution
        class_stats = StudentProfile.objects.filter(
            is_active=True,
            current_class__isnull=False
        ).values('current_class__display_name').annotate(
            count=Count('id')
        ).order_by('current_class__display_name')
        
        class_distribution = {}
        for stat in class_stats:
            class_name = stat['current_class__display_name'] or 'Not Assigned'
            class_distribution[class_name] = stat['count']
        
        # CBC pathway distribution
        cbc_stats = StudentProfile.objects.filter(
            is_active=True,
            cbc_pathway__isnull=False
        ).values('cbc_pathway').annotate(count=Count('id'))
        
        cbc_pathway_distribution = {}
        for stat in cbc_stats:
            pathway_display = dict(
                StudentProfile._meta.get_field('cbc_pathway').choices
            ).get(stat['cbc_pathway'], stat['cbc_pathway'])
            cbc_pathway_distribution[pathway_display] = stat['count']
        
        # Academic performance averages
        academic_stats = StudentProfile.objects.filter(
            is_active=True
        ).aggregate(
            avg_gpa=Avg('gpa'),
            avg_attendance=Avg('attendance_percentage'),
            max_gpa=Max('gpa'),
            min_gpa=Min('gpa')
        )
        
        # Fee status distribution
        fee_stats = StudentProfile.objects.filter(
            is_active=True
        ).values('fee_status').annotate(count=Count('id'))
        
        fee_distribution = {}
        for stat in fee_stats:
            fee_display = dict(
                StudentProfile._meta.get_field('fee_status').choices
            ).get(stat['fee_status'], stat['fee_status'])
            fee_distribution[fee_display] = stat['count']
        
        # Transport mode distribution
        transport_stats = StudentProfile.objects.filter(
            is_active=True
        ).values('transport_mode').annotate(count=Count('id'))
        
        transport_distribution = {}
        for stat in transport_stats:
            transport_display = dict(TRANSPORT_CHOICES).get(
                stat['transport_mode'], stat['transport_mode']
            )
            transport_distribution[transport_display] = stat['count']
        
        # Monthly enrollment trend (current year)
        current_year = timezone.now().year
        enrollment_trend = StudentProfile.objects.filter(
            created_at__year=current_year
        ).annotate(month=TruncMonth('created_at')).values(
            'month'
        ).annotate(count=Count('id')).order_by('month')
        
        # Recent enrollments (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_enrollments = StudentProfile.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        statistics = {
            'total_students': total_students,
            'active_students': active_students,
            'recent_enrollments': recent_enrollments,
            'gender_distribution': gender_distribution,
            'status_distribution': status_distribution,
            'class_distribution': class_distribution,
            'cbc_pathway_distribution': cbc_pathway_distribution,
            'fee_distribution': fee_distribution,
            'transport_distribution': transport_distribution,
            'academic_performance': {
                'average_gpa': round(academic_stats['avg_gpa'] or 0, 2),
                'average_attendance': round(academic_stats['avg_attendance'] or 0, 2),
                'highest_gpa': round(academic_stats['max_gpa'] or 0, 2),
                'lowest_gpa': round(academic_stats['min_gpa'] or 0, 2),
            },
            'enrollment_trend': [
                {
                    'month': trend['month'].strftime('%Y-%m'),
                    'count': trend['count']
                }
                for trend in enrollment_trend
            ],
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(statistics)
    
    except Exception as e:
        logger.error(f"Error getting student statistics: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_promote_students(request):
    """
    Bulk promote students to next class.
    """
    serializer = StudentPromotionSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        next_academic_year = data['next_academic_year']
        promote_all = data.get('promote_all', False)
        student_ids = data.get('student_ids', [])
        next_class = data.get('next_class')
        
        if promote_all:
            students = StudentProfile.objects.filter(
                is_active=True,
                student_status='active'
            )
        else:
            students = StudentProfile.objects.filter(
                id__in=student_ids,
                is_active=True,
                student_status='active'
            )
        
        promoted_count = 0
        failed_promotions = []
        
        for student in students:
            try:
                if next_class:
                    enrollment = StudentEnrollment.objects.create(
                        student_profile=student,
                        class_enrolled=next_class,
                        academic_year=next_academic_year,
                        enrollment_date=timezone.now().date(),
                        status='active',
                        remarks=f"Promoted to {next_class.display_name}",
                    )
                    
                    student.current_class = next_class
                    student.current_academic_year = next_academic_year
                    student.save()
                else:
                    enrollment = student.promote_to_next_class(next_academic_year)
                
                if enrollment:
                    promoted_count += 1
                else:
                    failed_promotions.append({
                        'student': student.admission_number,
                        'reason': 'Could not determine next class'
                    })
            
            except Exception as e:
                failed_promotions.append({
                    'student': student.admission_number,
                    'reason': str(e)
                })
        
        return Response({
            'message': f'Successfully promoted {promoted_count} student(s)',
            'promoted_count': promoted_count,
            'failed_promotions': failed_promotions,
            'total_attempted': len(students)
        })
    
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_student_report(request):
    """
    Generate student report with various filters.
    """
    serializer = StudentReportSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        queryset = StudentProfile.objects.all().select_related(
            'user', 'current_class', 'current_academic_year'
        )
        
        # Apply filters
        if data.get('start_date'):
            queryset = queryset.filter(created_at__gte=data['start_date'])
        
        if data.get('end_date'):
            queryset = queryset.filter(created_at__lte=data['end_date'])
        
        if data.get('class_filter'):
            queryset = queryset.filter(current_class=data['class_filter'])
        
        if data.get('status_filter'):
            queryset = queryset.filter(student_status=data['status_filter'])
        
        # Generate report data
        report_data = []
        
        for student in queryset:
            student_report = {
                'admission_number': student.admission_number,
                'full_name': student.full_name,
                'gender': student.user.get_gender_display(),
                'current_class': str(student.current_class) if student.current_class else 'Not Assigned',
                'academic_year': str(student.current_academic_year) if student.current_academic_year else 'Not Assigned',
                'student_status': student.get_student_status_display(),
                'gpa': float(student.gpa),
                'attendance_percentage': float(student.attendance_percentage),
            }
            
            if data.get('include_academic'):
                student_report.update({
                    'overall_grade': student.overall_grade,
                    'rank_in_class': student.rank_in_class,
                    'cbc_pathway': student.get_cbc_pathway_display() if student.cbc_pathway else 'N/A',
                    'portfolio_status': student.get_portfolio_status_display(),
                    'community_service_hours': student.community_service_hours_completed,
                })
            
            if data.get('include_medical'):
                student_report.update({
                    'blood_group': student.user.get_blood_group_display() if student.user.blood_group else 'Not Specified',
                    'allergies': student.allergies,
                    'health_conditions': student.health_conditions,
                })
            
            if data.get('include_financial'):
                student_report.update({
                    'fee_status': student.get_fee_status_display(),
                    'fee_arrears': float(student.fee_arrears),
                })
            
            report_data.append(student_report)
        
        return Response({
            'generated_at': timezone.now().isoformat(),
            'filters_applied': data,
            'total_students': len(report_data),
            'report': report_data
        })
    
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================================
# REPORTING VIEWS
# ============================================================================

class StudentDemographicsReportView(APIView):
    """
    API view for generating student demographics reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get all active students
            students = StudentProfile.objects.filter(is_active=True)
            
            # Gender distribution
            gender_stats = students.values('user__gender').annotate(
                count=Count('id')
            )
            
            gender_distribution = {}
            for stat in gender_stats:
                gender_display = dict(GENDER_CHOICES).get(
                    stat['user__gender'], stat['user__gender']
                )
                gender_distribution[gender_display] = stat['count']
            
            # Age distribution
            age_groups = {
                'Under 5': students.filter(user__date_of_birth__gt=timezone.now() - timedelta(days=5*365)),
                '5-10': students.filter(
                    user__date_of_birth__lte=timezone.now() - timedelta(days=5*365),
                    user__date_of_birth__gt=timezone.now() - timedelta(days=10*365)
                ),
                '11-14': students.filter(
                    user__date_of_birth__lte=timezone.now() - timedelta(days=10*365),
                    user__date_of_birth__gt=timezone.now() - timedelta(days=14*365)
                ),
                '15-18': students.filter(
                    user__date_of_birth__lte=timezone.now() - timedelta(days=14*365),
                    user__date_of_birth__gt=timezone.now() - timedelta(days=18*365)
                ),
                'Over 18': students.filter(user__date_of_birth__lte=timezone.now() - timedelta(days=18*365)),
            }
            
            age_distribution = {}
            for group, queryset in age_groups.items():
                age_distribution[group] = queryset.count()
            
            # Class distribution
            class_stats = students.filter(
                current_class__isnull=False
            ).values('current_class__display_name').annotate(
                count=Count('id')
            ).order_by('current_class__display_name')
            
            class_distribution = {}
            for stat in class_stats:
                class_name = stat['current_class__display_name'] or 'Not Assigned'
                class_distribution[class_name] = stat['count']
            
            # Status distribution
            status_stats = students.values('student_status').annotate(
                count=Count('id')
            )
            
            status_distribution = {}
            for stat in status_stats:
                status_display = dict(STUDENT_STATUS).get(
                    stat['student_status'], stat['student_status']
                )
                status_distribution[status_display] = stat['count']
            
            # CBC pathway distribution
            cbc_stats = students.filter(
                cbc_pathway__isnull=False
            ).values('cbc_pathway').annotate(count=Count('id'))
            
            cbc_pathway_distribution = {}
            for stat in cbc_stats:
                pathway_display = dict(
                    StudentProfile._meta.get_field('cbc_pathway').choices
                ).get(stat['cbc_pathway'], stat['cbc_pathway'])
                cbc_pathway_distribution[pathway_display] = stat['count']
            
            # Transport mode distribution
            transport_stats = students.values('transport_mode').annotate(
                count=Count('id')
            )
            
            transport_distribution = {}
            for stat in transport_stats:
                transport_display = dict(TRANSPORT_CHOICES).get(
                    stat['transport_mode'], stat['transport_mode']
                )
                transport_distribution[transport_display] = stat['count']
            
            # Blood group distribution
            blood_stats = students.values('user__blood_group').annotate(
                count=Count('id')
            )
            
            blood_group_distribution = {}
            for stat in blood_stats:
                blood_display = dict(BLOOD_GROUP_CHOICES).get(
                    stat['user__blood_group'], stat['user__blood_group']
                ) or 'Not Specified'
                blood_group_distribution[blood_display] = stat['count']
            
            # Generate summary statistics
            total_students = students.count()
            average_age = students.annotate(
                age=ExtractYear(timezone.now()) - ExtractYear('user__date_of_birth')
            ).aggregate(avg_age=Avg('age'))['avg_age'] or 0
            
            report = {
                'summary': {
                    'total_students': total_students,
                    'average_age': round(average_age, 1),
                    'report_generated': timezone.now().isoformat(),
                    'academic_year': None,
                },
                'gender_distribution': gender_distribution,
                'age_distribution': age_distribution,
                'class_distribution': class_distribution,
                'status_distribution': status_distribution,
                'cbc_pathway_distribution': cbc_pathway_distribution,
                'transport_distribution': transport_distribution,
                'blood_group_distribution': blood_group_distribution,
            }
            
            # Try to get current academic year
            try:
                from academics.models import AcademicYear
                current_year = AcademicYear.objects.get(is_current=True)
                report['summary']['academic_year'] = str(current_year)
            except ImportError:
                pass
            except AcademicYear.DoesNotExist:
                pass
            
            return Response(report)
            
        except Exception as e:
            logger.error(f"Error generating demographics report: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AcademicPerformanceReportView(APIView):
    """
    API view for generating academic performance reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get filter parameters
            academic_year_id = request.query_params.get('academic_year_id')
            class_id = request.query_params.get('class_id')
            
            # Base queryset
            students = StudentProfile.objects.filter(is_active=True)
            
            # Apply filters
            if academic_year_id:
                students = students.filter(current_academic_year_id=academic_year_id)
            
            if class_id:
                students = students.filter(current_class_id=class_id)
            
            # Overall performance statistics
            overall_stats = students.aggregate(
                avg_gpa=Avg('gpa'),
                max_gpa=Max('gpa'),
                min_gpa=Min('gpa'),
                avg_attendance=Avg('attendance_percentage'),
                total_students=Count('id')
            )
            
            # GPA distribution
            gpa_distribution = {
                'A (4.0-3.7)': students.filter(gpa__gte=3.7).count(),
                'A- (3.69-3.3)': students.filter(gpa__gte=3.3, gpa__lt=3.7).count(),
                'B+ (3.29-3.0)': students.filter(gpa__gte=3.0, gpa__lt=3.3).count(),
                'B (2.99-2.7)': students.filter(gpa__gte=2.7, gpa__lt=3.0).count(),
                'B- (2.69-2.3)': students.filter(gpa__gte=2.3, gpa__lt=2.7).count(),
                'C+ (2.29-2.0)': students.filter(gpa__gte=2.0, gpa__lt=2.3).count(),
                'C (1.99-1.7)': students.filter(gpa__gte=1.7, gpa__lt=2.0).count(),
                'C- (1.69-1.3)': students.filter(gpa__gte=1.3, gpa__lt=1.7).count(),
                'D+ (1.29-1.0)': students.filter(gpa__gte=1.0, gpa__lt=1.3).count(),
                'D (0.99-0.7)': students.filter(gpa__gte=0.7, gpa__lt=1.0).count(),
                'D- (Below 0.7)': students.filter(gpa__lt=0.7).count(),
            }
            
            # Class-wise performance
            class_performance = students.filter(
                current_class__isnull=False
            ).values('current_class__display_name').annotate(
                avg_gpa=Avg('gpa'),
                avg_attendance=Avg('attendance_percentage'),
                student_count=Count('id'),
                top_gpa=Max('gpa'),
                lowest_gpa=Min('gpa')
            ).order_by('current_class__display_name')
            
            # Subject-wise performance (if available)
            subject_performance = []
            try:
                from grading.models import Grade
                if class_id:
                    subject_stats = Grade.objects.filter(
                        student__in=User.objects.filter(
                            studentprofile__current_class_id=class_id
                        )
                    ).values('subject__name').annotate(
                        avg_score=Avg('score'),
                        max_score=Max('score'),
                        min_score=Min('score'),
                        count=Count('id')
                    ).order_by('subject__name')
                    
                    for stat in subject_stats:
                        subject_performance.append({
                            'subject': stat['subject__name'] or 'Unknown',
                            'average_score': round(stat['avg_score'] or 0, 2),
                            'highest_score': stat['max_score'] or 0,
                            'lowest_score': stat['min_score'] or 0,
                            'total_grades': stat['count'],
                        })
            except ImportError:
                pass
            
            # Top performing students
            top_students = students.order_by('-gpa')[:10].values(
                'admission_number',
                'user__first_name',
                'user__last_name',
                'gpa',
                'current_class__display_name'
            )
            
            # Students needing improvement
            improvement_needed = students.filter(gpa__lt=2.0).order_by('gpa')[:10].values(
                'admission_number',
                'user__first_name',
                'user__last_name',
                'gpa',
                'attendance_percentage',
                'current_class__display_name'
            )
            
            # Attendance statistics
            attendance_distribution = {
                'Excellent (90-100%)': students.filter(attendance_percentage__gte=90).count(),
                'Good (80-89%)': students.filter(attendance_percentage__gte=80, attendance_percentage__lt=90).count(),
                'Fair (70-79%)': students.filter(attendance_percentage__gte=70, attendance_percentage__lt=80).count(),
                'Poor (60-69%)': students.filter(attendance_percentage__gte=60, attendance_percentage__lt=70).count(),
                'Very Poor (Below 60%)': students.filter(attendance_percentage__lt=60).count(),
            }
            
            report = {
                'summary': {
                    'total_students': overall_stats['total_students'] or 0,
                    'average_gpa': round(overall_stats['avg_gpa'] or 0, 2),
                    'highest_gpa': round(overall_stats['max_gpa'] or 0, 2),
                    'lowest_gpa': round(overall_stats['min_gpa'] or 0, 2),
                    'average_attendance': round(overall_stats['avg_attendance'] or 0, 2),
                    'report_date': timezone.now().isoformat(),
                },
                'gpa_distribution': gpa_distribution,
                'attendance_distribution': attendance_distribution,
                'class_performance': list(class_performance),
                'subject_performance': subject_performance,
                'top_performers': list(top_students),
                'students_needing_improvement': list(improvement_needed),
            }
            
            return Response(report)
            
        except Exception as e:
            logger.error(f"Error generating academic performance report: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AttendanceReportView(APIView):
    """
    API view for generating attendance reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get filter parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            class_id = request.query_params.get('class_id')
            
            # Parse dates if provided
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date = timezone.now().date() - timedelta(days=30)
            
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = timezone.now().date()
            
            report_data = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_days': (end_date - start_date).days + 1,
                },
                'summary': {},
                'daily_attendance': [],
                'class_wise_summary': [],
                'individual_records': [],
                'report_generated': timezone.now().isoformat(),
            }
            
            try:
                from attendance.models import Attendance
                
                # Base queryset
                attendance_qs = Attendance.objects.filter(
                    date__gte=start_date,
                    date__lte=end_date
                )
                
                # Apply class filter if provided
                if class_id:
                    attendance_qs = attendance_qs.filter(
                        student__studentprofile__current_class_id=class_id
                    )
                
                # Overall attendance summary
                total_records = attendance_qs.count()
                present_count = attendance_qs.filter(status='present').count()
                absent_count = attendance_qs.filter(status='absent').count()
                late_count = attendance_qs.filter(status='late').count()
                
                report_data['summary'] = {
                    'total_records': total_records,
                    'present': present_count,
                    'absent': absent_count,
                    'late': late_count,
                    'attendance_rate': round((present_count / total_records * 100), 2) if total_records > 0 else 0,
                    'absentee_rate': round((absent_count / total_records * 100), 2) if total_records > 0 else 0,
                    'late_rate': round((late_count / total_records * 100), 2) if total_records > 0 else 0,
                }
                
                # Daily attendance breakdown
                daily_stats = attendance_qs.values('date').annotate(
                    total=Count('id'),
                    present=Count(Case(When(status='present', then=1))),
                    absent=Count(Case(When(status='absent', then=1))),
                    late=Count(Case(When(status='late', then=1))),
                ).order_by('date')
                
                for day in daily_stats:
                    report_data['daily_attendance'].append({
                        'date': day['date'].isoformat(),
                        'total': day['total'],
                        'present': day['present'],
                        'absent': day['absent'],
                        'late': day['late'],
                        'attendance_rate': round((day['present'] / day['total'] * 100), 2) if day['total'] > 0 else 0,
                    })
                
                # Class-wise attendance summary
                class_stats = attendance_qs.values(
                    'student__studentprofile__current_class__display_name'
                ).annotate(
                    total=Count('id'),
                    present=Count(Case(When(status='present', then=1))),
                    absent=Count(Case(When(status='absent', then=1))),
                    late=Count(Case(When(status='late', then=1))),
                ).order_by('student__studentprofile__current_class__display_name')
                
                for class_stat in class_stats:
                    class_name = class_stat['student__studentprofile__current_class__display_name'] or 'Not Assigned'
                    report_data['class_wise_summary'].append({
                        'class': class_name,
                        'total': class_stat['total'],
                        'present': class_stat['present'],
                        'absent': class_stat['absent'],
                        'late': class_stat['late'],
                        'attendance_rate': round((class_stat['present'] / class_stat['total'] * 100), 2) if class_stat['total'] > 0 else 0,
                    })
                
                # Top absentees
                top_absentees = attendance_qs.filter(status='absent').values(
                    'student__studentprofile__admission_number',
                    'student__first_name',
                    'student__last_name',
                    'student__studentprofile__current_class__display_name'
                ).annotate(
                    absent_count=Count('id'),
                    total_count=Count('student')
                ).order_by('-absent_count')[:10]
                
                report_data['top_absentees'] = list(top_absentees)
                
                # Perfect attendance students
                perfect_attendance = []
                try:
                    # Get students with no absences in the period
                    students_with_absences = attendance_qs.filter(
                        status='absent'
                    ).values_list('student_id', flat=True).distinct()
                    
                    students_with_perfect_attendance = User.objects.filter(
                        attendance_records__date__gte=start_date,
                        attendance_records__date__lte=end_date
                    ).exclude(id__in=students_with_absences).distinct()[:10]
                    
                    for student in students_with_perfect_attendance:
                        perfect_attendance.append({
                            'admission_number': student.studentprofile.admission_number,
                            'full_name': f"{student.first_name} {student.last_name}",
                            'class': str(student.studentprofile.current_class) if student.studentprofile.current_class else 'Not Assigned',
                            'total_days_present': attendance_qs.filter(
                                student=student, status='present'
                            ).count(),
                        })
                    
                    report_data['perfect_attendance_students'] = perfect_attendance
                    
                except Exception as e:
                    logger.warning(f"Could not get perfect attendance data: {str(e)}")
                
            except ImportError:
                report_data['error'] = 'Attendance module not installed or available'
            
            return Response(report_data)
            
        except Exception as e:
            logger.error(f"Error generating attendance report: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FinancialStatusReportView(APIView):
    """
    API view for generating financial status reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get filter parameters
            academic_year_id = request.query_params.get('academic_year_id')
            fee_status = request.query_params.get('fee_status')
            class_id = request.query_params.get('class_id')
            
            report_data = {
                'summary': {},
                'fee_status_distribution': {},
                'class_wise_financials': [],
                'payment_trends': [],
                'arrears_summary': [],
                'report_generated': timezone.now().isoformat(),
            }
            
            try:
                from finance.models import StudentFee, FeePayment
                
                # Base queryset
                fees_qs = StudentFee.objects.all()
                payments_qs = FeePayment.objects.all()
                
                # Apply filters
                if academic_year_id:
                    fees_qs = fees_qs.filter(academic_year_id=academic_year_id)
                    payments_qs = payments_qs.filter(academic_year_id=academic_year_id)
                
                if class_id:
                    fees_qs = fees_qs.filter(student__studentprofile__current_class_id=class_id)
                    payments_qs = payments_qs.filter(student__studentprofile__current_class_id=class_id)
                
                # Overall financial summary
                total_fees = fees_qs.aggregate(
                    total_amount=Sum('amount'),
                    total_paid=Sum('paid_amount'),
                    total_balance=Sum('balance')
                )
                
                report_data['summary'] = {
                    'total_fees': total_fees['total_amount'] or 0,
                    'total_paid': total_fees['total_paid'] or 0,
                    'total_balance': total_fees['total_balance'] or 0,
                    'collection_rate': round((total_fees['total_paid'] / total_fees['total_amount'] * 100), 2) 
                        if total_fees['total_amount'] and total_fees['total_amount'] > 0 else 0,
                    'total_students_with_fees': fees_qs.values('student').distinct().count(),
                }
                
                # Fee status distribution from StudentProfile
                if fee_status:
                    students = StudentProfile.objects.filter(fee_status=fee_status)
                else:
                    students = StudentProfile.objects.all()
                
                if class_id:
                    students = students.filter(current_class_id=class_id)
                
                fee_status_stats = students.values('fee_status').annotate(
                    count=Count('id')
                )
                
                for stat in fee_status_stats:
                    status_display = dict(
                        StudentProfile._meta.get_field('fee_status').choices
                    ).get(stat['fee_status'], stat['fee_status'])
                    report_data['fee_status_distribution'][status_display] = stat['count']
                
                # Class-wise financial summary
                class_financials = fees_qs.values(
                    'student__studentprofile__current_class__display_name'
                ).annotate(
                    total_amount=Sum('amount'),
                    total_paid=Sum('paid_amount'),
                    total_balance=Sum('balance'),
                    student_count=Count('student', distinct=True)
                ).order_by('student__studentprofile__current_class__display_name')
                
                for class_fin in class_financials:
                    class_name = class_fin['student__studentprofile__current_class__display_name'] or 'Not Assigned'
                    report_data['class_wise_financials'].append({
                        'class': class_name,
                        'total_amount': class_fin['total_amount'] or 0,
                        'total_paid': class_fin['total_paid'] or 0,
                        'total_balance': class_fin['total_balance'] or 0,
                        'student_count': class_fin['student_count'],
                        'collection_rate': round((class_fin['total_paid'] / class_fin['total_amount'] * 100), 2) 
                            if class_fin['total_amount'] and class_fin['total_amount'] > 0 else 0,
                    })
                
                # Monthly payment trends (last 6 months)
                six_months_ago = timezone.now() - timedelta(days=180)
                monthly_payments = payments_qs.filter(
                    payment_date__gte=six_months_ago
                ).annotate(
                    month=TruncMonth('payment_date')
                ).values('month').annotate(
                    total_paid=Sum('amount'),
                    payment_count=Count('id')
                ).order_by('month')
                
                for month_data in monthly_payments:
                    report_data['payment_trends'].append({
                        'month': month_data['month'].strftime('%Y-%m'),
                        'total_paid': month_data['total_paid'] or 0,
                        'payment_count': month_data['payment_count'],
                    })
                
                # Top students with arrears
                students_with_arrears = students.filter(
                    fee_arrears__gt=0
                ).order_by('-fee_arrears')[:20].values(
                    'admission_number',
                    'user__first_name',
                    'user__last_name',
                    'fee_arrears',
                    'current_class__display_name',
                    'fee_status'
                )
                
                report_data['arrears_summary'] = list(students_with_arrears)
                
                # Payment methods distribution
                payment_methods = payments_qs.values('payment_method').annotate(
                    total_amount=Sum('amount'),
                    count=Count('id')
                )
                
                report_data['payment_methods_distribution'] = {}
                for method in payment_methods:
                    method_name = method['payment_method'] or 'Unknown'
                    report_data['payment_methods_distribution'][method_name] = {
                        'total_amount': method['total_amount'] or 0,
                        'count': method['count'],
                    }
                
            except ImportError:
                report_data['error'] = 'Finance module not installed or available'
            
            return Response(report_data)
            
        except Exception as e:
            logger.error(f"Error generating financial status report: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CBCPathwayReportView(APIView):
    """
    API view for generating CBC pathway reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # Get filter parameters
            class_id = request.query_params.get('class_id')
            pathway = request.query_params.get('pathway')
            
            # Base queryset
            students = StudentProfile.objects.filter(
                is_active=True,
                cbc_pathway__isnull=False
            )
            
            # Apply filters
            if class_id:
                students = students.filter(current_class_id=class_id)
            
            if pathway:
                students = students.filter(cbc_pathway=pathway)
            
            # Overall CBC statistics
            total_cbc_students = students.count()
            total_students = StudentProfile.objects.filter(is_active=True).count()
            
            # Pathway distribution
            pathway_stats = students.values('cbc_pathway').annotate(
                count=Count('id'),
                avg_gpa=Avg('gpa'),
                avg_attendance=Avg('attendance_percentage')
            )
            
            pathway_distribution = []
            for stat in pathway_stats:
                pathway_display = dict(
                    StudentProfile._meta.get_field('cbc_pathway').choices
                ).get(stat['cbc_pathway'], stat['cbc_pathway'])
                
                pathway_distribution.append({
                    'pathway': pathway_display,
                    'count': stat['count'],
                    'percentage': round((stat['count'] / total_cbc_students * 100), 2) if total_cbc_students > 0 else 0,
                    'average_gpa': round(stat['avg_gpa'] or 0, 2),
                    'average_attendance': round(stat['avg_attendance'] or 0, 2),
                })
            
            # Class-wise pathway distribution
            class_pathways = students.filter(
                current_class__isnull=False
            ).values(
                'current_class__display_name',
                'cbc_pathway'
            ).annotate(
                count=Count('id')
            ).order_by('current_class__display_name', 'cbc_pathway')
            
            class_distribution = {}
            for stat in class_pathways:
                class_name = stat['current_class__display_name'] or 'Not Assigned'
                pathway_display = dict(
                    StudentProfile._meta.get_field('cbc_pathway').choices
                ).get(stat['cbc_pathway'], stat['cbc_pathway'])
                
                if class_name not in class_distribution:
                    class_distribution[class_name] = {}
                
                class_distribution[class_name][pathway_display] = stat['count']
            
            # Portfolio status
            portfolio_stats = students.values('portfolio_status').annotate(
                count=Count('id')
            )
            
            portfolio_distribution = {}
            for stat in portfolio_stats:
                status_display = dict(
                    StudentProfile._meta.get_field('portfolio_status').choices
                ).get(stat['portfolio_status'], stat['portfolio_status'])
                portfolio_distribution[status_display] = stat['count']
            
            # Community service hours
            cs_stats = students.aggregate(
                avg_hours=Avg('community_service_hours_completed'),
                total_hours=Sum('community_service_hours_completed'),
                max_hours=Max('community_service_hours_completed'),
                min_hours=Min('community_service_hours_completed')
            )
            
            # Top performers by pathway
            top_performers_by_pathway = {}
            for pathway_code, pathway_name in StudentProfile._meta.get_field('cbc_pathway').choices:
                pathway_students = students.filter(cbc_pathway=pathway_code).order_by('-gpa')[:5]
                
                if pathway_students.exists():
                    top_performers_by_pathway[pathway_name] = []
                    for student in pathway_students:
                        top_performers_by_pathway[pathway_name].append({
                            'admission_number': student.admission_number,
                            'full_name': student.full_name,
                            'gpa': float(student.gpa),
                            'class': str(student.current_class) if student.current_class else 'Not Assigned',
                            'community_service_hours': student.community_service_hours_completed,
                        })
            
            # Student competencies summary
            competencies_summary = {}
            try:
                from cbc.models import StudentCompetency
                
                for pathway_code, pathway_name in StudentProfile._meta.get_field('cbc_pathway').choices:
                    pathway_students = students.filter(cbc_pathway=pathway_code)
                    student_ids = pathway_students.values_list('id', flat=True)
                    
                    if student_ids:
                        competency_stats = StudentCompetency.objects.filter(
                            student_profile_id__in=student_ids
                        ).aggregate(
                            avg_competency=Avg('competency_level'),
                            total_assessed=Count('id')
                        )
                        
                        competencies_summary[pathway_name] = {
                            'average_competency_level': round(competency_stats['avg_competency'] or 0, 2),
                            'total_competencies_assessed': competency_stats['total_assessed'] or 0,
                            'student_count': pathway_students.count(),
                        }
            except ImportError:
                pass
            
            report = {
                'summary': {
                    'total_students': total_students,
                    'cbc_students': total_cbc_students,
                    'cbc_percentage': round((total_cbc_students / total_students * 100), 2) if total_students > 0 else 0,
                    'report_date': timezone.now().isoformat(),
                },
                'pathway_distribution': pathway_distribution,
                'class_distribution': class_distribution,
                'portfolio_distribution': portfolio_distribution,
                'community_service': {
                    'average_hours': round(cs_stats['avg_hours'] or 0, 1),
                    'total_hours': cs_stats['total_hours'] or 0,
                    'maximum_hours': cs_stats['max_hours'] or 0,
                    'minimum_hours': cs_stats['min_hours'] or 0,
                },
                'top_performers_by_pathway': top_performers_by_pathway,
                'competencies_summary': competencies_summary,
            }
            
            return Response(report)
            
        except Exception as e:
            logger.error(f"Error generating CBC pathway report: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )