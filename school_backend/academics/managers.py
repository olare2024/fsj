"""
comprehensive_academic_system/managers.py
Manager classes for academic models.
"""

import logging
from typing import Optional, Dict, List, Any, Tuple
from typing import TYPE_CHECKING
from django.db import models
from django.db.models import (
    Q, F, Count, Avg, Sum, 
    Max, Min, ExpressionWrapper, 
    FloatField, Case, When, Value, Func
)
from django.utils import timezone
from django.core.cache import cache
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

if TYPE_CHECKING:
    from .models import AcademicTerm


logger = logging.getLogger(__name__)


# ============================================================================
# BASE MANAGER CLASSES
# ============================================================================

class AcademicManager(models.Manager):
    """Base manager for academic models."""
    
    def active(self):
        """Get active records."""
        return self.filter(is_active=True, is_archived=False)
    
    def archived(self):
        """Get archived records."""
        return self.filter(is_archived=True)
    
    def with_stats(self):
        """Annotate with basic statistics."""
        return self.annotate(
            _created_month=models.functions.TruncMonth('created_at'),
            _updated_days_ago=ExpressionWrapper(
                timezone.now() - F('updated_at'),
                output_field=models.DurationField()
            )
        )


class SearchManager(AcademicManager):
    """Manager with full-text search capabilities."""
    
    def search(self, query: str, search_fields: List[str] = None):
        """Full-text search across relevant fields."""
        if not search_fields:
            search_fields = ['name', 'code', 'description']
        
        search_vector = SearchVector(*search_fields)
        search_query = SearchQuery(query)
        
        return self.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank', '-created_at')


# ============================================================================
# MODEL-SPECIFIC MANAGERS
# ============================================================================

class AcademicYearManager(AcademicManager):
    """Custom manager for AcademicYear."""
    
    def get_current(self) -> Optional['AcademicYear']:
        """Get current academic year."""
        cache_key = 'current_academic_year'
        current = cache.get(cache_key)
        
        if current is None:
            current = self.filter(
                is_current=True,
                is_active=True
            ).first()
            if current:
                cache.set(cache_key, current, 3600)  # Cache for 1 hour
        
        return current
    
    def get_active_years(self) -> models.QuerySet:
        """Get currently active academic years."""
        today = timezone.now().date()
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).order_by('-start_date')
    
    def get_upcoming_years(self) -> models.QuerySet:
        """Get upcoming academic years."""
        today = timezone.now().date()
        return self.filter(
            start_date__gt=today,
            is_active=True
        ).order_by('start_date')
    
    def get_past_years(self) -> models.QuerySet:
        """Get past academic years."""
        today = timezone.now().date()
        return self.filter(
            end_date__lt=today,
            is_active=True
        ).order_by('-end_date')
    
    def with_term_count(self) -> models.QuerySet:
        """Annotate with term count."""
        return self.annotate(
            term_count=Count('terms', distinct=True)
        )
    
    def with_class_count(self) -> models.QuerySet:
        """Annotate with class count."""
        return self.annotate(
            class_count=Count('classes', distinct=True)
        )
    
    def get_years_by_curriculum(self, curriculum: str) -> models.QuerySet:
        """Get academic years by curriculum system."""
        return self.filter(
            curriculum_system=curriculum,
            is_active=True
        ).order_by('-start_date')


class AcademicTermManager(AcademicManager):
    """Custom manager for AcademicTerm."""
    
    def get_current(self) -> Optional['AcademicTerm']:
        """Get current academic term."""
        cache_key = 'current_academic_term'
        current = cache.get(cache_key)
        
        if current is None:
            current = self.filter(
                is_current=True,
                is_active=True
            ).first()
            if current:
                cache.set(cache_key, current, 3600)
        
        return current
    
    def get_active_terms(self) -> models.QuerySet:
        """Get currently active terms."""
        today = timezone.now().date()
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).order_by('term_order')
    
    def get_upcoming_terms(self) -> models.QuerySet:
        """Get upcoming terms."""
        today = timezone.now().date()
        return self.filter(
            start_date__gt=today,
            is_active=True
        ).order_by('start_date')
    
    def get_past_terms(self) -> models.QuerySet:
        """Get past terms."""
        today = timezone.now().date()
        return self.filter(
            end_date__lt=today,
            is_active=True
        ).order_by('-end_date')
    
    def by_academic_year(self, year_id: str) -> models.QuerySet:
        """Get terms by academic year."""
        return self.filter(
            academic_year_id=year_id,
            is_active=True
        ).order_by('term_order')
    
    def with_progress(self) -> models.QuerySet:
        """Annotate with progress percentage."""
        today = timezone.now().date()
        
        return self.annotate(
            progress_percentage=Case(
                When(
                    start_date__isnull=False,
                    end_date__isnull=False,
                    then=Case(
                        When(
                            start_date__gt=today,
                            then=Value(0.0)
                        ),
                        When(
                            end_date__lt=today,
                            then=Value(100.0)
                        ),
                        default=ExpressionWrapper(
                            (F('duration_days') - Func(
                                F('end_date') - today,
                                function='GREATEST',
                                output_field=models.IntegerField()
                            )) * 100.0 / F('duration_days'),
                            output_field=models.FloatField()
                        ),
                        output_field=models.FloatField()
                    )
                ),
                default=Value(0.0),
                output_field=models.FloatField()
            )
        )


