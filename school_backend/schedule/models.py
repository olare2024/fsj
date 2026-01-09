# schedule/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
import logging

from academics.models import Class, Subject
from accounts.models import User

logger = logging.getLogger(__name__)


class BaseScheduleModel(models.Model):
    """Abstract base model for all schedule models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


# ==================== CURRICULUM MODELS ====================
class Curriculum(BaseScheduleModel):
    """Enhanced curriculum model for Delvok Academy"""
    CURRICULUM_CHOICES = [
        ('cbc', 'Competency Based Curriculum (CBC)'),
        ('8-4-4', '8-4-4 System'),
        ('igcse', 'Cambridge IGCSE'),
        ('ib', 'International Baccalaureate'),
        ('american', 'American Curriculum'),
    ]
    
    name = models.CharField(max_length=20, choices=CURRICULUM_CHOICES, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code e.g., CBC, IGCSE")
    description = models.TextField(blank=True)
    country = models.CharField(max_length=50, default='Kenya')
    
    # Curriculum settings
    terms_per_year = models.PositiveIntegerField(default=3)
    weeks_per_term = models.PositiveIntegerField(default=13)
    school_days_per_week = models.PositiveIntegerField(default=5)
    
    # Academic structure
    has_pre_primary = models.BooleanField(default=True)
    has_primary = models.BooleanField(default=True)
    has_secondary = models.BooleanField(default=True)
    
    # Status
    is_national = models.BooleanField(default=False)
    implementation_year = models.PositiveIntegerField(default=2017)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Curriculum"
        verbose_name_plural = "Curricula"

    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        """Set curriculum code based on name"""
        if not self.code:
            self.code = self.name.upper()
        super().save(*args, **kwargs)

    @property
    def total_weeks_per_year(self):
        return self.terms_per_year * self.weeks_per_term

    @property
    def total_school_days_per_year(self):
        return self.total_weeks_per_year * self.school_days_per_week


class GradeLevel(BaseScheduleModel):
    """Enhanced grade level model with Kenya education system support"""
    GRADE_CHOICES = [
        # CBC Levels
        ('pre_primary_1', 'Pre-Primary 1 (PP1)'),
        ('pre_primary_2', 'Pre-Primary 2 (PP2)'),
        ('grade_1', 'Grade 1'),
        ('grade_2', 'Grade 2'),
        ('grade_3', 'Grade 3'),
        ('grade_4', 'Grade 4'),
        ('grade_5', 'Grade 5'),
        ('grade_6', 'Grade 6'),
        ('grade_7', 'Grade 7'),
        ('grade_8', 'Grade 8'),
        ('grade_9', 'Grade 9'),
        ('grade_10', 'Grade 10'),
        ('grade_11', 'Grade 11'),
        ('grade_12', 'Grade 12'),
        # 8-4-4 Levels
        ('class_1', 'Class 1'),
        ('class_2', 'Class 2'),
        ('class_3', 'Class 3'),
        ('class_4', 'Class 4'),
        ('class_5', 'Class 5'),
        ('class_6', 'Class 6'),
        ('class_7', 'Class 7'),
        ('class_8', 'Class 8'),
        ('form_1', 'Form 1'),
        ('form_2', 'Form 2'),
        ('form_3', 'Form 3'),
        ('form_4', 'Form 4'),
    ]
    
    EDUCATION_LEVELS = [
        ('pre_primary', 'Pre-Primary'),
        ('lower_primary', 'Lower Primary'),
        ('upper_primary', 'Upper Primary'),
        ('lower_secondary', 'Lower Secondary'),
        ('upper_secondary', 'Upper Secondary'),
        ('tertiary', 'Tertiary'),
    ]
    
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='grade_levels')
    grade_code = models.CharField(max_length=20, choices=GRADE_CHOICES)
    name = models.CharField(max_length=50, help_text="Display name e.g., 'Form 1', 'Grade 5'")
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    order = models.PositiveIntegerField(help_text="Numerical order for sorting")
    
    # Age information
    typical_start_age = models.PositiveIntegerField(help_text="Typical starting age for this grade")
    typical_end_age = models.PositiveIntegerField(help_text="Typical ending age for this grade")
    
    # Academic requirements
    is_examination_class = models.BooleanField(default=False)
    has_national_exam = models.BooleanField(default=False)
    kicd_code = models.CharField(max_length=20, blank=True, null=True, help_text="KICD curriculum code")
    
    # Resources
    description = models.TextField(blank=True, null=True)
    learning_outcomes = models.TextField(blank=True, null=True, help_text="Expected learning outcomes")

    class Meta:
        unique_together = ('curriculum', 'grade_code')
        ordering = ['curriculum', 'order']
        verbose_name = "Grade Level"
        verbose_name_plural = "Grade Levels"

    def __str__(self):
        return f"{self.curriculum.get_name_display()} - {self.name}"

    def clean(self):
        """Validate grade level data"""
        if self.typical_start_age >= self.typical_end_age:
            raise ValidationError("Start age must be less than end age")
        
        # Validate education level based on grade
        self.validate_education_level()

    def validate_education_level(self):
        """Validate education level based on grade code"""
        level_mapping = {
            'pre_primary': ['pre_primary_1', 'pre_primary_2'],
            'lower_primary': ['grade_1', 'grade_2', 'grade_3'],
            'upper_primary': ['grade_4', 'grade_5', 'grade_6', 'class_5', 'class_6', 'class_7', 'class_8'],
            'lower_secondary': ['grade_7', 'grade_8', 'grade_9', 'form_1', 'form_2'],
            'upper_secondary': ['grade_10', 'grade_11', 'grade_12', 'form_3', 'form_4'],
        }
        
        for level, grades in level_mapping.items():
            if self.grade_code in grades and self.education_level != level:
                raise ValidationError(f"Grade {self.grade_code} should be in {level} education level")

    @property
    def next_grade(self):
        """Get the next grade level in sequence"""
        try:
            return GradeLevel.objects.get(
                curriculum=self.curriculum,
                order=self.order + 1
            )
        except GradeLevel.DoesNotExist:
            return None

    @property
    def previous_grade(self):
        """Get the previous grade level in sequence"""
        try:
            return GradeLevel.objects.get(
                curriculum=self.curriculum,
                order=self.order - 1
            )
        except GradeLevel.DoesNotExist:
            return None


# ==================== TIMETABLE MODELS ====================
class Period(BaseScheduleModel):
    """Enhanced period model for school timetable"""
    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
    ]
    
    PERIOD_TYPES = [
        ('academic', 'Academic Period'),
        ('break', 'Break Time'),
        ('assembly', 'Assembly'),
        ('sports', 'Sports/Games'),
        ('club', 'Club Activity'),
        ('remedial', 'Remedial Class'),
        ('pastoral', 'Pastoral Program'),
    ]
    
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    period_number = models.PositiveIntegerField(help_text="Period sequence for the day")
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_type = models.CharField(max_length=15, choices=PERIOD_TYPES, default='academic')
    
    # Academic associations
    Class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='periods')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='teaching_periods'
    )
    
    # Curriculum context
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    
    # Period details
    duration_minutes = models.PositiveIntegerField(editable=False, help_text="Duration in minutes")
    is_break = models.BooleanField(default=False)
    break_type = models.CharField(
        max_length=20,
        choices=[
            ('short_break', 'Short Break'),
            ('lunch', 'Lunch Break'),
            ('long_break', 'Long Break'),
        ],
        blank=True,
        null=True
    )
    
    # Room and resources
    room = models.CharField(max_length=50, blank=True, null=True, help_text="Specific room/lab")
    requires_special_equipment = models.BooleanField(default=False)
    equipment_notes = models.TextField(blank=True, null=True)
    
    # Recurrence
    is_recurring = models.BooleanField(default=True)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(blank=True, null=True)
    
    # Status
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    substitute_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='substitute_periods'
    )

    class Meta:
        unique_together = ("day_of_week", "start_time", "Class", "curriculum")
        ordering = ['day_of_week', 'period_number', 'start_time']
        indexes = [
            models.Index(fields=['day_of_week', 'start_time']),
            models.Index(fields=['Class', 'is_active']),
            models.Index(fields=['teacher', 'day_of_week']),
            models.Index(fields=['curriculum', 'grade_level']),
        ]
        verbose_name = "Period"
        verbose_name_plural = "Periods"

    def __str__(self):
        subject_str = f" - {self.subject.name}" if self.subject else ""
        return f"{self.Class.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}{subject_str}"

    def clean(self):
        """Validate period data"""
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        
        if self.valid_to and self.valid_from > self.valid_to:
            raise ValidationError("Valid to date must be after valid from date")
        
        # Calculate duration
        self.calculate_duration()
        
        # Validate teacher availability
        self.validate_teacher_availability()

    def calculate_duration(self):
        """Calculate duration in minutes"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        self.duration_minutes = end_minutes - start_minutes

    def validate_teacher_availability(self):
        """Check if teacher is available during this period"""
        if self.teacher and self.period_type == 'academic':
            conflicting_periods = Period.objects.filter(
                teacher=self.teacher,
                day_of_week=self.day_of_week,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                is_active=True,
                is_cancelled=False
            ).exclude(id=self.id)
            
            if conflicting_periods.exists():
                raise ValidationError(
                    f"Teacher {self.teacher.get_full_name()} is already teaching during this time"
                )

    def save(self, *args, **kwargs):
        self.calculate_duration()
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        """Check if this period is currently active"""
        now = timezone.now()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        return (self.day_of_week == current_day and 
                self.start_time <= current_time <= self.end_time and
                not self.is_cancelled)

    @property
    def is_upcoming(self):
        """Check if this period is upcoming today"""
        now = timezone.now()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        return (self.day_of_week == current_day and 
                current_time < self.start_time and
                not self.is_cancelled)

    def cancel_period(self, reason, substitute=None):
        """Cancel this period"""
        self.is_cancelled = True
        self.cancellation_reason = reason
        if substitute:
            self.substitute_teacher = substitute
        self.save()


