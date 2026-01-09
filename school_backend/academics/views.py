# academics/views.py
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q, F, Sum, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import csv

from .models import (
    AcademicYear, AcademicTerm, Subject, Class, SubjectAssignment,
    StudentEnrollment, LessonPlan, Syllabus, AcademicEvent
)
from .serializers import (
    AcademicTermMinimalSerializer, AcademicYearSerializer, AcademicYearDetailSerializer,
    AcademicTermSerializer, AcademicTermDetailSerializer,
    SubjectSerializer, SubjectDetailSerializer,
    ClassSerializer, ClassDetailSerializer,
    SubjectAssignmentSerializer, StudentEnrollmentSerializer,
    LessonPlanSerializer, SyllabusSerializer, AcademicEventSerializer,
    AcademicStatisticsSerializer, ClassStatisticsSerializer,
    TeacherWorkloadSerializer, BulkStudentEnrollmentSerializer,
    BulkSubjectAssignmentSerializer, AcademicSearchSerializer,
    EnrollmentReportSerializer
)
from students.models import StudentProfile
from teachers.models import TeacherProfile
from accounts.models import User
# In academics/views.py - ADD THIS BEFORE THE VIEWSETS

from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from accounts.models import User

class IsTeacherOrAdmin(IsAuthenticated):
    """Check if user is teacher or admin."""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Admin users have access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Teachers have access
        if hasattr(request.user, 'role'):
            return request.user.role in [User.Role.TEACHER, User.Role.ADMIN]
        
        # Check if user has teacher profile
        return hasattr(request.user, 'teacher_profile')

class BaseAcademicViewSet(viewsets.ModelViewSet):
    """Base ViewSet for academic models with common functionality."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Apply academic year filtering to all querysets."""
        queryset = super().get_queryset()
        academic_year = self.request.query_params.get('academic_year')
        
        if academic_year and hasattr(self.model, 'academic_year'):
            queryset = queryset.filter(academic_year_id=academic_year)
        
        return queryset


class AcademicYearViewSet(BaseAcademicViewSet):
    """
    ViewSet for comprehensive Academic Year management
    """
    
    queryset = AcademicYear.objects.all().order_by('-start_date')
    filterset_fields = ['is_current', 'is_active']
    search_fields = ['name', 'description', 'code']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['-start_date']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return AcademicYearDetailSerializer
        return AcademicYearSerializer

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """
        Set this academic year as current and unset all others.
        """
        # Unset current flag from all academic years
        AcademicYear.objects.filter(is_current=True).update(is_current=False)
        
        # Set this academic year as current
        academic_year = self.get_object()
        academic_year.is_current = True
        academic_year.save()
        
        serializer = self.get_serializer(academic_year)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current academic year with detailed information.
        """
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return Response(
                {'detail': 'No current academic year set'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get related data efficiently
        current_year = AcademicYear.objects.prefetch_related(
            Prefetch('terms', queryset=AcademicTerm.objects.filter(is_current=True)),
            Prefetch('classes', queryset=Class.objects.all()),
            Prefetch('academic_events', queryset=AcademicEvent.objects.filter(
                start_date__gte=timezone.now().date()
            )[:10])
        ).get(id=current_year.id)
        
        serializer = AcademicYearDetailSerializer(current_year)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get comprehensive statistics for an academic year.
        """
        academic_year = self.get_object()
        
        # Optimize queries using aggregation
        class_stats = Class.objects.filter(academic_year=academic_year).aggregate(
            total_classes=Count('id'),
            total_capacity=Sum('capacity')
        )
        
        enrollment_stats = StudentEnrollment.objects.filter(
            academic_year=academic_year,
            status='active'
        ).aggregate(
            total_students=Count('id'),
            male_students=Count('id', filter=Q(student__student_profile__gender='male')),
            female_students=Count('id', filter=Q(student__student_profile__gender='female'))
        )
        
        teacher_stats = TeacherProfile.objects.filter(is_active=True).aggregate(
            total_teachers=Count('id'),
            full_time=Count('id', filter=Q(employment_type='full_time')),
            part_time=Count('id', filter=Q(employment_type='part_time'))
        )
        
        event_stats = AcademicEvent.objects.filter(academic_year=academic_year).aggregate(
            total_events=Count('id'),
            upcoming_events=Count('id', filter=Q(start_date__gte=timezone.now().date()))
        )
        
        lesson_plan_stats = LessonPlan.objects.filter(
            academic_year=academic_year
        ).aggregate(
            total_plans=Count('id'),
            completed_plans=Count('id', filter=Q(is_completed=True))
        )
        
        stats = {
            'academic_year': {
                'name': academic_year.name,
                'duration_days': academic_year.duration_days,
                'progress_percentage': academic_year.progress_percentage
            },
            'classes': class_stats,
            'enrollments': enrollment_stats,
            'teachers': teacher_stats,
            'events': event_stats,
            'lesson_plans': lesson_plan_stats,
            'subject_stats': self._get_subject_statistics(academic_year),
            'class_distribution': self._get_class_distribution(academic_year)
        }
        
        return Response(stats)

    def _get_subject_statistics(self, academic_year):
        """Get subject statistics for the academic year."""
        return SubjectAssignment.objects.filter(
            academic_year=academic_year,
            is_active=True
        ).values(
            'subject__category'
        ).annotate(
            count=Count('subject_id', distinct=True),
            total_periods=Sum('periods_per_week')
        ).order_by('subject__category')

    def _get_class_distribution(self, academic_year):
        """Get class distribution statistics."""
        return Class.objects.filter(
            academic_year=academic_year
        ).values(
            'grade_level'
        ).annotate(
            class_count=Count('id'),
            total_students=Sum('current_strength'),
            avg_occupancy=Avg('occupancy_rate')
        ).order_by('grade_level')