class SubjectManager(SearchManager):
    """Custom manager for Subject."""
    
    def by_curriculum(self, curriculum: str) -> models.QuerySet:
        """Get subjects by curriculum."""
        return self.filter(
            curriculum_system=curriculum,
            is_active=True
        ).order_by('code')
    
    def by_grade_level(self, grade_level: str) -> models.QuerySet:
        """Get subjects by grade level."""
        return self.filter(
            grade_levels__contains=[grade_level],
            is_active=True
        ).order_by('code')
    
    def core_subjects(self) -> models.QuerySet:
        """Get core subjects."""
        return self.filter(
            category='core',
            is_active=True
        ).order_by('code')
    
    def elective_subjects(self) -> models.QuerySet:
        """Get elective subjects."""
        return self.filter(
            category='elective',
            is_active=True
        ).order_by('code')
    
    def cbc_subjects(self) -> models.QuerySet:
        """Get CBC subjects."""
        return self.filter(
            curriculum_system='cbc_kenya',
            is_active=True
        ).order_by('code')
    
    def by_department(self, department_id: str) -> models.QuerySet:
        """Get subjects by department."""
        return self.filter(
            department_id=department_id,
            is_active=True
        ).order_by('code')
    
    def with_teacher_count(self) -> models.QuerySet:
        """Annotate with teacher count."""
        return self.annotate(
            teacher_count=Count('subject_assignments__teacher', distinct=True)
        )
    
    def with_class_count(self) -> models.QuerySet:
        """Annotate with class count."""
        return self.annotate(
            class_count=Count('subject_assignments__class_assigned', distinct=True)
        )
    
    def by_education_level(self, education_level: str) -> models.QuerySet:
        """Get subjects by education level."""
        return self.filter(
            education_levels__contains=[education_level],
            is_active=True
        ).order_by('code')


class ClassManager(SearchManager):
    """Custom manager for Class."""
    
    def get_by_grade(self, grade_level: str, academic_year_id: Optional[str] = None) -> models.QuerySet:
        """Get classes by grade level."""
        queryset = self.filter(
            grade_level=grade_level,
            is_active=True
        )
        
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        
        return queryset.order_by('section')
    
    def get_available(self, academic_year_id: Optional[str] = None) -> models.QuerySet:
        """Get classes with available seats."""
        queryset = self.filter(is_active=True)
        
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        
        return queryset.annotate(
            available_seats=F('capacity') - F('current_strength')
        ).filter(available_seats__gt=0).order_by('grade_level', 'section')
    
    def by_teacher(self, teacher_id: str) -> models.QuerySet:
        """Get classes taught by a teacher."""
        return self.filter(
            subject_assignments__teacher_id=teacher_id,
            is_active=True
        ).distinct().order_by('grade_level', 'section')
    
    def with_statistics(self) -> models.QuerySet:
        """Get classes with statistics."""
        return self.annotate(
            student_count=Count('student_assignments', distinct=True),
            teacher_count=Count('subject_assignments__teacher', distinct=True),
            subject_count=Count('subject_assignments__subject', distinct=True),
            avg_performance=Avg('student_assignments__overall_average'),
            attendance_rate=Avg('student_assignments__attendance_rate')
        )
    
    def by_stream(self, stream_id: str) -> models.QuerySet:
        """Get classes by stream."""
        return self.filter(
            stream_id=stream_id,
            is_active=True
        ).order_by('grade_level', 'section')
    
    def by_academic_year(self, year_id: str) -> models.QuerySet:
        """Get classes by academic year."""
        return self.filter(
            academic_year_id=year_id,
            is_active=True
        ).order_by('grade_level', 'section')


class AssessmentQuerySet(models.QuerySet):
    """Custom queryset for Assessment model."""
    
    def by_type(self, assessment_type: str) -> 'AssessmentQuerySet':
        """Filter by assessment type."""
        return self.filter(assessment_type=assessment_type)
    
    def by_subject(self, subject_id: str) -> 'AssessmentQuerySet':
        """Filter by subject."""
        return self.filter(subject_id=subject_id)
    
    def by_class(self, class_id: str) -> 'AssessmentQuerySet':
        """Filter by class."""
        return self.filter(class_assigned_id=class_id)
    
    def by_term(self, term_id: str) -> 'AssessmentQuerySet':
        """Filter by academic term."""
        return self.filter(academic_term_id=term_id)
    
    def upcoming(self) -> 'AssessmentQuerySet':
        """Get upcoming assessments."""
        today = timezone.now().date()
        return self.filter(
            assessment_date__gte=today,
            assessment_status__in=['scheduled', 'draft']
        ).order_by('assessment_date')
    
    def past_due(self) -> 'AssessmentQuerySet':
        """Get past due assessments."""
        today = timezone.now().date()
        return self.filter(
            Q(due_date__lt=today) | Q(assessment_date__lt=today),
            assessment_status__in=['scheduled', 'in_progress']
        ).order_by('assessment_date')
    
    def with_statistics(self) -> 'AssessmentQuerySet':
        """Annotate with statistics."""
        return self.annotate(
            student_count=Count('student_results', distinct=True),
            average_score=Avg('student_results__total_score'),
            max_score=Max('student_results__total_score'),
            min_score=Min('student_results__total_score'),
            completion_rate=ExpressionWrapper(
                Count('student_results', filter=Q(student_results__submission_status='graded')) * 100.0 /
                Case(
                    When(class_assigned__current_strength__gt=0, then=F('class_assigned__current_strength')),
                    default=Value(1),
                    output_field=models.FloatField()
                ),
                output_field=models.FloatField()
            )
        )
    
    def with_related(self) -> 'AssessmentQuerySet':
        """Prefetch related objects."""
        return self.select_related(
            'subject', 'class_assigned', 'academic_year', 'academic_term'
        ).prefetch_related('student_results')