class Timetable(BaseScheduleModel):
    """Enhanced timetable model for academic scheduling"""
    TERM_CHOICES = [
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    ]
    
    TIMETABLE_TYPES = [
        ('academic', 'Academic Timetable'),
        ('exam', 'Examination Timetable'),
        ('special', 'Special Events Timetable'),
        ('remedial', 'Remedial Timetable'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g., Term 1 Timetable 2024")
    timetable_type = models.CharField(max_length=15, choices=TIMETABLE_TYPES, default='academic')
    
    # Academic context
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    term = models.IntegerField(choices=TERM_CHOICES)
    academic_year = models.CharField(max_length=9, help_text="Format: YYYY-YYYY")
    
    # Schedule details
    periods = models.ManyToManyField(Period, related_name='timetables', blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField()
    
    # Status and management
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['admin', 'teacher']}
    )
    
    # Metadata
    version = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this timetable")

    class Meta:
        unique_together = ('curriculum', 'grade_level', 'term', 'academic_year', 'timetable_type')
        ordering = ['academic_year', 'curriculum', 'grade_level', 'term']
        verbose_name = "Timetable"
        verbose_name_plural = "Timetables"

    def __str__(self):
        return f"{self.name} - {self.curriculum} {self.grade_level} Term {self.term} {self.academic_year}"

    def clean(self):
        """Validate timetable data"""
        if self.effective_from >= self.effective_to:
            raise ValidationError("Effective to date must be after effective from date")
        
        # Validate academic year format
        if not self.is_valid_academic_year():
            raise ValidationError("Academic year must be in format YYYY-YYYY")

    def is_valid_academic_year(self):
        """Validate academic year format"""
        try:
            start_year, end_year = map(int, self.academic_year.split('-'))
            return end_year == start_year + 1
        except (ValueError, AttributeError):
            return False

    def save(self, *args, **kwargs):
        """Handle timetable publishing"""
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_periods_per_week(self):
        """Calculate total periods per week"""
        return self.periods.filter(is_break=False).count()

    @property
    def subject_distribution(self):
        """Get distribution of subjects across the timetable"""
        from django.db.models import Count
        return self.periods.filter(
            is_break=False, 
            subject__isnull=False
        ).values('subject__name').annotate(
            count=Count('id')
        ).order_by('-count')

    def get_daily_schedule(self, day_of_week):
        """Get schedule for a specific day"""
        return self.periods.filter(
            day_of_week=day_of_week
        ).order_by('period_number')

    def clone_to_new_term(self, new_term, new_academic_year):
        """Clone timetable to a new term"""
        new_timetable = Timetable.objects.create(
            name=f"{self.name} (Copy)",
            curriculum=self.curriculum,
            grade_level=self.grade_level,
            term=new_term,
            academic_year=new_academic_year,
            effective_from=self.effective_from,
            effective_to=self.effective_to,
            version=1,
            is_active=False,
            is_published=False
        )
        
        # Clone periods
        for period in self.periods.all():
            new_period = Period.objects.create(
                day_of_week=period.day_of_week,
                period_number=period.period_number,
                start_time=period.start_time,
                end_time=period.end_time,
                period_type=period.period_type,
                Class=period.Class,
                subject=period.subject,
                teacher=period.teacher,
                curriculum=period.curriculum,
                grade_level=period.grade_level,
                duration_minutes=period.duration_minutes,
                is_break=period.is_break,
                break_type=period.break_type,
                room=period.room,
                requires_special_equipment=period.requires_special_equipment,
                equipment_notes=period.equipment_notes
            )
            new_timetable.periods.add(new_period)
        
        return new_timetable


class BreakTime(BaseScheduleModel):
    """Enhanced break time model"""
    BREAK_CHOICES = [
        ('short_break', 'Short Break'),
        ('lunch', 'Lunch Break'),
        ('long_break', 'Long Break'),
        ('assembly', 'Assembly'),
        ('sports', 'Sports/Games'),
        ('club', 'Club Period'),
    ]
    
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='breaks')
    break_type = models.CharField(max_length=20, choices=BREAK_CHOICES)
    name = models.CharField(max_length=50, blank=True, null=True, help_text="Custom break name")
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(editable=False)
    
    # Break specifics
    has_supervised_activities = models.BooleanField(default=False)
    activity_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Where break takes place")
    
    # Staffing
    supervising_teachers = models.ManyToManyField(
        User,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='supervised_breaks'
    )

    class Meta:
        ordering = ['timetable', 'start_time']
        verbose_name = "Break Time"
        verbose_name_plural = "Break Times"

    def __str__(self):
        break_name = self.name or self.get_break_type_display()
        return f"{self.timetable} - {break_name} ({self.start_time}-{self.end_time})"

    def save(self, *args, **kwargs):
        # Calculate duration in minutes
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        self.duration_minutes = end_minutes - start_minutes
        
        if not self.name:
            self.name = self.get_break_type_display()
            
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        """Check if break is currently ongoing"""
        now = timezone.now()
        current_time = now.time()
        return self.start_time <= current_time <= self.end_time


