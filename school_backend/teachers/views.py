# teachers/views.py
from rest_framework import viewsets, generics, status, permissions, filters as drf_filters
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum, Max, Min, F, Value, When, Case
from django.db.models.functions import ExtractYear, TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Department, TeacherProfile, TeacherDocument, TeacherQualification,
    TeacherTraining, TeacherAssignment, TeacherAttendance, TeacherLeave,
    ProfessionalStanding, PerformanceIndicator, TeacherTransfer
)
from .serializers import *
from .permissions import *
from .filters import *
from .pagination import StandardResultsSetPagination


# ============================================================================
# CUSTOM PERMISSION CLASSES
# ============================================================================

class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to only allow owners or admins to access object"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check if user owns the teacher profile
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        
        # Check if object belongs to user's teacher profile
        if hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.teacher == request.user
        
        return False


class IsDepartmentHOD(permissions.BasePermission):
    """Permission to allow Department HODs to access their department data"""
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        # Check if user is a teacher and HOD of any department
        if hasattr(request.user, 'teacher_profile'):
            return request.user.teacher_profile.departments_headed.exists()
        
        return False


# ============================================================================
# CUSTOM PAGINATION
# ============================================================================

class TeacherPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# DEPARTMENT VIEWS
# ============================================================================

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department CRUD operations"""
    
    queryset = Department.objects.filter(is_active=True).select_related('hod', 'academic_year')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Instantiate and return the list of permissions for this view."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their department
            if hasattr(self.request.user, 'teacher_profile'):
                teacher = self.request.user.teacher_profile
                if teacher.department:
                    queryset = queryset.filter(id=teacher.department.id)
                else:
                    queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        """Get all teachers in a department"""
        department = self.get_object()
        teachers = department.teachers.filter(is_active=True)
        
        page = self.paginate_queryset(teachers)
        if page is not None:
            serializer = TeacherProfileMinimalSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeacherProfileMinimalSerializer(teachers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get department statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total_departments': queryset.count(),
            'departments_by_category': queryset.values('tsc_category').annotate(
                count=Count('id')
            ).order_by('-count'),
            'departments_by_pathway': queryset.values('cbc_pathway').annotate(
                count=Count('id')
            ).order_by('-count'),
            'departments_without_hod': queryset.filter(hod__isnull=True).count(),
            'teacher_distribution': queryset.annotate(
                teacher_count=Count('teachers')
            ).values('name', 'teacher_count').order_by('-teacher_count')
        }
        
        return Response(stats)


# ============================================================================
# TEACHER PROFILE VIEWS
# ============================================================================

class TeacherProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherProfile CRUD operations"""
    
    queryset = TeacherProfile.objects.filter(is_active=True).select_related(
        'teacher', 'department'
    ).prefetch_related('subjects', 'classes')
    
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherProfileFilter
    search_fields = [
        'teacher__first_name', 'teacher__last_name', 'tsc_number',
        'teacher__email', 'teacher__phone_number', 'teacher__id_number'
    ]
    ordering_fields = [
        'teacher__last_name', 'teacher__first_name', 'tsc_number',
        'employment_date', 'created_at'
    ]
    ordering = ['teacher__last_name', 'teacher__first_name']
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return TeacherProfileCreateSerializer
        elif self.action == 'list':
            return TeacherProfileSummarySerializer
        elif self.action == 'retrieve':
            return TeacherProfileDetailSerializer
        return TeacherProfileSerializer
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own profile
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user)
            else:
                queryset = queryset.none()
        
        # Apply custom filters
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        teaching_level = self.request.query_params.get('teaching_level')
        if teaching_level:
            queryset = queryset.filter(teaching_level=teaching_level)
        
        employment_status = self.request.query_params.get('employment_status')
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        tsc_status = self.request.query_params.get('tsc_status')
        if tsc_status:
            queryset = queryset.filter(tsc_status=tsc_status)
        
        cbc_trained = self.request.query_params.get('cbc_trained')
        if cbc_trained:
            queryset = queryset.filter(cbc_trained=cbc_trained == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by user when creating teacher"""
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get teacher dashboard data"""
        teacher = self.get_object()
        
        # Check permission
        if not (request.user.is_staff or teacher.teacher == request.user):
            return Response(
                {"detail": "You do not have permission to access this dashboard."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get recent attendance (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_attendance = TeacherAttendance.objects.filter(
            teacher=teacher,
            date__gte=thirty_days_ago
        ).order_by('-date')[:10]
        
        # Get upcoming leaves
        today = timezone.now().date()
        upcoming_leaves = TeacherLeave.objects.filter(
            teacher=teacher,
            status='approved',
            start_date__gte=today
        ).order_by('start_date')[:5]
        
        # Get current assignments
        current_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).select_related('subject', 'class_assigned', 'academic_year')[:10]
        
        # Get recent trainings
        recent_trainings = TeacherTraining.objects.filter(
            teacher=teacher,
            status='completed'
        ).order_by('-end_date')[:5]
        
        # Get latest performance indicator
        performance_summary = PerformanceIndicator.objects.filter(
            teacher=teacher
        ).order_by('-evaluation_date').first()
        
        # Calculate workload summary
        workload_summary = teacher.calculate_workload()
        
        # Get compliance summary
        compliance_summary = {
            'tsc_compliant': teacher.tsc_compliant,
            'cbc_trained': teacher.cbc_trained,
            'tpd_valid': teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date >= today,
            'documents_verified': teacher.documents.filter(status='verified').count(),
            'qualifications_verified': teacher.qualifications.filter(verification_status='verified').count(),
        }
        
        data = {
            'profile': TeacherProfileSerializer(teacher).data,
            'recent_attendance': TeacherAttendanceSerializer(recent_attendance, many=True).data,
            'upcoming_leaves': TeacherLeaveSerializer(upcoming_leaves, many=True).data,
            'current_assignments': TeacherAssignmentSerializer(current_assignments, many=True).data,
            'recent_trainings': TeacherTrainingSerializer(recent_trainings, many=True).data,
            'performance_summary': PerformanceIndicatorSerializer(performance_summary).data if performance_summary else None,
            'workload_summary': workload_summary,
            'compliance_summary': compliance_summary,
        }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def tsc_report(self, request, pk=None):
        """Generate TSC compliance report"""
        teacher = self.get_object()
        
        # Check permission
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can generate TSC reports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report = teacher.generate_tsc_report()
        return Response(report)
    
    @action(detail=True, methods=['post'])
    def update_tpd(self, request, pk=None):
        """Update TPD module"""
        teacher = self.get_object()
        
        # Check permission
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can update TPD modules."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_module = request.data.get('module')
        completion_date = request.data.get('completion_date', timezone.now().date())
        
        if not new_module:
            return Response(
                {"detail": "Module number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_module = int(new_module)
        except ValueError:
            return Response(
                {"detail": "Module must be a number between 1 and 6."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = teacher.update_tpd_module(new_module, completion_date)
        
        if success:
            return Response(
                {"detail": f"TPD module updated to {new_module}."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid module number. Must be between 1 and 6."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def mark_cbc_trained(self, request, pk=None):
        """Mark teacher as CBC trained"""
        teacher = self.get_object()
        
        # Check permission
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can mark teachers as CBC trained."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        training_date = request.data.get('training_date', timezone.now().date())
        certificate_file = request.FILES.get('certificate')
        
        success = teacher.mark_cbc_trained(training_date, certificate_file)
        
        if success:
            return Response(
                {"detail": "Teacher marked as CBC trained."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to mark teacher as CBC trained."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get teacher statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total_teachers = queryset.count()
        active_teachers = queryset.filter(employment_status='active').count()
        
        # TSC compliance
        tsc_compliant = queryset.filter(
            tsc_status__in=['registered', 'provisional'],
            cbc_trained=True
        ).count()
        
        # CBC training
        cbc_trained = queryset.filter(cbc_trained=True).count()
        
        # Teachers on leave
        on_leave = queryset.filter(
            employment_status__in=['on_leave', 'study_leave', 'maternity_leave', 'paternity_leave', 'sick_leave']
        ).count()
        
        # TPD expiring soon (within 30 days)
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        tpd_expiring_soon = queryset.filter(
            tpd_next_renewal_date__range=[timezone.now().date(), thirty_days_later]
        ).count()
        
        # Distribution by department
        by_department = queryset.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Distribution by teaching level
        by_teaching_level = queryset.values('teaching_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Distribution by employment type
        by_employment_type = queryset.values('employment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Workload distribution
        workload_distribution = {
            'overloaded': queryset.filter(weekly_periods__gt=36).count(),
            'optimal': queryset.filter(weekly_periods__range=[23, 36]).count(),
            'underutilized': queryset.filter(weekly_periods__lt=23).count(),
            'no_load': queryset.filter(weekly_periods=0).count(),
        }
        
        # Compliance rate
        compliance_rate = (tsc_compliant / active_teachers * 100) if active_teachers > 0 else 0
        
        stats = {
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'tsc_compliant': tsc_compliant,
            'cbc_trained': cbc_trained,
            'on_leave': on_leave,
            'tpd_expiring_soon': tpd_expiring_soon,
            'by_department': {item['department__name']: item['count'] for item in by_department},
            'by_teaching_level': {item['teaching_level']: item['count'] for item in by_teaching_level},
            'by_employment_type': {item['employment_type']: item['count'] for item in by_employment_type},
            'workload_distribution': workload_distribution,
            'compliance_rate': round(compliance_rate, 2),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create teachers from CSV/Excel"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can perform bulk operations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkTeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                {"detail": f"{len(result['created_teachers'])} teachers created successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search teachers with advanced filters"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply additional search filters
        search_query = request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(teacher__first_name__icontains=search_query) |
                Q(teacher__last_name__icontains=search_query) |
                Q(tsc_number__icontains=search_query) |
                Q(teacher__id_number__icontains=search_query) |
                Q(teacher__email__icontains=search_query)
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TeacherProfileSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeacherProfileSummarySerializer(queryset, many=True)
        return Response(serializer.data)


class TeacherProfileByDepartmentView(generics.ListAPIView):
    """Get teachers by department"""
    
    serializer_class = TeacherProfileSummarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TeacherPagination
    
    def get_queryset(self):
        department_id = self.kwargs['department_id']
        return TeacherProfile.objects.filter(
            department_id=department_id,
            is_active=True
        ).select_related('teacher', 'department')


# ============================================================================
# TEACHER DOCUMENT VIEWS
# ============================================================================

class TeacherDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherDocument CRUD operations"""
    
    queryset = TeacherDocument.objects.filter(is_active=True).select_related(
        'teacher', 'verified_by'
    )
    serializer_class = TeacherDocumentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherDocumentFilter
    search_fields = ['title', 'description', 'teacher__teacher__first_name', 'teacher__teacher__last_name']
    ordering_fields = ['upload_date', 'expiry_date', 'title']
    ordering = ['-upload_date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own documents
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set uploaded by user and calculate file size"""
        document_file = serializer.validated_data.get('document_file')
        if document_file:
            serializer.save(file_size=document_file.size)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify or reject a document"""
        document = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can verify documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status', 'verified')
        notes = request.data.get('notes', '')
        
        success = document.verify_document(request.user, status_value, notes)
        
        if success:
            return Response(
                {"detail": f"Document marked as {status_value}."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to verify document."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get documents expiring soon (within 30 days)"""
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            expiry_date__range=[timezone.now().date(), thirty_days_later],
            status__in=['verified', 'pending']
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# TEACHER QUALIFICATION VIEWS
# ============================================================================

class TeacherQualificationViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherQualification CRUD operations"""
    
    queryset = TeacherQualification.objects.filter(is_active=True).select_related(
        'teacher', 'verified_by', 'document'
    )
    serializer_class = TeacherQualificationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherQualificationFilter
    search_fields = ['title', 'institution', 'field_of_study', 'certificate_number']
    ordering_fields = ['end_date', 'start_date', 'title']
    ordering = ['-end_date']
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own qualifications
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a qualification"""
        qualification = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can verify qualifications."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status', 'verified')
        notes = request.data.get('notes', '')
        
        success = qualification.verify_qualification(request.user, status_value, notes)
        
        if success:
            return Response(
                {"detail": f"Qualification marked as {status_value}."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to verify qualification."},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# TEACHER TRAINING VIEWS
# ============================================================================

class TeacherTrainingViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherTraining CRUD operations"""
    
    queryset = TeacherTraining.objects.filter(is_active=True).select_related(
        'teacher', 'document'
    )
    serializer_class = TeacherTrainingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherTrainingFilter
    search_fields = ['title', 'organizer', 'description', 'certificate_number']
    ordering_fields = ['start_date', 'end_date', 'title']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own trainings
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark training as completed"""
        training = self.get_object()
        
        # Check permission
        if not (request.user.is_staff or training.teacher.teacher == request.user):
            return Response(
                {"detail": "You do not have permission to complete this training."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        success = training.complete_training(score, feedback)
        
        if success:
            return Response(
                {"detail": "Training marked as completed."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to complete training."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming trainings"""
        today = timezone.now().date()
        
        queryset = self.get_queryset().filter(
            start_date__gte=today,
            status__in=['registered', 'in_progress']
        ).order_by('start_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# TEACHER ASSIGNMENT VIEWS
# ============================================================================

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherAssignment CRUD operations"""
    
    queryset = TeacherAssignment.objects.filter(is_active=True).select_related(
        'teacher', 'academic_year', 'term', 'subject', 'class_assigned', 'stream', 'approved_by'
    )
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherAssignmentFilter
    search_fields = ['title', 'description', 'teacher__teacher__first_name', 'teacher__teacher__last_name']
    ordering_fields = ['start_date', 'end_date', 'title']
    ordering = ['-start_date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own assignments
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set approved_by if user is admin"""
        if self.request.user.is_staff:
            serializer.save(approved_by=self.request.user, approval_date=timezone.now().date())
        else:
            serializer.save()
            
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get assignments for the logged-in teacher"""
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {"detail": "You do not have a teacher profile."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher_profile = request.user.teacher_profile
        queryset = self.get_queryset().filter(teacher=teacher_profile)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve assignment"""
        assignment = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can approve assignments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignment.approved_by = request.user
        assignment.approval_date = timezone.now().date()
        assignment.save()
        
        return Response(
            {"detail": "Assignment approved."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate assignment"""
        assignment = self.get_object()
        assignment.activate_assignment()
        
        return Response(
            {"detail": "Assignment activated."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate assignment"""
        assignment = self.get_object()
        assignment.deactivate_assignment()
        
        return Response(
            {"detail": "Assignment deactivated."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current assignments"""
        queryset = self.get_queryset().filter(
            is_active=True,
            end_date__gte=timezone.now().date()
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an assignment"""
        assignment = self.get_object()
        assignment.status = 'published'
        assignment.published_date = timezone.now()
        assignment.save()
        return Response({"detail": "Assignment published successfully."})
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish an assignment"""
        assignment = self.get_object()
        assignment.status = 'draft'
        assignment.save()
        return Response({"detail": "Assignment unpublished."})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an assignment"""
        assignment = self.get_object()
        assignment.status = 'closed'
        assignment.closed_date = timezone.now()
        assignment.save()
        return Response({"detail": "Assignment closed."})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate an assignment"""
        assignment = self.get_object()
        
        # Create a copy excluding some fields
        assignment_data = model_to_dict(assignment)
        exclude_fields = ['id', 'created_at', 'updated_at', 'published_date', 'closed_date']
        
        for field in exclude_fields:
            assignment_data.pop(field, None)
        
        # Update title if provided
        new_title = request.data.get('title', f"Copy of {assignment.title}")
        assignment_data['title'] = new_title
        
        # Create new assignment
        serializer = self.get_serializer(data=assignment_data)
        serializer.is_valid(raise_exception=True)
        new_assignment = serializer.save(teacher=assignment.teacher)
        
        return Response(
            {"detail": "Assignment duplicated successfully.", "id": new_assignment.id},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get assignment statistics for teacher"""
        teacher = request.user.teacher_profile
        queryset = self.get_queryset().filter(teacher=teacher)
        
        stats = {
            'total_assignments': queryset.count(),
            'draft_count': queryset.filter(status='draft').count(),
            'published_count': queryset.filter(status='published').count(),
            'graded_count': queryset.filter(status='graded').count(),
            'closed_count': queryset.filter(status='closed').count(),
            'archived_count': queryset.filter(status='archived').count(),
            'overdue_count': queryset.filter(due_date__lt=timezone.now().date(), status='published').count(),
            'total_submissions': TeacherAssignmentSubmission.objects.filter(
                assignment__teacher=teacher
            ).count(),
            'graded_submissions': TeacherAssignmentSubmission.objects.filter(
                assignment__teacher=teacher,
                status='graded'
            ).count(),
            'pending_grading_count': TeacherAssignmentSubmission.objects.filter(
                assignment__teacher=teacher,
                status='submitted'
            ).count(),
            'average_score': TeacherAssignmentSubmission.objects.filter(
                assignment__teacher=teacher,
                status='graded'
            ).aggregate(Avg('score'))['score__avg'] or 0,
        }
        
        return Response(stats)
# ============================================================================
# TEACHER ATTENDANCE VIEWS
# ============================================================================

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherAttendance CRUD operations"""
    
    queryset = TeacherAttendance.objects.select_related('teacher', 'verified_by')
    serializer_class = TeacherAttendanceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherAttendanceFilter
    search_fields = ['teacher__teacher__first_name', 'teacher__teacher__last_name', 'notes']
    ordering_fields = ['date', 'check_in_time', 'check_out_time']
    ordering = ['-date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own attendance
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set verified_by if user is admin"""
        if self.request.user.is_staff:
            serializer.save(verified_by=self.request.user, verification_time=timezone.now())
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update attendance records"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can perform bulk operations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkAttendanceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            attendance_records = serializer.validated_data['attendance_records']
            
            created_count = 0
            updated_count = 0
            
            for attendance_data in attendance_records:
                teacher = attendance_data['teacher']
                
                # Check if attendance already exists for this date
                attendance, created = TeacherAttendance.objects.update_or_create(
                    teacher=teacher,
                    date=date,
                    defaults=attendance_data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return Response({
                "detail": f"Attendance updated: {created_count} created, {updated_count} updated."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate attendance report"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can generate reports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AttendanceReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        teacher_id = validated_data.get('teacher_id')
        department_id = validated_data.get('department_id')
        
        queryset = self.get_queryset().filter(
            date__range=[start_date, end_date]
        )
        
        if teacher_id:
            queryset = queryset.filter(teacher=teacher_id)
        
        if department_id:
            queryset = queryset.filter(teacher__department_id=department_id)
        
        # Calculate statistics
        total_days = queryset.count()
        present_days = queryset.filter(status='present').count()
        absent_days = queryset.filter(status='absent').count()
        leave_days = queryset.filter(status='leave').count()
        late_days = queryset.filter(is_late=True).count()
        
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        average_working_hours = queryset.aggregate(
            avg_hours=Avg('working_hours')
        )['avg_hours'] or 0
        
        by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        report = {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'late_days': late_days,
            'attendance_rate': round(attendance_rate, 2),
            'average_working_hours': float(average_working_hours),
            'by_status': {item['status']: item['count'] for item in by_status},
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return Response(report)
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly attendance summary"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can view summaries."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        queryset = self.get_queryset().filter(
            date__year=year,
            date__month=month
        )
        
        summary = queryset.values('teacher').annotate(
            present_days=Count('id', filter=Q(status='present')),
            absent_days=Count('id', filter=Q(status='absent')),
            leave_days=Count('id', filter=Q(status='leave')),
            late_days=Count('id', filter=Q(is_late=True)),
            total_hours=Sum('working_hours')
        )
        
        return Response(summary)


# ============================================================================
# TEACHER LEAVE VIEWS
# ============================================================================

class TeacherLeaveViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherLeave CRUD operations"""
    
    queryset = TeacherLeave.objects.filter(is_active=True).select_related(
        'teacher', 'approved_by', 'rejected_by', 'cover_teacher'
    ).prefetch_related('documents')
    
    serializer_class = TeacherLeaveSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherLeaveFilter
    search_fields = ['reason', 'teacher__teacher__first_name', 'teacher__teacher__last_name']
    ordering_fields = ['start_date', 'end_date', 'applied_date']
    ordering = ['-applied_date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own leaves
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set applied date"""
        serializer.save(applied_date=timezone.now().date())
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit leave for approval"""
        leave = self.get_object()
        
        if leave.status != 'draft':
            return Response(
                {"detail": "Leave application has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = leave.submit_for_approval()
        
        if success:
            return Response(
                {"detail": "Leave application submitted for approval."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to submit leave application."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave application"""
        leave = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can approve leaves."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notes = request.data.get('notes', '')
        
        success = leave.approve_leave(request.user, notes)
        
        if success:
            return Response(
                {"detail": "Leave application approved."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to approve leave application."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave application"""
        leave = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can reject leaves."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', '')
        
        success = leave.reject_leave(request.user, reason)
        
        if success:
            return Response(
                {"detail": "Leave application rejected."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Failed to reject leave application."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending leave applications"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can view pending leaves."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(status='pending').order_by('applied_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current leaves (approved and in progress)"""
        today = timezone.now().date()
        
        queryset = self.get_queryset().filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).order_by('end_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# PROFESSIONAL STANDING VIEWS
# ============================================================================

class ProfessionalStandingViewSet(viewsets.ModelViewSet):
    """ViewSet for ProfessionalStanding CRUD operations"""
    
    queryset = ProfessionalStanding.objects.filter(is_active=True).select_related(
        'teacher', 'issued_by'
    )
    serializer_class = ProfessionalStandingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProfessionalStandingFilter
    search_fields = ['description', 'reference_number', 'teacher__teacher__first_name', 'teacher__teacher__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own records
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset


# ============================================================================
# PERFORMANCE INDICATOR VIEWS
# ============================================================================

class PerformanceIndicatorViewSet(viewsets.ModelViewSet):
    """ViewSet for PerformanceIndicator CRUD operations"""
    
    queryset = PerformanceIndicator.objects.select_related(
        'teacher', 'academic_year', 'term', 'evaluator'
    )
    serializer_class = PerformanceIndicatorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PerformanceIndicatorFilter
    search_fields = ['teacher__teacher__first_name', 'teacher__teacher__last_name', 'notes']
    ordering_fields = ['evaluation_date', 'overall_score']
    ordering = ['-evaluation_date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own performance indicators
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get performance summary"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = queryset.aggregate(
            average_overall_score=Avg('overall_score'),
            highest_score=Max('overall_score'),
            lowest_score=Min('overall_score'),
            total_evaluations=Count('id')
        )
        
        return Response(summary)


# ============================================================================
# TEACHER TRANSFER VIEWS
# ============================================================================

class TeacherTransferViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherTransfer CRUD operations"""
    
    queryset = TeacherTransfer.objects.filter(is_active=True).select_related(
        'teacher', 'from_school', 'to_school',
        'approved_by_sending', 'approved_by_receiving', 'approved_by_tsc'
    )
    serializer_class = TeacherTransferSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TeacherTransferFilter
    search_fields = ['reason', 'teacher__teacher__first_name', 'teacher__teacher__last_name']
    ordering_fields = ['applied_date', 'effective_date']
    ordering = ['-applied_date']
    
    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Custom queryset based on user role"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            # Regular teachers can only see their own transfers
            if hasattr(self.request.user, 'teacher_profile'):
                queryset = queryset.filter(teacher=self.request.user.teacher_profile)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set applied date"""
        serializer.save(applied_date=timezone.now().date())
    
    @action(detail=True, methods=['post'])
    def approve_sending(self, request, pk=None):
        """Approve transfer by sending school"""
        transfer = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can approve transfers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        transfer.approved_by_sending = request.user
        transfer.save()
        
        return Response(
            {"detail": "Transfer approved by sending school."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def approve_receiving(self, request, pk=None):
        """Approve transfer by receiving school"""
        transfer = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can approve transfers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        transfer.approved_by_receiving = request.user
        transfer.save()
        
        return Response(
            {"detail": "Transfer approved by receiving school."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def approve_tsc(self, request, pk=None):
        """Approve transfer by TSC"""
        transfer = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can approve transfers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        transfer.approved_by_tsc = request.user
        transfer.save()
        
        return Response(
            {"detail": "Transfer approved by TSC."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark transfer as completed"""
        transfer = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can complete transfers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        transfer.status = 'completed'
        transfer.handover_completed = True
        transfer.handover_date = timezone.now().date()
        transfer.save()
        
        return Response(
            {"detail": "Transfer marked as completed."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending transfers"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can view pending transfers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(status='pending').order_by('applied_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# DASHBOARD & ANALYTICS VIEWS
# ============================================================================

class TeacherDashboardView(APIView):
    """View for teacher dashboard"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data for current teacher"""
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {"detail": "User is not a teacher."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher = request.user.teacher_profile
        
        # Get dashboard data
        data = {
            'profile': TeacherProfileSerializer(teacher).data,
            'quick_stats': self._get_quick_stats(teacher),
            'recent_activities': self._get_recent_activities(teacher),
            'upcoming_events': self._get_upcoming_events(teacher),
            'compliance_status': self._get_compliance_status(teacher),
        }
        
        return Response(data)
    
    def _get_quick_stats(self, teacher):
        """Get quick statistics for dashboard"""
        today = timezone.now().date()
        
        # Current month attendance
        first_day = today.replace(day=1)
        attendance_stats = TeacherAttendance.objects.filter(
            teacher=teacher,
            date__range=[first_day, today]
        ).aggregate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            leave=Count('id', filter=Q(status='leave'))
        )
        
        # Current assignments
        current_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).count()
        
        # Pending leaves
        pending_leaves = TeacherLeave.objects.filter(
            teacher=teacher,
            status='pending'
        ).count()
        
        # Upcoming trainings
        upcoming_trainings = TeacherTraining.objects.filter(
            teacher=teacher,
            start_date__gte=today,
            status='registered'
        ).count()
        
        return {
            'attendance': attendance_stats,
            'current_assignments': current_assignments,
            'pending_leaves': pending_leaves,
            'upcoming_trainings': upcoming_trainings,
        }
    
    def _get_recent_activities(self, teacher):
        """Get recent activities"""
        activities = []
        
        # Recent attendance
        recent_attendance = TeacherAttendance.objects.filter(
            teacher=teacher
        ).order_by('-date')[:5]
        
        for attendance in recent_attendance:
            activities.append({
                'type': 'attendance',
                'date': attendance.date,
                'title': f"Attendance: {attendance.get_status_display()}",
                'description': f"Checked in: {attendance.check_in_time}, Checked out: {attendance.check_out_time}" if attendance.check_in_time else "",
            })
        
        # Recent leaves
        recent_leaves = TeacherLeave.objects.filter(
            teacher=teacher
        ).order_by('-applied_date')[:5]
        
        for leave in recent_leaves:
            activities.append({
                'type': 'leave',
                'date': leave.applied_date,
                'title': f"Leave Application: {leave.get_leave_type_display()}",
                'description': f"Status: {leave.get_status_display()}",
            })
        
        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return activities[:10]
    
    def _get_upcoming_events(self, teacher):
        """Get upcoming events"""
        today = timezone.now().date()
        events = []
        
        # Upcoming leaves
        upcoming_leaves = TeacherLeave.objects.filter(
            teacher=teacher,
            status='approved',
            start_date__gte=today
        ).order_by('start_date')[:5]
        
        for leave in upcoming_leaves:
            events.append({
                'type': 'leave',
                'date': leave.start_date,
                'title': f"Leave: {leave.get_leave_type_display()}",
                'description': f"Days: {leave.days_requested}",
            })
        
        # Upcoming trainings
        upcoming_trainings = TeacherTraining.objects.filter(
            teacher=teacher,
            start_date__gte=today,
            status='registered'
        ).order_by('start_date')[:5]
        
        for training in upcoming_trainings:
            events.append({
                'type': 'training',
                'date': training.start_date,
                'title': f"Training: {training.title}",
                'description': f"Organizer: {training.organizer}",
            })
        
        # Upcoming appraisals
        if teacher.next_appraisal_date and teacher.next_appraisal_date >= today:
            events.append({
                'type': 'appraisal',
                'date': teacher.next_appraisal_date,
                'title': "Performance Appraisal",
                'description': "Next performance review",
            })
        
        # Sort by date
        events.sort(key=lambda x: x['date'])
        
        return events[:10]
    
    def _get_compliance_status(self, teacher):
        """Get compliance status"""
        today = timezone.now().date()
        
        return {
            'tsc_compliant': teacher.tsc_compliant,
            'cbc_trained': teacher.cbc_trained,
            'tpd_valid': teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date >= today,
            'documents_complete': self._check_documents_complete(teacher),
        }
    
    def _check_documents_complete(self, teacher):
        """Check if all required documents are uploaded and verified"""
        required_documents = teacher.documents.filter(is_required=True)
        if not required_documents.exists():
            return False
        
        verified_documents = required_documents.filter(status='verified')
        return verified_documents.count() == required_documents.count()


class AdminDashboardView(APIView):
    """View for admin dashboard"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get admin dashboard data"""
        data = {
            'teacher_statistics': self._get_teacher_statistics(),
            'attendance_statistics': self._get_attendance_statistics(),
            'leave_statistics': self._get_leave_statistics(),
            'compliance_statistics': self._get_compliance_statistics(),
            'recent_activities': self._get_recent_activities(),
        }
        
        return Response(data)
    
    def _get_teacher_statistics(self):
        """Get teacher statistics"""
        queryset = TeacherProfile.objects.filter(is_active=True)
        
        stats = queryset.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(employment_status='active')),
            on_leave=Count('id', filter=Q(employment_status__in=['on_leave', 'study_leave', 'maternity_leave', 'paternity_leave', 'sick_leave'])),
            cbc_trained=Count('id', filter=Q(cbc_trained=True)),
        )
        
        # Department distribution
        department_dist = queryset.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            **stats,
            'department_distribution': department_dist,
        }
    
    def _get_attendance_statistics(self):
        """Get attendance statistics"""
        today = timezone.now().date()
        first_day = today.replace(day=1)
        
        stats = TeacherAttendance.objects.filter(
            date__range=[first_day, today]
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            leave=Count('id', filter=Q(status='leave')),
            late=Count('id', filter=Q(is_late=True)),
        )
        
        return stats
    
    def _get_leave_statistics(self):
        """Get leave statistics"""
        today = timezone.now().date()
        
        stats = TeacherLeave.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).aggregate(
            total=Count('id'),
            annual=Count('id', filter=Q(leave_type='annual')),
            sick=Count('id', filter=Q(leave_type='sick')),
            maternity=Count('id', filter=Q(leave_type='maternity')),
            paternity=Count('id', filter=Q(leave_type='paternity')),
        )
        
        return stats
    
    def _get_compliance_statistics(self):
        """Get compliance statistics"""
        queryset = TeacherProfile.objects.filter(is_active=True, employment_status='active')
        
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        stats = queryset.aggregate(
            tsc_compliant=Count('id', filter=Q(
                tsc_status__in=['registered', 'provisional'],
                cbc_trained=True
            )),
            tpd_expiring=Count('id', filter=Q(
                tpd_next_renewal_date__range=[today, thirty_days_later]
            )),
        )
        
        return stats
    
    def _get_recent_activities(self):
        """Get recent admin activities"""
        activities = []
        
        # Recent leave applications
        recent_leaves = TeacherLeave.objects.filter(
            status='pending'
        ).order_by('-applied_date')[:5]
        
        for leave in recent_leaves:
            activities.append({
                'type': 'leave_pending',
                'date': leave.applied_date,
                'title': f"Pending Leave: {leave.teacher.full_name}",
                'description': f"{leave.get_leave_type_display()} - {leave.days_requested} days",
            })
        
        # Recent transfers
        recent_transfers = TeacherTransfer.objects.filter(
            status='pending'
        ).order_by('-applied_date')[:5]
        
        for transfer in recent_transfers:
            activities.append({
                'type': 'transfer_pending',
                'date': transfer.applied_date,
                'title': f"Pending Transfer: {transfer.teacher.full_name}",
                'description': f"From: {transfer.from_school.name} To: {transfer.to_school.name}",
            })
        
        # Recent documents for verification
        recent_documents = TeacherDocument.objects.filter(
            status='pending'
        ).order_by('-upload_date')[:5]
        
        for document in recent_documents:
            activities.append({
                'type': 'document_pending',
                'date': document.upload_date,
                'title': f"Document Pending: {document.teacher.full_name}",
                'description': f"{document.get_document_type_display()}",
            })
        
        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return activities[:10]


# ============================================================================
# REPORT VIEWS
# ============================================================================

class TeacherReportView(APIView):
    """View for generating teacher reports"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Generate teacher report"""
        report_type = request.query_params.get('type', 'summary')
        
        if report_type == 'summary':
            return self._get_summary_report(request)
        elif report_type == 'tsc_compliance':
            return self._get_tsc_compliance_report(request)
        elif report_type == 'workload':
            return self._get_workload_report(request)
        elif report_type == 'attendance':
            return self._get_attendance_report(request)
        else:
            return Response(
                {"detail": "Invalid report type."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_summary_report(self, request):
        """Generate summary report"""
        queryset = TeacherProfile.objects.filter(is_active=True)
        
        # Apply filters
        department_id = request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        teaching_level = request.query_params.get('teaching_level')
        if teaching_level:
            queryset = queryset.filter(teaching_level=teaching_level)
        
        employment_status = request.query_params.get('employment_status')
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        # Generate report data
        report_data = []
        for teacher in queryset:
            report_data.append({
                'name': teacher.full_name,
                'tsc_number': teacher.tsc_number,
                'department': teacher.department.name if teacher.department else '',
                'designation': teacher.get_designation_display(),
                'teaching_level': teacher.get_teaching_level_display(),
                'employment_status': teacher.get_employment_status_display(),
                'years_of_service': teacher.years_of_service,
                'cbc_trained': 'Yes' if teacher.cbc_trained else 'No',
                'tpd_module': teacher.tpd_current_module,
                'tpd_renewal': teacher.tpd_next_renewal_date,
                'workload_periods': teacher.weekly_periods,
                'performance_rating': teacher.performance_rating,
            })
        
        return Response({
            'report_type': 'teacher_summary',
            'generated_at': timezone.now(),
            'total_teachers': len(report_data),
            'data': report_data,
        })
    
    def _get_tsc_compliance_report(self, request):
        """Generate TSC compliance report"""
        queryset = TeacherProfile.objects.filter(is_active=True, employment_status='active')
        
        compliance_data = []
        for teacher in queryset:
            tsc_compliant = teacher.tsc_compliant
            compliance_data.append({
                'name': teacher.full_name,
                'tsc_number': teacher.tsc_number,
                'tsc_status': teacher.get_tsc_status_display(),
                'cbc_trained': 'Yes' if teacher.cbc_trained else 'No',
                'tpd_valid': 'Yes' if teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date >= timezone.now().date() else 'No',
                'tsc_compliant': 'Yes' if tsc_compliant else 'No',
                'missing_requirements': self._get_missing_requirements(teacher),
            })
        
        compliant_count = sum(1 for item in compliance_data if item['tsc_compliant'] == 'Yes')
        compliance_rate = (compliant_count / len(compliance_data) * 100) if compliance_data else 0
        
        return Response({
            'report_type': 'tsc_compliance',
            'generated_at': timezone.now(),
            'total_teachers': len(compliance_data),
            'compliant_teachers': compliant_count,
            'compliance_rate': round(compliance_rate, 2),
            'data': compliance_data,
        })
    
    def _get_missing_requirements(self, teacher):
        """Get missing TSC requirements"""
        missing = []
        
        if not teacher.tsc_number or teacher.tsc_status not in ['registered', 'provisional']:
            missing.append('TSC Registration')
        
        if not teacher.cbc_trained and teacher.teaching_level == 'junior_secondary':
            missing.append('CBC Training')
        
        if teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date < timezone.now().date():
            missing.append('TPD Renewal')
        
        return missing
    
    def _get_workload_report(self, request):
        """Generate workload report"""
        queryset = TeacherProfile.objects.filter(is_active=True, employment_status='active')
        
        workload_data = []
        for teacher in queryset:
            utilization = (teacher.weekly_periods / 45 * 100) if teacher.weekly_periods else 0
            workload_status = 'overloaded' if utilization > 100 else 'high' if utilization > 80 else 'optimal' if utilization > 50 else 'low'
            
            workload_data.append({
                'name': teacher.full_name,
                'department': teacher.department.name if teacher.department else '',
                'weekly_periods': teacher.weekly_periods,
                'teaching_hours': float(teacher.teaching_load_hours),
                'utilization_percentage': round(utilization, 2),
                'workload_status': workload_status,
                'assignments_count': teacher.assignments.filter(is_active=True).count(),
            })
        
        # Calculate statistics
        stats = {
            'overloaded': sum(1 for item in workload_data if item['workload_status'] == 'overloaded'),
            'high': sum(1 for item in workload_data if item['workload_status'] == 'high'),
            'optimal': sum(1 for item in workload_data if item['workload_status'] == 'optimal'),
            'low': sum(1 for item in workload_data if item['workload_status'] == 'low'),
            'average_periods': sum(item['weekly_periods'] for item in workload_data) / len(workload_data) if workload_data else 0,
            'average_hours': sum(item['teaching_hours'] for item in workload_data) / len(workload_data) if workload_data else 0,
        }
        
        return Response({
            'report_type': 'workload',
            'generated_at': timezone.now(),
            'total_teachers': len(workload_data),
            'statistics': stats,
            'data': workload_data,
        })
    
    def _get_attendance_report(self, request):
        """Generate attendance report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        if not start_date:
            start_date = timezone.now().date().replace(day=1)
        
        queryset = TeacherAttendance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('teacher')
        
        # Group by teacher
        attendance_by_teacher = {}
        for attendance in queryset:
            teacher_id = attendance.teacher.id
            if teacher_id not in attendance_by_teacher:
                attendance_by_teacher[teacher_id] = {
                    'teacher': attendance.teacher.full_name,
                    'department': attendance.teacher.department.name if attendance.teacher.department else '',
                    'present_days': 0,
                    'absent_days': 0,
                    'leave_days': 0,
                    'late_days': 0,
                    'total_hours': 0,
                }
            
            data = attendance_by_teacher[teacher_id]
            if attendance.status == 'present':
                data['present_days'] += 1
                data['total_hours'] += float(attendance.working_hours)
                if attendance.is_late:
                    data['late_days'] += 1
            elif attendance.status == 'absent':
                data['absent_days'] += 1
            elif attendance.status == 'leave':
                data['leave_days'] += 1
        
        # Convert to list
        attendance_data = list(attendance_by_teacher.values())
        
        # Calculate statistics
        total_days = (datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.strptime(start_date, '%Y-%m-%d').date()).days + 1
        
        for data in attendance_data:
            data['attendance_rate'] = round((data['present_days'] / total_days * 100), 2) if total_days > 0 else 0
            data['average_hours_per_day'] = round(data['total_hours'] / data['present_days'], 2) if data['present_days'] > 0 else 0
        
        return Response({
            'report_type': 'attendance',
            'generated_at': timezone.now(),
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days,
            },
            'total_teachers': len(attendance_data),
            'data': attendance_data,
        })


# ============================================================================
# FILE EXPORT VIEWS
# ============================================================================

class ExportTeachersView(APIView):
    """Export teachers to CSV"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Export teacher data"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers_export.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Full Name', 'TSC Number', 'ID Number', 'Email', 'Phone',
            'Employment Type', 'Employment Status', 'Teaching Level',
            'Department', 'Designation', 'CBC Trained', 'TPD Module',
            'Weekly Periods', 'Performance Rating', 'Salary Scale'
        ])
        
        # Get filtered queryset
        queryset = TeacherProfile.objects.filter(is_active=True)
        
        # Apply filters
        filters = TeacherProfileFilter(request.GET, queryset=queryset)
        queryset = filters.qs
        
        # Write data
        for teacher in queryset:
            writer.writerow([
                teacher.full_name,
                teacher.tsc_number,
                teacher.teacher.id_number,
                teacher.teacher.email,
                teacher.teacher.phone_number,
                teacher.get_employment_type_display(),
                teacher.get_employment_status_display(),
                teacher.get_teaching_level_display(),
                teacher.department.name if teacher.department else '',
                teacher.get_designation_display(),
                'Yes' if teacher.cbc_trained else 'No',
                teacher.tpd_current_module,
                teacher.weekly_periods,
                teacher.performance_rating or '',
                teacher.salary_scale or '',
            ])
        
        return response


# ============================================================================
# PUBLIC VIEWS (FOR FRONTEND INTEGRATION)
# ============================================================================

class PublicTeacherListView(generics.ListAPIView):
    """Public view for teacher list (with limited data)"""
    
    queryset = TeacherProfile.objects.filter(
        is_active=True,
        employment_status='active'
    ).select_related('teacher', 'department')
    
    serializer_class = TeacherProfileMinimalSerializer
    permission_classes = [AllowAny]
    pagination_class = TeacherPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['teacher__first_name', 'teacher__last_name', 'tsc_number']
    
    def get_queryset(self):
        """Apply additional filters for public view"""
        queryset = super().get_queryset()
        
        # Only show teachers who have agreed to be publicly listed
        queryset = queryset.filter(teacher__is_public=True)
        
        return queryset


# ============================================================================
# CUSTOM ACTION VIEWS
# ============================================================================

class SendNotificationView(APIView):
    """Send notifications to teachers"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Send notification to selected teachers"""
        teacher_ids = request.data.get('teacher_ids', [])
        message = request.data.get('message', '')
        notification_type = request.data.get('type', 'general')
        
        if not teacher_ids or not message:
            return Response(
                {"detail": "Teacher IDs and message are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teachers = TeacherProfile.objects.filter(
            id__in=teacher_ids,
            is_active=True
        )
        
        sent_count = 0
        failed_count = 0
        
        for teacher in teachers:
            try:
                # In a real implementation, you would send actual notifications
                # via email, SMS, or push notification
                self._send_notification(teacher, message, notification_type)
                sent_count += 1
            except Exception as e:
                failed_count += 1
        
        return Response({
            "detail": f"Notifications sent: {sent_count} successful, {failed_count} failed."
        })
    
    def _send_notification(self, teacher, message, notification_type):
        """Send notification to a teacher"""
        # This is a placeholder for actual notification logic
        # In production, you would integrate with:
        # - Email service (SendGrid, Mailgun)
        # - SMS service (AfricasTalking, Twilio)
        # - Push notifications (Firebase, OneSignal)
        
        # For now, just log the notification
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Notification to {teacher.full_name} ({teacher.tsc_number}): {message}")


class SyncTSCDataView(APIView):
    """Sync teacher data with TSC API"""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Sync teacher data with TSC"""
        teacher_id = request.data.get('teacher_id')
        
        if teacher_id:
            # Sync single teacher
            try:
                teacher = TeacherProfile.objects.get(id=teacher_id)
                result = self._sync_teacher_with_tsc(teacher)
                return Response(result)
            except TeacherProfile.DoesNotExist:
                return Response(
                    {"detail": "Teacher not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Sync all teachers
            teachers = TeacherProfile.objects.filter(
                is_active=True,
                tsc_status__in=['registered', 'provisional']
            )
            
            results = []
            for teacher in teachers:
                try:
                    result = self._sync_teacher_with_tsc(teacher)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'teacher': teacher.full_name,
                        'tsc_number': teacher.tsc_number,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return Response(results)
    
    def _sync_teacher_with_tsc(self, teacher):
        """Sync individual teacher with TSC API"""
        # This is a placeholder for TSC API integration
        # In production, you would make actual API calls to TSC
        
        # Mock implementation
        tsc_data = {
            'status': 'registered',
            'category': teacher.tsc_category,
            'registration_date': teacher.tsc_registration_date.isoformat(),
            'last_updated': timezone.now().isoformat(),
        }
        
        # Update teacher with TSC data
        teacher.tsc_status = tsc_data['status']
        teacher.save()
        
        return {
            'teacher': teacher.full_name,
            'tsc_number': teacher.tsc_number,
            'status': 'synced',
            'data': tsc_data
        }