class StudentAssessmentQuerySet(models.QuerySet):
    """Custom queryset for StudentAssessment model."""
    
    def by_student(self, student_id: str) -> 'StudentAssessmentQuerySet':
        """Filter by student."""
        return self.filter(student_id=student_id)
    
    def by_assessment(self, assessment_id: str) -> 'StudentAssessmentQuerySet':
        """Filter by assessment."""
        return self.filter(assessment_id=assessment_id)
    
    def graded(self) -> 'StudentAssessmentQuerySet':
        """Get graded assessments."""
        return self.filter(submission_status='graded')
    
    def pending(self) -> 'StudentAssessmentQuerySet':
        """Get pending assessments."""
        return self.filter(submission_status__in=['not_started', 'in_progress', 'submitted'])
    
    def passing(self, pass_mark: float = 40.0) -> 'StudentAssessmentQuerySet':
        """Get passing assessments."""
        return self.filter(percentage__gte=pass_mark)
    
    def failing(self, pass_mark: float = 40.0) -> 'StudentAssessmentQuerySet':
        """Get failing assessments."""
        return self.filter(percentage__lt=pass_mark)
    
    def with_performance(self) -> 'StudentAssessmentQuerySet':
        """Annotate with performance metrics."""
        return self.annotate(
            performance_level=Case(
                When(percentage__gte=80, then=Value('excellent')),
                When(percentage__gte=70, then=Value('good')),
                When(percentage__gte=60, then=Value('average')),
                When(percentage__gte=50, then=Value('below_average')),
                When(percentage__gte=40, then=Value('poor')),
                default=Value('fail'),
                output_field=models.CharField()
            )
        )
    
    def by_academic_year(self, year_id: str) -> 'StudentAssessmentQuerySet':
        """Filter by academic year."""
        return self.filter(assessment__academic_year_id=year_id)
    
    def by_term(self, term_id: str) -> 'StudentAssessmentQuerySet':
        """Filter by academic term."""
        return self.filter(assessment__academic_term_id=term_id)


class ReportCardManager(AcademicManager):
    """Custom manager for ReportCard."""
    
    def by_student(self, student_id: str) -> models.QuerySet:
        """Get report cards by student."""
        return self.filter(
            student_id=student_id,
            is_active=True
        ).order_by('-academic_year', '-academic_term')
    
    def by_class(self, class_id: str) -> models.QuerySet:
        """Get report cards by class."""
        return self.filter(
            class_assigned_id=class_id,
            is_active=True
        ).order_by('-academic_year', '-academic_term')
    
    def published(self) -> models.QuerySet:
        """Get published report cards."""
        return self.filter(
            is_published=True,
            is_active=True
        )
    
    def by_academic_year(self, year_id: str) -> models.QuerySet:
        """Get report cards by academic year."""
        return self.filter(
            academic_year_id=year_id,
            is_active=True
        ).order_by('-academic_term', 'student')
    
    def with_performance_stats(self) -> models.QuerySet:
        """Annotate with performance statistics."""
        return self.annotate(
            performance_rating=Case(
                When(average_percentage__gte=80, then=Value('excellent')),
                When(average_percentage__gte=70, then=Value('very_good')),
                When(average_percentage__gte=60, then=Value('good')),
                When(average_percentage__gte=50, then=Value('average')),
                When(average_percentage__gte=40, then=Value('below_average')),
                default=Value('poor'),
                output_field=models.CharField()
            )
        )
    
    def get_latest_by_student(self, student_id: str) -> Optional['ReportCard']:
        """Get the latest report card for a student."""
        return self.filter(
            student_id=student_id,
            is_published=True
        ).order_by('-academic_year', '-academic_term').first()


class GradingSystemManager(AcademicManager):
    """Custom manager for GradingSystem."""
    
    def active_systems(self) -> models.QuerySet:
        """Get active grading systems."""
        return self.filter(
            is_active=True,
            is_archived=False
        ).order_by('name')
    
    def default_system(self) -> Optional['GradingSystem']:
        """Get the default grading system."""
        return self.filter(
            is_default=True,
            is_active=True
        ).first()
    
    def by_curriculum(self, curriculum_id: str) -> models.QuerySet:
        """Get grading systems by curriculum."""
        return self.filter(
            curriculum_id=curriculum_id,
            is_active=True
        ).order_by('name')
    
    def by_type(self, system_type: str) -> models.QuerySet:
        """Get grading systems by type."""
        return self.filter(
            system_type=system_type,
            is_active=True
        ).order_by('name')
    
    def with_usage_count(self) -> models.QuerySet:
        """Annotate with usage count."""
        return self.annotate(
            usage_count=Count('gradebooks', distinct=True)
        )