class AcademicTermViewSet(BaseAcademicViewSet):
    """
    ViewSet for Academic Term management.
    """
    
    queryset = AcademicTerm.objects.all().order_by('academic_year', 'term_order')
    filterset_fields = ['academic_year', 'is_current', 'is_active']
    search_fields = ['name', 'academic_year__name', 'academic_year__code']
    ordering_fields = ['start_date', 'end_date', 'term_order']
    ordering = ['academic_year', 'term_order']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return AcademicTermDetailSerializer
        return AcademicTermSerializer

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """
        Set this term as current within its academic year.
        """
        term = self.get_object()
        
        # Unset current flag from all terms in the same academic year
        AcademicTerm.objects.filter(
            academic_year=term.academic_year,
            is_current=True
        ).update(is_current=False)
        
        # Set this term as current
        term.is_current = True
        term.save()
        
        serializer = self.get_serializer(term)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """
        Get events for a specific term with pagination.
        """
        term = self.get_object()
        page = self.paginate_queryset(term.academic_events.all())
        
        if page is not None:
            serializer = AcademicEventSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AcademicEventSerializer(term.academic_events.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Get detailed term progress information.
        """
        term = self.get_object()
        
        # Get lesson plan completion rate
        lesson_plan_stats = LessonPlan.objects.filter(
            term=term
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        # Calculate syllabus completion
        syllabus_progress = Syllabus.objects.filter(
            academic_year=term.academic_year
        ).aggregate(
            avg_completion=Avg('completion_percentage')
        )
        
        progress_info = {
            'term': {
                'name': term.name,
                'progress_percentage': term.progress_percentage,
                'days_elapsed': term.days_elapsed,
                'days_remaining': term.days_remaining
            },
            'lesson_plans': {
                'completion_rate': (
                    lesson_plan_stats['completed'] / lesson_plan_stats['total'] * 100
                    if lesson_plan_stats['total'] > 0 else 0
                ),
                **lesson_plan_stats
            },
            'syllabus': syllabus_progress,
            'weeks': {
                'current_week': term.current_week,
                'total_weeks': term.total_weeks
            }
        }
        
        return Response(progress_info)


class SubjectViewSet(BaseAcademicViewSet):
    """
    ViewSet for Subject management with curriculum support.
    """
    
    queryset = Subject.objects.all().order_by('category', 'name')
    filterset_fields = ['category', 'curriculum', 'is_compulsory', 'is_active', 'difficulty_level']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'category', 'credits']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return SubjectSerializer

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        """
        Get teachers assigned to this subject.
        """
        subject = self.get_object()
        academic_year = request.query_params.get('academic_year')
        
        assignments = SubjectAssignment.objects.filter(
            subject=subject,
            is_active=True
        )
        
        if academic_year:
            assignments = assignments.filter(academic_year_id=academic_year)
        
        # Use select_related for better performance
        teachers = TeacherProfile.objects.filter(
            id__in=assignments.values('teacher')
        ).select_related('user')
        
        # Use minimal serializer for list view
        from teachers.serializers import TeacherMinimalSerializer
        page = self.paginate_queryset(teachers)
        
        if page is not None:
            serializer = TeacherMinimalSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TeacherMinimalSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get available subject categories with counts.
        """
        categories = Subject.objects.values('category').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        ).order_by('category')
        
        return Response({
            'categories': dict(Subject.SUBJECT_CATEGORIES),
            'statistics': list(categories)
        })

    @action(detail=False, methods=['get'])
    def by_curriculum(self, request):
        """
        Get subjects grouped by curriculum.
        """
        curriculum = request.query_params.get('curriculum')
        grade_level = request.query_params.get('grade_level')
        
        queryset = self.get_queryset()
        
        if curriculum:
            queryset = queryset.filter(curriculum=curriculum)
        
        if grade_level:
            queryset = queryset.filter(grade_levels__contains=[grade_level])
        
        subjects_by_curriculum = {}
        for subject in queryset.select_related('department'):
            if subject.curriculum not in subjects_by_curriculum:
                subjects_by_curriculum[subject.curriculum] = []
            
            subjects_by_curriculum[subject.curriculum].append(
                SubjectSerializer(subject).data
            )
        
        return Response(subjects_by_curriculum)

    @action(detail=True, methods=['get'])
    def syllabus(self, request, pk=None):
        """
        Get syllabus for this subject.
        """
        subject = self.get_object()
        academic_year = request.query_params.get('academic_year')
        
        syllabus_qs = Syllabus.objects.filter(subject=subject)
        
        if academic_year:
            syllabus_qs = syllabus_qs.filter(academic_year_id=academic_year)
        
        syllabus = syllabus_qs.order_by('-version').first()
        
        if syllabus:
            serializer = SyllabusSerializer(syllabus)
            return Response(serializer.data)
        
        return Response(
            {'detail': 'No syllabus found for the specified criteria'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """
        Get all assignments for this subject.
        """
        subject = self.get_object()
        academic_year = request.query_params.get('academic_year')
        
        assignments = SubjectAssignment.objects.filter(
            subject=subject,
            is_active=True
        ).select_related(
            'teacher__user', 'class_assigned', 'academic_year'
        )
        
        if academic_year:
            assignments = assignments.filter(academic_year_id=academic_year)
        
        page = self.paginate_queryset(assignments)
        
        if page is not None:
            serializer = SubjectAssignmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SubjectAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class ClassViewSet(BaseAcademicViewSet):
    """
    ViewSet for Class management with student and subject associations.
    """
    
    queryset = Class.objects.all().order_by('grade_level', 'section')
    filterset_fields = ['academic_year', 'grade_level', 'stream', 'is_active']
    search_fields = ['name', 'section', 'room_number', 'grade_level']
    ordering_fields = ['name', 'grade_level', 'section', 'current_strength']
    ordering = ['grade_level', 'section']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ClassDetailSerializer
        return ClassSerializer

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get students in this class with detailed information.
        """
        class_obj = self.get_object()
        
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=class_obj,
            status='active'
        ).select_related(
            'student__student_profile'
        ).order_by('roll_number')
        
        page = self.paginate_queryset(enrollments)
        
        if page is not None:
            serializer = StudentEnrollmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StudentEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """
        Get subjects taught in this class with teacher assignments.
        """
        class_obj = self.get_object()
        
        assignments = SubjectAssignment.objects.filter(
            class_assigned=class_obj,
            is_active=True
        ).select_related('subject', 'teacher__user')
        
        subjects_data = []
        for assignment in assignments:
            subjects_data.append({
                'assignment_id': assignment.id,
                'subject': SubjectSerializer(assignment.subject).data,
                'teacher': {
                    'id': assignment.teacher.id,
                    'full_name': assignment.teacher.user.get_full_name() if assignment.teacher.user else None,
                    'staff_id': assignment.teacher.staff_id,
                    'email': assignment.teacher.user.email if assignment.teacher.user else None
                },
                'periods_per_week': assignment.periods_per_week,
                'is_class_teacher': assignment.is_class_teacher,
                'effective_from': assignment.effective_from,
                'effective_until': assignment.effective_until
            })
        
        return Response({
            'class': ClassSerializer(class_obj).data,
            'subjects': subjects_data,
            'total_subjects': len(subjects_data),
            'total_periods': sum(item['periods_per_week'] for item in subjects_data)
        })

    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """
        Get class timetable (placeholder for timetable integration).
        """
        class_obj = self.get_object()
        
        # This would integrate with a timetable app
        # For now, return basic information
        return Response({
            'class': ClassSerializer(class_obj).data,
            'timetable': {
                'status': 'not_implemented',
                'message': 'Timetable functionality to be implemented with timetable module',
                'integration_hint': 'Use class ID to fetch timetable from timetable service'
            }
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get comprehensive class statistics.
        """
        class_obj = self.get_object()
        
        # Get enrollment statistics with aggregation
        enrollment_stats = StudentEnrollment.objects.filter(
            class_enrolled=class_obj,
            status='active'
        ).aggregate(
            total_students=Count('id'),
            male_students=Count('id', filter=Q(student__student_profile__gender='male')),
            female_students=Count('id', filter=Q(student__student_profile__gender='female')),
            avg_roll_number=Avg('roll_number')
        )
        
        # Get subject statistics
        subject_stats = SubjectAssignment.objects.filter(
            class_assigned=class_obj,
            is_active=True
        ).aggregate(
            total_subjects=Count('subject_id', distinct=True),
            total_periods=Sum('periods_per_week'),
            teachers_count=Count('teacher_id', distinct=True)
        )
        
        # Get class teacher info
        class_teacher_info = None
        if class_obj.class_teacher and class_obj.class_teacher.user:
            class_teacher_info = {
                'id': class_obj.class_teacher.id,
                'full_name': class_obj.class_teacher.user.get_full_name(),
                'staff_id': class_obj.class_teacher.staff_id,
                'email': class_obj.class_teacher.user.email
            }
        
        stats = {
            'class_info': {
                'name': class_obj.name,
                'display_name': class_obj.display_name,
                'grade_level': class_obj.get_grade_level_display(),
                'section': class_obj.section,
                'room_number': class_obj.room_number
            },
            'capacity': {
                'total': class_obj.capacity,
                'current': class_obj.current_strength,
                'available': class_obj.available_seats,
                'occupancy_rate': class_obj.occupancy_rate,
                'is_full': class_obj.is_full
            },
            'enrollments': enrollment_stats,
            'subjects': subject_stats,
            'class_teacher': class_teacher_info,
            'academic_year': {
                'id': str(class_obj.academic_year.id),
                'name': class_obj.academic_year.name
            } if class_obj.academic_year else None
        }
        
        return Response(stats)

    @action(detail=True, methods=['post'])
    def assign_class_teacher(self, request, pk=None):
        """
        Assign or change class teacher.
        """
        class_obj = self.get_object()
        teacher_id = request.data.get('teacher_id')
        
        if not teacher_id:
            return Response(
                {'error': 'teacher_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            teacher = TeacherProfile.objects.get(id=teacher_id)
            class_obj.class_teacher = teacher
            class_obj.save()
            
            # Also update subject assignment if exists
            SubjectAssignment.objects.filter(
                class_assigned=class_obj,
                teacher=teacher,
                is_active=True
            ).update(is_class_teacher=True)
            
            return Response({
                'message': f'Class teacher assigned successfully to {teacher.user.get_full_name()}',
                'class': ClassSerializer(class_obj).data
            })
            
        except TeacherProfile.DoesNotExist:
            return Response(
                {'error': 'Teacher not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SubjectAssignmentViewSet(BaseAcademicViewSet):
    """
    ViewSet for Subject Assignment management linking teachers to classes and subjects.
    """
    
    queryset = SubjectAssignment.objects.all().order_by('class_assigned', 'subject')
    serializer_class = SubjectAssignmentSerializer
    filterset_fields = ['teacher', 'subject', 'class_assigned', 'academic_year', 'is_active', 'is_class_teacher']
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name', 'subject__name', 'class_assigned__name']
    ordering_fields = ['teacher__user__last_name', 'subject__name', 'periods_per_week']
    ordering = ['class_assigned', 'subject']

    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """
        Bulk assign subjects to teachers with validation.
        """
        serializer = BulkSubjectAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        created_assignments = []
        errors = []
        
        for teacher_id in data['teacher_ids']:
            try:
                # Check for existing assignment
                existing_assignment = SubjectAssignment.objects.filter(
                    teacher_id=teacher_id,
                    subject_id=data['subject_id'],
                    class_assigned_id=data['class_id'],
                    academic_year_id=data['academic_year_id']
                ).first()
                
                if existing_assignment:
                    if existing_assignment.is_active:
                        errors.append(f"Teacher {teacher_id} already has an active assignment")
                        continue
                    else:
                        # Reactivate existing assignment
                        existing_assignment.is_active = True
                        existing_assignment.periods_per_week = data['periods_per_week']
                        existing_assignment.save()
                        created_assignments.append(existing_assignment)
                else:
                    # Create new assignment
                    assignment = SubjectAssignment.objects.create(
                        teacher_id=teacher_id,
                        subject_id=data['subject_id'],
                        class_assigned_id=data['class_id'],
                        academic_year_id=data['academic_year_id'],
                        periods_per_week=data['periods_per_week'],
                        assigned_date=timezone.now().date()
                    )
                    created_assignments.append(assignment)
                    
            except Exception as e:
                errors.append(f"Failed to assign teacher {teacher_id}: {str(e)}")
        
        result_serializer = SubjectAssignmentSerializer(created_assignments, many=True)
        return Response({
            'created': result_serializer.data,
            'total_created': len(created_assignments),
            'errors': errors,
            'total_errors': len(errors)
        }, status=status.HTTP_207_MULTI_STATUS)

    @action(detail=False, methods=['get'])
    def teacher_workload(self, request):
        """
        Get teacher workload statistics with filtering.
        """
        academic_year = request.query_params.get('academic_year')
        department = request.query_params.get('department')
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        if department:
            queryset = queryset.filter(teacher__department_id=department)
        
        workload_data = queryset.values(
            'teacher_id', 'teacher__user__first_name', 'teacher__user__last_name',
            'teacher__employment_type', 'teacher__department__name'
        ).annotate(
            total_periods=Sum('periods_per_week'),
            total_classes=Count('class_assigned', distinct=True),
            total_subjects=Count('subject', distinct=True),
            class_teacher_count=Count('id', filter=Q(is_class_teacher=True))
        ).order_by('-total_periods')
        
        # Calculate workload percentage based on employment type
        for item in workload_data:
            max_periods = 40 if item['teacher__employment_type'] == 'full_time' else 20
            item['workload_percentage'] = min(100, (item['total_periods'] / max_periods) * 100)
            item['teacher_name'] = f"{item['teacher__user__first_name']} {item['teacher__user__last_name']}"
            item['employment_type'] = item['teacher__employment_type']
            item['department'] = item['teacher__department__name']
            
            # Clean up the data structure
            item.pop('teacher__user__first_name', None)
            item.pop('teacher__user__last_name', None)
            item.pop('teacher__employment_type', None)
            item.pop('teacher__department__name', None)
        
        serializer = TeacherWorkloadSerializer(workload_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_teacher(self, request):
        """
        Get all assignments for a specific teacher.
        """
        teacher_id = request.query_params.get('teacher_id')
        academic_year = request.query_params.get('academic_year')
        
        if not teacher_id:
            return Response(
                {'error': 'teacher_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            teacher_id=teacher_id,
            is_active=True
        ).select_related(
            'subject', 'class_assigned', 'academic_year'
        )
        
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StudentEnrollmentViewSet(BaseAcademicViewSet):
    """
    ViewSet for Student Enrollment management with bulk operations.
    """
    
    queryset = StudentEnrollment.objects.all().order_by('class_enrolled', 'roll_number')
    serializer_class = StudentEnrollmentSerializer
    filterset_fields = ['student', 'class_enrolled', 'academic_year', 'status', 'house']
    search_fields = [
        'student__first_name', 'student__last_name',
        'enrollment_number', 'previous_school',
        'student__student_profile__admission_number'
    ]
    ordering_fields = ['enrollment_date', 'roll_number', 'student__last_name']
    ordering = ['class_enrolled', 'roll_number']

    @action(detail=False, methods=['post'])
    def bulk_enroll(self, request):
        """
        Bulk enroll students with proper error handling and rollback.
        """
        serializer = BulkStudentEnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        created_enrollments = []
        errors = []
        
        # Get class and academic year for validation
        try:
            class_obj = Class.objects.get(id=data['class_id'])
            academic_year = AcademicYear.objects.get(id=data['academic_year_id'])
            
            # Check class capacity
            current_enrollments = StudentEnrollment.objects.filter(
                class_enrolled=class_obj,
                academic_year=academic_year,
                status='active'
            ).count()
            
            available_seats = class_obj.capacity - current_enrollments
            
            if available_seats < len(data['student_ids']):
                return Response({
                    'error': f'Insufficient seats. Available: {available_seats}, Requested: {len(data["student_ids"])}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (Class.DoesNotExist, AcademicYear.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Process each student
        for student_id in data['student_ids']:
            try:
                # Get student user through profile
                student_profile = StudentProfile.objects.select_related('user').get(id=student_id)
                student = student_profile.user
                
                # Check if student is already enrolled
                existing_enrollment = StudentEnrollment.objects.filter(
                    student=student,
                    academic_year=academic_year
                ).exists()
                
                if existing_enrollment:
                    errors.append(f"Student {student.get_full_name()} is already enrolled for {academic_year.name}")
                    continue
                
                # Generate roll number if needed
                if data.get('assign_roll_numbers', True):
                    last_roll = StudentEnrollment.objects.filter(
                        class_enrolled=class_obj,
                        academic_year=academic_year
                    ).exclude(roll_number=None).order_by('-roll_number').first()
                    
                    roll_number = (last_roll.roll_number + 1) if last_roll else 1
                else:
                    roll_number = None
                
                # Create enrollment
                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    class_enrolled=class_obj,
                    academic_year=academic_year,
                    enrollment_date=data['enrollment_date'],
                    roll_number=roll_number,
                    status='active'
                )
                
                created_enrollments.append(enrollment)
                
            except StudentProfile.DoesNotExist:
                errors.append(f"Student profile with ID {student_id} not found")
            except Exception as e:
                errors.append(f"Failed to enroll student {student_id}: {str(e)}")
        
        result_serializer = StudentEnrollmentSerializer(created_enrollments, many=True)
        return Response({
            'created': result_serializer.data,
            'total_created': len(created_enrollments),
            'errors': errors,
            'total_errors': len(errors)
        }, status=status.HTTP_207_MULTI_STATUS)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export enrollments to CSV with filtering options.
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="enrollments_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Enrollment Number', 'Student Name', 'Admission Number',
            'Class', 'Grade Level', 'Academic Year',
            'Enrollment Date', 'Status', 'Roll Number', 'House',
            'Gender', 'Date of Birth'
        ])
        
        # Apply filters to queryset
        queryset = self.filter_queryset(self.get_queryset())
        enrollments = queryset.select_related(
            'student__student_profile', 'class_enrolled', 'academic_year'
        )
        
        for enrollment in enrollments:
            student_profile = enrollment.student.student_profile
            writer.writerow([
                enrollment.enrollment_number,
                enrollment.student.get_full_name(),
                student_profile.admission_number if student_profile else 'N/A',
                enrollment.class_enrolled.display_name,
                enrollment.class_enrolled.get_grade_level_display(),
                enrollment.academic_year.name,
                enrollment.enrollment_date,
                enrollment.get_status_display(),
                enrollment.roll_number,
                enrollment.get_house_display() if enrollment.house else '',
                student_profile.gender if student_profile else 'N/A',
                student_profile.date_of_birth if student_profile else ''
            ])
        
        return response

    @action(detail=False, methods=['get'])
    def report(self, request):
        """
        Generate comprehensive enrollment reports.
        """
        serializer = EnrollmentReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        report_type = data.get('report_type', 'summary')
        
        # Base queryset
        enrollments = StudentEnrollment.objects.filter(
            academic_year_id=data['academic_year']
        ).select_related(
            'student__student_profile', 'class_enrolled', 'academic_year'
        )
        
        # Apply filters
        if data.get('grade_level'):
            enrollments = enrollments.filter(
                class_enrolled__grade_level=data['grade_level']
            )
        
        if data.get('status'):
            enrollments = enrollments.filter(status=data['status'])
        
        if data.get('cbc_pathway'):
            enrollments = enrollments.filter(cbc_pathway_selection=data['cbc_pathway'])
        
        if report_type == 'summary':
            summary = enrollments.aggregate(
                total=Count('id'),
                active=Count('id', filter=Q(status='active')),
                transferred=Count('id', filter=Q(status='transferred')),
                graduated=Count('id', filter=Q(status='graduated')),
                withdrawn=Count('id', filter=Q(status='withdrawn')),
                male=Count('id', filter=Q(student__student_profile__gender='male')),
                female=Count('id', filter=Q(student__student_profile__gender='female'))
            )
            
            # Add class-wise distribution
            class_distribution = enrollments.values(
                'class_enrolled__name',
                'class_enrolled__grade_level'
            ).annotate(
                total=Count('id'),
                active=Count('id', filter=Q(status='active')),
                male=Count('id', filter=Q(student__student_profile__gender='male')),
                female=Count('id', filter=Q(student__student_profile__gender='female'))
            ).order_by('class_enrolled__grade_level', 'class_enrolled__name')
            
            return Response({
                'summary': summary,
                'class_distribution': list(class_distribution),
                'generated_at': timezone.now()
            })
        
        elif report_type == 'detailed':
            page = self.paginate_queryset(enrollments)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(enrollments, many=True)
            return Response(serializer.data)
        
        elif report_type == 'analytics':
            # Time-based analytics
            monthly_enrollments = enrollments.extra(
                select={'month': "DATE_TRUNC('month', enrollment_date)"}
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            # Status transition analysis
            status_changes = enrollments.values(
                'status',
                'status_changed_date__month'
            ).annotate(
                count=Count('id')
            ).order_by('status_changed_date__month')
            
            return Response({
                'monthly_trends': list(monthly_enrollments),
                'status_analysis': list(status_changes),
                'retention_rate': self._calculate_retention_rate(data['academic_year'])
            })
        
        return Response(
            {'error': 'Invalid report type'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _calculate_retention_rate(self, academic_year_id):
        """Calculate student retention rate."""
        current_year = AcademicYear.objects.get(id=academic_year_id)
        previous_year = AcademicYear.objects.filter(
            end_date__lt=current_year.start_date
        ).order_by('-end_date').first()
        
        if not previous_year:
            return None
        
        # Get students from previous year
        previous_enrollments = StudentEnrollment.objects.filter(
            academic_year=previous_year,
            status='active'
        ).values_list('student_id', flat=True)
        
        # Get returning students
        returning_students = StudentEnrollment.objects.filter(
            academic_year=current_year,
            student_id__in=previous_enrollments,
            status='active'
        ).count()
        
        total_previous = len(previous_enrollments)
        
        return {
            'previous_year_total': total_previous,
            'returning_students': returning_students,
            'retention_rate': (returning_students / total_previous * 100) if total_previous > 0 else 0
        }

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get active enrollments only with pagination.
        """
        active_enrollments = self.filter_queryset(
            self.get_queryset().filter(status='active')
        )
        
        page = self.paginate_queryset(active_enrollments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(active_enrollments, many=True)
        return Response(serializer.data)


class LessonPlanViewSet(BaseAcademicViewSet):
    """ViewSet for managing lesson plans."""
    serializer_class = LessonPlanSerializer
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'subject', 'class_assigned', 'date', 'is_completed', 'is_active']
    search_fields = ['title', 'sub_topic__name', 'learning_objectives']
    ordering_fields = ['date', 'title', 'class_assigned__grade_level', 'created_at']
    
    # FIX: Changed from 'lesson_date' to 'date'
    queryset = LessonPlan.objects.all().order_by('-date', 'class_assigned')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacherOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset to add filtering."""
        queryset = super().get_queryset()
        
        # Non-admin teachers can only see their own lesson plans
        if not self.request.user.is_staff and hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by academic year
        academic_year_id = self.request.query_params.get('academic_year')
        if academic_year_id:
            queryset = queryset.filter(
                date__gte=AcademicYear.objects.get(id=academic_year_id).start_date,
                date__lte=AcademicYear.objects.get(id=academic_year_id).end_date
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set teacher when creating lesson plan."""
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(teacher=self.request.user.teacher_profile)
        else:
            serializer.save()
    
    @action(detail=False, methods=['GET'])
    def upcoming(self, request):
        """Get upcoming lesson plans."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date__gte=today, is_completed=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def completed(self, request):
        """Get completed lesson plans."""
        queryset = self.get_queryset().filter(is_completed=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_subject(self, request):
        """Get lesson plans grouped by subject."""
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response(
                {'error': 'subject_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(subject_id=subject_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_class(self, request):
        """Get lesson plans grouped by class."""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(class_assigned_id=class_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def mark_completed(self, request, pk=None):
        """Mark lesson plan as completed."""
        lesson_plan = self.get_object()
        
        # Check permissions
        if not (request.user.is_staff or lesson_plan.teacher.teacher == request.user):
            return Response(
                {'error': 'You do not have permission to mark this lesson plan as completed'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        lesson_plan.is_completed = True
        lesson_plan.save()
        
        serializer = self.get_serializer(lesson_plan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def calendar_view(self, request):
        """Get lesson plans for calendar view."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            date__range=[start_date, end_date]
        ).select_related('subject', 'class_assigned', 'teacher')
        
        calendar_data = []
        for lesson_plan in queryset:
            calendar_data.append({
                'id': str(lesson_plan.id),
                'title': f"{lesson_plan.subject.name} - {lesson_plan.class_assigned.display_name}",
                'start': lesson_plan.date.isoformat(),
                'end': lesson_plan.date.isoformat(),
                'color': self._get_subject_color(lesson_plan.subject),
                'extendedProps': {
                    'subject': lesson_plan.subject.name,
                    'class': lesson_plan.class_assigned.display_name,
                    'teacher': lesson_plan.teacher.teacher.get_full_name(),
                    'is_completed': lesson_plan.is_completed,
                    'url': f"/api/v1/academics/lesson-plans/{lesson_plan.id}/"
                }
            })
        
        return Response(calendar_data)
    
    def _get_subject_color(self, subject):
        """Get color for subject in calendar."""
        # Simple color mapping based on subject name
        color_map = {
            'mathematics': '#FF6B6B',
            'english': '#4ECDC4',
            'kiswahili': '#45B7D1',
            'science': '#96CEB4',
            'social studies': '#FFEAA7',
            'cre': '#DDA0DD',
            'pre-technical': '#98D8C8',
            'agriculture': '#F7DC6F',
            'business studies': '#BB8FCE',
            'computer': '#85C1E9',
            'physics': '#F1948A',
            'chemistry': '#82E0AA',
            'biology': '#F8C471',
            'history': '#F5B7B1',
            'geography': '#AED6F1',
        }
        
        subject_name_lower = subject.name.lower()
        for key, color in color_map.items():
            if key in subject_name_lower:
                return color
        
        # Default color
        return '#D5DBDB'
    
    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get lesson plan statistics."""
        if not request.user.is_staff and not hasattr(request.user, 'teacher_profile'):
            return Response(
                {'error': 'Only teachers and admins can view lesson plan statistics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        # If teacher, filter to their lesson plans
        if hasattr(request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=request.user.teacher_profile)
        
        # Get date range from query params or default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        if request.query_params.get('start_date'):
            start_date = request.query_params.get('start_date')
        if request.query_params.get('end_date'):
            end_date = request.query_params.get('end_date')
        
        queryset = queryset.filter(date__range=[start_date, end_date])
        
        statistics = {
            'total_plans': queryset.count(),
            'completed_plans': queryset.filter(is_completed=True).count(),
            'pending_plans': queryset.filter(is_completed=False).count(),
            'completion_rate': round(
                (queryset.filter(is_completed=True).count() / max(queryset.count(), 1)) * 100, 2
            ),
            'by_subject': list(queryset.values('subject__name').annotate(
                count=Count('id'),
                completed=Count('id', filter=Q(is_completed=True))
            ).order_by('-count')),
            'by_class': list(queryset.values('class_assigned__display_name').annotate(
                count=Count('id'),
                completed=Count('id', filter=Q(is_completed=True))
            ).order_by('-count')),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return Response(statistics)

class SyllabusViewSet(BaseAcademicViewSet):
    """
    ViewSet for Syllabus management with progress tracking.
    """
    
    queryset = Syllabus.objects.all().order_by('subject', 'academic_year')
    serializer_class = SyllabusSerializer
    filterset_fields = ['subject', 'academic_year', 'curriculum', 'is_complete']
    search_fields = ['subject__name', 'learning_outcomes', 'title']
    ordering_fields = ['subject__name', 'academic_year__name', 'version']
    ordering = ['subject', 'academic_year']

    @action(detail=True, methods=['post'])
    def mark_topic_completed(self, request, pk=None):
        """
        Mark a topic as completed or not completed.
        """
        syllabus = self.get_object()
        topic_index = request.data.get('topic_index')
        completed = request.data.get('completed', True)
        
        if topic_index is None:
            return Response(
                {'error': 'topic_index is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            syllabus.mark_topic_completed(int(topic_index), completed)
            serializer = self.get_serializer(syllabus)
            return Response({
                'message': f'Topic {topic_index} marked as {"completed" if completed else "not completed"}',
                'syllabus': serializer.data
            })
        except IndexError:
            return Response(
                {'error': 'Invalid topic index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Get detailed syllabus progress information.
        """
        syllabus = self.get_object()
        
        # Calculate topic statistics
        topics = syllabus.topics or []
        completed_topics = syllabus.completed_topics or []
        
        topic_stats = []
        for i, topic in enumerate(topics):
            topic_stats.append({
                'index': i,
                'title': topic.get('title', f'Topic {i + 1}'),
                'completed': i in completed_topics,
                'estimated_hours': topic.get('estimated_hours', 0),
                'competencies': topic.get('competencies', [])
            })
        
        # Calculate completion by competency
        competency_completion = {}
        for topic in topic_stats:
            for competency in topic['competencies']:
                if competency not in competency_completion:
                    competency_completion[competency] = {'total': 0, 'completed': 0}
                
                competency_completion[competency]['total'] += 1
                if topic['completed']:
                    competency_completion[competency]['completed'] += 1
        
        return Response({
            'syllabus_info': {
                'title': syllabus.title,
                'subject': syllabus.subject.name,
                'version': syllabus.version,
                'academic_year': syllabus.academic_year.name
            },
            'progress': {
                'completion_percentage': syllabus.completion_percentage,
                'topics_count': syllabus.topics_count,
                'completed_topics_count': syllabus.completed_topics_count,
                'remaining_topics': syllabus.topics_count - syllabus.completed_topics_count,
                'estimated_total_hours': sum(t.get('estimated_hours', 0) for t in topics),
                'completed_hours': sum(
                    t.get('estimated_hours', 0) 
                    for i, t in enumerate(topics) 
                    if i in completed_topics
                )
            },
            'topic_details': topic_stats,
            'competency_coverage': competency_completion,
            'next_topic': self._get_next_topic(topic_stats)
        })

    def _get_next_topic(self, topic_stats):
        """Get the next incomplete topic."""
        for topic in topic_stats:
            if not topic['completed']:
                return topic
        return None


class AcademicEventViewSet(BaseAcademicViewSet):
    """ViewSet for managing academic events."""
    serializer_class = AcademicEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'is_active', 'is_published', 'is_cancelled', 'academic_year', 'term']
    search_fields = ['title', 'description', 'location', 'organizer__name']
    ordering_fields = ['start_date', 'end_date', 'priority', 'created_at']
    
    # FIX: Changed from 'start_time' to just 'start_date'
    queryset = AcademicEvent.objects.all().order_by('start_date', 'priority')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset to add filtering."""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Show only published events to non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True, is_active=True)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by target audience
        target_audience = self.request.query_params.get('target_audience')
        if target_audience:
            queryset = queryset.filter(target_audience__icontains=target_audience)
        
        return queryset
    
    @action(detail=False, methods=['GET'])
    def upcoming(self, request):
        """Get upcoming events."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            start_date__gte=today,
            is_active=True,
            is_cancelled=False
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def current(self, request):
        """Get current events (ongoing today)."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True,
            is_cancelled=False
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def past(self, request):
        """Get past events."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            end_date__lt=today,
            is_active=True
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def calendar_view(self, request):
        """Get events for calendar view."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            start_date__gte=start_date,
            end_date__lte=end_date,
            is_active=True,
            is_cancelled=False
        )
        
        calendar_data = []
        for event in queryset:
            # Determine event color based on type or priority
            color = self._get_event_color(event)
            
            calendar_data.append({
                'id': str(event.id),
                'title': event.title,
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'color': color,
                'allDay': True,  # Events are all-day since there's no time field
                'extendedProps': {
                    'event_type': event.event_type,
                    'location': event.location,
                    'organizer': event.organizer.name if event.organizer else None,
                    'priority': event.priority,
                    'description': event.description,
                    'url': f"/api/v1/academics/events/{event.id}/"
                }
            })
        
        return Response(calendar_data)
    
    def _get_event_color(self, event):
        """Get color for event in calendar."""
        # Color mapping based on event type
        color_map = {
            'exam': '#FF6B6B',  # Red for exams
            'holiday': '#4ECDC4',  # Teal for holidays
            'meeting': '#45B7D1',  # Blue for meetings
            'training': '#96CEB4',  # Green for training
            'competition': '#FFEAA7',  # Yellow for competitions
            'ceremony': '#DDA0DD',  # Purple for ceremonies
            'parent_event': '#98D8C8',  # Mint for parent events
            'sports': '#F7DC6F',  # Orange for sports
            'cultural': '#BB8FCE',  # Lavender for cultural events
        }
        
        # Try to get color from event type
        if event.event_type in color_map:
            return color_map[event.event_type]
        
        # Default colors based on priority
        priority_colors = {
            'high': '#FF6B6B',  # Red for high priority
            'medium': '#F7DC6F',  # Yellow for medium priority
            'low': '#96CEB4',  # Green for low priority
        }
        
        return priority_colors.get(event.priority, '#D5DBDB')  # Gray default
    
    @action(detail=False, methods=['GET'])
    def by_type(self, request):
        """Get events grouped by type."""
        queryset = self.get_queryset().filter(is_active=True)
        
        events_by_type = {}
        for event in queryset:
            if event.event_type not in events_by_type:
                events_by_type[event.event_type] = {
                    'count': 0,
                    'upcoming': 0,
                    'past': 0,
                    'events': []
                }
            
            events_by_type[event.event_type]['count'] += 1
            
            today = timezone.now().date()
            if event.start_date > today:
                events_by_type[event.event_type]['upcoming'] += 1
            elif event.end_date < today:
                events_by_type[event.event_type]['past'] += 1
            
            events_by_type[event.event_type]['events'].append({
                'id': str(event.id),
                'title': event.title,
                'start_date': event.start_date,
                'end_date': event.end_date,
                'priority': event.priority
            })
        
        return Response(events_by_type)
    
    @action(detail=True, methods=['POST'])
    def publish(self, request, pk=None):
        """Publish an event."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can publish events'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event = self.get_object()
        event.is_published = True
        event.updated_by = request.user
        event.save()
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        """Cancel an event."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can cancel events'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event = self.get_object()
        event.is_cancelled = True
        event.updated_by = request.user
        event.save()
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def countdown(self, request):
        """Get countdown to next important events."""
        today = timezone.now().date()
        
        # Get upcoming high-priority events
        upcoming_events = self.get_queryset().filter(
            start_date__gte=today,
            is_active=True,
            is_cancelled=False,
            priority='high'
        ).order_by('start_date')[:5]
        
        countdown_data = []
        for event in upcoming_events:
            days_until = (event.start_date - today).days
            
            countdown_data.append({
                'id': str(event.id),
                'title': event.title,
                'event_type': event.event_type,
                'start_date': event.start_date,
                'days_until': days_until,
                'priority': event.priority,
                'location': event.location
            })
        
        return Response(countdown_data)
    
    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get event statistics."""
        queryset = self.get_queryset().filter(is_active=True)
        
        # Get date range from query params or default to current academic year
        try:
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                start_date = current_year.start_date
                end_date = current_year.end_date
            else:
                # Default to current year
                start_date = timezone.now().date().replace(month=1, day=1)
                end_date = timezone.now().date().replace(month=12, day=31)
        except:
            start_date = timezone.now().date().replace(month=1, day=1)
            end_date = timezone.now().date().replace(month=12, day=31)
        
        if request.query_params.get('start_date'):
            start_date = request.query_params.get('start_date')
        if request.query_params.get('end_date'):
            end_date = request.query_params.get('end_date')
        
        queryset = queryset.filter(
            start_date__gte=start_date,
            end_date__lte=end_date
        )
        
        statistics = {
            'total_events': queryset.count(),
            'published_events': queryset.filter(is_published=True).count(),
            'cancelled_events': queryset.filter(is_cancelled=True).count(),
            'by_type': list(queryset.values('event_type').annotate(
                count=Count('id'),
                published=Count('id', filter=Q(is_published=True)),
                cancelled=Count('id', filter=Q(is_cancelled=True))
            ).order_by('-count')),
            'by_priority': list(queryset.values('priority').annotate(
                count=Count('id')
            ).order_by('-count')),
            'by_month': list(queryset.extra(
                {'month': "EXTRACT(month FROM start_date)"}
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return Response(statistics)

# ==================== DASHBOARD AND ANALYTICS VIEWS ====================

class AcademicDashboardView(APIView):
    """API view for academic dashboard data."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        current_year = AcademicYear.objects.filter(is_current=True).first()
        current_term = AcademicTerm.objects.filter(is_current=True).first()
        
        if not current_year:
            return Response({'error': 'No current academic year set'}, status=404)
        
        # Get statistics with efficient queries
        class_stats = Class.objects.filter(academic_year=current_year).aggregate(
            total=Count('id'),
            total_capacity=Sum('capacity'),
            total_students=Sum('current_strength')
        )
        
        enrollment_stats = StudentEnrollment.objects.filter(
            academic_year=current_year,
            status='active'
        ).aggregate(
            total=Count('id'),
            new_this_month=Count('id', filter=Q(
                enrollment_date__gte=timezone.now().replace(day=1)
            ))
        )
        
        teacher_stats = TeacherProfile.objects.filter(is_active=True).aggregate(
            total=Count('id'),
            with_assignments=Count('id', filter=Q(
                subject_assignments__is_active=True,
                subject_assignments__academic_year=current_year
            ))
        )
        
        event_stats = AcademicEvent.objects.filter(
            academic_year=current_year,
            is_published=True
        ).aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(start_date__gte=timezone.now().date()))
        )
        
        # Get recent activities
        recent_enrollments = StudentEnrollment.objects.filter(
            academic_year=current_year
        ).select_related('student__student_profile', 'class_enrolled')[:5]
        
        upcoming_events = AcademicEvent.objects.filter(
            academic_year=current_year,
            start_date__gte=timezone.now().date(),
            is_published=True
        ).select_related('organizer')[:5]
        
        recent_lesson_plans = LessonPlan.objects.filter(
            academic_year=current_year
        ).select_related('teacher__user', 'subject', 'class_assigned')[:5]
        
        # Class occupancy overview
        class_occupancy = Class.objects.filter(
            academic_year=current_year
        ).values(
            'name', 'display_name', 'grade_level'
        ).annotate(
            occupancy_rate=Avg('occupancy_rate'),
            student_count=F('current_strength')
        ).order_by('grade_level', 'name')[:10]
        
        dashboard_data = {
            'overview': {
                'academic_year': {
                    'id': str(current_year.id),
                    'name': current_year.name,
                    'progress': current_year.progress_percentage
                },
                'current_term': AcademicTermMinimalSerializer(current_term).data if current_term else None,
                'statistics': {
                    'classes': class_stats,
                    'enrollments': enrollment_stats,
                    'teachers': teacher_stats,
                    'events': event_stats
                }
            },
            'recent_activities': {
                'enrollments': StudentEnrollmentSerializer(recent_enrollments, many=True).data,
                'events': AcademicEventSerializer(upcoming_events, many=True).data,
                'lesson_plans': LessonPlanSerializer(recent_lesson_plans, many=True).data
            },
            'class_overview': class_occupancy,
            'quick_links': self._get_quick_links(request.user),
            'last_updated': timezone.now()
        }
        
        return Response(dashboard_data)
    
    def _get_quick_links(self, user):
        """Get quick links based on user permissions."""
        links = []
        
        # Common links for all authenticated users
        links.append({'name': 'My Classes', 'url': '/api/academics/classes/my/'})
        links.append({'name': 'Upcoming Events', 'url': '/api/academics/events/upcoming/'})
        
        # Admin/Staff specific links
        if user.is_staff or user.is_superuser:
            links.append({'name': 'Manage Academic Years', 'url': '/api/academics/years/'})
            links.append({'name': 'Bulk Enrollment', 'url': '/api/academics/enrollments/bulk_enroll/'})
            links.append({'name': 'Teacher Workload', 'url': '/api/academics/assignments/teacher_workload/'})
        
        # Teacher specific links
        if hasattr(user, 'teacher_profile'):
            links.append({'name': 'My Lesson Plans', 'url': '/api/academics/lesson-plans/my/'})
            links.append({'name': 'My Assignments', 'url': '/api/academics/assignments/by_teacher/'})
        
        return links


class ClassStatisticsView(APIView):
    """API view for class statistics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        academic_year = request.query_params.get('academic_year')
        grade_level = request.query_params.get('grade_level')
        
        classes = Class.objects.all()
        
        if academic_year:
            classes = classes.filter(academic_year_id=academic_year)
        
        if grade_level:
            classes = classes.filter(grade_level=grade_level)
        
        # Optimize query with prefetch
        classes = classes.prefetch_related(
            Prefetch('enrollments', queryset=StudentEnrollment.objects.filter(status='active')),
            Prefetch('subject_assignments', queryset=SubjectAssignment.objects.filter(is_active=True))
        )
        
        statistics = []
        for class_obj in classes:
            # Get gender distribution
            gender_dist = class_obj.enrollments.aggregate(
                male=Count('id', filter=Q(student__student_profile__gender='male')),
                female=Count('id', filter=Q(student__student_profile__gender='female'))
            )
            
            stats = {
                'class_id': str(class_obj.id),
                'class_name': class_obj.display_name,
                'grade_level': class_obj.get_grade_level_display(),
                'section': class_obj.section,
                'teacher': class_obj.class_teacher.user.get_full_name() if class_obj.class_teacher and class_obj.class_teacher.user else None,
                'capacity': {
                    'total': class_obj.capacity,
                    'current': class_obj.current_strength,
                    'available': class_obj.available_seats,
                    'occupancy_rate': class_obj.occupancy_rate
                },
                'gender_distribution': gender_dist,
                'subject_count': class_obj.subject_assignments.count(),
                'teacher_count': class_obj.subject_assignments.values('teacher').distinct().count()
            }
            statistics.append(stats)
        
        # Calculate summary statistics
        if statistics:
            summary = {
                'total_classes': len(statistics),
                'total_students': sum(s['capacity']['current'] for s in statistics),
                'total_capacity': sum(s['capacity']['total'] for s in statistics),
                'average_occupancy': sum(s['capacity']['occupancy_rate'] for s in statistics) / len(statistics),
                'gender_summary': {
                    'male': sum(s['gender_distribution']['male'] for s in statistics),
                    'female': sum(s['gender_distribution']['female'] for s in statistics)
                }
            }
        else:
            summary = {}
        
        return Response({
            'statistics': statistics,
            'summary': summary,
            'filters': {
                'academic_year': academic_year,
                'grade_level': grade_level
            }
        })


class TeacherWorkloadView(APIView):
    """API view for teacher workload statistics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        academic_year = request.query_params.get('academic_year')
        department = request.query_params.get('department')
        
        assignments = SubjectAssignment.objects.filter(is_active=True)
        
        if academic_year:
            assignments = assignments.filter(academic_year_id=academic_year)
        
        if department:
            assignments = assignments.filter(teacher__department_id=department)
        
        workload_data = assignments.values(
            'teacher_id', 'teacher__user__first_name', 'teacher__user__last_name',
            'teacher__employment_type', 'teacher__department__name'
        ).annotate(
            total_periods=Sum('periods_per_week'),
            total_classes=Count('class_assigned', distinct=True),
            total_subjects=Count('subject', distinct=True),
            class_teacher_count=Count('id', filter=Q(is_class_teacher=True))
        ).order_by('-total_periods')
        
        # Calculate workload percentage
        for item in workload_data:
            # Determine max periods based on employment type
            if item['teacher__employment_type'] == 'full_time':
                max_periods = 40
            elif item['teacher__employment_type'] == 'part_time':
                max_periods = 20
            else:
                max_periods = 30  # Default
            
            item['workload_percentage'] = min(100, (item['total_periods'] / max_periods) * 100)
            item['workload_status'] = self._get_workload_status(item['workload_percentage'])
            item['teacher_name'] = f"{item['teacher__user__first_name']} {item['teacher__user__last_name']}"
            item['employment_type'] = item['teacher__employment_type']
            item['department'] = item['teacher__department__name']
        
        serializer = TeacherWorkloadSerializer(workload_data, many=True)
        
        # Calculate summary statistics
        if workload_data:
            summary = {
                'total_teachers': len(workload_data),
                'average_periods': sum(item['total_periods'] for item in workload_data) / len(workload_data),
                'average_workload': sum(item['workload_percentage'] for item in workload_data) / len(workload_data),
                'overloaded_count': sum(1 for item in workload_data if item['workload_percentage'] > 90),
                'optimal_count': sum(1 for item in workload_data if 70 <= item['workload_percentage'] <= 90),
                'underloaded_count': sum(1 for item in workload_data if item['workload_percentage'] < 70)
            }
        else:
            summary = {}
        
        return Response({
            'workload_data': serializer.data,
            'summary': summary,
            'filters_applied': {
                'academic_year': academic_year,
                'department': department
            }
        })
    
    def _get_workload_status(self, percentage):
        """Determine workload status based on percentage."""
        if percentage > 90:
            return 'overloaded'
        elif percentage >= 70:
            return 'optimal'
        else:
            return 'underloaded'


class AcademicSearchView(APIView):
    """API view for academic search across multiple models."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = AcademicSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data.get('query', '')
        results = {
            'subjects': [],
            'classes': [],
            'events': [],
            'teachers': [],
            'students': []
        }
        
        if query:
            # Search subjects with optimization
            subjects = Subject.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(description__icontains=query)
            ).select_related('department')[:10]
            results['subjects'] = SubjectSerializer(subjects, many=True).data
            
            # Search classes
            classes = Class.objects.filter(
                Q(name__icontains=query) |
                Q(section__icontains=query) |
                Q(room_number__icontains=query) |
                Q(display_name__icontains=query)
            ).select_related('academic_year', 'class_teacher__user')[:10]
            results['classes'] = ClassSerializer(classes, many=True).data
            
            # Search events
            events = AcademicEvent.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue__icontains=query)
            ).select_related('academic_year', 'organizer')[:10]
            results['events'] = AcademicEventSerializer(events, many=True).data
            
            # Search teachers
            teachers = TeacherProfile.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(staff_id__icontains=query) |
                Q(qualification__icontains=query)
            ).select_related('user', 'department')[:10]
            from teachers.serializers import TeacherMinimalSerializer
            results['teachers'] = TeacherMinimalSerializer(teachers, many=True).data
            
            # Search students (through enrollments)
            enrollments = StudentEnrollment.objects.filter(
                Q(student__first_name__icontains=query) |
                Q(student__last_name__icontains=query) |
                Q(enrollment_number__icontains=query)
            ).select_related('student__student_profile', 'class_enrolled')[:10]
            results['students'] = StudentEnrollmentSerializer(enrollments, many=True).data
        
        # Add counts
        results['counts'] = {
            'subjects': len(results['subjects']),
            'classes': len(results['classes']),
            'events': len(results['events']),
            'teachers': len(results['teachers']),
            'students': len(results['students'])
        }
        
        return Response(results)


# ==================== SIMPLIFIED VIEWS (Replace old duplicate views) ====================

class AcademicOverviewView(APIView):
    """Get academic overview and dashboard data."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Use the dashboard view instead
        dashboard_view = AcademicDashboardView()
        return dashboard_view.get(request)


# ==================== UTILITY VIEWS ====================

class ExportEnrollmentsCSVView(APIView):
    """API view to export enrollments as CSV."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Use the export_csv action from StudentEnrollmentViewSet
        enrollment_viewset = StudentEnrollmentViewSet()
        enrollment_viewset.request = request
        enrollment_viewset.format_kwarg = None
        
        return enrollment_viewset.export_csv(request)


class AcademicCalendarView(APIView):
    """Get academic calendar data for full calendar.js or similar."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Use the calendar action from AcademicEventViewSet
        event_viewset = AcademicEventViewSet()
        event_viewset.request = request
        event_viewset.format_kwarg = None
        
        return event_viewset.calendar(request)