# ==================== CURRICULUM MAPPING MODELS ====================
class CurriculumSubjectMapping(BaseScheduleModel):
    """Enhanced mapping of subjects to curricula and grade levels"""
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Subject classification
    is_core = models.BooleanField(default=True, help_text="Core or elective subject")
    is_examinable = models.BooleanField(default=True)
    subject_category = models.CharField(
        max_length=20,
        choices=[
            ('languages', 'Languages'),
            ('sciences', 'Sciences'),
            ('humanities', 'Humanities'),
            ('technical', 'Technical Subjects'),
            ('arts', 'Creative Arts'),
            ('physical', 'Physical Education'),
            ('religious', 'Religious Education'),
            ('life_skills', 'Life Skills'),
        ],
        default='sciences'
    )
    
    # Academic requirements
    periods_per_week = models.PositiveIntegerField(default=5)
    recommended_duration = models.PositiveIntegerField(
        default=40,
        help_text="Recommended minutes per period"
    )
    annual_teaching_weeks = models.PositiveIntegerField(
        default=39,
        help_text="Weeks allocated for teaching this subject annually"
    )
    
    # Kenya-specific
    kicd_code = models.CharField(max_length=20, blank=True, null=True, help_text="KICD subject code")
    is_compulsory = models.BooleanField(default=True)
    
    # Resources
    recommended_books = models.TextField(blank=True, null=True)
    learning_outcomes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('curriculum', 'grade_level', 'subject')
        ordering = ['curriculum', 'grade_level', 'subject_category', 'subject']
        verbose_name = "Curriculum Subject Mapping"
        verbose_name_plural = "Curriculum Subject Mappings"

    def __str__(self):
        core_status = "Core" if self.is_core else "Elective"
        return f"{self.curriculum} - {self.grade_level} - {self.subject.name} ({core_status})"

    @property
    def total_teaching_minutes_per_week(self):
        return self.periods_per_week * self.recommended_duration

    @property
    def total_teaching_hours_per_year(self):
        total_minutes = self.total_teaching_minutes_per_week * self.annual_teaching_weeks
        return total_minutes / 60


