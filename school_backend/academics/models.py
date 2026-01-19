# academic/models.py

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import BaseModel, User


# ============================================================================
# CONSTANTS AND ENUMS
# ============================================================================

class AcademicLevel(models.TextChoices):
    """Academic level choices"""
    PRESCHOOL = 'preschool', _('Preschool')
    PRIMARY = 'primary', _('Primary School')
    JUNIOR_SECONDARY = 'junior_secondary', _('Junior Secondary School')
    SENIOR_SECONDARY = 'senior_secondary', _('Senior Secondary School')
    TERTIARY = 'tertiary', _('Tertiary/College')


class GradeScale(models.TextChoices):
    """Grading scale choices"""
    PERCENTAGE = 'percentage', _('Percentage (0-100)')
    LETTER_GRADE = 'letter_grade', _('Letter Grade (A-F)')
    GPA = 'gpa', _('GPA (0-4.0)')
    POINTS = 'points', _('Points System')
    COMPETENCY = 'competency', _('Competency Based')


class AssessmentType(models.TextChoices):
    """Assessment type choices"""
    EXAM = 'exam', _('Exam')
    TEST = 'test', _('Test')
    QUIZ = 'quiz', _('Quiz')
    ASSIGNMENT = 'assignment', _('Assignment')
    PROJECT = 'project', _('Project')
    PRACTICAL = 'practical', _('Practical')
    ORAL = 'oral', _('Oral Exam')
    PARTICIPATION = 'participation', _('Participation')
    HOMEWORK = 'homework', _('Homework')
    CONTINUOUS_ASSESSMENT = 'continuous_assessment', _('Continuous Assessment')


class AttendanceStatus(models.TextChoices):
    """Attendance status choices"""
    PRESENT = 'present', _('Present')
    ABSENT = 'absent', _('Absent')
    LATE = 'late', _('Late')
    EXCUSED = 'excused', _('Excused')
    HALF_DAY = 'half_day', _('Half Day')
    SICK_LEAVE = 'sick_leave', _('Sick Leave')
    OTHER = 'other', _('Other')


class DayOfWeek(models.TextChoices):
    """Day of week choices"""
    MONDAY = 'monday', _('Monday')
    TUESDAY = 'tuesday', _('Tuesday')
    WEDNESDAY = 'wednesday', _('Wednesday')
    THURSDAY = 'thursday', _('Thursday')
    FRIDAY = 'friday', _('Friday')
    SATURDAY = 'saturday', _('Saturday')
    SUNDAY = 'sunday', _('Sunday')


class TermType(models.TextChoices):
    """Academic term type choices"""
    FIRST_TERM = 'first_term', _('First Term')
    SECOND_TERM = 'second_term', _('Second Term')
    THIRD_TERM = 'third_term', _('Third Term')
    SUMMER_TERM = 'summer_term', _('Summer Term')
    SPECIAL_TERM = 'special_term', _('Special Term')


class AcademicStatus(models.TextChoices):
    """Student academic status"""
    ACTIVE = 'active', _('Active')
    PROBATION = 'probation', _('Academic Probation')
    WARNING = 'warning', _('Academic Warning')
    SUSPENDED = 'suspended', _('Suspended')
    GRADUATED = 'graduated', _('Graduated')
    DROPPED = 'dropped', _('Dropped Out')
    TRANSFERRED = 'transferred', _('Transferred')


# ============================================================================
# BASE CLASSES AND MIXINS
# ============================================================================

class AcademicMixin(models.Model):
    """Mixin for academic year and term tracking"""
    
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year"),
        help_text=_("Format: YYYY-YYYY")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    
    class Meta:
        abstract = True
    
    def clean(self):
        """Validate academic year format"""
        if self.academic_year:
            try:
                years = self.academic_year.split('-')
                if len(years) != 2:
                    raise ValidationError(_("Academic year must be in format YYYY-YYYY"))
                int(years[0])
                int(years[1])
                if int(years[1]) != int(years[0]) + 1:
                    raise ValidationError(_("Second year must be one greater than first year"))
            except (ValueError, IndexError):
                raise ValidationError(_("Invalid academic year format"))


# ============================================================================
# ACADEMIC STRUCTURE MODELS
# ============================================================================

class AcademicYear(BaseModel, AcademicMixin):
    """Academic year configuration"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Academic Year Name"),
        help_text=_("e.g., 2023-2024 Academic Year")
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("Current Academic Year")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    # Term dates
    first_term_start = models.DateField(verbose_name=_("First Term Start"))
    first_term_end = models.DateField(verbose_name=_("First Term End"))
    second_term_start = models.DateField(verbose_name=_("Second Term Start"))
    second_term_end = models.DateField(verbose_name=_("Second Term End"))
    third_term_start = models.DateField(verbose_name=_("Third Term Start"), null=True, blank=True)
    third_term_end = models.DateField(verbose_name=_("Third Term End"), null=True, blank=True)
    
    # Configuration
    min_attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        verbose_name=_("Minimum Attendance Percentage"),
        help_text=_("Minimum attendance required to pass")
    )
    passing_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name=_("Passing Grade"),
        help_text=_("Minimum grade to pass")
    )
    max_absent_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Maximum Absent Days"),
        help_text=_("Maximum days a student can be absent")
    )
    
    class Meta:
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")
        ordering = ['-start_date']
        unique_together = ['academic_year', 'term']
        indexes = [
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['is_current']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year} - {self.get_term_display()})"
    
    def save(self, *args, **kwargs):
        """Ensure only one current academic year"""
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
    
    def get_term_dates(self, term):
        """Get start and end dates for a specific term"""
        term_dates = {
            TermType.FIRST_TERM: (self.first_term_start, self.first_term_end),
            TermType.SECOND_TERM: (self.second_term_start, self.second_term_end),
            TermType.THIRD_TERM: (self.third_term_start, self.third_term_end),
        }
        return term_dates.get(term, (None, None))
    
    def is_date_in_term(self, check_date, term=None):
        """Check if a date falls within this academic term"""
        if term:
            start_date, end_date = self.get_term_dates(term)
            return start_date <= check_date <= end_date
        else:
            return self.start_date <= check_date <= self.end_date
    
    def get_current_term(self):
        """Get current term based on today's date"""
        today = date.today()
        
        if self.first_term_start <= today <= self.first_term_end:
            return TermType.FIRST_TERM
        elif self.second_term_start <= today <= self.second_term_end:
            return TermType.SECOND_TERM
        elif self.third_term_start and self.third_term_end:
            if self.third_term_start <= today <= self.third_term_end:
                return TermType.THIRD_TERM
        return None
    
    def get_days_in_term(self, term=None):
        """Get number of school days in term"""
        if term:
            start_date, end_date = self.get_term_dates(term)
        else:
            start_date, end_date = self.start_date, self.end_date
        
        if not start_date or not end_date:
            return 0
        
        days = (end_date - start_date).days + 1
        # Remove weekends (assuming Saturday and Sunday)
        weekend_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                weekend_days += 1
            current_date += timedelta(days=1)
        
        return days - weekend_days
    
    @classmethod
    def get_current_academic_year(cls):
        """Get current academic year"""
        try:
            return cls.objects.get(is_current=True)
        except cls.DoesNotExist:
            return None


