"""
Academic Views for Kenyan CBC School Management System

This module contains all API views and endpoints for academic management,
including setup checks, data export, and comprehensive reporting.
"""

import csv
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from django.core.cache import cache
from django.db.models import Q, Count, Avg, Max, Min, Sum, Prefetch
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound


from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend


from accounts.models import User
from students.models import StudentProfile
from teachers.models import TeacherProfile
from .models import *
from .serializers import *
from .filters import *
from .permissions import *
from .utils.cache_utils import CacheManager
from .utils.performance_monitor import performance_monitor
from .utils.export_utils import ExportManager

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

class StandardPagination(PageNumberPagination):
    """Standard pagination configuration."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class LargePagination(PageNumberPagination):
    """Pagination for large datasets."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


# ============================================================================
# MIXINS AND BASE CLASSES
# ============================================================================

class CacheMixin:
    """Mixin for caching view responses."""
    
    cache_duration = 60 * 5  # 5 minutes default
    cache_key_prefix = None
    
    def get_cache_key(self, request=None):
        """Generate cache key for this view."""
        if not self.cache_key_prefix:
            self.cache_key_prefix = f"{self.__class__.__name__.lower()}_"
        
        if request:
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            params_str = str(sorted(request.GET.items()))
            return f"{self.cache_key_prefix}{user_id}_{hash(params_str)}"
        return f"{self.cache_key_prefix}default"
    
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PerformanceMixin:
    """Mixin for performance monitoring."""
    
    @performance_monitor
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @performance_monitor
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class BulkOperationsMixin:
    """Mixin for bulk operations."""
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Bulk create objects."""
        serializer = self.get_bulk_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    
    def get_bulk_serializer(self, *args, **kwargs):
        """Get bulk serializer class."""
        raise NotImplementedError("Subclasses must implement get_bulk_serializer")


class ExportMixin:
    """Mixin for data export functionality."""
    
    export_formats = ['csv', 'json', 'excel']
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_data(self, request):
        """Export data in various formats."""
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type not in self.export_formats:
            return Response(
                {'error': f'Invalid format. Available formats: {", ".join(self.export_formats)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return ExportManager.export_data(
            data=serializer.data,
            format_type=format_type,
            filename=self.get_export_filename(),
            model_name=self.queryset.model.__name__
        )
    
    def get_export_filename(self):
        """Get export filename."""
        return f"{self.queryset.model.__name__.lower()}_export"


class BaseViewSet(
    CacheMixin,
    PerformanceMixin,
    ExportMixin,
    viewsets.ModelViewSet
):
    """Base ViewSet with common configuration."""
    
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = StandardPagination
    filter_backends = [
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ]
    
    def get_queryset(self):
        """Override to apply common filters."""
        queryset = super().get_queryset()
        return queryset.filter(is_active=True)


# ============================================================================
# ACADEMIC STRUCTURE VIEWSETS
# ============================================================================

class AcademicYearViewSet(BaseViewSet):
    """ViewSet for AcademicYear model."""
    
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filterset_class = AcademicYearFilter
    search_fields = ['name', 'academic_year', 'code']
    ordering_fields = ['start_date', 'end_date', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('current_academic_year').prefetch_related('terms')
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Set this academic year as current."""
        academic_year = self.get_object()
        AcademicYear.objects.filter(is_current=True).update(is_current=False)
        academic_year.is_current = True
        academic_year.save()
        
        return Response({
            'status': 'success',
            'message': f'{academic_year.name} set as current academic year',
            'academic_year': AcademicYearSerializer(academic_year).data
        })
    
    @action(detail=True, methods=['get'])
    def terms(self, request, pk=None):
        """Get all terms for this academic year."""
        academic_year = self.get_object()
        terms = academic_year.academic_terms.all()
        serializer = AcademicTermSerializer(terms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this academic year."""
        academic_year = self.get_object()
        
        stats = {
            'total_terms': academic_year.academic_terms.count(),
            'total_classes': Class.objects.filter(
                academic_year=academic_year.academic_year
            ).count(),
            'total_enrollments': Enrollment.objects.filter(
                academic_year=academic_year.academic_year
            ).count(),
            'total_assessments': Assessment.objects.filter(
                academic_year=academic_year.academic_year
            ).count(),
        }
        
        return Response(stats)


class AcademicTermViewSet(BaseViewSet):
    """ViewSet for AcademicTerm model."""
    
    queryset = AcademicTerm.objects.all()
    serializer_class = AcademicTermSerializer
    filterset_class = AcademicTermFilter
    search_fields = ['name', 'academic_year__name', 'term_type']
    ordering_fields = ['start_date', 'end_date', 'term_type']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('academic_year')
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Set this term as current."""
        term = self.get_object()
        AcademicTerm.objects.filter(
            academic_year=term.academic_year,
            is_current=True
        ).update(is_current=False)
        term.is_current = True
        term.save()
        
        return Response({
            'status': 'success',
            'message': f'{term.name} set as current term',
            'term': AcademicTermSerializer(term).data
        })
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get schedule for this term."""
        term = self.get_object()
        schedules = term.schedules.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get attendance summary for this term."""
        term = self.get_object()
        summary = term.get_attendance_summary()
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def performance_summary(self, request, pk=None):
        """Get performance summary for this term."""
        term = self.get_object()
        summary = term.get_performance_summary()
        return Response(summary)


class GradeLevelViewSet(BaseViewSet):
    """ViewSet for GradeLevel model."""
    
    queryset = GradeLevel.objects.all()
    serializer_class = GradeLevelSerializer
    filterset_class = GradeLevelFilter
    search_fields = ['name', 'code', 'level']
    ordering_fields = ['order', 'level', 'name']
    
    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """Get classes for this grade level."""
        grade_level = self.get_object()
        classes = grade_level.classes.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get subjects for this grade level."""
        grade_level = self.get_object()
        subjects = grade_level.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def competency_areas(self, request, pk=None):
        """Get competency areas for this grade level."""
        grade_level = self.get_object()
        competency_areas = grade_level.competency_areas.all()
        serializer = CompetencyAreaSerializer(competency_areas, many=True)
        return Response(serializer.data)


class SubjectViewSet(BaseViewSet):
    """ViewSet for Subject model."""
    
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filterset_class = SubjectFilter
    search_fields = ['name', 'code', 'description', 'category']
    ordering_fields = ['name', 'code', 'is_core', 'category']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('grade_levels', 'prerequisites')
    
    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        """Get teachers for this subject."""
        subject = self.get_object()
        teachers = subject.get_teachers()
        serializer = UserBasicSerializer(teachers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get assessments for this subject."""
        subject = self.get_object()
        assessments = subject.assessments.all()
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance statistics for this subject."""
        subject = self.get_object()
        
        performance_data = {
            'average_score': subject.get_average_score(),
            'student_count': subject.get_student_count(),
            'pass_rate': self.calculate_pass_rate(subject),
        }
        
        return Response(performance_data)
    
    def calculate_pass_rate(self, subject):
        """Calculate pass rate for a subject."""
        grades = Grade.objects.filter(subject=subject)
        total = grades.count()
        if total == 0:
            return 0
        passed = grades.filter(is_passing=True).count()
        return (passed / total) * 100


# ============================================================================
# CLASS AND GROUPING VIEWSETS
# ============================================================================

class ClassViewSet(BaseViewSet):
    """ViewSet for Class model."""
    
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filterset_class = ClassFilter
    search_fields = ['name', 'code', 'grade_level__name']
    ordering_fields = ['name', 'code', 'grade_level__order']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'grade_level', 'form_teacher', 'assistant_teacher', 'classroom'
        ).prefetch_related('enrollments')
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students in this class."""
        class_obj = self.get_object()
        enrollments = class_obj.enrollments.filter(status='active')
        students = [enrollment.student for enrollment in enrollments]
        serializer = StudentMinimalSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get subjects taught in this class."""
        class_obj = self.get_object()
        subjects = class_obj.get_subjects()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """Get timetable for this class."""
        class_obj = self.get_object()
        timetable = Schedule.objects.filter(
            class_assigned=class_obj,
            academic_year=class_obj.academic_year,
            term=class_obj.term,
            is_active=True
        )
        serializer = ScheduleSerializer(timetable, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get attendance summary for this class."""
        class_obj = self.get_object()
        summary = class_obj.get_attendance_summary()
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def performance_summary(self, request, pk=None):
        """Get performance summary for this class."""
        class_obj = self.get_object()
        summary = class_obj.get_average_performance()
        return Response(summary)


# ============================================================================
# ENROLLMENT VIEWSETS
# ============================================================================

class EnrollmentViewSet(BaseViewSet):
    """ViewSet for Enrollment model."""
    
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filterset_class = EnrollmentFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'class_assigned__name', 'enrollment_number'
    ]
    ordering_fields = ['enrollment_date', 'status', 'academic_status']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'student', 'class_assigned', 'created_by'
        ).prefetch_related('subject_enrollments')
    
    @action(detail=True, methods=['get'])
    def academic_performance(self, request, pk=None):
        """Get academic performance for this enrollment."""
        enrollment = self.get_object()
        performance = enrollment.get_academic_performance()
        return Response(performance)
    
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get attendance summary for this enrollment."""
        enrollment = self.get_object()
        summary = enrollment.get_attendance_summary()
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def subject_enrollments(self, request, pk=None):
        """Get subject enrollments for this enrollment."""
        enrollment = self.get_object()
        subject_enrollments = enrollment.subject_enrollments.all()
        serializer = SubjectEnrollmentSerializer(subject_enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change enrollment status."""
        enrollment = self.get_object()
        new_status = request.data.get('status')
        remarks = request.data.get('remarks', '')
        
        if new_status not in dict(Enrollment._meta.get_field('status').choices):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = new_status
        if remarks:
            enrollment.remarks = remarks
        enrollment.save()
        
        return Response({
            'status': 'success',
            'message': f'Enrollment status changed to {new_status}',
            'enrollment': EnrollmentSerializer(enrollment).data
        })


class EnrollmentBulkViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet for bulk enrollment operations."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Bulk create enrollments."""
        serializer = EnrollmentBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# ASSESSMENT AND GRADING VIEWSETS
# ============================================================================

class AssessmentViewSet(BaseViewSet):
    """ViewSet for Assessment model."""
    
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    filterset_class = AssessmentFilter
    search_fields = ['name', 'code', 'subject__name', 'description']
    ordering_fields = ['date', 'assessment_type', 'total_marks']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'subject', 'class_assigned', 'created_by'
        ).prefetch_related('grades')
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish assessment results."""
        assessment = self.get_object()
        assessment.publish_results()
        
        return Response({
            'status': 'success',
            'message': 'Assessment results published',
            'assessment': AssessmentSerializer(assessment).data
        })
    
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """Get grades for this assessment."""
        assessment = self.get_object()
        grades = assessment.grades.all()
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this assessment."""
        assessment = self.get_object()
        
        statistics = {
            'class_average': assessment.get_class_average(),
            'pass_rate': assessment.get_pass_rate(),
            'total_students': assessment.grades.count(),
            'top_performers': [
                {
                    'student': grade.student.get_full_name(),
                    'score': grade.score,
                    'grade': grade.grade
                }
                for grade in assessment.get_top_performers(limit=5)
            ]
        }
        
        return Response(statistics)