# ==================== SPECIAL SCHEDULE MODELS ====================
class SpecialSchedule(BaseScheduleModel):
    """Model for special schedules (exams, events, etc.)"""
    SCHEDULE_TYPES = [
        ('examination', 'Examination Schedule'),
        ('event', 'Special Event'),
        ('holiday', 'Holiday Schedule'),
        ('makeup', 'Make-up Classes'),
        ('staff_development', 'Staff Development'),
    ]
    
    name = models.CharField(max_length=200)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Timing
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default='08:00')
    end_time = models.TimeField(default='16:00')
    
    # Affected groups
    affected_curricula = models.ManyToManyField(Curriculum, blank=True)
    affected_grade_levels = models.ManyToManyField(GradeLevel, blank=True)
    affected_Classs = models.ManyToManyField(Class, blank=True)
    
    # Status
    is_whole_school = models.BooleanField(default=False)
    requires_attendance = models.BooleanField(default=False)
    
    # Organization
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['admin', 'teacher']}
    )
    location = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['start_date', 'start_time']
        verbose_name = "Special Schedule"
        verbose_name_plural = "Special Schedules"

    def __str__(self):
        return f"{self.name} - {self.start_date} to {self.end_date}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date")

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class TimetableAdjustment(BaseScheduleModel):
    """Model for temporary timetable adjustments"""
    ADJUSTMENT_TYPES = [
        ('cancellation', 'Class Cancellation'),
        ('room_change', 'Room Change'),
        ('time_change', 'Time Change'),
        ('teacher_change', 'Teacher Change'),
        ('substitution', 'Teacher Substitution'),
    ]
    
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    adjustment_date = models.DateField()
    
    # Adjustment details
    original_value = models.CharField(max_length=200, blank=True, null=True)
    new_value = models.CharField(max_length=200, blank=True, null=True)
    
    # Reason and approval
    reason = models.TextField()
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_adjustments'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_adjustments',
        limit_choices_to={'role__in': ['admin', 'teacher']}
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['adjustment_date', 'period']
        verbose_name = "Timetable Adjustment"
        verbose_name_plural = "Timetable Adjustments"

    def __str__(self):
        return f"{self.get_adjustment_type_display()} for {self.period} on {self.adjustment_date}"

    def approve(self, approved_by):
        """Approve this adjustment"""
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()