class AcademicTerm(BaseModel):
    """Academic term model for detailed term management"""
    TERM_TYPE_CHOICES = [
        ('term1', 'Term 1'),
        ('term2', 'Term 2'), 
        ('term3', 'Term 3'),
    ]

    ACADEMIC_STATUS_CHOICES = [
       ('active', 'Active'),
       ('inactive', 'Inactive'),
    ]
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='academic_terms',
        verbose_name=_("Academic Year")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Term Name"),
        help_text=_("e.g., First Term 2023-2024")
    )
    term_type = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term Type")
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("Current Term")
    )
    
    # Term-specific configurations
    registration_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Registration Deadline")
    )
    fee_payment_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fee Payment Deadline")
    )
    examination_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Examination Start Date")
    )
    examination_end = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Examination End Date")
    )
    closing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Closing Date")
    )
    next_term_starts = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Next Term Starts")
    )
    
    # Term statistics
    total_instructional_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Instructional Days")
    )
    total_holidays = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Holidays")
    )
    minimum_attendance_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Minimum Attendance Days"),
        help_text=_("Minimum days required for promotion")
    )
    
    # Academic requirements
    minimum_pass_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name=_("Minimum Pass Percentage")
    )
    assessment_weight = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Assessment Weight Distribution"),
        help_text=_("Weight distribution for different assessment types")
    )
    
    # Fee structure reference - IMPORTANT: Use string reference to avoid circular import
    fee_structure = models.ForeignKey(
        'finance.FeeStructure',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Fee Structure")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    class Meta:
        verbose_name = _("Academic Term")
        verbose_name_plural = _("Academic Terms")
        ordering = ['academic_year', 'start_date']
        unique_together = ['academic_year', 'term_type']
        indexes = [
            models.Index(fields=['academic_year', 'term_type']),
            models.Index(fields=['is_current']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.academic_year.academic_year}"
    
    def clean(self):
        """Validate term dates"""
        if self.start_date >= self.end_date:
            raise ValidationError(_("End date must be after start date"))
        
        # Validate term is within academic year
        if not (self.academic_year.start_date <= self.start_date <= self.academic_year.end_date):
            raise ValidationError(_("Term start date must be within academic year"))
        
        if not (self.academic_year.start_date <= self.end_date <= self.academic_year.end_date):
            raise ValidationError(_("Term end date must be within academic year"))
        
        # Validate term doesn't overlap with other terms in same academic year
        overlapping_terms = AcademicTerm.objects.filter(
            academic_year=self.academic_year
        ).exclude(pk=self.pk if self.pk else None)
        
        for term in overlapping_terms:
            if (self.start_date <= term.end_date and self.end_date >= term.start_date):
                raise ValidationError(
                    _("Term dates overlap with existing term: {}").format(term.name)
                )
        
        # Validate registration and fee deadlines
        if self.registration_deadline and self.registration_deadline > self.start_date:
            raise ValidationError(_("Registration deadline must be before term start date"))
        
        if self.fee_payment_deadline and self.fee_payment_deadline > self.start_date:
            raise ValidationError(_("Fee payment deadline must be before term start date"))
    
    def save(self, *args, **kwargs):
        """Ensure only one current term per academic year"""
        if self.is_current:
            AcademicTerm.objects.filter(
                academic_year=self.academic_year,
                is_current=True
            ).exclude(pk=self.pk if self.pk else None).update(is_current=False)
        
        # Set default assessment weights if not provided
        if not self.assessment_weight:
            self.assessment_weight = {
                'exam': 40.0,
                'test': 30.0,
                'assignment': 15.0,
                'participation': 15.0,
            }
        
        super().save(*args, **kwargs)
    
    @property
    def duration_days(self):
        """Get term duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_active(self):
        """Check if term is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def days_remaining(self):
        """Get days remaining in term"""
        today = date.today()
        if today < self.start_date:
            return (self.start_date - today).days
        elif self.start_date <= today <= self.end_date:
            return (self.end_date - today).days
        else:
            return 0
    
    def get_instructional_days(self, include_weekends=False):
        """Calculate instructional days in term"""
        days = self.duration_days
        if not include_weekends:
            # Remove weekends
            weekend_days = 0
            current_date = self.start_date
            while current_date <= self.end_date:
                if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    weekend_days += 1
                current_date += timedelta(days=1)
            days -= weekend_days
        
        # Subtract holidays
        holidays = self.academic_events.filter(event_type='holiday', is_holiday=True)
        holiday_days = 0
        for holiday in holidays:
            if holiday.start_date <= self.end_date and holiday.end_date >= self.start_date:
                # Calculate overlapping days
                overlap_start = max(self.start_date, holiday.start_date)
                overlap_end = min(self.end_date, holiday.end_date)
                holiday_days += (overlap_end - overlap_start).days + 1
        
        days -= holiday_days
        return max(0, days)
    
    def update_statistics(self):
        """Update term statistics"""
        from .models import Attendance, Enrollment
        
        # Calculate instructional days
        self.total_instructional_days = self.get_instructional_days()
        
        # Calculate holiday count
        holidays = self.academic_events.filter(event_type='holiday', is_holiday=True)
        holiday_days = 0
        for holiday in holidays:
            if holiday.start_date <= self.end_date and holiday.end_date >= self.start_date:
                overlap_start = max(self.start_date, holiday.start_date)
                overlap_end = min(self.end_date, holiday.end_date)
                holiday_days += (overlap_end - overlap_start).days + 1
        self.total_holidays = holiday_days
        
        self.save()
    
    def get_enrollment_count(self):
        """Get number of students enrolled in this term"""
        from .models import Enrollment
        return Enrollment.objects.filter(
            academic_year=self.academic_year.academic_year,
            term=self.term_type
        ).count()
    
    def get_attendance_summary(self):
        """Get attendance summary for this term"""
        from .models import Attendance
        attendance = Attendance.objects.filter(
            academic_year=self.academic_year.academic_year,
            term=self.term_type,
            date__range=[self.start_date, self.end_date]
        )
        
        summary = attendance.aggregate(
            total_records=Count('id'),
            present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
            absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
            late=Count('id', filter=Q(status=AttendanceStatus.LATE))
        )
        
        return {
            'total_records': summary['total_records'] or 0,
            'present': summary['present'] or 0,
            'absent': summary['absent'] or 0,
            'late': summary['late'] or 0,
            'attendance_rate': (summary['present'] / summary['total_records'] * 100) if summary['total_records'] > 0 else 0,
        }
    
    def get_performance_summary(self):
        """Get academic performance summary for this term"""
        from .models import Grade
        grades = Grade.objects.filter(
            assessment__academic_year=self.academic_year.academic_year,
            assessment__term=self.term_type
        )
        
        summary = grades.aggregate(
            average_score=Avg('score'),
            total_assessments=Count('assessment', distinct=True),
            total_students=Count('student', distinct=True),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )
        
        return {
            'average_score': summary['average_score'] or 0,
            'total_assessments': summary['total_assessments'] or 0,
            'total_students': summary['total_students'] or 0,
            'highest_score': summary['highest_score'] or 0,
            'lowest_score': summary['lowest_score'] or 0,
        }
    
    def get_upcoming_events(self, days=30):
        """Get upcoming events for this term"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return self.academic_events.filter(
            start_date__gte=today,
            start_date__lte=future_date
        ).order_by('start_date', 'start_time')
    
    @classmethod
    def get_current_term(cls):
        """Get current academic term"""
        try:
            return cls.objects.get(is_current=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_upcoming_terms(cls, count=3):
        """Get upcoming academic terms"""
        today = date.today()
        return cls.objects.filter(
            start_date__gte=today
        ).order_by('start_date')[:count]


class GradeLevel(BaseModel):
    """Grade/Class level structure"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Grade Level Name"),
        help_text=_("e.g., Grade 1, Form 1, Year 1")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Grade Code"),
        help_text=_("Short code, e.g., G1, F1")
    )
    level = models.CharField(
        max_length=20,
        choices=AcademicLevel.choices,
        verbose_name=_("Academic Level")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order for sorting grades")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    age_range_min = models.PositiveIntegerField(
        verbose_name=_("Minimum Age"),
        help_text=_("Minimum age for this grade")
    )
    age_range_max = models.PositiveIntegerField(
        verbose_name=_("Maximum Age"),
        help_text=_("Maximum age for this grade")
    )
    next_grade = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_grades',
        verbose_name=_("Next Grade Level")
    )
    curriculum = models.CharField(
        max_length=50,
        choices=settings.CURRICULUM_CHOICES if hasattr(settings, 'CURRICULUM_CHOICES') else [],
        blank=True,
        verbose_name=_("Curriculum")
    )
    max_students = models.PositiveIntegerField(
        default=40,
        verbose_name=_("Maximum Students"),
        help_text=_("Maximum number of students in this grade")
    )
    
    class Meta:
        verbose_name = _("Grade Level")
        verbose_name_plural = _("Grade Levels")
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['level']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def student_count(self):
        """Get current number of students in this grade"""
        return self.classes.filter(is_active=True).aggregate(
            total=Sum('students_count')
        )['total'] or 0
    
    @property
    def available_slots(self):
        """Calculate available student slots"""
        return max(0, self.max_students - self.student_count)


