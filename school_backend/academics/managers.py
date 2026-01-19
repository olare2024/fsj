# academics/managers.py

import logging
from datetime import timedelta

from django.db import models
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, Value, When, Case, FloatField
from django.core.cache import cache
from django.utils import timezone
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import FieldError

logger = logging.getLogger(__name__)


class BaseActiveManager(models.Manager):
    """Base manager that safely filters by is_active only when models are ready"""
    
    def get_queryset(self):
        """Safely filter by is_active when models are ready"""
        try:
            # Try to filter by is_active if the field exists
            return super().get_queryset().filter(is_active=True)
        except (FieldError, OperationalError, ProgrammingError) as e:
            # During imports or before tables exist, return unfiltered queryset
            logger.debug(f"Returning unfiltered queryset for {self.model.__name__}: {e}")
            return super().get_queryset()
    
    def all_active(self):
        """Explicitly get all active records (safe to use anywhere)"""
        return super().get_queryset().filter(is_active=True)


class AcademicYearManager(BaseActiveManager):
    """Enhanced manager for AcademicYear model with caching and query optimization"""

    def current(self, use_cache=True):
        """Get current academic year with optimization"""
        if use_cache:
            cache_key = "current_academic_year"
            current_year = cache.get(cache_key)
            
            if current_year is None:
                current_year = self._get_current_year()
                if current_year:
                    cache.set(cache_key, current_year, 300)  # Cache for 5 minutes
            return current_year
        return self._get_current_year()
    
    def _get_current_year(self):
        """Internal method to get current academic year from database"""
        try:
            return (
                self.all_active()
                .filter(is_current=True)
                .select_related("created_by", "updated_by")
                .first()
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch current academic year: {e}")
            return None

    def upcoming(self, limit=5):
        """Get upcoming academic years"""
        try:
            today = timezone.now().date()
            return (
                self.all_active()
                .filter(start_date__gt=today)
                .select_related("created_by", "updated_by")
                .order_by("start_date")[:limit]
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch upcoming academic years: {e}")
            return self.none()

    def active_years(self):
        """Get currently active academic years (date range)"""
        try:
            today = timezone.now().date()
            return (
                self.all_active()
                .filter(start_date__lte=today, end_date__gte=today)
                .select_related("created_by", "updated_by")
                .order_by("-start_date")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch active academic years: {e}")
            return self.none()

    def get_years_with_stats(self):
        """Get academic years with basic statistics"""
        try:
            return (
                self.all_active()
                .annotate(
                    term_count=Count("terms", filter=Q(terms__is_active=True)),
                    syllabus_count=Count(
                        "cbc_syllabuses", filter=Q(cbc_syllabuses__is_active=True)
                    ),
                )
                .order_by("-start_date")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch academic years with stats: {e}")
            return self.none()

    def by_code(self, code):
        """Get academic year by code"""
        try:
            return self.all_active().filter(code=code).first()
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch academic year by code {code}: {e}")
            return None

    def with_progress(self):
        """Get academic years annotated with progress percentage"""
        try:
            today = timezone.now().date()
            return (
                self.all_active()
                .annotate(
                    days_elapsed=ExpressionWrapper(
                        today - F("start_date"),
                        output_field=models.DurationField(),
                    ),
                    total_days=ExpressionWrapper(
                        F("end_date") - F("start_date"),
                        output_field=models.DurationField(),
                    ),
                )
                .annotate(
                    progress_percentage=Case(
                        When(
                            total_days__gt=0,
                            then=ExpressionWrapper(
                                F("days_elapsed") * 100.0 / F("total_days"),
                                output_field=FloatField(),
                            ),
                        ),
                        default=Value(0),
                        output_field=FloatField(),
                    )
                )
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not calculate academic year progress: {e}")
            return self.none()

    def get_recent_years(self, years=5):
        """Get recent academic years"""
        try:
            return (
                self.all_active()
                .order_by("-start_date")
                .select_related("created_by", "updated_by")[:years]
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch recent academic years: {e}")
            return self.none()

    def get_years_by_type(self, year_type):
        """Get academic years by type"""
        try:
            return (
                self.all_active()
                .filter(year_type=year_type)
                .select_related("created_by", "updated_by")
                .order_by("-start_date")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch academic years by type {year_type}: {e}")
            return self.none()

    def clear_current_cache(self):
        """Clear the current academic year cache"""
        cache.delete("current_academic_year")
        logger.debug("Cleared current academic year cache")


class AcademicTermManager(BaseActiveManager):
    """Enhanced manager for AcademicTerm model with caching"""

    def current(self, use_cache=True):
        """Get current term with optimization"""
        if use_cache:
            cache_key = "current_academic_term"
            current_term = cache.get(cache_key)
            
            if current_term is None:
                current_term = self._get_current_term()
                if current_term:
                    cache.set(cache_key, current_term, 300)  # Cache for 5 minutes
            return current_term
        return self._get_current_term()
    
    def _get_current_term(self):
        """Internal method to get current academic term from database"""
        try:
            return (
                self.all_active()
                .filter(is_current=True)
                .select_related(
                    "academic_year",
                    "created_by",
                    "updated_by",
                )
                .first()
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch current academic term: {e}")
            return None

    def by_academic_year(self, academic_year_id):
        """Get terms by academic year"""
        try:
            return (
                self.all_active()
                .filter(academic_year_id=academic_year_id)
                .select_related(
                    "academic_year",
                    "created_by",
                    "updated_by",
                )
                .order_by("term_number")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch terms for academic year {academic_year_id}: {e}")
            return self.none()

    def active_terms(self):
        """Get currently active terms"""
        try:
            today = timezone.now().date()
            return (
                self.all_active()
                .filter(start_date__lte=today, end_date__gte=today)
                .select_related(
                    "academic_year",
                    "created_by",
                    "updated_by",
                )
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch active terms: {e}")
            return self.none()

    def upcoming_terms(self, days=30):
        """Get terms starting within the next X days"""
        try:
            today = timezone.now().date()
            future_date = today + timedelta(days=days)
            return (
                self.all_active()
                .filter(start_date__range=[today, future_date])
                .select_related(
                    "academic_year",
                    "created_by",
                    "updated_by",
                )
                .order_by("start_date")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch upcoming terms: {e}")
            return self.none()

    def terms_with_stats(self):
        """Get terms with basic statistics"""
        try:
            return (
                self.all_active()
                .select_related("academic_year")
                .annotate(
                    assessment_count=Count(
                        "assessments", filter=Q(assessments__is_active=True)
                    ),
                    timetable_count=Count(
                        "timetables", filter=Q(timetables__is_active=True)
                    ),
                    report_card_count=Count(
                        "report_cards", filter=Q(report_cards__is_active=True)
                    ),
                )
                .order_by("academic_year", "term_number")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch terms with stats: {e}")
            return self.none()

    def by_term_number(self, academic_year_id, term_number):
        """Get specific term by number"""
        try:
            return (
                self.all_active()
                .filter(academic_year_id=academic_year_id, term_number=term_number)
                .select_related(
                    "academic_year",
                    "created_by",
                    "updated_by",
                )
                .first()
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch term {term_number} for academic year {academic_year_id}: {e}")
            return None

    def with_progress(self):
        """Get terms annotated with progress percentage"""
        try:
            today = timezone.now().date()
            return (
                self.all_active()
                .annotate(
                    days_elapsed=Case(
                        When(
                            start_date__lte=today,
                            end_date__gte=today,
                            then=today - F("start_date"),
                        ),
                        When(end_date__lt=today, then=F("end_date") - F("start_date")),
                        default=Value(0),
                        output_field=models.DurationField(),
                    ),
                    total_days=ExpressionWrapper(
                        F("end_date") - F("start_date"),
                        output_field=models.DurationField(),
                    ),
                )
                .annotate(
                    progress_percentage=Case(
                        When(
                            total_days__gt=0,
                            then=ExpressionWrapper(
                                F("days_elapsed") * 100.0 / F("total_days"),
                                output_field=FloatField(),
                            ),
                        ),
                        default=Value(0),
                        output_field=FloatField(),
                    )
                )
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not calculate term progress: {e}")
            return self.none()

    def clear_current_cache(self):
        """Clear the current term cache"""
        cache.delete("current_academic_term")
        logger.debug("Cleared current academic term cache")


class GradeLevelManager(BaseActiveManager):
    """Enhanced manager for GradeLevel model"""

    def by_education_stage(self, stage):
        """Get grade levels by education stage"""
        try:
            return (
                self.all_active()
                .filter(education_stage=stage)
                .select_related("created_by", "updated_by")
                .order_by("level")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch grade levels by stage {stage}: {e}")
            return self.none()

    def early_years_education(self):
        """Get Pre-primary 1 & 2 and Grade 1-3"""
        try:
            return self.all_active().filter(
                education_stage__in=["pre-primary", "lower-primary"]
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch early years education: {e}")
            return self.none()

    def middle_school_education(self):
        """Get Grade 4-9"""
        try:
            return self.all_active().filter(
                education_stage__in=["upper-primary", "lower-secondary"]
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch middle school education: {e}")
            return self.none()

    def senior_school(self):
        """Get Grade 10-12"""
        try:
            return self.all_active().filter(education_stage="senior-school")
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch senior school: {e}")
            return self.none()

    def get_grade_levels_with_stats(self):
        """Get grade levels with basic statistics"""
        try:
            return (
                self.all_active()
                .annotate(
                    stream_count=Count("streams", filter=Q(streams__is_active=True)),
                    syllabus_count=Count(
                        "cbc_syllabuses", filter=Q(cbc_syllabuses__is_active=True)
                    ),
                )
                .order_by("level")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch grade levels with stats: {e}")
            return self.none()

    def by_level(self, level):
        """Get grade level by numeric level"""
        try:
            return self.all_active().filter(level=level).first()
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch grade level {level}: {e}")
            return None

    def by_pathway(self, pathway):
        """Get grade levels by pathway"""
        try:
            return (
                self.all_active()
                .filter(pathway=pathway)
                .select_related("created_by", "updated_by")
                .order_by("level")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch grade levels by pathway {pathway}: {e}")
            return self.none()


class StreamManager(BaseActiveManager):
    """Enhanced manager for Stream model"""

    def with_available_seats(self, academic_year=None):
        """Get streams with available seats"""
        try:
            if not academic_year:
                academic_year = AcademicYear.objects.current()
            
            if not academic_year:
                return self.none()
            
            streams = self.all_active().annotate(
                current_enrollment=Count(
                    "student_assignments",
                    filter=Q(
                        student_assignments__academic_year=academic_year,
                        student_assignments__is_active=True,
                    ),
                ),
                available_seats=ExpressionWrapper(
                    F("capacity") - F("current_enrollment"),
                    output_field=models.IntegerField(),
                ),
            ).filter(available_seats__gt=0)
            
            return streams
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch streams with available seats: {e}")
            return self.none()

    def by_grade_level(self, grade_level_id):
        """Get streams by grade level"""
        try:
            return (
                self.all_active()
                .filter(grade_level_id=grade_level_id)
                .select_related(
                    "grade_level",
                    "class_teacher",
                    "classroom",
                    "created_by",
                    "updated_by",
                )
                .order_by("name")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch streams for grade level {grade_level_id}: {e}")
            return self.none()

    def full_streams(self, academic_year=None):
        """Get full streams"""
        try:
            if not academic_year:
                academic_year = AcademicYear.objects.current()
            
            if not academic_year:
                return self.none()
            
            streams = self.all_active().annotate(
                current_enrollment=Count(
                    "student_assignments",
                    filter=Q(
                        student_assignments__academic_year=academic_year,
                        student_assignments__is_active=True,
                    ),
                ),
            ).filter(current_enrollment__gte=F("capacity"))
            
            return streams
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch full streams: {e}")
            return self.none()

    def get_streams_with_stats(self, academic_year=None):
        """Get streams with enrollment statistics"""
        try:
            streams = self.all_active().select_related(
                "grade_level",
                "class_teacher",
                "classroom",
            )
            
            if academic_year:
                streams = streams.annotate(
                    current_enrollment=Count(
                        "student_assignments",
                        filter=Q(
                            student_assignments__academic_year=academic_year,
                            student_assignments__is_active=True,
                        ),
                    ),
                    capacity_percentage=ExpressionWrapper(
                        F("current_enrollment") * 100.0 / F("capacity"),
                        output_field=FloatField(),
                    ),
                )
            
            return streams
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch streams with stats: {e}")
            return self.none()

    def by_class_teacher(self, teacher_id):
        """Get streams by class teacher"""
        try:
            return (
                self.all_active()
                .filter(class_teacher_id=teacher_id)
                .select_related(
                    "grade_level",
                    "classroom",
                    "created_by",
                    "updated_by",
                )
                .order_by("grade_level__level", "name")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch streams for teacher {teacher_id}: {e}")
            return self.none()

    def by_classroom(self, classroom_id):
        """Get streams by classroom"""
        try:
            return (
                self.all_active()
                .filter(classroom_id=classroom_id)
                .select_related(
                    "grade_level",
                    "class_teacher",
                    "created_by",
                    "updated_by",
                )
                .order_by("grade_level__level", "name")
            )
        except (FieldError, OperationalError, ProgrammingError) as e:
            logger.warning(f"Could not fetch streams for classroom {classroom_id}: {e}")
            return self.none()


# ============================================================================
# QUERYSET CLASSES
# ============================================================================

class AcademicYearQuerySet(models.QuerySet):
    """Custom queryset methods for AcademicYear"""
    
    def with_term_counts(self):
        """Annotate with term counts"""
        try:
            return self.annotate(
                active_term_count=Count(
                    "terms", filter=Q(terms__is_active=True)
                ),
                completed_term_count=Count(
                    "terms", filter=Q(terms__term_status="completed")
                ),
            )
        except (FieldError, OperationalError, ProgrammingError):
            return self
    
    def with_progress(self):
        """Annotate with progress information"""
        try:
            today = timezone.now().date()
            return self.annotate(
                days_elapsed=ExpressionWrapper(
                    today - F("start_date"),
                    output_field=models.DurationField(),
                ),
                total_days=ExpressionWrapper(
                    F("end_date") - F("start_date"),
                    output_field=models.DurationField(),
                ),
            ).annotate(
                progress_percentage=Case(
                    When(
                        total_days__gt=0,
                        then=ExpressionWrapper(
                            F("days_elapsed") * 100.0 / F("total_days"),
                            output_field=FloatField(),
                        ),
                    ),
                    default=Value(0),
                    output_field=FloatField(),
                )
            )
        except (FieldError, OperationalError, ProgrammingError):
            return self


class AcademicTermQuerySet(models.QuerySet):
    """Custom queryset methods for AcademicTerm"""
    
    def with_assessment_counts(self):
        """Annotate with assessment counts"""
        try:
            return self.annotate(
                assessment_count=Count(
                    "assessments", filter=Q(assessments__is_active=True)
                ),
                satisfactory_assessments=Count(
                    "assessments",
                    filter=Q(assessments__is_active=True)
                    & Q(assessments__overall_grade__in=["EE", "ME"]),
                ),
            )
        except (FieldError, OperationalError, ProgrammingError):
            return self
    
    def with_progress(self):
        """Annotate with progress information"""
        try:
            today = timezone.now().date()
            return self.annotate(
                days_elapsed=Case(
                    When(
                        start_date__lte=today,
                        end_date__gte=today,
                        then=today - F("start_date"),
                    ),
                    When(end_date__lt=today, then=F("end_date") - F("start_date")),
                    default=Value(0),
                    output_field=models.DurationField(),
                ),
                total_days=ExpressionWrapper(
                    F("end_date") - F("start_date"),
                    output_field=models.DurationField(),
                ),
            ).annotate(
                progress_percentage=Case(
                    When(
                        total_days__gt=0,
                        then=ExpressionWrapper(
                            F("days_elapsed") * 100.0 / F("total_days"),
                            output_field=FloatField(),
                        ),
                    ),
                    default=Value(0),
                    output_field=FloatField(),
                )
            )
        except (FieldError, OperationalError, ProgrammingError):
            return self


# ============================================================================
# MODEL MANAGER REGISTRATION HELPERS
# ============================================================================

def create_academic_year_manager():
    """Factory function to create AcademicYear manager with custom queryset"""
    return AcademicYearManager.from_queryset(AcademicYearQuerySet)()


def create_academic_term_manager():
    """Factory function to create AcademicTerm manager with custom queryset"""
    return AcademicTermManager.from_queryset(AcademicTermQuerySet)()