# ==================== SIGNAL HANDLERS ====================
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Timetable)
def handle_timetable_publishing(sender, instance, created, **kwargs):
    """Handle notifications when timetable is published"""
    if instance.is_published and instance.is_active:
        from users.models import UserNotification
        
        # Notify teachers
        teachers = User.objects.filter(
            role='teacher',
            teaching_periods__timetables=instance
        ).distinct()
        
        for teacher in teachers:
            UserNotification.objects.create(
                user=teacher,
                notification_type='academic',
                priority='normal',
                title=f'New Timetable Published: {instance.name}',
                message=f'The {instance.name} has been published and is now active.',
                action_url=f'/timetable/{instance.id}',
                action_text='View Timetable'
            )
        
        logger.info(f"Timetable {instance.name} published and notifications sent")


@receiver(post_save, sender=Period)
def validate_period_conflicts(sender, instance, created, **kwargs):
    """Check for scheduling conflicts when periods are created/updated"""
    if created and instance.period_type == 'academic':
        # Check for Class conflicts
        Class_conflicts = Period.objects.filter(
            Class=instance.Class,
            day_of_week=instance.day_of_week,
            start_time__lt=instance.end_time,
            end_time__gt=instance.start_time,
            is_active=True,
            is_cancelled=False
        ).exclude(id=instance.id)
        
        if Class_conflicts.exists():
            logger.warning(
                f"Class conflict detected for {instance.Class.name} "
                f"on {instance.day_of_week} {instance.start_time}-{instance.end_time}"
            )