class Subject(BaseModel):
    """Academic subject model"""
    CATEGORY_CHOICES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective Subject'),
        ('extracurricular', 'Extracurricular'),
        ('vocational', 'Vocational'),
    ]
    name = models.CharField(
        max_length=200,
        verbose_name=_("Subject Name")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Subject Code")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    grade_levels = models.ManyToManyField(
        GradeLevel,
        related_name='subjects',
        blank=True,
        verbose_name=_("Grade Levels")
    )
    is_core = models.BooleanField(
        default=True,
        verbose_name=_("Core Subject"),
        help_text=_("Is this a core/compulsory subject?")
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Category"),
        help_text=_("e.g., Sciences, Languages, Arts")
    )
    credit_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Credit Hours")
    )
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.0,
        verbose_name=_("Passing Score")
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.0,
        verbose_name=_("Maximum Score")
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Department")
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for',
        verbose_name=_("Prerequisites")
    )
    syllabus = models.FileField(
        upload_to='syllabus/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Syllabus Document")
    )
    
    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        ordering = ['code', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_core']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_teachers(self, academic_year=None):
        """Get teachers teaching this subject"""
        from .models import TeacherAssignment
        assignments = TeacherAssignment.objects.filter(subject=self)
        if academic_year:
            assignments = assignments.filter(academic_year=academic_year)
        return assignments.values_list('teacher', flat=True).distinct()
    
    def get_student_count(self, academic_year=None):
        """Get number of students enrolled in this subject"""
        from .models import Enrollment
        enrollments = Enrollment.objects.filter(subject=self)
        if academic_year:
            enrollments = enrollments.filter(academic_year=academic_year)
        return enrollments.count()
    
    def get_average_score(self, academic_year=None):
        """Get average score for this subject"""
        from .models import Grade
        grades = Grade.objects.filter(subject=self)
        if academic_year:
            grades = grades.filter(academic_year=academic_year)
        avg = grades.aggregate(Avg('score'))['score__avg']
        return avg if avg else 0


# ============================================================================
# COMPETENCY-BASED EDUCATION MODELS (For CBC curriculum)
# ============================================================================

class CompetencyArea(BaseModel):
    """Competency/learning area for competency-based curricula (CBC)"""
    CURRICULUM_CHOICES = [
        ('cbc', 'Competency Based Curriculum'),
        ('8-4-4', '8-4-4 System'),
        ('igcse', 'IGCSE'),
        ('ib', 'International Baccalaureate'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_("Competency Area Name"),
        help_text=_("e.g., Communication and Collaboration, Critical Thinking, Creativity")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Competency Code")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    curriculum = models.CharField(
        max_length=50,
        choices=settings.CURRICULUM_CHOICES if hasattr(settings, 'CURRICULUM_CHOICES') else [],
        default='cbc',
        verbose_name=_("Curriculum"),
        help_text=_("Curriculum this competency area belongs to")
    )
    grade_levels = models.ManyToManyField(
        GradeLevel,
        related_name='competency_areas',
        blank=True,
        verbose_name=_("Grade Levels"),
        help_text=_("Grade levels where this competency is assessed")
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name='competency_areas',
        blank=True,
        verbose_name=_("Subjects"),
        help_text=_("Subjects that contribute to this competency")
    )
    
    # Assessment parameters
    assessment_method = models.CharField(
        max_length=50,
        choices=[
            ('observation', _('Observation')),
            ('portfolio', _('Portfolio Assessment')),
            ('rubric', _('Rubric Assessment')),
            ('project', _('Project Work')),
            ('practical', _('Practical Assessment')),
            ('self_assessment', _('Self-Assessment')),
            ('peer_assessment', _('Peer Assessment')),
        ],
        default='rubric',
        verbose_name=_("Assessment Method")
    )
    
    # Competency levels
    levels = models.JSONField(
        default=list,
        verbose_name=_("Competency Levels"),
        help_text=_("List of competency levels with descriptions")
    )
    
    parent_area = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_areas',
        verbose_name=_("Parent Competency Area")
    )
    
    is_core = models.BooleanField(
        default=True,
        verbose_name=_("Core Competency"),
        help_text=_("Is this a core competency area?")
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order for display and sorting")
    )
    
    class Meta:
        verbose_name = _("Competency Area")
        verbose_name_plural = _("Competency Areas")
        ordering = ['curriculum', 'order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['curriculum']),
            models.Index(fields=['is_core']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_competency_levels(self):
        """Get structured competency levels"""
        if not self.levels:
            # Default levels for CBC
            self.levels = [
                {
                    'level': 1,
                    'name': _('Beginning'),
                    'description': _('Student is beginning to demonstrate the competency'),
                    'min_score': 0,
                    'max_score': 40,
                },
                {
                    'level': 2,
                    'name': _('Developing'),
                    'description': _('Student is developing the competency'),
                    'min_score': 41,
                    'max_score': 60,
                },
                {
                    'level': 3,
                    'name': _('Competent'),
                    'description': _('Student demonstrates the competency'),
                    'min_score': 61,
                    'max_score': 80,
                },
                {
                    'level': 4,
                    'name': _('Exceeding'),
                    'description': _('Student exceeds expectations for the competency'),
                    'min_score': 81,
                    'max_score': 100,
                },
            ]
            self.save()
        
        return self.levels
    
    def get_level_for_score(self, score):
        """Get competency level for a given score"""
        levels = self.get_competency_levels()
        for level in levels:
            if level['min_score'] <= score <= level['max_score']:
                return level
        return None
    
    @property
    def student_count(self):
        """Get number of students assessed in this competency area"""
        return self.competency_assessments.count()
    
    def get_related_skills(self):
        """Get related skills for this competency area"""
        # You might want to create a Skill model related to CompetencyArea
        return []


class CompetencyAssessment(BaseModel):
    """Student competency assessment record"""
    LEVEL_CHOICES = [
        ('beginning', 'Beginning'),
        ('developing', 'Developing'),
        ('achieved', 'Achieved'),
        ('exceeded', 'Exceeded'),
        ('excellent', 'Excellent'),
    ]
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='competency_assessments',
        verbose_name=_("Student")
    )
    competency_area = models.ForeignKey(
        CompetencyArea,
        on_delete=models.CASCADE,
        related_name='competency_assessments',
        verbose_name=_("Competency Area")
    )
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name='competency_assessments',
        verbose_name=_("Grade Level")
    )
    
    # Assessment details
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Score")
    )
    level = models.CharField(
        max_length=50,
        verbose_name=_("Competency Level")
    )
    assessed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_competency_assessments',
        verbose_name=_("Assessed By")
    )
    assessment_date = models.DateField(
        default=date.today,
        verbose_name=_("Assessment Date")
    )
    
    # Evidence and documentation
    evidence = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Assessment Evidence"),
        help_text=_("List of evidence supporting the assessment")
    )
    comments = models.TextField(
        blank=True,
        verbose_name=_("Comments")
    )
    
    # Status
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified")
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_competency_assessments',
        verbose_name=_("Verified By")
    )
    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Verified Date")
    )
    
    class Meta:
        verbose_name = _("Competency Assessment")
        verbose_name_plural = _("Competency Assessments")
        unique_together = ['student', 'competency_area', 'academic_year', 'term']
        ordering = ['academic_year', 'term', 'competency_area']
        indexes = [
            models.Index(fields=['student', 'competency_area']),
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['grade_level', 'level']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.competency_area.name}: {self.score}"
    
    def save(self, *args, **kwargs):
        """Set competency level based on score"""
        if self.score is not None:
            level_data = self.competency_area.get_level_for_score(float(self.score))
            if level_data:
                self.level = level_data['name']
        super().save(*args, **kwargs)


# ============================================================================
# PHYSICAL INFRASTRUCTURE MODELS
# ============================================================================

class Classroom(BaseModel):
    """Physical classroom model"""
    
    room_number = models.CharField(
        max_length=50,
        verbose_name=_("Room Number")
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Room Name")
    )
    building = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Building")
    )
    floor = models.IntegerField(
        default=1,
        verbose_name=_("Floor")
    )
    capacity = models.PositiveIntegerField(
        default=40,
        verbose_name=_("Capacity"),
        help_text=_("Maximum number of students")
    )
    facilities = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Facilities"),
        help_text=_("List of available facilities")
    )
    is_special = models.BooleanField(
        default=False,
        verbose_name=_("Special Room"),
        help_text=_("e.g., Laboratory, Computer Lab, Music Room")
    )
    special_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Special Room Type")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_("Available")
    )
    
    class Meta:
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = ['building', 'floor', 'room_number']
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['building']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.room_number})"
        return f"Room {self.room_number}"
    
    @property
    def current_class(self):
        """Get current class using this room"""
        from .models import Class
        now = timezone.now()
        return Class.objects.filter(
            classroom=self,
            schedule__start_time__lte=now,
            schedule__end_time__gte=now
        ).first()
    
    def get_schedule(self, date=None):
        """Get schedule for this classroom"""
        from .models import Schedule
        if not date:
            date = timezone.now().date()
        
        return Schedule.objects.filter(
            classroom=self,
            date=date
        ).order_by('start_time')


# ============================================================================
# CLASS AND GROUPING MODELS
# ============================================================================