# ============================================================================
# CUSTOM QUERYSET MANAGERS
# ============================================================================

class CurriculumManager(SearchManager):
    """Custom manager for Curriculum."""
    
    def active_curricula(self) -> models.QuerySet:
        """Get active curricula."""
        return self.filter(
            is_active=True,
            is_archived=False
        ).order_by('name')
    
    def by_country(self, country: str) -> models.QuerySet:
        """Get curricula by country."""
        return self.filter(
            country__iexact=country,
            is_active=True
        ).order_by('name')
    
    def national_curricula(self) -> models.QuerySet:
        """Get national curricula."""
        return self.filter(
            is_national=True,
            is_active=True
        ).order_by('country', 'name')
    
    def with_subject_count(self) -> models.QuerySet:
        """Annotate with subject count."""
        return self.annotate(
            subject_count=Count('syllabi__subject', distinct=True)
        )


class StreamManager(SearchManager):
    """Custom manager for Stream."""
    
    def active_streams(self) -> models.QuerySet:
        """Get active streams."""
        return self.filter(
            is_active=True,
            is_archived=False
        ).order_by('name')
    
    def by_type(self, stream_type: str) -> models.QuerySet:
        """Get streams by type."""
        return self.filter(
            stream_type=stream_type,
            is_active=True
        ).order_by('name')
    
    def cbc_pathways(self) -> models.QuerySet:
        """Get CBC pathways."""
        return self.filter(
            stream_type='cbc_pathway',
            is_active=True
        ).order_by('name')
    
    def with_enrollment_stats(self) -> models.QuerySet:
        """Annotate with enrollment statistics."""
        return self.annotate(
            enrollment_percentage=ExpressionWrapper(
                F('current_enrollment') * 100.0 / Case(
                    When(capacity__gt=0, then=F('capacity')),
                    default=Value(1),
                    output_field=models.FloatField()
                ),
                output_field=models.FloatField()
            )
        )
    
    def available_for_admissions(self) -> models.QuerySet:
        """Get streams available for admissions."""
        return self.filter(
            is_active_for_admissions=True,
            is_active=True
        ).order_by('name')


class AcademicEventManager(AcademicManager):
    """Custom manager for AcademicEvent."""
    
    def upcoming_events(self, days: int = 30) -> models.QuerySet:
        """Get upcoming events."""
        today = timezone.now().date()
        future_date = today + timezone.timedelta(days=days)
        
        return self.filter(
            start_date__range=[today, future_date],
            is_active=True
        ).order_by('start_date', 'start_time')
    
    def current_events(self) -> models.QuerySet:
        """Get currently happening events."""
        today = timezone.now().date()
        
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).order_by('start_time')
    
    def by_type(self, event_type: str) -> models.QuerySet:
        """Get events by type."""
        return self.filter(
            event_type=event_type,
            is_active=True
        ).order_by('-start_date')
    
    def by_scope(self, scope: str) -> models.QuerySet:
        """Get events by scope."""
        return self.filter(
            event_scope=scope,
            is_active=True
        ).order_by('-start_date')
    
    def by_priority(self, priority: str) -> models.QuerySet:
        """Get events by priority."""
        return self.filter(
            priority=priority,
            is_active=True
        ).order_by('start_date')
    
    def school_wide_events(self) -> models.QuerySet:
        """Get school-wide events."""
        return self.filter(
            event_scope='school_wide',
            is_active=True
        ).order_by('start_date')


class LessonPlanManager(AcademicManager):
    """Custom manager for LessonPlan."""
    
    def by_teacher(self, teacher_id: str) -> models.QuerySet:
        """Get lesson plans by teacher."""
        return self.filter(
            teacher_id=teacher_id,
            is_active=True
        ).order_by('-lesson_date', '-lesson_time')
    
    def by_class(self, class_id: str) -> models.QuerySet:
        """Get lesson plans by class."""
        return self.filter(
            class_assigned_id=class_id,
            is_active=True
        ).order_by('-lesson_date', '-lesson_time')
    
    def by_subject(self, subject_id: str) -> models.QuerySet:
        """Get lesson plans by subject."""
        return self.filter(
            subject_id=subject_id,
            is_active=True
        ).order_by('-lesson_date', '-lesson_time')
    
    def upcoming_lessons(self, days: int = 7) -> models.QuerySet:
        """Get upcoming lessons."""
        today = timezone.now().date()
        future_date = today + timezone.timedelta(days=days)
        
        return self.filter(
            lesson_date__range=[today, future_date],
            is_active=True
        ).order_by('lesson_date', 'lesson_time')
    
    def today_lessons(self) -> models.QuerySet:
        """Get today's lessons."""
        today = timezone.now().date()
        
        return self.filter(
            lesson_date=today,
            is_active=True
        ).order_by('lesson_time')
    
    def completed_lessons(self) -> models.QuerySet:
        """Get completed lessons."""
        return self.filter(
            lesson_status='completed',
            is_active=True
        ).order_by('-lesson_date', '-lesson_time')
    
    def with_completion_stats(self) -> models.QuerySet:
        """Annotate with completion statistics."""
        return self.annotate(
            is_overdue=Case(
                When(
                    lesson_date__lt=timezone.now().date(),
                    lesson_status='planned',
                    then=Value(True)
                ),
                default=Value(False),
                output_field=models.BooleanField()
            )
        )