class GradeViewSet(BaseViewSet):
    """ViewSet for Grade model."""
    
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filterset_class = GradeFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'assessment__name', 'subject__name'
    ]
    ordering_fields = ['score', 'percentage', 'grade']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'student', 'assessment', 'subject',
            'class_assigned', 'enrollment', 'graded_by'
        )


class GradeBulkViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet for bulk grade operations."""
    
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Bulk create grades."""
        serializer = GradeBulkCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)


class TranscriptViewSet(BaseViewSet):
    """ViewSet for Transcript model."""
    
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    filterset_class = TranscriptFilter
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['academic_year', 'gpa', 'class_rank']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'student', 'generated_by'
        )
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate transcript."""
        transcript = self.get_object()
        transcript.calculate_gpa()
        transcript.calculate_cgpa()
        transcript.update_ranks()
        transcript.save()
        
        return Response({
            'status': 'success',
            'message': 'Transcript generated successfully',
            'transcript': TranscriptSerializer(transcript).data
        })


# ============================================================================
# ATTENDANCE VIEWSETS
# ============================================================================

class AttendanceViewSet(BaseViewSet):
    """ViewSet for Attendance model."""
    
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filterset_class = AttendanceFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'reason', 'remarks'
    ]
    ordering_fields = ['date', 'status', 'check_in_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'student', 'enrollment', 'class_assigned', 'verified_by'
        )
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Bulk create attendance records."""
        serializer = AttendanceBulkCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='daily-summary')
    def daily_summary(self, request):
        """Get daily attendance summary."""
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance = Attendance.objects.filter(date=date)
        summary = attendance.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused'))
        )
        
        attendance_rate = (
            (summary['present'] / summary['total'] * 100)
            if summary['total'] > 0 else 0
        )
        
        return Response({
            'date': date,
            'summary': summary,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    @action(detail=False, methods=['get'], url_path='class-summary')
    def class_summary(self, request):
        """Get class attendance summary."""
        class_id = request.query_params.get('class_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date().isoformat())
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            class_obj = Class.objects.get(id=class_id)
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (Class.DoesNotExist, ValueError):
            return Response(
                {'error': 'Invalid parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summary = Attendance.get_class_attendance_summary(
            class_obj,
            start_date or class_obj.created_at.date(),
            end_date
        )
        
        return Response(summary)


class AttendanceReportViewSet(BaseViewSet):
    """ViewSet for AttendanceReport model."""
    
    queryset = AttendanceReport.objects.all()
    serializer_class = AttendanceReportSerializer
    filterset_class = AttendanceReportFilter
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['period_end', 'attendance_percentage']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('student', 'enrollment', 'generated_by')
    
    @action(detail=True, methods=['post'])
    def update_statistics(self, request, pk=None):
        """Update attendance statistics."""
        report = self.get_object()
        report.update_statistics()
        report.detect_patterns()
        report.save()
        
        return Response({
            'status': 'success',
            'message': 'Attendance statistics updated',
            'report': AttendanceReportSerializer(report).data
        })
    
    @action(detail=True, methods=['post'])
    def notify_parent(self, request, pk=None):
        """Notify parent about attendance issues."""
        report = self.get_object()
        success = report.notify_parent()
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Parent notified successfully'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to notify parent or already notified'
            })


# ============================================================================
# TIMETABLE AND SCHEDULING VIEWSETS
# ============================================================================

class ScheduleViewSet(BaseViewSet):
    """ViewSet for Schedule model."""
    
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    filterset_class = ScheduleFilter
    search_fields = [
        'subject__name', 'teacher__first_name',
        'teacher__last_name', 'class_assigned__name'
    ]
    ordering_fields = ['day_of_week', 'start_time', 'end_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'class_assigned', 'subject', 'teacher', 'classroom'
        )
    
    @action(detail=False, methods=['get'], url_path='class-timetable')
    def class_timetable(self, request):
        """Get timetable for a class."""
        class_id = request.query_params.get('class_id')
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                {'error': 'Class not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        timetable = Schedule.get_class_timetable(class_obj)
        serializer = ScheduleSerializer(timetable, many=True)
        
        return Response({
            'class': ClassSerializer(class_obj).data,
            'timetable': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='teacher-timetable')
    def teacher_timetable(self, request):
        """Get timetable for a teacher."""
        teacher_id = request.query_params.get('teacher_id')
        
        if not teacher_id:
            return Response(
                {'error': 'teacher_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            teacher = User.objects.get(id=teacher_id, role='teacher')
        except User.DoesNotExist:
            return Response(
                {'error': 'Teacher not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        timetable = Schedule.get_teacher_timetable(teacher)
        serializer = ScheduleSerializer(timetable, many=True)
        
        return Response({
            'teacher': UserBasicSerializer(teacher).data,
            'timetable': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='weekly-schedule')
    def weekly_schedule(self, request):
        """Generate weekly schedule for a class."""
        class_id = request.query_params.get('class_id')
        academic_year = request.query_params.get('academic_year')
        term = request.query_params.get('term')
        
        if not all([class_id, academic_year, term]):
            return Response(
                {'error': 'class_id, academic_year, and term are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                {'error': 'Class not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        schedule_data = Schedule.generate_weekly_schedule(
            class_obj, academic_year, term
        )
        
        return Response({
            'class': ClassSerializer(class_obj).data,
            'academic_year': academic_year,
            'term': term,
            'weekly_schedule': schedule_data
        })


class TeacherAssignmentViewSet(BaseViewSet):
    """ViewSet for TeacherAssignment model."""
    
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    filterset_class = TeacherAssignmentFilter
    search_fields = [
        'teacher__first_name', 'teacher__last_name',
        'subject__name', 'class_assigned__name'
    ]
    ordering_fields = ['start_date', 'end_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'teacher', 'subject', 'class_assigned'
        )


# ============================================================================
# COMPETENCY-BASED EDUCATION VIEWSETS
# ============================================================================

class CompetencyAreaViewSet(BaseViewSet):
    """ViewSet for CompetencyArea model."""
    
    queryset = CompetencyArea.objects.all()
    serializer_class = CompetencyAreaSerializer
    filterset_class = CompetencyAreaFilter
    search_fields = ['name', 'code', 'description', 'curriculum']
    ordering_fields = ['name', 'code', 'order', 'curriculum']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('grade_levels', 'subjects', 'child_areas')
    
    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get competency assessments for this area."""
        competency_area = self.get_object()
        assessments = competency_area.competency_assessments.all()
        serializer = CompetencyAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this competency area."""
        competency_area = self.get_object()
        
        assessments = competency_area.competency_assessments.all()
        if assessments.exists():
            avg_score = assessments.aggregate(Avg('score'))['score__avg']
            total_students = assessments.values('student').distinct().count()
        else:
            avg_score = 0
            total_students = 0
        
        return Response({
            'competency_area': competency_area.name,
            'average_score': avg_score,
            'total_students': total_students,
            'student_count': competency_area.student_count,
            'levels': competency_area.get_competency_levels()
        })


class CompetencyAssessmentViewSet(BaseViewSet):
    """ViewSet for CompetencyAssessment model."""
    
    queryset = CompetencyAssessment.objects.all()
    serializer_class = CompetencyAssessmentSerializer
    filterset_class = CompetencyAssessmentFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'competency_area__name', 'level'
    ]
    ordering_fields = ['score', 'assessment_date', 'level']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'student', 'competency_area', 'grade_level',
            'assessed_by', 'verified_by'
        )


# ============================================================================
# INFRASTRUCTURE VIEWSETS
# ============================================================================

class ClassroomViewSet(BaseViewSet):
    """ViewSet for Classroom model."""
    
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filterset_class = ClassroomFilter
    search_fields = ['room_number', 'name', 'building', 'description']
    ordering_fields = ['building', 'floor', 'room_number', 'capacity']
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get schedule for this classroom."""
        classroom = self.get_object()
        schedule = classroom.get_schedule()
        serializer = ScheduleSerializer(schedule, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def current_usage(self, request, pk=None):
        """Get current usage of this classroom."""
        classroom = self.get_object()
        current_class = classroom.current_class
        
        if current_class:
            return Response({
                'is_occupied': True,
                'current_class': {
                    'id': current_class.id,
                    'name': current_class.name,
                    'subject': current_class.subject.name if hasattr(current_class, 'subject') else None,
                    'teacher': current_class.teacher.get_full_name() if current_class.teacher else None,
                    'start_time': current_class.schedule.start_time if hasattr(current_class, 'schedule') else None,
                    'end_time': current_class.schedule.end_time if hasattr(current_class, 'schedule') else None,
                }
            })
        else:
            return Response({
                'is_occupied': False,
                'current_class': None
            })


# ============================================================================
# ACADEMIC REPORT VIEWSETS
# ============================================================================

class AcademicReportViewSet(BaseViewSet):
    """ViewSet for AcademicReport model."""
    
    queryset = AcademicReport.objects.all()
    serializer_class = AcademicReportSerializer
    filterset_class = AcademicReportFilter
    search_fields = [
        'student__first_name', 'student__last_name',
        'form_teacher_comment', 'head_teacher_comment'
    ]
    ordering_fields = ['academic_year', 'gpa', 'overall_score']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('student', 'enrollment', 'generated_by')
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate academic report."""
        report = self.get_object()
        report.generate_report()
        report.save()
        
        return Response({
            'status': 'success',
            'message': 'Academic report generated',
            'report': AcademicReportSerializer(report).data
        })
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish academic report."""
        report = self.get_object()
        report.publish_report()
        
        return Response({
            'status': 'success',
            'message': 'Academic report published',
            'report': AcademicReportSerializer(report).data
        })


# ============================================================================
# EVENT AND CONFIGURATION VIEWSETS
# ============================================================================

class AcademicEventViewSet(BaseViewSet):
    """ViewSet for AcademicEvent model."""
    
    queryset = AcademicEvent.objects.all()
    serializer_class = AcademicEventSerializer
    filterset_class = AcademicEventFilter
    search_fields = ['title', 'description', 'location', 'organizer']
    ordering_fields = ['start_date', 'end_date', 'event_type']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('participants', 'affected_classes')
    
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming_events(self, request):
        """Get upcoming events."""
        days = int(request.query_params.get('days', 30))
        events = AcademicEvent.get_upcoming_events(days)
        serializer = AcademicEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-date')
    def events_by_date(self, request):
        """Get events for a specific date."""
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        events = AcademicEvent.get_events_for_date(date)
        serializer = AcademicEventSerializer(events, many=True)
        return Response(serializer.data)


class GradingScaleViewSet(BaseViewSet):
    """ViewSet for GradingScale model."""
    
    queryset = GradingScale.objects.all()
    serializer_class = GradingScaleSerializer
    filterset_class = GradingScaleFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'scale_type', 'academic_level']
    
    @action(detail=True, methods=['get'])
    def calculate_grade(self, request, pk=None):
        """Calculate grade for a given score."""
        grading_scale = self.get_object()
        score = request.query_params.get('score')
        max_score = request.query_params.get('max_score', 100)
        
        if not score:
            return Response(
                {'error': 'score parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            score = float(score)
            max_score = float(max_score)
        except ValueError:
            return Response(
                {'error': 'score and max_score must be numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grade_info = grading_scale.get_grade_for_score(score, max_score)
        
        if grade_info:
            return Response(grade_info)
        else:
            return Response(
                {'error': 'Unable to calculate grade for given score'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AcademicConfigurationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet for AcademicConfiguration model."""
    
    queryset = AcademicConfiguration.objects.all()
    serializer_class = AcademicConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_object(self):
        """Always return the single configuration instance."""
        return AcademicConfiguration.load()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current academic configuration."""
        config = self.get_object()
        serializer = self.get_serializer(config)
        return Response(serializer.data)


# ============================================================================
# SETUP AND HEALTH CHECK API VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def setup_check(request):
    """Check if academic system is properly set up."""
    checks = {
        'academic_years': AcademicYear.objects.filter(is_active=True).exists(),
        'academic_terms': AcademicTerm.objects.filter(is_active=True).exists(),
        'grade_levels': GradeLevel.objects.filter(is_active=True).exists(),
        'subjects': Subject.objects.filter(is_active=True).exists(),
        'classrooms': Classroom.objects.filter(is_active=True).exists(),
        'competency_areas': CompetencyArea.objects.filter(is_active=True).exists(),
        'current_academic_year': AcademicYear.objects.filter(is_current=True).exists(),
        'current_academic_term': AcademicTerm.objects.filter(is_current=True).exists(),
    }
    
    is_setup_complete = all(checks.values())
    
    # Identify missing setup items
    missing_items = []
    for key, exists in checks.items():
        if not exists:
            missing_items.append({
                'name': key.replace('_', ' ').title(),
                'key': key,
                'priority': 1 if key in ['academic_years', 'grade_levels', 'subjects'] else 2
            })
    
    return Response({
        'is_setup_complete': is_setup_complete,
        'checks': checks,
        'missing_items': missing_items,
        'missing_count': len(missing_items),
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 2)  # Cache for 2 minutes
def essential_data(request):
    """Get essential data for initial UI rendering."""
    data = {}
    
    # Academic years
    data['academic_years'] = list(
        AcademicYear.objects.filter(is_active=True)
        .values('id', 'name', 'academic_year', 'is_current')
        .order_by('-start_date')[:10]
    )
    
    # Current academic year
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if current_year:
        data['current_year'] = {
            'id': current_year.id,
            'name': current_year.name,
            'academic_year': current_year.academic_year,
        }
    
    # Grade levels
    data['grade_levels'] = list(
        GradeLevel.objects.filter(is_active=True)
        .values('id', 'name', 'code', 'level')
        .order_by('order')[:12]
    )
    
    # Subjects
    data['subjects'] = list(
        Subject.objects.filter(is_active=True)
        .values('id', 'name', 'code', 'category')
        .order_by('name')[:50]
    )
    
    # Classrooms
    data['classrooms'] = list(
        Classroom.objects.filter(is_active=True)
        .values('id', 'name', 'room_number', 'capacity', 'building')
        .order_by('building', 'room_number')[:30]
    )
    
    # Competency areas
    data['competency_areas'] = list(
        CompetencyArea.objects.filter(is_active=True)
        .values('id', 'name', 'code', 'curriculum')
        .order_by('name')[:20]
    )
    
    return Response({
        'data': data,
        'counts': {key: len(value) for key, value in data.items()},
        'has_minimum_data': (
            len(data.get('grade_levels', [])) > 0 and
            len(data.get('subjects', [])) > 0
        ),
        'timestamp': timezone.now().isoformat()
    })


# ============================================================================
# DASHBOARD AND ANALYTICS API VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_statistics(request):
    """Get dashboard statistics."""
    today = timezone.now().date()
    
    # Get current academic year
    current_year = AcademicYear.get_current_academic_year()
    current_term = AcademicTerm.get_current_term() if current_year else None
    
    # Counts
    total_students = User.objects.filter(role='student', is_active=True).count()
    total_teachers = User.objects.filter(role='teacher', is_active=True).count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(date=today)
    attendance_summary = today_attendance.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    )
    
    attendance_rate = (
        (attendance_summary['present'] / attendance_summary['total'] * 100)
        if attendance_summary['total'] > 0 else 0
    )
    
    # Performance statistics
    grades = Grade.objects.all()
    avg_score = grades.aggregate(Avg('score'))['score__avg'] or 0
    
    # Upcoming assessments
    upcoming_assessments = Assessment.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=7)
    ).count()
    
    # Upcoming events
    upcoming_events = AcademicEvent.get_upcoming_events(days=7).count()
    
    statistics = {
        'overview': {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'total_subjects': total_subjects,
        },
        'attendance': {
            'today_total': attendance_summary['total'],
            'today_present': attendance_summary['present'],
            'today_absent': attendance_summary['absent'],
            'today_late': attendance_summary['late'],
            'attendance_rate': round(attendance_rate, 2),
        },
        'performance': {
            'average_score': round(avg_score, 2),
            'total_assessments': grades.count(),
        },
        'upcoming': {
            'assessments': upcoming_assessments,
            'events': upcoming_events,
        },
        'current_academic': {
            'year': current_year.name if current_year else None,
            'term': current_term.name if current_term else None,
        },
        'date': today.isoformat()
    }
    
    return Response(statistics)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_performance(request):
    """Get class performance analysis."""
    academic_year = request.query_params.get('academic_year')
    term = request.query_params.get('term')
    
    classes = Class.objects.all()
    
    if academic_year:
        classes = classes.filter(academic_year=academic_year)
    if term:
        classes = classes.filter(term=term)
    
    performance_data = []
    
    for class_obj in classes:
        # Get grades for this class
        grades = Grade.objects.filter(class_assigned=class_obj)
        
        if grades.exists():
            stats = grades.aggregate(
                avg_score=Avg('score'),
                highest_score=Max('score'),
                lowest_score=Min('score'),
                total_students=Count('student', distinct=True)
            )
            
            # Calculate pass rate
            total_grades = grades.count()
            passing_grades = grades.filter(is_passing=True).count()
            pass_rate = (passing_grades / total_grades * 100) if total_grades > 0 else 0
            
            # Attendance rate
            attendance_summary = class_obj.get_attendance_summary()
            
            performance_data.append({
                'class_id': class_obj.id,
                'class_name': class_obj.name,
                'grade_level': class_obj.grade_level.name,
                'total_students': class_obj.students_count,
                'average_score': round(stats['avg_score'] or 0, 2),
                'highest_score': stats['highest_score'] or 0,
                'lowest_score': stats['lowest_score'] or 0,
                'pass_rate': round(pass_rate, 2),
                'attendance_rate': attendance_summary.get('attendance_rate', 0),
            })
    
    return Response(performance_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_progress(request, student_id):
    """Get student progress tracking."""
    try:
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get student's enrollments
    enrollments = Enrollment.objects.filter(student=student, status='active')
    
    if not enrollments.exists():
        return Response(
            {'error': 'Student has no active enrollments'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    current_enrollment = enrollments.latest('enrollment_date')
    
    # Get grades
    grades = Grade.objects.filter(student=student)
    
    # Get attendance
    attendance = Attendance.objects.filter(student=student)
    
    # Calculate statistics
    if grades.exists():
        avg_score = grades.aggregate(Avg('score'))['score__avg']
        improvement_rate = self.calculate_improvement_rate(grades)
    else:
        avg_score = 0
        improvement_rate = 0
    
    if attendance.exists():
        attendance_summary = attendance.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present'))
        )
        attendance_percentage = (
            attendance_summary['present'] / attendance_summary['total'] * 100
            if attendance_summary['total'] > 0 else 0
        )
    else:
        attendance_percentage = 0
    
    # Subject progress
    subject_progress = []
    for enrollment in enrollments:
        subject_enrollments = enrollment.subject_enrollments.all()
        for se in subject_enrollments:
            subject_grades = grades.filter(subject=se.subject)
            if subject_grades.exists():
                subject_avg = subject_grades.aggregate(Avg('score'))['score__avg']
                subject_progress.append({
                    'subject': se.subject.name,
                    'average_score': subject_avg or 0,
                    'grade': se.grade,
                    'is_passing': se.score >= se.subject.passing_score if se.score else False,
                })
    
    progress_data = {
        'student': {
            'id': student.id,
            'name': student.get_full_name(),
            'student_id': student.student_id,
        },
        'current_class': current_enrollment.class_assigned.name,
        'current_grade_level': current_enrollment.class_assigned.grade_level.name,
        'current_gpa': self.calculate_gpa(grades),
        'attendance_percentage': round(attendance_percentage, 2),
        'improvement_rate': round(improvement_rate, 2),
        'subject_progress': subject_progress,
        'predicted_grade': self.predict_grade(avg_score, improvement_rate),
        'timestamp': timezone.now().isoformat()
    }
    
    return Response(progress_data)


# ============================================================================
# EXPORT API VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_grades(request):
    """Export grades as CSV."""
    academic_year = request.query_params.get('academic_year')
    term = request.query_params.get('term')
    class_id = request.query_params.get('class_id')
    
    grades = Grade.objects.all()
    
    if academic_year:
        grades = grades.filter(academic_year=academic_year)
    if term:
        grades = grades.filter(term=term)
    if class_id:
        grades = grades.filter(class_assigned_id=class_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grades_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Class',
        'Subject', 'Assessment', 'Score',
        'Grade', 'Percentage', 'Assessment Date',
        'Graded By'
    ])
    
    for grade in grades.select_related(
        'student', 'class_assigned', 'subject',
        'assessment', 'graded_by'
    ):
        writer.writerow([
            grade.student.student_id,
            grade.student.get_full_name(),
            grade.class_assigned.name,
            grade.subject.name,
            grade.assessment.name,
            grade.score,
            grade.grade,
            grade.percentage,
            grade.assessment.date,
            grade.graded_by.get_full_name() if grade.graded_by else ''
        ])
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_attendance(request):
    """Export attendance as CSV."""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    class_id = request.query_params.get('class_id')
    
    attendance = Attendance.objects.all()
    
    if start_date:
        attendance = attendance.filter(date__gte=start_date)
    if end_date:
        attendance = attendance.filter(date__lte=end_date)
    if class_id:
        attendance = attendance.filter(class_assigned_id=class_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Class',
        'Date', 'Status', 'Check-in Time',
        'Check-out Time', 'Reason', 'Verified By'
    ])
    
    for record in attendance.select_related(
        'student', 'class_assigned', 'verified_by'
    ):
        writer.writerow([
            record.student.student_id,
            record.student.get_full_name(),
            record.class_assigned.name,
            record.date,
            record.get_status_display(),
            record.check_in_time or '',
            record.check_out_time or '',
            record.reason or '',
            record.verified_by.get_full_name() if record.verified_by else ''
        ])
    
    return response


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_improvement_rate(grades):
    """Calculate improvement rate based on recent grades."""
    if not grades.exists():
        return 0
    
    # Get latest grades (last 5 assessments)
    latest_grades = list(grades.order_by('-assessment__date')[:5])
    
    if len(latest_grades) < 2:
        return 0
    
    # Calculate improvement between first and last
    first_score = latest_grades[-1].score
    last_score = latest_grades[0].score
    
    if first_score == 0:
        return 0
    
    improvement = ((last_score - first_score) / first_score) * 100
    return improvement


def calculate_gpa(grades):
    """Calculate GPA from grades."""
    if not grades.exists():
        return 0
    
    total_grade_points = 0
    total_weight = 0
    
    for grade in grades:
        if grade.grade_point:
            weight = grade.assessment.weight or 1
            total_grade_points += grade.grade_point * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0
    
    return total_grade_points / total_weight


def predict_grade(current_score, improvement_rate):
    """Predict final grade based on current score and improvement rate."""
    if not current_score:
        return None
    
    predicted_score = current_score * (1 + improvement_rate / 100)
    
    if predicted_score >= 90:
        return 'A+'
    elif predicted_score >= 80:
        return 'A'
    elif predicted_score >= 70:
        return 'B+'
    elif predicted_score >= 60:
        return 'B'
    elif predicted_score >= 50:
        return 'C+'
    elif predicted_score >= 40:
        return 'C'
    elif predicted_score >= 30:
        return 'D'
    else:
        return 'F'