class Class(BaseModel, AcademicMixin):
    """Class/Stream model - grouping of students in same grade"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Class Name"),
        help_text=_("e.g., Form 1A, Grade 3B")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Class Code")
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_("Grade Level")
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
        verbose_name=_("Assigned Classroom")
    )
    form_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='form_classes',
        verbose_name=_("Form Teacher")
    )
    assistant_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='assistant_classes',
        verbose_name=_("Assistant Teacher")
    )
    max_students = models.PositiveIntegerField(
        default=40,
        verbose_name=_("Maximum Students")
    )
    students_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Current Student Count")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
        ordering = ['grade_level__order', 'name']
        unique_together = ['academic_year', 'term', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['grade_level']),
            models.Index(fields=['form_teacher']),
            models.Index(fields=['academic_year', 'term']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} {self.get_term_display()}"
    
    def save(self, *args, **kwargs):
        """Update student count on save"""
        if self.pk:
            from .models import Enrollment
            self.students_count = Enrollment.objects.filter(
                class_assigned=self,
                academic_year=self.academic_year,
                term=self.term,
                is_active=True
            ).count()
        super().save(*args, **kwargs)
    
    @property
    def available_slots(self):
        """Calculate available student slots"""
        return max(0, self.max_students - self.students_count)
    
    def get_students(self):
        """Get all students in this class"""
        from .models import Enrollment
        return Enrollment.objects.filter(
            class_assigned=self,
            academic_year=self.academic_year,
            term=self.term,
            is_active=True
        ).select_related('student')
    
    def get_subjects(self):
        """Get subjects taught in this class"""
        from .models import TeacherAssignment
        assignments = TeacherAssignment.objects.filter(
            class_assigned=self,
            academic_year=self.academic_year,
            term=self.term
        ).select_related('subject')
        return set(assignment.subject for assignment in assignments)
    
    def get_average_performance(self):
        """Get class average performance"""
        from .models import Grade
        grades = Grade.objects.filter(
            class_assigned=self,
            academic_year=self.academic_year,
            term=self.term
        )
        
        result = grades.aggregate(
            avg_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score'),
            total_students=Count('student', distinct=True)
        )
        
        return {
            'average_score': result['avg_score'] or 0,
            'highest_score': result['highest_score'] or 0,
            'lowest_score': result['lowest_score'] or 0,
            'total_students': result['total_students'] or 0,
        }
    
    def get_attendance_summary(self):
        """Get class attendance summary"""
        from .models import Attendance
        attendance = Attendance.objects.filter(
            class_assigned=self,
            academic_year=self.academic_year,
            term=self.term,
            date__gte=date.today() - timedelta(days=30)
        )
        
        total_records = attendance.count()
        if total_records == 0:
            return {
                'present_percentage': 0,
                'absent_percentage': 0,
                'late_percentage': 0,
            }
        
        present_count = attendance.filter(status=AttendanceStatus.PRESENT).count()
        absent_count = attendance.filter(status=AttendanceStatus.ABSENT).count()
        late_count = attendance.filter(status=AttendanceStatus.LATE).count()
        
        return {
            'present_percentage': (present_count / total_records) * 100,
            'absent_percentage': (absent_count / total_records) * 100,
            'late_percentage': (late_count / total_records) * 100,
            'total_records': total_records,
        }


# ============================================================================
# ENROLLMENT AND STUDENT ACADEMIC RECORDS
# ============================================================================

class Enrollment(BaseModel, AcademicMixin):
    """Student enrollment in a class"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
        ('transferred', 'Transferred'),
    ]
    
    ACADEMIC_STATUS_CHOICES = [
        ('passing', 'Passing'),
        ('failing', 'Failing'),
        ('at_risk', 'At Risk'),
        ('probation', 'Probation'),
        ('honors', 'Honors'),
    ]



    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='enrollments',
        verbose_name=_("Student")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Assigned Class")
    )
    enrollment_date = models.DateField(
        default=date.today,
        verbose_name=_("Enrollment Date")
    )
    enrollment_type = models.CharField(
        max_length=20,
        choices=[
            ('new', _('New Student')),
            ('transfer', _('Transfer Student')),
            ('repeat', _('Repeating Student')),
            ('promoted', _('Promoted Student')),
        ],
        default='new',
        verbose_name=_("Enrollment Type")
    )
    enrollment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Enrollment Number")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('suspended', _('Suspended')),
            ('graduated', _('Graduated')),
            ('withdrawn', _('Withdrawn')),
            ('transferred', _('Transferred')),
        ],
        default='active',
        verbose_name=_("Enrollment Status")
    )
    academic_status = models.CharField(
        max_length=20,
        choices=AcademicStatus.choices,
        default=AcademicStatus.ACTIVE,
        verbose_name=_("Academic Status")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_enrollments',
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['enrollment_number']),
            models.Index(fields=['status']),
            models.Index(fields=['academic_status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_assigned}"
    
    def save(self, *args, **kwargs):
        """Generate enrollment number and update student's current class"""
        if not self.enrollment_number:
            self.enrollment_number = self.generate_enrollment_number()
        
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new or self.status == 'active':
            # Update student's current class in User model
            self.student.current_class = self.class_assigned.name
            self.student.grade_level = self.class_assigned.grade_level.name
            self.student.academic_year = self.academic_year
            self.student.save()
            
            # Update class student count
            self.class_assigned.save()
    
    def generate_enrollment_number(self):
        """Generate unique enrollment number"""
        year = date.today().year
        prefix = f"ENR-{year}-"
        
        last_enrollment = Enrollment.objects.filter(
            enrollment_number__startswith=prefix
        ).order_by('-enrollment_number').first()
        
        if last_enrollment and last_enrollment.enrollment_number:
            try:
                last_number = int(last_enrollment.enrollment_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:05d}"
    
    def get_academic_performance(self):
        """Get academic performance for this enrollment"""
        from .models import Grade
        grades = Grade.objects.filter(
            enrollment=self,
            academic_year=self.academic_year,
            term=self.term
        )
        
        performance = grades.aggregate(
            average_score=Avg('score'),
            total_subjects=Count('subject', distinct=True),
            passed_subjects=Count('subject', distinct=True, filter=Q(score__gte=self.class_assigned.grade_level.passing_score) if hasattr(self.class_assigned.grade_level, 'passing_score') else Q(score__gte=40)),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )
        
        return {
            'average_score': performance['average_score'] or 0,
            'total_subjects': performance['total_subjects'] or 0,
            'passed_subjects': performance['passed_subjects'] or 0,
            'highest_score': performance['highest_score'] or 0,
            'lowest_score': performance['lowest_score'] or 0,
            'pass_percentage': (performance['passed_subjects'] / performance['total_subjects'] * 100) if performance['total_subjects'] > 0 else 0,
        }
    
    def get_attendance_summary(self):
        """Get attendance summary for this enrollment"""
        from .models import Attendance
        attendance = Attendance.objects.filter(
            enrollment=self,
            academic_year=self.academic_year,
            term=self.term
        )
        
        summary = attendance.aggregate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
            absent_days=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
            late_days=Count('id', filter=Q(status=AttendanceStatus.LATE)),
            excused_days=Count('id', filter=Q(status=AttendanceStatus.EXCUSED))
        )
        
        total = summary['total_days'] or 0
        if total > 0:
            return {
                'total_days': total,
                'present_days': summary['present_days'] or 0,
                'absent_days': summary['absent_days'] or 0,
                'late_days': summary['late_days'] or 0,
                'excused_days': summary['excused_days'] or 0,
                'attendance_percentage': (summary['present_days'] / total) * 100,
            }
        
        return {
            'total_days': 0,
            'present_days': 0,
            'absent_days': 0,
            'late_days': 0,
            'excused_days': 0,
            'attendance_percentage': 0,
        }
    
    def get_subject_enrollments(self):
        """Get subject enrollments for this student"""
        from .models import SubjectEnrollment
        return SubjectEnrollment.objects.filter(
            enrollment=self,
            academic_year=self.academic_year,
            term=self.term
        ).select_related('subject')


class SubjectEnrollment(BaseModel, AcademicMixin):
    """Student enrollment in specific subjects"""
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('withdrawn', 'Withdrawn'),
        ('failed', 'Failed'),
    ]
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='subject_enrollments',
        verbose_name=_("Enrollment")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_enrollments',
        verbose_name=_("Subject")
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='teaching_subject_enrollments',
        verbose_name=_("Assigned Teacher")
    )
    enrollment_date = models.DateField(
        default=date.today,
        verbose_name=_("Enrollment Date")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Active')),
            ('completed', _('Completed')),
            ('dropped', _('Dropped')),
            ('failed', _('Failed')),
        ],
        default='active',
        verbose_name=_("Status")
    )
    grade = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Final Grade")
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Final Score")
    )
    credits_earned = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Credits Earned")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    
    class Meta:
        verbose_name = _("Subject Enrollment")
        verbose_name_plural = _("Subject Enrollments")
        unique_together = ['enrollment', 'subject', 'academic_year', 'term']
        ordering = ['subject__name']
        indexes = [
            models.Index(fields=['enrollment', 'subject']),
            models.Index(fields=['status']),
            models.Index(fields=['grade']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student.get_full_name()} - {self.subject.name}"
    
    def calculate_final_grade(self):
        """Calculate final grade based on assessments"""
        from .models import Assessment, Grade
        assessments = Assessment.objects.filter(
            subject_enrollment=self,
            academic_year=self.academic_year,
            term=self.term
        )
        
        if not assessments.exists():
            return None
        
        # Calculate weighted average
        total_weight = 0
        weighted_score = 0
        
        for assessment in assessments:
            weight = assessment.weight or 1
            grade = Grade.objects.filter(
                assessment=assessment,
                student=self.enrollment.student
            ).first()
            
            if grade and grade.score:
                total_weight += weight
                weighted_score += grade.score * weight
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
            self.score = final_score
            self.grade = self.convert_to_grade(final_score)
            self.save()
            
            return final_score
        
        return None
    
    def convert_to_grade(self, score):
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        elif score >= 30:
            return 'D'
        else:
            return 'F'
    
    def get_assessment_grades(self):
        """Get all assessment grades for this subject enrollment"""
        from .models import Assessment, Grade
        assessments = Assessment.objects.filter(
            subject_enrollment=self,
            academic_year=self.academic_year,
            term=self.term
        )
        
        grades_data = []
        for assessment in assessments:
            grade = Grade.objects.filter(
                assessment=assessment,
                student=self.enrollment.student
            ).first()
            
            if grade:
                grades_data.append({
                    'assessment': assessment.name,
                    'type': assessment.get_assessment_type_display(),
                    'score': grade.score,
                    'grade': grade.grade,
                    'weight': assessment.weight,
                    'date': assessment.date,
                })
        
        return grades_data


# ============================================================================
# ASSESSMENT AND GRADING MODELS
# ============================================================================

class Assessment(BaseModel, AcademicMixin):
    """Assessment/exam model"""
    ASSESSMENT_TYPE_CHOICES = [
        ('formative', 'Formative'),
        ('summative', 'Summative'),
        ('practical', 'Practical'),
        ('project', 'Project'),
        ('portfolio', 'Portfolio'),
        ('observation', 'Observation'),
    ]
    name = models.CharField(
        max_length=200,
        verbose_name=_("Assessment Name")
    )
    code = models.CharField(
        max_length=50,
        verbose_name=_("Assessment Code")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='academic_assessments',
        verbose_name=_("Subject")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='academic_assessments',
        verbose_name=_("Class")
    )
    assessment_type = models.CharField(
        max_length=30,
        choices=AssessmentType.choices,
        verbose_name=_("Assessment Type")
    )
    date = models.DateField(verbose_name=_("Assessment Date"))
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Start Time")
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("End Time")
    )
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100.0,
        verbose_name=_("Total Marks")
    )
    passing_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=40.0,
        verbose_name=_("Passing Marks")
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Weight"),
        help_text=_("Weight in final grade calculation")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    instructions = models.TextField(
        blank=True,
        verbose_name=_("Instructions")
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Results Published")
    )
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published Date")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assessments_new',
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Assessment")
        verbose_name_plural = _("Assessments")
        ordering = ['-date', 'start_time']
        indexes = [
            models.Index(fields=['subject', 'class_assigned']),
            models.Index(fields=['assessment_type']),
            models.Index(fields=['date']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject.name} ({self.get_assessment_type_display()})"
    
    def get_class_average(self):
        """Calculate class average for this assessment"""
        from .models import Grade
        grades = Grade.objects.filter(assessment=self)
        avg = grades.aggregate(Avg('score'))['score__avg']
        return avg if avg else 0
    
    def get_pass_rate(self):
        """Calculate pass rate for this assessment"""
        from .models import Grade
        grades = Grade.objects.filter(assessment=self)
        total = grades.count()
        if total == 0:
            return 0
        
        passed = grades.filter(score__gte=self.passing_marks).count()
        return (passed / total) * 100
    
    def get_top_performers(self, limit=5):
        """Get top performers for this assessment"""
        from .models import Grade
        return Grade.objects.filter(
            assessment=self
        ).select_related('student').order_by('-score')[:limit]
    
    def publish_results(self):
        """Publish assessment results"""
        self.is_published = True
        self.published_date = timezone.now()
        self.save()


class Grade(BaseModel):
    """Student grade/score model"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='academic_grades',
        verbose_name=_("Student")
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='grades_assesments_new',
        verbose_name=_("Assessment")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_grades',
        verbose_name=_("Subject")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='class_grades_new',
        verbose_name=_("Class")
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='enrolling_grades',
        verbose_name=_("Enrollment")
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Score")
    )
    grade = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Grade")
    )
    grade_point = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Grade Point")
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Percentage"),
        help_text=_("Score as percentage of total marks")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    is_absent = models.BooleanField(
        default=False,
        verbose_name=_("Absent")
    )
    is_exempted = models.BooleanField(
        default=False,
        verbose_name=_("Exempted")
    )
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_records_academic',
        verbose_name=_("Graded By")
    )
    graded_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Graded Date")
    )
    
    class Meta:
        verbose_name = _("Grade")
        verbose_name_plural = _("Grades")
        unique_together = ['student', 'assessment']
        ordering = ['-assessment__date', 'student']
        indexes = [
            models.Index(fields=['student', 'assessment']),
            models.Index(fields=['subject', 'class_assigned']),
            models.Index(fields=['score']),
            models.Index(fields=['grade']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assessment.name}: {self.score}"
    
    def save(self, *args, **kwargs):
        """Calculate percentage, grade, and grade point"""
        if self.score is not None and self.assessment.total_marks > 0:
            self.percentage = (self.score / self.assessment.total_marks) * 100
        
        # Calculate grade and grade point
        if self.score is not None and not self.is_absent and not self.is_exempted:
            self.grade = self.calculate_grade(self.percentage)
            self.grade_point = self.calculate_grade_point(self.grade)
        
        super().save(*args, **kwargs)
    
    def calculate_grade(self, percentage):
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        elif percentage >= 30:
            return 'D'
        else:
            return 'F'
    
    def calculate_grade_point(self, grade):
        """Calculate grade point based on letter grade"""
        grade_points = {
            'A+': 4.0,
            'A': 4.0,
            'B+': 3.5,
            'B': 3.0,
            'C+': 2.5,
            'C': 2.0,
            'D': 1.0,
            'F': 0.0,
        }
        return grade_points.get(grade, 0.0)
    
    @property
    def is_passing(self):
        """Check if grade is passing"""
        if self.is_absent or self.is_exempted:
            return False
        return self.score >= self.assessment.passing_marks
    
    @property
    def grade_description(self):
        """Get grade description"""
        descriptions = {
            'A+': _('Excellent'),
            'A': _('Very Good'),
            'B+': _('Good'),
            'B': _('Above Average'),
            'C+': _('Average'),
            'C': _('Below Average'),
            'D': _('Poor'),
            'F': _('Fail'),
        }
        return descriptions.get(self.grade, _('No Grade'))


class Transcript(BaseModel):
    """Student academic transcript"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='transcripts',
        verbose_name=_("Student")
    )
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("GPA")
    )
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("CGPA")
    )
    total_credits = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Total Credits")
    )
    credits_earned = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Credits Earned")
    )
    class_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Class Rank")
    )
    grade_level_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Grade Level Rank")
    )
    overall_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Overall Rank")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_transcripts',
        verbose_name=_("Generated By")
    )
    generated_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Generated Date")
    )
    is_official = models.BooleanField(
        default=False,
        verbose_name=_("Official Transcript")
    )
    document = models.FileField(
        upload_to='transcripts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Transcript Document")
    )
    
    class Meta:
        verbose_name = _("Transcript")
        verbose_name_plural = _("Transcripts")
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['gpa']),
            models.Index(fields=['class_rank']),
        ]
    
    def __str__(self):
        return f"Transcript - {self.student.get_full_name()} - {self.academic_year} {self.term}"
    
    def calculate_gpa(self):
        """Calculate GPA for this transcript"""
        from .models import Grade
        grades = Grade.objects.filter(
            student=self.student,
            assessment__academic_year=self.academic_year,
            assessment__term=self.term,
            grade_point__isnull=False
        )
        
        if not grades.exists():
            return 0.0
        
        total_grade_points = sum(g.grade_point * (g.assessment.weight or 1) for g in grades if g.grade_point)
        total_weight = sum(g.assessment.weight or 1 for g in grades)
        
        if total_weight > 0:
            return total_grade_points / total_weight
        
        return 0.0
    
    def calculate_cgpa(self):
        """Calculate cumulative GPA up to this term"""
        from .models import Transcript
        previous_transcripts = Transcript.objects.filter(
            student=self.student,
            academic_year__lt=self.academic_year
        ).order_by('academic_year', 'term')
        
        total_gpa = 0
        count = 0
        
        for transcript in previous_transcripts:
            if transcript.gpa:
                total_gpa += transcript.gpa
                count += 1
        
        if self.gpa:
            total_gpa += self.gpa
            count += 1
        
        if count > 0:
            return total_gpa / count
        
        return 0.0
    
    def update_ranks(self):
        """Update class, grade level, and overall ranks"""
        from .models import Transcript
        from django.db.models import Window, F
        from django.db.models.functions import DenseRank
        
        # Update all transcripts for this academic year and term
        transcripts = Transcript.objects.filter(
            academic_year=self.academic_year,
            term=self.term,
            gpa__isnull=False
        )
        
        # Class rank
        class_transcripts = transcripts.filter(
            student__current_class=self.student.current_class
        ).order_by('-gpa')
        
        for rank, transcript in enumerate(class_transcripts, start=1):
            transcript.class_rank = rank
            transcript.save(update_fields=['class_rank'])
        
        # Grade level rank
        grade_transcripts = transcripts.filter(
            student__grade_level=self.student.grade_level
        ).order_by('-gpa')
        
        for rank, transcript in enumerate(grade_transcripts, start=1):
            transcript.grade_level_rank = rank
            transcript.save(update_fields=['grade_level_rank'])
        
        # Overall rank
        for rank, transcript in enumerate(transcripts.order_by('-gpa'), start=1):
            transcript.overall_rank = rank
            transcript.save(update_fields=['overall_rank'])
    
    def generate_document(self):
        """Generate transcript document"""
        # This would be implemented with a document generation library
        # like ReportLab, WeasyPrint, or similar
        pass