# ============================================================================
# BULK OPERATION MANAGERS
# ============================================================================

class BulkOperationManager:
    """Manager for bulk operations."""
    
    @staticmethod
    def bulk_update_class_strengths(class_ids: List[str]) -> Dict[str, Any]:
        """Bulk update class strengths."""
        from django.apps import apps
        
        try:
            StudentClassAssignment = apps.get_model('students', 'StudentClassAssignment')
            Class = apps.get_model('academic', 'Class')
            
            results = []
            for class_id in class_ids:
                try:
                    class_obj = Class.objects.get(id=class_id)
                    count = StudentClassAssignment.objects.filter(
                        class_enrolled=class_obj,
                        enrollment_status='active',
                        is_active=True
                    ).count()
                    
                    Class.objects.filter(id=class_id).update(current_strength=count)
                    results.append({
                        'class_id': class_id,
                        'status': 'success',
                        'new_strength': count
                    })
                except Class.DoesNotExist:
                    results.append({
                        'class_id': class_id,
                        'status': 'error',
                        'error': 'Class not found'
                    })
                except Exception as e:
                    results.append({
                        'class_id': class_id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return {
                'total': len(class_ids),
                'successful': len([r for r in results if r['status'] == 'success']),
                'failed': len([r for r in results if r['status'] == 'error']),
                'results': results
            }
            
        except LookupError as e:
            return {
                'total': len(class_ids),
                'successful': 0,
                'failed': len(class_ids),
                'error': str(e)
            }
    
    @staticmethod
    def bulk_generate_report_cards(term_id: str) -> Dict[str, Any]:
        """Bulk generate report cards for a term."""
        from django.apps import apps
        
        try:
            ReportCard = apps.get_model('academic', 'ReportCard')
            GradeBook = apps.get_model('academic', 'GradeBook')
            AcademicTerm = apps.get_model('academic', 'AcademicTerm')
            
            term = AcademicTerm.objects.get(id=term_id)
            students = GradeBook.objects.filter(
                academic_term=term,
                is_completed=True
            ).values('student').distinct()
            
            results = []
            for student_data in students:
                try:
                    report_card, created = ReportCard.objects.get_or_create(
                        student_id=student_data['student'],
                        academic_year=term.academic_year,
                        academic_term=term,
                        defaults={'is_generated': False}
                    )
                    
                    if not report_card.is_generated:
                        report_card.generate_report()
                    
                    results.append({
                        'student_id': student_data['student'],
                        'status': 'success',
                        'created': created,
                        'report_card_id': str(report_card.id)
                    })
                except Exception as e:
                    results.append({
                        'student_id': student_data['student'],
                        'status': 'error',
                        'error': str(e)
                    })
            
            return {
                'term': term.name,
                'total_students': len(students),
                'processed': len(results),
                'successful': len([r for r in results if r['status'] == 'success']),
                'failed': len([r for r in results if r['status'] == 'error']),
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# ============================================================================
# ANALYTICS AND REPORTING MANAGERS
# ============================================================================

class AnalyticsManager:
    """Manager for academic analytics."""
    
    @staticmethod
    def get_academic_year_analytics(year_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for an academic year."""
        from django.apps import apps
        
        try:
            AcademicYear = apps.get_model('academic', 'AcademicYear')
            Class = apps.get_model('academic', 'Class')
            Subject = apps.get_model('academic', 'Subject')
            GradeBook = apps.get_model('academic', 'GradeBook')
            
            year = AcademicYear.objects.get(id=year_id)
            
            # Class statistics
            class_stats = Class.objects.filter(
                academic_year=year,
                is_active=True
            ).aggregate(
                total_classes=Count('id'),
                total_capacity=Sum('capacity'),
                total_students=Sum('current_strength'),
                avg_occupancy=Avg('current_strength') * 100.0 / Avg('capacity')
            )
            
            # Subject statistics
            subject_stats = Subject.objects.filter(
                subject_assignments__academic_year=year,
                is_active=True
            ).aggregate(
                total_subjects=Count('id', distinct=True),
                avg_periods=Avg('periods_per_week')
            )
            
            # Performance statistics
            performance_stats = GradeBook.objects.filter(
                academic_year=year,
                is_completed=True
            ).aggregate(
                avg_performance=Avg('total_score'),
                pass_rate=Avg(
                    Case(
                        When(total_score__gte=F('subject__minimum_pass_mark'), then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                ) * 100
            )
            
            return {
                'academic_year': {
                    'id': str(year.id),
                    'name': year.name,
                    'code': year.code,
                    'status': year.status,
                    'progress': year.progress_percentage
                },
                'class_statistics': class_stats,
                'subject_statistics': subject_stats,
                'performance_statistics': performance_stats,
                'term_count': year.terms.count(),
                'assessment_count': year.assessments.count(),
                'report_card_count': year.report_cards.filter(is_published=True).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting academic year analytics: {e}")
            return {
                'error': str(e)
            }
    
    @staticmethod
    def get_class_performance_analytics(class_id: str, term_id: str = None) -> Dict[str, Any]:
        """Get performance analytics for a class."""
        from django.apps import apps
        
        try:
            Class = apps.get_model('academic', 'Class')
            GradeBook = apps.get_model('academic', 'GradeBook')
            StudentAssessment = apps.get_model('assessments', 'StudentAssessment')
            
            class_obj = Class.objects.get(id=class_id)
            
            # Build filters
            filters = {
                'class_assigned': class_obj,
                'is_completed': True
            }
            
            if term_id:
                filters['academic_term_id'] = term_id
            
            # Grade book analytics
            gradebook_stats = GradeBook.objects.filter(**filters).aggregate(
                avg_score=Avg('total_score'),
                max_score=Max('total_score'),
                min_score=Min('total_score'),
                pass_rate=Avg(
                    Case(
                        When(total_score__gte=F('subject__minimum_pass_mark'), then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                ) * 100,
                total_assessments=Count('id')
            )
            
            # Subject-wise performance
            subject_performance = GradeBook.objects.filter(**filters).values(
                'subject__name',
                'subject__code'
            ).annotate(
                avg_score=Avg('total_score'),
                pass_rate=Avg(
                    Case(
                        When(total_score__gte=F('subject__minimum_pass_mark'), then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                ) * 100,
                student_count=Count('student', distinct=True)
            ).order_by('-avg_score')
            
            # Top performing students
            top_students = GradeBook.objects.filter(**filters).values(
                'student__full_name',
                'student__admission_number'
            ).annotate(
                avg_score=Avg('total_score'),
                subject_count=Count('subject', distinct=True)
            ).order_by('-avg_score')[:10]
            
            return {
                'class': {
                    'id': str(class_obj.id),
                    'name': class_obj.display_name,
                    'grade_level': class_obj.get_grade_level_display(),
                    'strength': class_obj.current_strength,
                    'capacity': class_obj.capacity
                },
                'overall_statistics': gradebook_stats,
                'subject_performance': list(subject_performance),
                'top_students': list(top_students),
                'total_subjects': len(subject_performance)
            }
            
        except Exception as e:
            logger.error(f"Error getting class performance analytics: {e}")
            return {
                'error': str(e)
            }
    
    @staticmethod
    def get_student_progress_analytics(student_id: str, year_id: str = None) -> Dict[str, Any]:
        """Get progress analytics for a student."""
        from django.apps import apps
        
        try:
            StudentProfile = apps.get_model('students', 'StudentProfile')
            GradeBook = apps.get_model('academic', 'GradeBook')
            ReportCard = apps.get_model('academic', 'ReportCard')
            
            student = StudentProfile.objects.get(id=student_id)
            
            # Build filters
            filters = {
                'student': student,
                'is_completed': True
            }
            
            if year_id:
                filters['academic_year_id'] = year_id
            
            # Grade book analytics
            gradebook_stats = GradeBook.objects.filter(**filters).aggregate(
                avg_score=Avg('total_score'),
                max_score=Max('total_score'),
                min_score=Min('total_score'),
                total_subjects=Count('subject', distinct=True),
                passed_subjects=Count(
                    'id',
                    filter=Q(total_score__gte=F('subject__minimum_pass_mark'))
                )
            )
            
            # Term-wise performance
            term_performance = GradeBook.objects.filter(**filters).values(
                'academic_term__name',
                'academic_term__term_order'
            ).annotate(
                avg_score=Avg('total_score'),
                subject_count=Count('subject', distinct=True)
            ).order_by('academic_term__term_order')
            
            # Subject-wise performance
            subject_performance = GradeBook.objects.filter(**filters).values(
                'subject__name',
                'subject__code',
                'subject__category'
            ).annotate(
                avg_score=Avg('total_score'),
                grade=Max('grade'),
                is_passing=Max(
                    Case(
                        When(total_score__gte=F('subject__minimum_pass_mark'), then=True),
                        default=False,
                        output_field=models.BooleanField()
                    )
                )
            ).order_by('-avg_score')
            
            # Report card history
            report_cards = ReportCard.objects.filter(
                student=student,
                is_published=True
            ).order_by('-academic_year', '-academic_term').values(
                'academic_year__name',
                'academic_term__name',
                'average_percentage',
                'overall_grade',
                'class_position',
                'attendance_percentage'
            )[:5]
            
            return {
                'student': {
                    'id': str(student.id),
                    'name': student.full_name,
                    'admission_number': student.admission_number,
                    'current_class': student.current_class.display_name if student.current_class else None
                },
                'overall_statistics': gradebook_stats,
                'term_performance': list(term_performance),
                'subject_performance': list(subject_performance),
                'report_card_history': list(report_cards),
                'pass_rate': (gradebook_stats['passed_subjects'] / gradebook_stats['total_subjects'] * 100 
                            if gradebook_stats['total_subjects'] > 0 else 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting student progress analytics: {e}")
            return {
                'error': str(e)
            }


# ============================================================================
# CACHE MANAGEMENT MANAGERS
# ============================================================================

class CacheManager:
    """Manager for cache operations."""
    
    CACHE_KEYS = {
        'current_academic_year': 'current_academic_year',
        'current_academic_term': 'current_academic_term',
        'active_academic_years': 'active_academic_years',
        'school_info': 'school_info_{}',
        'class_statistics': 'class_stats_{}',
        'subject_list': 'subject_list_{}',
    }
    
    @classmethod
    def clear_academic_cache(cls, specific_keys: List[str] = None) -> bool:
        """Clear academic cache."""
        from django.core.cache import cache
        
        try:
            if specific_keys:
                for key in specific_keys:
                    cache.delete(key)
            else:
                # Clear all academic cache keys
                for key_pattern in cls.CACHE_KEYS.values():
                    if '{}' in key_pattern:
                        # Delete pattern-based keys
                        cache.delete_pattern(key_pattern.format('*'))
                    else:
                        cache.delete(key_pattern)
            
            return True
        except Exception as e:
            logger.error(f"Error clearing academic cache: {e}")
            return False
    
    @classmethod
    def get_cached_data(cls, cache_key: str, fetch_function, timeout: int = 3600, **kwargs):
        """Get cached data or fetch and cache."""
        from django.core.cache import cache
        
        data = cache.get(cache_key)
        
        if data is None:
            data = fetch_function(**kwargs)
            if data is not None:
                cache.set(cache_key, data, timeout)
        
        return data
    
    @classmethod
    def invalidate_class_cache(cls, class_id: str) -> bool:
        """Invalidate cache for a specific class."""
        from django.core.cache import cache
        
        cache_key = cls.CACHE_KEYS['class_statistics'].format(class_id)
        cache.delete(cache_key)
        
        return True
    
    @classmethod
    def invalidate_subject_cache(cls, curriculum: str = None) -> bool:
        """Invalidate subject cache."""
        from django.core.cache import cache
        
        if curriculum:
            cache_key = cls.CACHE_KEYS['subject_list'].format(curriculum)
            cache.delete(cache_key)
        else:
            # Delete all subject list caches
            cache.delete_pattern(cls.CACHE_KEYS['subject_list'].format('*'))
        
        return True


# ============================================================================
# EXPORT/IMPORT MANAGERS
# ============================================================================

class ExportManager:
    """Manager for data export operations."""
    
    @staticmethod
    def export_academic_data(format_type: str = 'json', filters: Dict[str, Any] = None) -> Any:
        """Export academic data in specified format."""
        import json
        import csv
        from io import StringIO
        from django.apps import apps
        
        try:
            data = {
                'academic_years': [],
                'academic_terms': [],
                'classes': [],
                'subjects': [],
                'assessments': [],
            }
            
            # Export academic years
            academic_years = apps.get_model('academic', 'AcademicYear').objects.filter(is_active=True)
            if filters and 'academic_year' in filters:
                academic_years = academic_years.filter(id=filters['academic_year'])
            
            for ay in academic_years:
                data['academic_years'].append({
                    'id': str(ay.id),
                    'name': ay.name,
                    'code': ay.code,
                    'start_date': ay.start_date.isoformat() if ay.start_date else None,
                    'end_date': ay.end_date.isoformat() if ay.end_date else None,
                    'curriculum': ay.curriculum_system,
                    'is_current': ay.is_current,
                })
            
            # Export academic terms
            academic_terms = apps.get_model('academic', 'AcademicTerm').objects.filter(is_active=True)
            if filters:
                if 'academic_year' in filters:
                    academic_terms = academic_terms.filter(academic_year_id=filters['academic_year'])
                if 'term' in filters:
                    academic_terms = academic_terms.filter(id=filters['term'])
            
            for term in academic_terms:
                data['academic_terms'].append({
                    'id': str(term.id),
                    'name': term.name,
                    'code': term.code,
                    'start_date': term.start_date.isoformat() if term.start_date else None,
                    'end_date': term.end_date.isoformat() if term.end_date else None,
                    'academic_year': term.academic_year.name,
                    'term_order': term.term_order,
                })
            
            # Export classes
            classes = apps.get_model('academic', 'Class').objects.filter(is_active=True)
            if filters:
                if 'academic_year' in filters:
                    classes = classes.filter(academic_year_id=filters['academic_year'])
                if 'grade_level' in filters:
                    classes = classes.filter(grade_level=filters['grade_level'])
                if 'stream' in filters:
                    classes = classes.filter(stream_id=filters['stream'])
            
            for cls in classes:
                data['classes'].append({
                    'id': str(cls.id),
                    'name': cls.display_name,
                    'code': cls.code,
                    'grade_level': cls.grade_level,
                    'section': cls.section,
                    'stream': cls.stream.name if cls.stream else None,
                    'capacity': cls.capacity,
                    'current_strength': cls.current_strength,
                    'class_teacher': cls.class_teacher.full_name if cls.class_teacher else None,
                })
            
            # Export subjects
            subjects = apps.get_model('academic', 'Subject').objects.filter(is_active=True)
            if filters:
                if 'curriculum' in filters:
                    subjects = subjects.filter(curriculum_system=filters['curriculum'])
                if 'grade_level' in filters:
                    subjects = subjects.filter(grade_levels__contains=[filters['grade_level']])
            
            for subject in subjects:
                data['subjects'].append({
                    'id': str(subject.id),
                    'name': subject.name,
                    'code': subject.code,
                    'category': subject.category,
                    'curriculum': subject.curriculum_system,
                    'credits': float(subject.credits),
                    'periods_per_week': subject.periods_per_week,
                    'grade_levels': subject.grade_levels,
                })
            
            # Format-specific processing
            if format_type == 'json':
                return json.dumps(data, indent=2, default=str)
            elif format_type == 'csv':
                output = StringIO()
                writer = csv.writer(output)
                
                # Write headers
                writer.writerow(['Type', 'ID', 'Name', 'Code', 'Details'])
                
                # Write data
                for ay in data['academic_years']:
                    writer.writerow([
                        'Academic Year',
                        ay['id'],
                        ay['name'],
                        ay['code'],
                        f"Start: {ay['start_date']}, End: {ay['end_date']}"
                    ])
                
                for term in data['academic_terms']:
                    writer.writerow([
                        'Academic Term',
                        term['id'],
                        term['name'],
                        term['code'],
                        f"Year: {term['academic_year']}, Order: {term['term_order']}"
                    ])
                
                for cls in data['classes']:
                    writer.writerow([
                        'Class',
                        cls['id'],
                        cls['name'],
                        cls['code'],
                        f"Grade: {cls['grade_level']}, Students: {cls['current_strength']}/{cls['capacity']}"
                    ])
                
                for subject in data['subjects']:
                    writer.writerow([
                        'Subject',
                        subject['id'],
                        subject['name'],
                        subject['code'],
                        f"Category: {subject['category']}, Credits: {subject['credits']}"
                    ])
                
                return output.getvalue()
            
            return None
            
        except Exception as e:
            logger.error(f"Error exporting academic data: {e}")
            return None
    
    @staticmethod
    def export_student_report(student_id: str, format_type: str = 'pdf') -> Any:
        """Export student report."""
        # This would typically integrate with a report generation library
        # For now, return a placeholder
        return f"Student report for {student_id} in {format_type} format"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_class_average(class_id: str, academic_year_id: str = None) -> float:
    """Calculate class average performance."""
    from django.apps import apps
    
    try:
        GradeBook = apps.get_model('academic', 'GradeBook')
        
        filters = {
            'class_assigned_id': class_id,
            'is_completed': True
        }
        
        if academic_year_id:
            filters['academic_year_id'] = academic_year_id
        
        result = GradeBook.objects.filter(**filters).aggregate(
            avg_score=Avg('total_score')
        )
        
        return float(result['avg_score'] or 0)
        
    except Exception as e:
        logger.error(f"Error calculating class average: {e}")
        return 0.0


def calculate_student_gpa(student_id: str, academic_year_id: str = None) -> float:
    """Calculate student GPA."""
    from django.apps import apps
    
    try:
        GradeBook = apps.get_model('academic', 'GradeBook')
        
        filters = {
            'student_id': student_id,
            'is_completed': True
        }
        
        if academic_year_id:
            filters['academic_year_id'] = academic_year_id
        
        grade_books = GradeBook.objects.filter(**filters)
        
        total_grade_points = 0
        total_credits = 0
        
        for gb in grade_books:
            if gb.points and gb.subject.credits:
                total_grade_points += float(gb.points) * float(gb.subject.credits)
                total_credits += float(gb.subject.credits)
        
        if total_credits > 0:
            return total_grade_points / total_credits
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Error calculating student GPA: {e}")
        return 0.0


def get_student_rank(student_id: str, class_id: str, academic_year_id: str, academic_term_id: str) -> int:
    """Get student rank in class."""
    from django.apps import apps
    
    try:
        GradeBook = apps.get_model('academic', 'GradeBook')
        
        # Get all students in the class with their average scores
        students = GradeBook.objects.filter(
            class_assigned_id=class_id,
            academic_year_id=academic_year_id,
            academic_term_id=academic_term_id,
            is_completed=True
        ).values('student').annotate(
            total_average=Avg('total_score')
        ).order_by('-total_average')
        
        # Find student position
        for index, student_data in enumerate(students, start=1):
            if student_data['student'] == student_id:
                return index
        
        return None
        
    except Exception as e:
        logger.error(f"Error calculating student rank: {e}")
        return None


def validate_academic_data(data: Dict[str, Any], model_type: str) -> List[str]:
    """Validate academic data before import/creation."""
    errors = []
    
    if model_type == 'academic_year':
        required_fields = ['name', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate dates
        if 'start_date' in data and 'end_date' in data:
            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
                if start_date >= end_date:
                    errors.append("End date must be after start date")
            except ValueError:
                errors.append("Invalid date format")
    
    elif model_type == 'subject':
        required_fields = ['name', 'code', 'category']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate category
        valid_categories = ['core', 'elective', 'cbc_core', 'cbc_optional', 'pathway_core', 'pathway_elective']
        if 'category' in data and data['category'] not in valid_categories:
            errors.append(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    return errors


# ============================================================================
# EXPORT ALL MANAGERS
# ============================================================================

__all__ = [
    # Base Managers
    'AcademicManager',
    'SearchManager',
    
    # Model-specific Managers
    'AcademicYearManager',
    'AcademicTermManager',
    'SubjectManager',
    'ClassManager',
    'ReportCardManager',
    'GradingSystemManager',
    'CurriculumManager',
    'StreamManager',
    'AcademicEventManager',
    'LessonPlanManager',
    
    # QuerySets
    'AssessmentQuerySet',
    'StudentAssessmentQuerySet',
    
    # Specialized Managers
    'BulkOperationManager',
    'AnalyticsManager',
    'CacheManager',
    'ExportManager',
    
    # Utility Functions
    'calculate_class_average',
    'calculate_student_gpa',
    'get_student_rank',
    'validate_academic_data',
]