# ============================================================================
# ATTENDANCE MODELS
# ============================================================================

class Attendance(BaseModel, AcademicMixin):
    """Student attendance record"""
    STATUS_CHOICES = [

        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendances',
        verbose_name=_("Student")
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_("Enrollment")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_("Class")
    )
    date = models.DateField(verbose_name=_("Date"))
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        verbose_name=_("Status")
    )
    check_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Check-in Time")
    )
    check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Check-out Time")
    )
    reason = models.TextField(
        blank=True,
        verbose_name=_("Reason for Absence/Late")
    )
    medical_certificate = models.FileField(
        upload_to='medical_certificates/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Medical Certificate")
    )
    parent_note = models.FileField(
        upload_to='parent_notes/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Parent Note")
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['teacher', 'admin', 'head_teacher']},
        related_name='verified_attendances',
        verbose_name=_("Verified By")
    )
    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Verified Date")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    
    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendance Records")
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['class_assigned', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} ({self.get_status_display()})"
    
    @property
    def duration(self):
        """Calculate duration if both check-in and check-out times exist"""
        if self.check_in_time and self.check_out_time:
            check_in_dt = datetime.combine(self.date, self.check_in_time)
            check_out_dt = datetime.combine(self.date, self.check_out_time)
            if check_out_dt < check_in_dt:
                check_out_dt += timedelta(days=1)
            return check_out_dt - check_in_dt
        return None
    
    @property
    def is_late(self):
        """Check if student was late (after 8:30 AM)"""
        if self.check_in_time:
            late_time = datetime.strptime('08:30', '%H:%M').time()
            return self.check_in_time > late_time
        return False
    
    @classmethod
    def mark_daily_attendance(cls, class_obj, date, attendance_data):
        """Mark attendance for entire class on a specific date"""
        from django.db import transaction
        
        with transaction.atomic():
            created_count = 0
            updated_count = 0
            
            for student_data in attendance_data:
                student_id = student_data['student_id']
                status = student_data['status']
                reason = student_data.get('reason', '')
                check_in = student_data.get('check_in_time')
                check_out = student_data.get('check_out_time')
                
                # Get student
                from accounts.models import User
                try:
                    student = User.objects.get(id=student_id, role='student')
                except User.DoesNotExist:
                    continue
                
                # Get enrollment
                enrollment = Enrollment.objects.filter(
                    student=student,
                    class_assigned=class_obj,
                    academic_year=class_obj.academic_year,
                    term=class_obj.term,
                    status='active'
                ).first()
                
                if not enrollment:
                    continue
                
                # Create or update attendance
                attendance, created = cls.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'enrollment': enrollment,
                        'class_assigned': class_obj,
                        'academic_year': class_obj.academic_year,
                        'term': class_obj.term,
                        'status': status,
                        'reason': reason,
                        'check_in_time': check_in,
                        'check_out_time': check_out,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return {
                'created': created_count,
                'updated': updated_count,
                'total': created_count + updated_count
            }
    
    @classmethod
    def get_class_attendance_summary(cls, class_obj, start_date, end_date):
        """Get attendance summary for a class over date range"""
        attendance = cls.objects.filter(
            class_assigned=class_obj,
            date__range=[start_date, end_date]
        )
        
        summary = attendance.aggregate(
            total_records=Count('id'),
            present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
            absent=Count('id', filter=Q(status=AttendanceStatus.ABSENT)),
            late=Count('id', filter=Q(status=AttendanceStatus.LATE)),
            excused=Count('id', filter=Q(status=AttendanceStatus.EXCUSED)),
            half_day=Count('id', filter=Q(status=AttendanceStatus.HALF_DAY))
        )
        
        total = summary['total_records'] or 0
        if total > 0:
            return {
                'total_days': (end_date - start_date).days + 1,
                'total_records': total,
                'present': summary['present'] or 0,
                'absent': summary['absent'] or 0,
                'late': summary['late'] or 0,
                'excused': summary['excused'] or 0,
                'half_day': summary['half_day'] or 0,
                'attendance_rate': (summary['present'] / total) * 100 if total > 0 else 0,
            }
        
        return {
            'total_days': (end_date - start_date).days + 1,
            'total_records': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0,
            'half_day': 0,
            'attendance_rate': 0,
        }
class Stream(BaseModel):
    """Stream/Division model for class groupings"""
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Stream Name"),
        help_text=_("e.g., East, West, Science, Arts")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Stream Code")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    color_code = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_("Color Code")
    )
    capacity = models.IntegerField(
        default=30,
        verbose_name=_("Capacity")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Stream")
        verbose_name_plural = _("Streams")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def current_student_count(self):
        """Get number of students currently in this stream"""
        return self.classes.filter(
            academic_year__is_current=True,
            term__is_current=True
        ).count()
    
    @property
    def available_slots(self):
        """Get available slots in this stream"""
        return max(0, self.capacity - self.current_student_count)



class AttendanceReport(BaseModel):
    """Attendance report and analytics"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendance_reports_new',
        verbose_name=_("Student")
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_reports',
        verbose_name=_("Enrollment")
    )
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    period_start = models.DateField(verbose_name=_("Period Start"))
    period_end = models.DateField(verbose_name=_("Period End"))
    
    # Statistics
    total_school_days = models.PositiveIntegerField(verbose_name=_("Total School Days"))
    days_present = models.PositiveIntegerField(verbose_name=_("Days Present"))
    days_absent = models.PositiveIntegerField(verbose_name=_("Days Absent"))
    days_late = models.PositiveIntegerField(verbose_name=_("Days Late"))
    days_excused = models.PositiveIntegerField(verbose_name=_("Days Excused"))
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Attendance Percentage")
    )
    
    # Patterns
    consecutive_absences = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Maximum Consecutive Absences")
    )
    frequent_absence_pattern = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Frequent Absence Pattern")
    )
    
    # Warnings
    is_at_risk = models.BooleanField(
        default=False,
        verbose_name=_("At Risk of Failing Attendance")
    )
    warning_level = models.CharField(
        max_length=20,
        choices=[
            ('none', _('None')),
            ('warning', _('Warning')),
            ('severe', _('Severe')),
            ('critical', _('Critical')),
        ],
        default='none',
        verbose_name=_("Warning Level")
    )
    
    # Parent notifications
    parent_notified = models.BooleanField(
        default=False,
        verbose_name=_("Parent Notified")
    )
    last_notification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Notification Date")
    )
    
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_academic_reports',
        verbose_name=_("Generated By")
    )
    generated_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Generated Date")
    )
    
    class Meta:
        verbose_name = _("Attendance Report")
        verbose_name_plural = _("Attendance Reports")
        ordering = ['-period_end', 'student']
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['attendance_percentage']),
            models.Index(fields=['is_at_risk']),
        ]
    
    def __str__(self):
        return f"Attendance Report - {self.student.get_full_name()} - {self.period_start} to {self.period_end}"
    
    def update_statistics(self):
        """Update attendance statistics from attendance records"""
        attendance = Attendance.objects.filter(
            student=self.student,
            date__range=[self.period_start, self.period_end]
        )
        
        self.days_present = attendance.filter(status=AttendanceStatus.PRESENT).count()
        self.days_absent = attendance.filter(status=AttendanceStatus.ABSENT).count()
        self.days_late = attendance.filter(status=AttendanceStatus.LATE).count()
        self.days_excused = attendance.filter(status=AttendanceStatus.EXCUSED).count()
        
        total_attendance = attendance.count()
        if total_attendance > 0:
            self.attendance_percentage = (self.days_present / total_attendance) * 100
        
        # Check if at risk
        min_attendance = getattr(settings, 'MIN_ATTENDANCE_PERCENTAGE', 75)
        self.is_at_risk = self.attendance_percentage < min_attendance
        
        # Determine warning level
        if self.attendance_percentage < 50:
            self.warning_level = 'critical'
        elif self.attendance_percentage < 65:
            self.warning_level = 'severe'
        elif self.attendance_percentage < 75:
            self.warning_level = 'warning'
        else:
            self.warning_level = 'none'
        
        self.save()
    
    def detect_patterns(self):
        """Detect attendance patterns"""
        attendance = Attendance.objects.filter(
            student=self.student,
            date__range=[self.period_start, self.period_end]
        ).order_by('date')
        
        # Detect consecutive absences
        consecutive = 0
        max_consecutive = 0
        for record in attendance:
            if record.status == AttendanceStatus.ABSENT:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        self.consecutive_absences = max_consecutive
        
        # Detect day-of-week patterns
        day_patterns = {}
        absences_by_day = attendance.filter(status=AttendanceStatus.ABSENT).values_list('date', flat=True)
        
        for absence_date in absences_by_day:
            day_name = absence_date.strftime('%A')
            day_patterns[day_name] = day_patterns.get(day_name, 0) + 1
        
        self.frequent_absence_pattern = day_patterns
        self.save()
    
    def notify_parent(self):
        """Notify parent about attendance issues"""
        if self.is_at_risk and not self.parent_notified:
            # Send notification to parent
            parent_email = self.student.parent_email
            if parent_email:
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                subject = _("Attendance Alert - {student_name}").format(
                    student_name=self.student.get_full_name()
                )
                
                html_message = render_to_string('academic/attendance_alert_email.html', {
                    'student': self.student,
                    'report': self,
                    'period_start': self.period_start,
                    'period_end': self.period_end,
                })
                
                plain_message = strip_tags(html_message)
                
                try:
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [parent_email],
                        html_message=html_message
                    )
                    
                    self.parent_notified = True
                    self.last_notification_date = date.today()
                    self.save()
                    
                    return True
                except Exception as e:
                    logger.error(f"Failed to send attendance alert: {e}")
        
        return False


# ============================================================================
# TIMETABLE AND SCHEDULING MODELS
# ============================================================================

class Schedule(BaseModel):
    """Class schedule/timetable"""
    
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='class_schedules',
        verbose_name=_("Class")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='schedules_new',
        verbose_name=_("Subject")
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='schedules',
        verbose_name=_("Teacher")
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules',
        verbose_name=_("Classroom")
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DayOfWeek.choices,
        verbose_name=_("Day of Week")
    )
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    is_recurring = models.BooleanField(
        default=True,
        verbose_name=_("Recurring Schedule")
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Schedule Start Date")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Schedule End Date")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    color_code = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name=_("Color Code")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['class_assigned', 'day_of_week']),
            models.Index(fields=['teacher', 'day_of_week']),
            models.Index(fields=['subject', 'day_of_week']),
            models.Index(fields=['academic_year', 'term']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.class_assigned.name} - {self.day_of_week} {self.start_time}-{self.end_time}"
    
    @property
    def duration(self):
        """Calculate duration in minutes"""
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        return (end_dt - start_dt).seconds // 60
    
    @property
    def is_current(self):
        """Check if this schedule is currently active"""
        now = timezone.now()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        if current_day != self.day_of_week:
            return False
        
        return self.start_time <= current_time <= self.end_time
    
    def clean(self):
        """Validate schedule timing"""
        if self.start_time >= self.end_time:
            raise ValidationError(_("End time must be after start time"))
        
        # Check for overlapping schedules
        overlapping = Schedule.objects.filter(
            class_assigned=self.class_assigned,
            day_of_week=self.day_of_week,
            academic_year=self.academic_year,
            term=self.term,
            is_active=True
        ).exclude(pk=self.pk if self.pk else None)
        
        for schedule in overlapping:
            if (self.start_time < schedule.end_time and 
                self.end_time > schedule.start_time):
                raise ValidationError(
                    _("Schedule overlaps with existing schedule: {} - {}").format(
                        schedule.subject.name, schedule.teacher.get_full_name()
                    )
                )
        
        # Check teacher availability
        teacher_conflict = Schedule.objects.filter(
            teacher=self.teacher,
            day_of_week=self.day_of_week,
            academic_year=self.academic_year,
            term=self.term,
            is_active=True
        ).exclude(pk=self.pk if self.pk else None)
        
        for schedule in teacher_conflict:
            if (self.start_time < schedule.end_time and 
                self.end_time > schedule.start_time):
                raise ValidationError(
                    _("Teacher {} is already teaching {} during this time").format(
                        self.teacher.get_full_name(), schedule.subject.name
                    )
                )
        
        # Check classroom availability
        if self.classroom:
            classroom_conflict = Schedule.objects.filter(
                classroom=self.classroom,
                day_of_week=self.day_of_week,
                academic_year=self.academic_year,
                term=self.term,
                is_active=True
            ).exclude(pk=self.pk if self.pk else None)
            
            for schedule in classroom_conflict:
                if (self.start_time < schedule.end_time and 
                    self.end_time > schedule.start_time):
                    raise ValidationError(
                        _("Classroom {} is already booked for {} during this time").format(
                            self.classroom.room_number, schedule.subject.name
                        )
                    )
    
    @classmethod
    def get_class_timetable(cls, class_obj, academic_year=None, term=None):
        """Get complete timetable for a class"""
        if not academic_year:
            academic_year = class_obj.academic_year
        if not term:
            term = class_obj.term
        
        return cls.objects.filter(
            class_assigned=class_obj,
            academic_year=academic_year,
            term=term,
            is_active=True
        ).order_by('day_of_week', 'start_time').select_related(
            'subject', 'teacher', 'classroom'
        )
    
    @classmethod
    def get_teacher_timetable(cls, teacher, academic_year=None, term=None):
        """Get complete timetable for a teacher"""
        current_academic_year = AcademicYear.get_current_academic_year()
        if not academic_year and current_academic_year:
            academic_year = current_academic_year.academic_year
        if not term and current_academic_year:
            term = current_academic_year.get_current_term()
        
        return cls.objects.filter(
            teacher=teacher,
            academic_year=academic_year,
            term=term,
            is_active=True
        ).order_by('day_of_week', 'start_time').select_related(
            'subject', 'class_assigned', 'classroom'
        )
    
    @classmethod
    def generate_weekly_schedule(cls, class_obj, academic_year, term):
        """Generate weekly schedule for a class"""
        days = [day[0] for day in DayOfWeek.choices]
        
        schedule_data = {}
        for day in days:
            schedule_data[day] = cls.objects.filter(
                class_assigned=class_obj,
                day_of_week=day,
                academic_year=academic_year,
                term=term,
                is_active=True
            ).order_by('start_time').select_related(
                'subject', 'teacher', 'classroom'
            )
        
        return schedule_data


# ============================================================================
# TEACHER ASSIGNMENT AND MANAGEMENT
# ============================================================================

class TeacherAssignment(BaseModel, AcademicMixin):
    """Teacher assignment to classes and subjects"""
    
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='assignments_teacher',
        verbose_name=_("Teacher")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        verbose_name=_("Subject")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='teacher_assignment_new',
        verbose_name=_("Class")
    )
    is_class_teacher = models.BooleanField(
        default=False,
        verbose_name=_("Class Teacher")
    )
    assignment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', _('Full Time')),
            ('part_time', _('Part Time')),
            ('substitute', _('Substitute')),
            ('visiting', _('Visiting Faculty')),
        ],
        default='full_time',
        verbose_name=_("Assignment Type")
    )
    hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Hours Per Week")
    )
    start_date = models.DateField(
        default=date.today,
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("End Date")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_("Remarks")
    )
    
    class Meta:
        verbose_name = _("Teacher Assignment")
        verbose_name_plural = _("Teacher Assignments")
        unique_together = ['teacher', 'subject', 'class_assigned', 'academic_year', 'term']
        ordering = ['teacher', 'class_assigned', 'subject']
        indexes = [
            models.Index(fields=['teacher', 'subject', 'class_assigned']),
            models.Index(fields=['is_active']),
            models.Index(fields=['academic_year', 'term']),
        ]
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.subject.name} - {self.class_assigned.name}"
    
    @property
    def duration(self):
        """Calculate assignment duration in days"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return (date.today() - self.start_date).days
    
    def get_teaching_hours(self):
        """Calculate total teaching hours based on schedule"""
        from .models import Schedule
        schedules = Schedule.objects.filter(
            teacher=self.teacher,
            subject=self.subject,
            class_assigned=self.class_assigned,
            academic_year=self.academic_year,
            term=self.term,
            is_active=True
        )
        
        total_minutes = 0
        for schedule in schedules:
            total_minutes += schedule.duration
        
        return total_minutes / 60  # Convert to hours


# ============================================================================
# ACADEMIC REPORTS AND ANALYTICS
# ============================================================================

class AcademicReport(BaseModel):
    """Comprehensive academic report for students"""
    TERM_CHOICES = [
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('annual', 'Annual'),
    ]
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='academic_reports_new',
        verbose_name=_("Student")
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='academic_reports',
        verbose_name=_("Enrollment")
    )
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    
    # Performance metrics
    overall_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Overall Score")
    )
    overall_grade = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Overall Grade")
    )
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("GPA")
    )
    class_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Class Rank")
    )
    grade_level_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Grade Level Rank")
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Attendance Percentage")
    )
    
    # Subject performance
    subject_performance = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Subject Performance")
    )
    
    # Strengths and weaknesses
    strengths = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Strengths")
    )
    weaknesses = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Areas for Improvement")
    )
    
    # Teacher comments
    form_teacher_comment = models.TextField(
        blank=True,
        verbose_name=_("Form Teacher's Comment")
    )
    head_teacher_comment = models.TextField(
        blank=True,
        verbose_name=_("Head Teacher's Comment")
    )
    
    # Recommendations
    recommendations = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Recommendations")
    )
    
    # Status
    promotion_status = models.CharField(
        max_length=20,
        choices=[
            ('promoted', _('Promoted')),
            ('retained', _('Retained')),
            ('conditional', _('Conditional Promotion')),
            ('pending', _('Pending Review')),
        ],
        default='pending',
        verbose_name=_("Promotion Status")
    )
    
    # Report generation
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name=_("Generated By")
    )
    generated_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Generated Date")
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Published")
    )
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published Date")
    )
    report_document = models.FileField(
        upload_to='academic_reports/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_("Report Document")
    )
    
    class Meta:
        verbose_name = _("Academic Report")
        verbose_name_plural = _("Academic Reports")
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-academic_year', '-term', 'student']
        indexes = [
            models.Index(fields=['student', 'academic_year', 'term']),
            models.Index(fields=['overall_grade']),
            models.Index(fields=['promotion_status']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"Academic Report - {self.student.get_full_name()} - {self.academic_year} {self.term}"
    
    def generate_report(self):
        """Generate comprehensive academic report"""
        # Calculate overall performance
        from .models import Grade, Attendance
        
        # Get all grades for this term
        grades = Grade.objects.filter(
            student=self.student,
            assessment__academic_year=self.academic_year,
            assessment__term=self.term
        )
        
        if grades.exists():
            # Calculate overall score and grade
            total_score = sum(g.score for g in grades)
            total_possible = sum(g.assessment.total_marks for g in grades)
            
            if total_possible > 0:
                self.overall_score = (total_score / total_possible) * 100
                self.overall_grade = self.convert_to_grade(self.overall_score)
            
            # Calculate subject-wise performance
            subject_data = {}
            for grade in grades:
                subject = grade.subject
                if subject.id not in subject_data:
                    subject_data[subject.id] = {
                        'subject_name': subject.name,
                        'subject_code': subject.code,
                        'scores': [],
                        'total_possible': 0,
                    }
                
                subject_data[subject.id]['scores'].append(grade.score)
                subject_data[subject.id]['total_possible'] += grade.assessment.total_marks
            
            # Calculate subject averages
            self.subject_performance = []
            for subject_id, data in subject_data.items():
                avg_score = sum(data['scores']) / len(data['scores'])
                percentage = (sum(data['scores']) / data['total_possible']) * 100 if data['total_possible'] > 0 else 0
                grade = self.convert_to_grade(percentage)
                
                self.subject_performance.append({
                    'subject_id': subject_id,
                    'subject_name': data['subject_name'],
                    'subject_code': data['subject_code'],
                    'average_score': avg_score,
                    'percentage': percentage,
                    'grade': grade,
                    'is_passing': percentage >= 40,  # Assuming 40% passing
                })
        
        # Get attendance data
        attendance = Attendance.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            term=self.term
        )
        
        if attendance.exists():
            total_days = attendance.count()
            present_days = attendance.filter(status=AttendanceStatus.PRESENT).count()
            self.attendance_percentage = (present_days / total_days) * 100 if total_days > 0 else 0
        
        # Analyze strengths and weaknesses
        self.analyze_performance()
        
        # Determine promotion status
        self.determine_promotion_status()
        
        self.save()
    
    def analyze_performance(self):
        """Analyze student performance to identify strengths and weaknesses"""
        self.strengths = []
        self.weaknesses = []
        
        for subject in self.subject_performance:
            if subject['percentage'] >= 80:
                self.strengths.append({
                    'subject': subject['subject_name'],
                    'score': subject['percentage'],
                    'grade': subject['grade'],
                })
            elif subject['percentage'] < 40:
                self.weaknesses.append({
                    'subject': subject['subject_name'],
                    'score': subject['percentage'],
                    'grade': subject['grade'],
                    'recommendation': 'Needs extra help and tutoring',
                })
        
        # Add attendance analysis
        if self.attendance_percentage < 75:
            self.weaknesses.append({
                'area': 'Attendance',
                'score': self.attendance_percentage,
                'recommendation': 'Needs to improve attendance record',
            })
    
    def determine_promotion_status(self):
        """Determine promotion status based on academic performance"""
        # Check if student passed all subjects
        failed_subjects = [s for s in self.subject_performance if not s['is_passing']]
        
        if not failed_subjects and self.attendance_percentage >= 75:
            self.promotion_status = 'promoted'
        elif len(failed_subjects) <= 2 and self.attendance_percentage >= 65:
            self.promotion_status = 'conditional'
        else:
            self.promotion_status = 'retained'
    
    def convert_to_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        elif percentage >= 30:
            return 'D'
        else:
            return 'F'
    
    def publish_report(self):
        """Publish the academic report"""
        self.is_published = True
        self.published_date = timezone.now()
        self.save()
        
        # Generate PDF document
        self.generate_pdf()
    
    def generate_pdf(self):
        """Generate PDF version of the report"""
        # Implementation using a PDF generation library
        # This would typically use ReportLab, WeasyPrint, or similar
        pass


# ============================================================================
# EVENT AND HOLIDAY MODELS
# ============================================================================

class AcademicEvent(BaseModel):
    """Academic events and holidays"""
    EVENT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('parent_meeting', 'Parent Meeting'),
        ('staff_meeting', 'Staff Meeting'),
        ('holiday', 'Holiday'),
        ('exam', 'Examination'),
    ]


    title = models.CharField(
        max_length=200,
        verbose_name=_("Event Title")
    )
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('holiday', _('Holiday')),
            ('exam', _('Examination')),
            ('parent_meeting', _('Parent Meeting')),
            ('sports_day', _('Sports Day')),
            ('cultural_event', _('Cultural Event')),
            ('field_trip', _('Field Trip')),
            ('workshop', _('Workshop')),
            ('other', _('Other')),
        ],
        verbose_name=_("Event Type")
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Start Time")
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("End Time")
    )
    academic_year = models.CharField(
        max_length=20,
        verbose_name=_("Academic Year")
    )
    term = models.CharField(
        max_length=20,
        choices=TermType.choices,
        verbose_name=_("Term")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Location")
    )
    organizer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Organizer")
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='academic_events',
        verbose_name=_("Participants")
    )
    affected_classes = models.ManyToManyField(
        Class,
        blank=True,
        related_name='academic_events',
        verbose_name=_("Affected Classes")
    )
    is_holiday = models.BooleanField(
        default=False,
        verbose_name=_("Is Holiday")
    )
    color_code = models.CharField(
        max_length=7,
        default='#e74c3c',
        verbose_name=_("Color Code")
    )
    
    class Meta:
        verbose_name = _("Academic Event")
        verbose_name_plural = _("Academic Events")
        ordering = ['start_date', 'start_time']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['is_holiday']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    @property
    def duration_days(self):
        """Calculate event duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def is_current(self):
        """Check if event is currently ongoing"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    def clean(self):
        """Validate event dates"""
        if self.end_date < self.start_date:
            raise ValidationError(_("End date must be after start date"))
        
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValidationError(_("End time must be after start time"))
    
    @classmethod
    def get_upcoming_events(cls, days=30):
        """Get upcoming events within specified days"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return cls.objects.filter(
            start_date__gte=today,
            start_date__lte=future_date
        ).order_by('start_date', 'start_time')
    
    @classmethod
    def get_events_for_date(cls, target_date, academic_year=None, term=None):
        """Get events for a specific date"""
        query = cls.objects.filter(
            start_date__lte=target_date,
            end_date__gte=target_date
        )
        
        if academic_year:
            query = query.filter(academic_year=academic_year)
        if term:
            query = query.filter(term=term)
        
        return query.order_by('start_time')


# ============================================================================
# ACADEMIC CONFIGURATION
# ============================================================================

class GradingScale(BaseModel):
    """Grading scale configuration"""
    SCALE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('letter', 'Letter Grade'),
        ('cbc', 'CBC Scale'),
        ('points', 'Points'),
    ]
    
    ACADEMIC_LEVEL_CHOICES = [
        ('pre_primary', 'Pre-Primary'),
        ('lower_primary', 'Lower Primary'),
        ('upper_primary', 'Upper Primary'),
        ('lower_secondary', 'Lower Secondary'),
        ('senior_secondary', 'Senior Secondary'),
    ]
    name = models.CharField(
        max_length=100,
        verbose_name=_("Grading Scale Name")
    )
    scale_type = models.CharField(
        max_length=20,
        choices=GradeScale.choices,
        verbose_name=_("Scale Type")
    )
    academic_level = models.CharField(
        max_length=30,
        choices=AcademicLevel.choices,
        blank=True,
        verbose_name=_("Academic Level")
    )
    curriculum = models.CharField(
        max_length=50,
        choices=settings.CURRICULUM_CHOICES if hasattr(settings, 'CURRICULUM_CHOICES') else [],
        blank=True,
        verbose_name=_("Curriculum")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Scale")
    )
    
    # Grade ranges (stored as JSON for flexibility)
    grade_ranges = models.JSONField(
        default=list,
        verbose_name=_("Grade Ranges"),
        help_text=_("List of grade ranges with min, max, grade, points, description")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    class Meta:
        verbose_name = _("Grading Scale")
        verbose_name_plural = _("Grading Scales")
        ordering = ['name']
        indexes = [
            models.Index(fields=['scale_type']),
            models.Index(fields=['academic_level']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_grade_for_score(self, score, max_score=100):
        """Get grade for a given score"""
        if max_score != 100:
            score = (score / max_score) * 100
        
        for grade_range in self.grade_ranges:
            min_score = grade_range.get('min_score', 0)
            max_score = grade_range.get('max_score', 100)
            
            if min_score <= score <= max_score:
                return {
                    'grade': grade_range.get('grade'),
                    'points': grade_range.get('points'),
                    'description': grade_range.get('description'),
                }
        
        return None
    
    def save(self, *args, **kwargs):
        """Ensure only one default scale per type and level"""
        if self.is_default:
            GradingScale.objects.filter(
                scale_type=self.scale_type,
                academic_level=self.academic_level,
                is_default=True
            ).exclude(pk=self.pk if self.pk else None).update(is_default=False)
        
        super().save(*args, **kwargs)


class AcademicConfiguration(BaseModel):
    """Academic system configuration"""
    
    current_academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configurations',
        verbose_name=_("Current Academic Year")
    )
    default_grading_scale = models.ForeignKey(
        GradingScale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Default Grading Scale")
    )
    min_attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        verbose_name=_("Minimum Attendance Percentage")
    )
    passing_grade_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name=_("Passing Grade Percentage")
    )
    max_absent_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Maximum Absent Days")
    )
    school_start_time = models.TimeField(
        default='08:00',
        verbose_name=_("School Start Time")
    )
    school_end_time = models.TimeField(
        default='16:00',
        verbose_name=_("School End Time")
    )
    period_duration = models.PositiveIntegerField(
        default=45,
        verbose_name=_("Period Duration (minutes)")
    )
    break_duration = models.PositiveIntegerField(
        default=15,
        verbose_name=_("Break Duration (minutes)")
    )
    lunch_duration = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Lunch Duration (minutes)")
    )
    
    # Assessment weights
    exam_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        verbose_name=_("Exam Weight (%)")
    )
    test_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        verbose_name=_("Test Weight (%)")
    )
    assignment_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        verbose_name=_("Assignment Weight (%)")
    )
    participation_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        verbose_name=_("Participation Weight (%)")
    )
    
    # Promotion criteria
    min_promotion_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        verbose_name=_("Minimum Promotion Score (%)")
    )
    max_failed_subjects = models.PositiveIntegerField(
        default=2,
        verbose_name=_("Maximum Failed Subjects for Promotion")
    )
    
    # Notification settings
    attendance_warning_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.00,
        verbose_name=_("Attendance Warning Threshold (%)")
    )
    send_attendance_alerts = models.BooleanField(
        default=True,
        verbose_name=_("Send Attendance Alerts")
    )
    send_performance_alerts = models.BooleanField(
        default=True,
        verbose_name=_("Send Performance Alerts")
    )
    
    # Other settings
    enable_online_submission = models.BooleanField(
        default=True,
        verbose_name=_("Enable Online Assignment Submission")
    )
    enable_parent_portal = models.BooleanField(
        default=True,
        verbose_name=_("Enable Parent Portal")
    )
    result_publication_delay = models.PositiveIntegerField(
        default=7,
        verbose_name=_("Result Publication Delay (days)")
    )
    
    class Meta:
        verbose_name = _("Academic Configuration")
        verbose_name_plural = _("Academic Configurations")
    
    def __str__(self):
        return "Academic Configuration"
    
    def save(self, *args, **kwargs):
        """Ensure only one configuration exists"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass
    
    @classmethod
    def load(cls):
        """Load or create academic configuration"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj