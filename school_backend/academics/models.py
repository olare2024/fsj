"""
academics/models.py
Enhanced academic models for comprehensive school management system.
Supports multiple curricula including CBC, 8-4-4, IGCSE, IB, and more.
"""

import uuid
import logging
from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache
from django.db import models
from django.db.models import Q, F
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from students.models import StudentEnrollment
from teachers.models import TeacherProfile

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS AND CHOICES
# ============================================================================

# House Choices
HOUSE_CHOICES = [
    ('unity', 'Unity House'),
    ('courage', 'Courage House'),
    ('wisdom', 'Wisdom House'),
    ('success', 'Success House'),
    ('excellence', 'Excellence House'),
    ('integrity', 'Integrity House'),
    ('bravery', 'Bravery House'),
    ('honor', 'Honor House'),
]

# Grade Level Choices
GRADE_LEVEL_CHOICES = (
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
    ('grade_10', 'Grade 10 (Senior 1)'),
    ('grade_11', 'Grade 11 (Senior 2)'),
    ('grade_12', 'Grade 12 (Senior 3)'),
)

# Stream Choices
STREAM_CHOICES = (
    ('general', 'General (G4-9)'),
    ('stem', 'STEM Pathway'),
    ('social_sciences', 'Social Sciences Pathway'),
    ('arts_sports', 'Arts & Sports Pathway'),
    ('pure_science', 'Pure Science (STEM)'),
    ('applied_science', 'Applied Science (STEM)'),
    ('technical', 'Technical & Engineering (STEM)'),
)

# Education Level Choices
EDUCATION_LEVELS = (
    ('early_years', 'Early Years (Pre-primary - Grade 3)'),
    ('middle_school', 'Middle School (Grade 4 - Grade 9)'),
    ('senior_school', 'Senior School (Grade 10 - Grade 12)'),
    ('foundation', 'Foundation Level'),
    ('intermediate', 'Intermediate Level'),
    ('advanced', 'Advanced Level'),
)

# CBC Pathway Choices
CBC_PATHWAY_CHOICES = (
    ('stem', 'Science, Technology, Engineering & Mathematics'),
    ('social_sciences', 'Social Sciences'),
    ('arts_sports', 'Arts and Sports'),
)

# Senior School Track Choices
SENIOR_SCHOOL_TRACKS = (
    ('stem_science', 'STEM - Pure Sciences'),
    ('stem_technical', 'STEM - Technical & Engineering'),
    ('stem_applied', 'STEM - Applied Sciences'),
    ('social_sciences_general', 'Social Sciences - General'),
    ('social_sciences_business', 'Social Sciences - Business'),
    ('social_sciences_humanities', 'Social Sciences - Humanities'),
    ('arts_performing', 'Arts - Performing Arts'),
    ('arts_visual', 'Arts - Visual & Creative Arts'),
    ('sports_performance', 'Sports - Performance'),
    ('sports_management', 'Sports - Management'),
)

# Subject Category Choices
SUBJECT_CATEGORIES = (
    ('core', 'Core'),
    ('elective', 'Elective'),
    ('cbc_core', 'CBC Core Competency'),
    ('cbc_optional', 'CBC Optional'),
    ('pathway_core', 'Pathway Core'),
    ('pathway_elective', 'Pathway Elective'),
    ('technical', 'Technical'),
    ('languages', 'Languages'),
    ('arts', 'Creative Arts'),
    ('sciences', 'Sciences'),
    ('humanities', 'Humanities'),
    ('physical', 'Physical Education'),
    ('religious', 'Religious Education'),
)

# Assessment Type Choices
ASSESSMENT_TYPES = (
    ('knec', 'KNEC National Exams'),
    ('school_based', 'School-Based Assessment'),
    ('portfolio', 'Portfolio Assessment'),
    ('practical', 'Practical Assessment'),
    ('project', 'Project Work'),
    ('cat', 'Continuous Assessment Test (CAT)'),
    ('assignment', 'Assignment'),
    ('oral', 'Oral Assessment'),
    ('demonstration', 'Skill Demonstration'),
)

# Curriculum Choices
CURRICULUM_CHOICES = (
    ('cbc', 'Competency Based Curriculum (CBC)'),
    ('8-4-4', '8-4-4 System'),
    ('icse', 'ICSE'),
    ('igcse', 'IGCSE'),
    ('american', 'American'),
    ('combined', 'Combined'),
    ('ib', 'International Baccalaureate'),
    ('montessori', 'Montessori'),
)

# Difficulty Level Choices
DIFFICULTY_LEVELS = (
    ('basic', 'Basic'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('honors', 'Honors'),
)

# Term Choices
TERM_CHOICES = (
    ('term_1', 'Term 1'),
    ('term_2', 'Term 2'),
    ('term_3', 'Term 3'),
    ('semester_1', 'Semester 1'),
    ('semester_2', 'Semester 2'),
    ('trimester_1', 'Trimester 1'),
    ('trimester_2', 'Trimester 2'),
    ('trimester_3', 'Trimester 3'),
)

# Event Type Choices
EVENT_TYPE_CHOICES = (
    ('exam', 'Examination'),
    ('assessment', 'Assessment'),
    ('holiday', 'Holiday'),
    ('sports', 'Sports Event'),
    ('cultural', 'Cultural Event'),
    ('meeting', 'Staff Meeting'),
    ('parent_meeting', 'Parent-Teacher Meeting'),
    ('workshop', 'Workshop'),
    ('ceremony', 'Ceremony'),
    ('field_trip', 'Field Trip'),
)

# Priority Choices
PRIORITY_CHOICES = (
    ('low', 'Low Priority'),
    ('medium', 'Medium Priority'),
    ('high', 'High Priority'),
    ('critical', 'Critical'),
)

# Enrollment Status Choices
ENROLLMENT_STATUS = (
    ('active', 'Active'),
    ('transferred', 'Transferred'),
    ('graduated', 'Graduated'),
    ('withdrawn', 'Withdrawn'),
    ('suspended', 'Suspended'),
)


# ============================================================================
# BASE MODEL
# ============================================================================

class BaseAcademicModel(models.Model):
    """
    Enhanced abstract base model for all academic models with audit trail.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_entries',
        verbose_name=_("Created By")
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_entries',
        verbose_name=_("Updated By")
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

    def get_audit_info(self):
        """
        Get audit information for the model.
        
        Returns:
            dict: Audit information including created/updated dates and users.
        """
        return {
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by.get_full_name() if self.created_by else 'System',
            'updated_by': self.updated_by.get_full_name() if self.updated_by else 'System'
        }

    def save(self, *args, **kwargs):
        """
        Auto-set audit fields if user is available in request.
        """
        from django.contrib.auth.models import AnonymousUser
        request = getattr(settings, 'CURRENT_REQUEST', None)
        
        if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            if not self.pk and not self.created_by:
                self.created_by = request.user
            if not self.updated_by:
                self.updated_by = request.user
        
        super().save(*args, **kwargs)


# ============================================================================
# MANAGER CLASSES
# ============================================================================

class AcademicYearManager(models.Manager):
    """Custom manager for AcademicYear with caching support."""
    
    def get_current(self):
        """Get current academic year with caching."""
        cache_key = 'current_academic_year'
        current_year = cache.get(cache_key)
        
        if current_year is None:
            current_year = self.filter(is_current=True).first()
            if current_year:
                cache.set(cache_key, current_year, 3600)
        return current_year
    
    def get_active_years(self):
        """Get all active academic years (based on date)."""
        today = timezone.now().date()
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        )
    
    def get_upcoming_years(self):
        """Get upcoming academic years."""
        today = timezone.now().date()
        return self.filter(
            start_date__gt=today,
            is_active=True
        ).order_by('start_date')


class AcademicTermManager(models.Manager):
    """Custom manager for AcademicTerm."""
    
    def get_current(self):
        """Get current academic term."""
        today = timezone.now().date()
        return self.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).first()
    
    def get_by_academic_year(self, academic_year):
        """Get all terms for a specific academic year."""
        return self.filter(academic_year=academic_year, is_active=True)


class SubjectManager(models.Manager):
    """Custom manager for Subject model."""
    
    def get_by_curriculum(self, curriculum):
        """Get subjects by curriculum."""
        return self.filter(curriculum=curriculum, is_active=True)
    
    def get_by_grade_level(self, grade_level):
        """Get subjects by grade level."""
        return self.filter(
            grade_levels__contains=[grade_level],
            is_active=True
        )
    
    def core_subjects(self):
        """Get all core subjects."""
        return self.filter(category='core', is_active=True)
    
    def elective_subjects(self):
        """Get all elective subjects."""
        return self.filter(category='elective', is_active=True)


class ClassManager(models.Manager):
    """Custom manager for Class model."""
    
    def get_by_grade_level(self, grade_level, academic_year=None):
        """Get classes by grade level."""
        queryset = self.filter(grade_level=grade_level, is_active=True)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        return queryset
    
    def get_available_classes(self, academic_year=None):
        """Get classes with available seats."""
        from .models import AcademicYear
        if not academic_year:
            current_year = AcademicYear.objects.get_current()
            if current_year:
                academic_year = current_year
        if academic_year:
            return self.filter(
                academic_year=academic_year,
                is_active=True
            ).annotate(
                available_seats=models.F('capacity') - models.F('current_strength')
            ).filter(available_seats__gt=0)
        return self.none()
    
    def get_by_class_teacher(self, teacher):
        """Get classes taught by a specific teacher."""
        return self.filter(class_teacher=teacher, is_active=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_student_model(model_name):
    """
    Safely get student model without circular imports.
    
    Args:
        model_name (str): Name of the model to retrieve.
    
    Returns:
        Model or None: The model class if found, None otherwise.
    """
    try:
        return apps.get_model('students', model_name)
    except LookupError:
        return None


# ============================================================================
# MAIN MODELS
# ============================================================================

class Subject(BaseAcademicModel):
    """Enhanced Subject management with comprehensive curriculum support."""
    
    # Basic Information
    name = models.CharField(max_length=100, verbose_name=_("Subject Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Subject Code"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Academic Information
    category = models.CharField(
        max_length=20, 
        choices=SUBJECT_CATEGORIES, 
        default='core',
        verbose_name=_("Category")
    )
    
    curriculum = models.CharField(
        max_length=20,
        choices=CURRICULUM_CHOICES,
        default='cbc',
        verbose_name=_("Curriculum")
    )
    
    # CBC-Specific Fields
    cbc_competency_area = models.CharField(
        max_length=30,
        choices=[
            ('communication', 'Communication and Collaboration'),
            ('critical_thinking', 'Critical Thinking and Problem Solving'),
            ('creativity', 'Creativity and Imagination'),
            ('citizenship', 'Citizenship'),
            ('digital_literacy', 'Digital Literacy'),
            ('learning_to_learn', 'Learning to Learn'),
            ('self_efficacy', 'Self-efficacy'),
        ],
        blank=True,
        null=True,
        verbose_name=_("CBC Competency Area")
    )
    
    cbc_pathway = models.CharField(
        max_length=20,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    is_cbc_core = models.BooleanField(default=False, verbose_name=_("Is CBC Core Subject"))
    is_compulsory = models.BooleanField(default=True, verbose_name=_("Is Compulsory"))
    
    # Grade Levels
    grade_levels = models.JSONField(
        default=list,
        help_text=_("Grade levels where this subject is taught"),
        verbose_name=_("Grade Levels")
    )
    
    # Academic Requirements
    credits = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name=_("Credits")
    )
    
    periods_per_week = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Periods per Week")
    )
    
    practical_weight = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Practical Weight (%)")
    )
    
    # Assessment Information
    assessment_methods = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Recommended assessment methods"),
        verbose_name=_("Assessment Methods")
    )
    
    project_based = models.BooleanField(
        default=False,
        verbose_name=_("Project Based")
    )
    
    # Resources
    resources_required = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Required resources for teaching this subject"),
        verbose_name=_("Resources Required")
    )
    
    recommended_books = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Recommended textbooks and references"),
        verbose_name=_("Recommended Books")
    )
    
    # Prerequisites
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        help_text=_("Prerequisite subjects"),
        verbose_name=_("Prerequisites")
    )
    
    # Department Information
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects',
        verbose_name=_("Department")
    )
    
    # Teacher Requirements
    minimum_qualification = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Minimum Qualification")
    )
    
    # Status Flags
    is_examined = models.BooleanField(default=True, verbose_name=_("Is Examined"))
    is_elective = models.BooleanField(default=False, verbose_name=_("Is Elective"))
    
    # Additional Information
    syllabus_link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Syllabus Link")
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )

    objects = SubjectManager()

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        ordering = ['code', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['curriculum']),
            models.Index(fields=['is_cbc_core']),
            models.Index(fields=['cbc_pathway']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """Auto-generate code and set CBC flags."""
        if not self.code and self.name:
            # Generate code from name (first 3 letters uppercase)
            self.code = ''.join(c for c in self.name[:3] if c.isalpha()).upper()
            
            # Ensure uniqueness
            count = Subject.objects.filter(code=self.code).exclude(pk=self.pk).count()
            if count > 0:
                self.code = f"{self.code}{count + 1}"
        
        # Auto-set CBC flags
        if self.curriculum == 'cbc' and self.category in ['cbc_core', 'pathway_core']:
            self.is_cbc_core = True
        
        super().save(*args, **kwargs)

    def clean(self):
        """Validate subject data."""
        errors = {}
        
        if self.practical_weight < 0 or self.practical_weight > 100:
            errors['practical_weight'] = _("Practical weight must be between 0 and 100")
        
        if self.periods_per_week < 1 or self.periods_per_week > 20:
            errors['periods_per_week'] = _("Periods per week must be between 1 and 20")
        
        if errors:
            raise ValidationError(errors)

    @property
    def weekly_hours(self):
        """Calculate weekly hours (assuming 40-minute periods)."""
        return round(self.periods_per_week * 40 / 60, 1)

    @property
    def is_cbc_subject(self):
        """Check if this is a CBC subject."""
        return self.curriculum == 'cbc'

    @property
    def subject_info(self):
        """Get comprehensive subject information."""
        return {
            'name': self.name,
            'code': self.code,
            'category': self.get_category_display(),
            'curriculum': self.get_curriculum_display(),
            'is_cbc': self.is_cbc_subject,
            'is_core': self.is_cbc_core,
            'is_compulsory': self.is_compulsory,
            'weekly_hours': self.weekly_hours,
            'credits': float(self.credits),
            'practical_weight': self.practical_weight,
            'project_based': self.project_based,
        }

# academics/models.py
class School(models.Model):
    """Model for school information"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    motto = models.CharField(max_length=255, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='school/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class AcademicYear(BaseAcademicModel):
    """Enhanced Academic year management with comprehensive curriculum support."""
    
    # Curriculum System Choices
    CURRICULUM_SYSTEMS = [
        ('cbc_kenya', 'Kenya CBC (Competency Based Curriculum)'),
        ('8-4-4_kenya', 'Kenya 8-4-4 System'),
        ('igcse', 'Cambridge IGCSE'),
        ('ib', 'International Baccalaureate'),
        ('american', 'American Common Core'),
        ('british', 'British National Curriculum'),
        ('indian', 'Indian CBSE/ICSE'),
        ('nigeria_bec', 'Nigeria BEC'),
        ('south_africa_caps', 'South Africa CAPS'),
        ('uganda_competency', 'Uganda Competency Based'),
        ('tanzania_competency', 'Tanzania Competency Based'),
        ('custom', 'Custom/Institutional'),
        ('mixed', 'Mixed/Combined'),
    ]
    
    # Academic Structure Choices
    ACADEMIC_STRUCTURES = [
        ('cbc_2_6_3_3', 'CBC 2-6-3-3 (Kenya)'),
        ('8_4_4', '8-4-4 System (Kenya)'),
        ('6_3_3_4', '6-3-3-4 (Nigeria)'),
        ('7_5', '7-5 (Uganda/Tanzania)'),
        ('5_3_4', '5-3-4 (American)'),
        ('ib_pyp_myp_dp', 'IB PYP-MYP-DP'),
        ('igcse_a_level', 'IGCSE + A-Levels'),
        ('custom_structure', 'Custom Structure'),
    ]
    
    # Grading System Choices
    GRADING_SYSTEMS = [
        ('cbc_competency', 'CBC Competency-Based'),
        ('cbc_points', 'CBC Points System'),
        ('8_4_4_grading', '8-4-4 Grading'),
        ('percentage', 'Percentage System'),
        ('letter_grade', 'Letter Grades (A-F)'),
        ('ib_1_7', 'IB 1-7 Scale'),
        ('igcse_a_star_g', 'IGCSE A*-G'),
        ('gpa_4_0', 'GPA 4.0 Scale'),
        ('gpa_5_0', 'GPA 5.0 Scale'),
        ('descriptive', 'Descriptive Assessment'),
        ('mixed', 'Mixed System'),
    ]
    
    # Term Structure Choices
    TERM_STRUCTURES = [
        ('three_terms', '3 Terms (Trimester)'),
        ('two_terms', '2 Terms (Semester)'),
        ('four_terms', '4 Terms (Quarter)'),
        ('six_terms', '6 Terms (Hexamester)'),
        ('american_quarters', 'American 4 Quarters'),
        ('ib_sessions', 'IB Sessions'),
        ('continuous', 'Continuous Assessment'),
    ]
    
    # Language Mode Choices
    LANGUAGE_MODE = [
        ('english', 'English Medium'),
        ('bilingual', 'Bilingual'),
        ('vernacular', 'Vernacular Medium'),
        ('french', 'French Medium'),
        ('arabic', 'Arabic Medium'),
        ('multilingual', 'Multilingual'),
    ]
    
    # Assessment Model Choices
    ASSESSMENT_MODELS = [
        ('cbc_continuous', 'CBC Continuous Assessment'),
        ('exam_focused', 'Exam-Focused'),
        ('portfolio_based', 'Portfolio-Based'),
        ('project_based', 'Project-Based'),
        ('competency_based', 'Competency-Based'),
        ('mixed_assessment', 'Mixed Assessment'),
    ]
    
    # External Exam Choices
    EXTERNAL_EXAMS = [
        ('kpsea_kjsea_kcse', 'KPSEA + KJSEA + KCSE (Kenya CBC)'),
        ('knec_8_4_4', 'KCPE + KCSE (Kenya 8-4-4)'),
        ('igcse_exams', 'Cambridge IGCSE Exams'),
        ('ib_exams', 'IB Examinations'),
        ('wassce', 'WASSCE (West Africa)'),
        ('neco', 'NECO (Nigeria)'),
        ('psle', 'PSLE (Tanzania)'),
        ('uce_uce', 'UCE + UACE (Uganda)'),
        ('sat_act', 'SAT/ACT (American)'),
        ('none', 'No External Exams'),
        ('custom', 'Custom Exam Schedule'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Academic Year Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Year Code"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_current = models.BooleanField(default=False, verbose_name=_("Current Year"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Curriculum System Configuration
    curriculum_system = models.CharField(
        max_length=30,
        choices=CURRICULUM_SYSTEMS,
        default='cbc_kenya',
        verbose_name=_("Curriculum System")
    )
    
    # Academic Structure Configuration
    academic_structure = models.CharField(
        max_length=30,
        choices=ACADEMIC_STRUCTURES,
        default='cbc_2_6_3_3',
        verbose_name=_("Academic Structure")
    )
    
    # Grading System Configuration
    grading_system = models.CharField(
        max_length=30,
        choices=GRADING_SYSTEMS,
        default='cbc_competency',
        verbose_name=_("Grading System")
    )
    
    # Term Structure
    term_structure = models.CharField(
        max_length=30,
        choices=TERM_STRUCTURES,
        default='three_terms',
        verbose_name=_("Term Structure")
    )
    
    total_terms = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text=_("Total number of terms in this academic year"),
        verbose_name=_("Total Terms")
    )
    
    # Language Configuration
    language_mode = models.CharField(
        max_length=20,
        choices=LANGUAGE_MODE,
        default='english',
        verbose_name=_("Language of Instruction")
    )
    
    additional_languages = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Additional languages taught"),
        verbose_name=_("Additional Languages")
    )
    
    # Assessment Configuration
    assessment_model = models.CharField(
        max_length=30,
        choices=ASSESSMENT_MODELS,
        default='cbc_continuous',
        verbose_name=_("Assessment Model")
    )
    
    # National/External Exam Configuration
    external_exams = models.CharField(
        max_length=30,
        choices=EXTERNAL_EXAMS,
        default='kpsea_kjsea_kcse',
        verbose_name=_("External Examinations")
    )
    
    # Financial Configuration
    fee_structure = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Fee structure configuration for this academic year"),
        verbose_name=_("Fee Structure")
    )
    
    currency = models.CharField(
        max_length=3,
        default='KES',
        help_text=_("Currency code (ISO 4217)"),
        verbose_name=_("Currency")
    )
    
    # Academic Calendar Configuration
    important_dates = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Important academic dates and deadlines"),
        verbose_name=_("Important Dates")
    )
    
    holiday_calendar = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Holiday calendar configuration"),
        verbose_name=_("Holiday Calendar")
    )
    
    # CBC-Specific Configuration
    cbc_configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("CBC-specific configuration"),
        verbose_name=_("CBC Configuration")
    )
    
    # IB/IGCSE Specific Configuration
    international_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("International curriculum configuration"),
        verbose_name=_("International Config")
    )
    
    # Reporting Configuration
    report_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Report card and transcript configuration"),
        verbose_name=_("Report Configuration")
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata for the academic year"),
        verbose_name=_("Metadata")
    )
    
    # Status Flags
    is_configured = models.BooleanField(default=False, verbose_name=_("Is Configured"))
    is_locked = models.BooleanField(default=False, verbose_name=_("Is Locked"))
    allow_admissions = models.BooleanField(default=True, verbose_name=_("Allow Admissions"))
    allow_assessments = models.BooleanField(default=True, verbose_name=_("Allow Assessments"))
    allow_transcripts = models.BooleanField(default=True, verbose_name=_("Allow Transcripts"))

    objects = AcademicYearManager()

    class Meta:
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_current']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['code']),
            models.Index(fields=['curriculum_system']),
            models.Index(fields=['academic_structure']),
            models.Index(fields=['is_configured']),
            models.Index(fields=['is_locked']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['is_current'],
                condition=Q(is_current=True),
                name='unique_current_academic_year'
            ),
            models.CheckConstraint(
                check=Q(end_date__gt=F('start_date')),
                name='end_date_after_start_date'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.get_curriculum_system_display()}"

    def save(self, *args, **kwargs):
        """Ensure only one academic year is marked as current and generate code."""
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
            cache.delete('current_academic_year')
        
        if not self.code and self.name:
            year_part = ''.join(filter(str.isdigit, self.name))
            self.code = f"AY{year_part}" if year_part else f"AY{self.start_date.year}"
        
        # Auto-configure based on curriculum system
        if not self.is_configured:
            self.auto_configure_curriculum()
        
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate academic year dates and configuration."""
        errors = {}
        
        # Date validation
        if self.start_date >= self.end_date:
            errors['end_date'] = _("End date must be after start date")
        
        # Date range validation (reasonable academic year)
        if (self.end_date - self.start_date).days > 400:
            errors['end_date'] = _("Academic year duration should not exceed 400 days")
        
        if (self.end_date - self.start_date).days < 180:
            errors['end_date'] = _("Academic year should be at least 180 days")
        
        # Check for overlapping academic years
        overlapping_years = AcademicYear.objects.filter(
            Q(start_date__lte=self.end_date, end_date__gte=self.start_date)
        ).exclude(pk=self.pk)
        
        if overlapping_years.exists():
            errors['start_date'] = _("Academic year dates overlap with existing academic year")
            errors['end_date'] = _("Academic year dates overlap with existing academic year")
        
        # Curriculum-specific validation
        if self.curriculum_system == 'cbc_kenya' and not self.cbc_configuration:
            errors['cbc_configuration'] = _("CBC configuration is required for Kenya CBC system")
        
        if errors:
            raise ValidationError(errors)

    def auto_configure_curriculum(self):
        """Auto-configure settings based on selected curriculum system."""
        config_map = {
            'cbc_kenya': {
                'academic_structure': 'cbc_2_6_3_3',
                'grading_system': 'cbc_competency',
                'term_structure': 'three_terms',
                'assessment_model': 'cbc_continuous',
                'external_exams': 'kpsea_kjsea_kcse',
                'cbc_configuration': self.get_default_cbc_config(),
            },
            '8-4-4_kenya': {
                'academic_structure': '8_4_4',
                'grading_system': '8_4_4_grading',
                'term_structure': 'three_terms',
                'assessment_model': 'exam_focused',
                'external_exams': 'knec_8_4_4',
            },
            'igcse': {
                'academic_structure': 'igcse_a_level',
                'grading_system': 'igcse_a_star_g',
                'term_structure': 'two_terms',
                'assessment_model': 'exam_focused',
                'external_exams': 'igcse_exams',
                'international_config': self.get_default_igcse_config(),
            },
            'ib': {
                'academic_structure': 'ib_pyp_myp_dp',
                'grading_system': 'ib_1_7',
                'term_structure': 'ib_sessions',
                'assessment_model': 'portfolio_based',
                'external_exams': 'ib_exams',
                'international_config': self.get_default_ib_config(),
            },
            'american': {
                'academic_structure': '5_3_4',
                'grading_system': 'gpa_4_0',
                'term_structure': 'american_quarters',
                'assessment_model': 'mixed_assessment',
                'external_exams': 'sat_act',
            },
            'nigeria_bec': {
                'academic_structure': '6_3_3_4',
                'grading_system': 'percentage',
                'term_structure': 'three_terms',
                'assessment_model': 'exam_focused',
                'external_exams': 'wassce',
            },
        }
        
        if self.curriculum_system in config_map:
            config = config_map[self.curriculum_system]
            for key, value in config.items():
                if hasattr(self, key) and not getattr(self, key):
                    setattr(self, key, value)
            
            self.is_configured = True

    def get_default_cbc_config(self):
        """Get default CBC configuration."""
        return {
            'pathways': ['stem', 'social_sciences', 'arts_sports'],
            'assessment_windows': {
                'kpsea': {'grade': 6, 'month': 'November'},
                'kjsea': {'grade': 9, 'month': 'October'},
                'kcse': {'grade': 12, 'month': 'November'},
            },
            'competency_areas': [
                'communication',
                'critical_thinking',
                'creativity',
                'citizenship',
                'digital_literacy',
                'learning_to_learn',
                'self_efficacy',
            ],
            'portfolio_required': True,
            'community_service_hours': 40,
            'parental_engagement_required': True,
        }

    def get_default_igcse_config(self):
        """Get default IGCSE configuration."""
        return {
            'exam_series': ['march', 'june', 'november'],
            'core_subjects': ['english', 'mathematics', 'sciences'],
            'extended_subjects': [],
            'grading_scale': 'A*-G',
            'coursework_percentage': 20,
            'practical_percentage': 30,
        }

    def get_default_ib_config(self):
        """Get default IB configuration."""
        return {
            'programme': 'diploma',
            'core_components': ['tok', 'ee', 'cas'],
            'subject_groups': 6,
            'minimum_hl': 3,
            'cas_hours': 150,
            'grading_scale': '1-7',
        }

    # ============ PROPERTIES ============

    @property
    def is_cbc(self):
        """Check if this academic year uses CBC system."""
        return self.curriculum_system == 'cbc_kenya'

    @property
    def is_international(self):
        """Check if this academic year uses international curriculum."""
        international_curriculums = ['igcse', 'ib', 'american', 'british']
        return self.curriculum_system in international_curriculums

    @property
    def is_african(self):
        """Check if this academic year uses African curriculum."""
        african_curriculums = [
            'cbc_kenya', '8-4-4_kenya', 'nigeria_bec', 
            'south_africa_caps', 'uganda_competency', 'tanzania_competency'
        ]
        return self.curriculum_system in african_curriculums

    @property
    def is_currently_active(self):
        """Check if current date is within academic year."""
        if not self.start_date or not self.end_date:
            return False
        
        try:
            today = timezone.now().date()
            return self.start_date <= today <= self.end_date
        except (TypeError, AttributeError):
            return False

    @property
    def duration_days(self):
        """Calculate academic year duration in days."""
        if self.start_date and self.end_date:
            try:
                return (self.end_date - self.start_date).days + 1
            except (TypeError, AttributeError):
                return 0
        return 0

    @property
    def progress_percentage(self):
        """Calculate progress through the academic year."""
        if not self.start_date or not self.end_date:
            return 0
        
        try:
            today = timezone.now().date()
            
            if not self.is_currently_active:
                return 100 if today > self.end_date else 0
            
            total_days = self.duration_days
            if total_days == 0:
                return 0
            
            days_passed = (today - self.start_date).days
            return min(100, max(0, (days_passed / total_days) * 100))
        except (TypeError, AttributeError):
            return 0

    @property
    def status(self):
        """Get academic year status."""
        if not self.start_date or not self.end_date:
            return "upcoming"
        
        try:
            today = timezone.now().date()
            if self.is_current:
                return "current"
            elif today < self.start_date:
                return "upcoming"
            elif self.start_date <= today <= self.end_date:
                return "active"
            else:
                return "completed"
        except (TypeError, AttributeError):
            return "upcoming"

    @property
    def curriculum_info(self):
        """Get comprehensive curriculum information."""
        return {
            'system': self.get_curriculum_system_display(),
            'structure': self.get_academic_structure_display(),
            'grading': self.get_grading_system_display(),
            'terms': self.get_term_structure_display(),
            'assessment': self.get_assessment_model_display(),
            'exams': self.get_external_exams_display(),
            'language': self.get_language_mode_display(),
            'is_cbc': self.is_cbc,
            'is_international': self.is_international,
            'is_african': self.is_african,
        }

    # ============ METHODS ============

    def get_statistics(self):
        """Get academic year statistics."""
        try:
            stats = {
                'total_students': StudentEnrollment.objects.filter(
                    academic_year=self,
                    status='active'
                ).count(),
                'total_teachers': TeacherProfile.objects.filter(is_active=True).count(),
                'total_classes': self.classes.count(),
                'total_subjects': Subject.objects.filter(is_active=True).count(),
            }
            
            # Add curriculum-specific statistics
            if self.is_cbc:
                stats.update({
                    'cbc_pathways': len(self.cbc_configuration.get('pathways', [])),
                    'portfolio_students': self._get_portfolio_students_count(),
                })
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def _get_portfolio_students_count(self):
        """Get count of students with portfolios (for CBC)."""
        try:
            from .models import CBCPortfolio
            return CBCPortfolio.objects.filter(
                academic_year=self,
                is_complete=True
            ).values('student').distinct().count()
        except Exception:
            return 0

    def get_current_term(self):
        """Get the current active term for this academic year."""
        return self.terms.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            is_active=True
        ).first()

    def generate_academic_calendar(self):
        """Generate academic calendar for the year."""
        calendar = {
            'academic_year': self.name,
            'curriculum': self.curriculum_info,
            'dates': {
                'start': self.start_date,
                'end': self.end_date,
                'duration_days': self.duration_days,
            },
            'terms': [],
            'important_dates': self.important_dates,
            'holidays': self.holiday_calendar,
        }
        
        for term in self.terms.all():
            term_data = {
                'name': term.get_name_display(),
                'start_date': term.start_date,
                'end_date': term.end_date,
                'duration_weeks': term.teaching_weeks,
                'holidays': term.holidays,
                'assessment_periods': term.assessment_periods
            }
            calendar['terms'].append(term_data)
        
        # Add curriculum-specific events
        if self.is_cbc:
            calendar['cbc_assessment_windows'] = self.cbc_configuration.get('assessment_windows', {})
        
        return calendar

    def get_curriculum_requirements(self):
        """Get curriculum-specific requirements."""
        requirements = {
            'general': {
                'attendance_rate': 80,
                'passing_grade': 40,
                'min_subjects': 8,
                'max_subjects': 14,
            }
        }
        
        if self.is_cbc:
            requirements['cbc'] = {
                'portfolio_completion': True,
                'community_service_hours': 40,
                'practical_assessment_weight': 40,
                'parent_engagement_required': True,
            }
        elif self.curriculum_system == 'ib':
            requirements['ib'] = {
                'cas_hours': 150,
                'tok_essay': True,
                'extended_essay': True,
                'hl_subjects': 3,
                'sl_subjects': 3,
            }
        elif self.curriculum_system == 'igcse':
            requirements['igcse'] = {
                'core_subjects': 3,
                'extended_subjects': 4,
                'coursework_percentage': 20,
                'practical_percentage': 30,
            }
        
        return requirements

    def validate_configuration(self):
        """Validate the academic year configuration."""
        errors = []
        
        if not self.start_date or not self.end_date:
            errors.append("Start and end dates are required")
        
        if self.curriculum_system == 'cbc_kenya' and not self.cbc_configuration:
            errors.append("CBC configuration is required for Kenya CBC system")
        
        if self.curriculum_system in ['igcse', 'ib'] and not self.international_config:
            errors.append(f"Configuration required for {self.get_curriculum_system_display()}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': self.get_configuration_warnings(),
        }

    def get_configuration_warnings(self):
        """Get configuration warnings."""
        warnings = []
        
        if self.duration_days < 200:
            warnings.append("Academic year duration is less than 200 days")
        
        if not self.important_dates:
            warnings.append("No important dates configured")
        
        if self.allow_admissions and self.is_locked:
            warnings.append("Admissions allowed but academic year is locked")
        
        return warnings

    def lock_academic_year(self):
        """Lock the academic year to prevent changes."""
        if not self.is_locked:
            self.is_locked = True
            self.save()
            return True
        return False

    def unlock_academic_year(self):
        """Unlock the academic year for changes."""
        if self.is_locked:
            self.is_locked = False
            self.save()
            return True
        return False

    def get_term_structure_info(self):
        """Get detailed term structure information."""
        term_info = {
            'structure': self.get_term_structure_display(),
            'total_terms': self.total_terms,
            'estimated_weeks_per_term': self.duration_days // (7 * self.total_terms) if self.total_terms > 0 else 0,
        }
        
        if self.term_structure == 'three_terms':
            term_info['term_names'] = ['Term 1', 'Term 2', 'Term 3']
        elif self.term_structure == 'two_terms':
            term_info['term_names'] = ['Semester 1', 'Semester 2']
        elif self.term_structure == 'four_terms':
            term_info['term_names'] = ['Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4']
        
        return term_info

    def get_assessment_schedule(self):
        """Get assessment schedule for the academic year."""
        schedule = {
            'internal_assessments': [],
            'external_exams': [],
        }
        
        if self.external_exams != 'none':
            schedule['external_exams'] = self.get_external_exam_schedule()
        
        # Add term assessments
        for term in self.terms.all():
            if term.assessment_periods:
                schedule['internal_assessments'].extend(term.assessment_periods)
        
        return schedule

    def get_external_exam_schedule(self):
        """Get external exam schedule based on curriculum."""
        exam_schedules = {
            'kpsea_kjsea_kcse': [
                {'exam': 'KPSEA', 'grade': 6, 'month': 'November'},
                {'exam': 'KJSEA', 'grade': 9, 'month': 'October'},
                {'exam': 'KCSE', 'grade': 12, 'month': 'November'},
            ],
            'knec_8_4_4': [
                {'exam': 'KCPE', 'grade': 8, 'month': 'November'},
                {'exam': 'KCSE', 'grade': 12, 'month': 'November'},
            ],
            'igcse_exams': [
                {'exam': 'IGCSE', 'months': ['May/June', 'October/November']},
            ],
            'wassce': [
                {'exam': 'WASSCE', 'month': 'May/June'},
            ],
        }
        
        return exam_schedules.get(self.external_exams, [])


class AcademicTerm(BaseAcademicModel):
    """Enhanced Academic term management within an academic year."""
    
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='terms',
        verbose_name=_("Academic Year")
    )
    name = models.CharField(
        max_length=20, 
        choices=TERM_CHOICES,
        verbose_name=_("Term Name")
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_current = models.BooleanField(default=False, verbose_name=_("Current Term"))
    
    # Term configuration
    term_order = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text=_("Order of term within academic year"),
        verbose_name=_("Term Order")
    )
    
    # Academic periods
    assessment_periods = models.JSONField(
        default=list, 
        help_text=_("Assessment periods within the term"),
        verbose_name=_("Assessment Periods")
    )
    holidays = models.JSONField(
        default=list, 
        help_text=_("Holidays and breaks during the term"),
        verbose_name=_("Holidays")
    )
    important_dates = models.JSONField(
        default=list,
        help_text=_("Important academic dates and deadlines"),
        verbose_name=_("Important Dates")
    )
    
    # Financial information
    term_fees = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Term-specific fee structure"),
        verbose_name=_("Term Fees")
    )

    objects = AcademicTermManager()

    class Meta:
        verbose_name = _("Academic Term")
        verbose_name_plural = _("Academic Terms")
        unique_together = ['academic_year', 'name']
        ordering = ['academic_year', 'term_order']
        indexes = [
            models.Index(fields=['academic_year', 'name']),
            models.Index(fields=['is_current']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['term_order']),
        ]

    def __str__(self):
        return f"{self.academic_year.name} - {self.get_name_display()}"

    def save(self, *args, **kwargs):
        """Ensure only one term is marked as current per academic year."""
        if self.is_current:
            AcademicTerm.objects.filter(
                academic_year=self.academic_year, 
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate term dates."""
        errors = {}
        
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            errors['end_date'] = _("End date must be after start date")
        
        if self.academic_year and self.start_date and self.end_date:
            if (self.start_date < self.academic_year.start_date or 
                self.end_date > self.academic_year.end_date):
                errors['start_date'] = _("Term dates must be within the academic year dates")
                errors['end_date'] = _("Term dates must be within the academic year dates")
        
        if self.academic_year and self.start_date and self.end_date:
            overlapping_terms = AcademicTerm.objects.filter(
                academic_year=self.academic_year
            ).filter(
                Q(start_date__lte=self.end_date, end_date__gte=self.start_date)
            ).exclude(pk=self.pk)
            
            if overlapping_terms.exists():
                errors['start_date'] = _("Term dates overlap with another term in the same academic year")
                errors['end_date'] = _("Term dates overlap with another term in the same academic year")
        
        if errors:
            raise ValidationError(errors)

    # ============ PROPERTIES ============

    @property
    def duration_days(self):
        """Calculate term duration in days."""
        if not self.start_date or not self.end_date:
            return 0
        try:
            return (self.end_date - self.start_date).days + 1
        except (TypeError, AttributeError):
            return 0

    @property
    def is_currently_active(self):
        """Check if term is currently active."""
        if not self.start_date or not self.end_date:
            return False
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def teaching_weeks(self):
        """Calculate actual teaching weeks excluding holidays."""
        if not self.start_date or not self.end_date:
            return 0
        
        total_days = self.duration_days
        if total_days == 0:
            return 0
            
        total_weeks = total_days // 7
        holiday_weeks = len(self.holidays) if self.holidays else 0
        return max(0, total_weeks - holiday_weeks)

    @property
    def progress_percentage(self):
        """Calculate progress through the term."""
        if not self.start_date or not self.end_date:
            return 0
            
        if not self.is_currently_active:
            if self.end_date and timezone.now().date() > self.end_date:
                return 100
            return 0
        
        total_days = self.duration_days
        if total_days == 0:
            return 0
        
        try:
            days_passed = (timezone.now().date() - self.start_date).days
            return min(100, max(0, (days_passed / total_days) * 100))
        except (TypeError, AttributeError):
            return 0

    @property
    def status(self):
        """Get term status."""
        if not self.start_date or not self.end_date:
            return "upcoming"
        
        today = timezone.now().date()
        if self.is_current:
            return "current"
        elif today < self.start_date:
            return "upcoming"
        elif self.start_date <= today <= self.end_date:
            return "active"
        else:
            return "completed"

    # ============ METHODS ============

    def get_academic_events(self):
        """Get all academic events for this term."""
        return self.academic_events.filter(is_active=True)

    def get_holidays_list(self):
        """Get formatted holidays list."""
        return self.holidays if self.holidays else []


class SubTopic(BaseAcademicModel):
    """Enhanced sub-topic model for detailed curriculum breakdown with CBC alignment."""
    
    # Basic Information
    topic = models.CharField(max_length=200, verbose_name=_("Main Topic"))
    name = models.CharField(max_length=200, verbose_name=_("Sub Topic Name"))
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    
    # Academic Information
    code = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_("Sub Topic Code")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    
    # CBC Alignment
    competency_alignment = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific competencies developed in this sub-topic"),
        verbose_name=_("Competency Alignment")
    )
    
    # Content Details
    learning_objectives = models.JSONField(
        default=list, 
        help_text=_("Specific learning objectives for this sub-topic"),
        verbose_name=_("Learning Objectives")
    )
    key_concepts = models.JSONField(
        default=list,
        help_text=_("Key concepts covered in this sub-topic"),
        verbose_name=_("Key Concepts")
    )
    skills_developed = models.JSONField(
        default=list,
        help_text=_("Skills developed through this sub-topic"),
        verbose_name=_("Skills Developed")
    )
    
    # Time Allocation
    estimated_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=2.0,
        help_text=_("Estimated teaching hours required"),
        verbose_name=_("Estimated Hours")
    )
    priority = models.CharField(
        max_length=15,
        choices=[
            ('high', 'High Priority'),
            ('medium', 'Medium Priority'),
            ('low', 'Low Priority'),
            ('core', 'Core Competency'),
            ('extension', 'Extension Activity'),
        ],
        default='medium',
        verbose_name=_("Priority")
    )
    
    # Resources
    teaching_resources = models.JSONField(
        default=list,
        help_text=_("Required teaching resources"),
        verbose_name=_("Teaching Resources")
    )
    assessment_methods = models.JSONField(
        default=list,
        help_text=_("Recommended assessment methods"),
        verbose_name=_("Assessment Methods")
    )
    
    # Differentiated Instruction
    differentiation_strategies = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Strategies for different learner types"),
        verbose_name=_("Differentiation Strategies")
    )
    
    # Project Integration
    project_connections = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Potential project connections"),
        verbose_name=_("Project Connections")
    )
    
    # Status and Tracking
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    completion_date = models.DateField(null=True, blank=True, verbose_name=_("Completion Date"))
    
    # Prerequisites
    prerequisite_topics = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        help_text=_("Prerequisite sub-topics"),
        verbose_name=_("Prerequisite Topics")
    )

    class Meta:
        verbose_name = _("Sub Topic")
        verbose_name_plural = _("Sub Topics")
        ordering = ['subject', 'topic', 'order', 'name']
        indexes = [
            models.Index(fields=['subject', 'topic']),
            models.Index(fields=['code']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['priority']),
            models.Index(fields=['subject', 'order']),
        ]

    def __str__(self):
        return f"{self.topic}: {self.name}"

    def save(self, *args, **kwargs):
        """Generate code if not provided and auto-align competencies."""
        if not self.code and self.name:
            # Generate a code from subject code and sub-topic name
            subject_code = self.subject.code if self.subject else 'GEN'
            clean_name = ''.join(c for c in self.name if c.isalnum()).upper()
            self.code = f"{subject_code}-{clean_name[:10]}" if clean_name else f"{subject_code}-ST{self.id}"
        
        # Auto-align competencies for CBC subjects
        if self.subject.is_cbc_subject and not self.competency_alignment:
            if self.subject.cbc_competency_area:
                self.competency_alignment = [self.subject.cbc_competency_area]
        
        super().save(*args, **kwargs)

    # ============ PROPERTIES ============

    @property
    def full_name(self):
        """Get full display name."""
        return f"{self.topic}: {self.name}"

    @property
    def estimated_periods(self):
        """Convert estimated hours to periods (assuming 40-minute periods)."""
        return int(self.estimated_hours * 60 / 40)

    @property
    def is_cbc_aligned(self):
        """Check if sub-topic is CBC aligned."""
        return bool(self.competency_alignment) or self.subject.is_cbc_subject

    @property
    def difficulty_assessment(self):
        """Assess difficulty based on various factors."""
        difficulty_score = 0
        
        if self.priority == 'high':
            difficulty_score += 2
        elif self.priority == 'core':
            difficulty_score += 3
        
        if self.estimated_hours > 3:
            difficulty_score += 1
        
        if self.project_connections:
            difficulty_score += 1
        
        # Map score to difficulty level
        if difficulty_score >= 3:
            return "Challenging"
        elif difficulty_score >= 2:
            return "Moderate"
        else:
            return "Basic"

    # ============ METHODS ============

    def get_related_lesson_plans(self):
        """Get lesson plans related to this sub-topic."""
        from .models import LessonPlan
        return LessonPlan.objects.filter(sub_topic=self)

    def mark_completed(self):
        """Mark sub-topic as completed."""
        self.is_completed = True
        self.completion_date = timezone.now().date()
        self.save()

    def get_competency_details(self):
        """Get detailed competency information."""
        if not self.competency_alignment:
            return None
        
        details = []
        for competency in self.competency_alignment:
            try:
                display_name = dict(self._meta.get_field('competency_alignment').choices).get(competency, competency)
                details.append({
                    'code': competency,
                    'name': display_name,
                    'description': self._get_competency_description(competency),
                })
            except (KeyError, ValueError):
                details.append({'code': competency, 'name': competency})
        
        return details

    def _get_competency_description(self, competency_code):
        """Get description for a competency code."""
        competency_descriptions = {
            'communication': "Ability to express ideas clearly and collaborate effectively",
            'critical_thinking': "Capacity to analyze, evaluate, and solve problems",
            'creativity': "Ability to generate innovative ideas and solutions",
            'citizenship': "Understanding of civic responsibilities and community engagement",
            'digital_literacy': "Proficiency in using digital tools and technologies",
            'learning_to_learn': "Skills for self-directed and lifelong learning",
            'self_efficacy': "Confidence in one's ability to accomplish tasks",
        }
        return competency_descriptions.get(competency_code, "")

    def get_differentiation_options(self, learner_type):
        """Get differentiation strategies for specific learner types."""
        strategies = self.differentiation_strategies.get(learner_type, [])
        
        if not strategies and self.subject.is_cbc_subject:
            # Provide default strategies for CBC
            default_strategies = {
                'slow_learner': [
                    "Break into smaller steps",
                    "Provide additional examples",
                    "Use visual aids",
                    "Allow extra time",
                ],
                'fast_learner': [
                    "Extension activities",
                    "Independent projects",
                    "Peer teaching opportunities",
                    "Advanced challenges",
                ],
                'special_needs': [
                    "Adapted materials",
                    "Assistive technology",
                    "Modified assessments",
                    "Individual support",
                ],
            }
            strategies = default_strategies.get(learner_type, [])
        
        return strategies

    def validate_prerequisites(self, student):
        """Check if student has completed prerequisite topics."""
        if not self.prerequisite_topics.exists():
            return True
        
        # Check if student has completed all prerequisites
        completed_topics = student.completed_subtopics.filter(
            sub_topic__in=self.prerequisite_topics.all()
        )
        return completed_topics.count() == self.prerequisite_topics.count()

    def get_resource_summary(self):
        """Get summary of required resources."""
        summary = {
            'total_resources': len(self.teaching_resources),
            'digital_resources': sum(1 for r in self.teaching_resources if r.get('type') == 'digital'),
            'physical_resources': sum(1 for r in self.teaching_resources if r.get('type') == 'physical'),
            'special_equipment': any(r.get('special') for r in self.teaching_resources),
        }
        return summary

    def create_lesson_template(self):
        """Create a lesson template based on this sub-topic."""
        template = {
            'topic': self.topic,
            'sub_topic': self.name,
            'duration_hours': float(self.estimated_hours),
            'learning_objectives': self.learning_objectives,
            'key_concepts': self.key_concepts,
            'activities': self._suggest_activities(),
            'assessment_methods': self.assessment_methods,
            'differentiation': self.differentiation_strategies,
            'resources': self.teaching_resources,
        }
        
        if self.project_connections:
            template['project_ideas'] = self.project_connections
        
        return template

    def _suggest_activities(self):
        """Suggest activities based on sub-topic content."""
        activities = []
        
        # Add competency-based activities for CBC
        if self.competency_alignment:
            for competency in self.competency_alignment:
                activity = {
                    'type': 'competency_development',
                    'competency': competency,
                    'description': f"Activity to develop {self._get_competency_description(competency)}",
                    'duration': '30 minutes',
                }
                activities.append(activity)
        
        # Add project-based activities
        if self.project_connections:
            activities.append({
                'type': 'project_work',
                'description': "Hands-on project work",
                'duration': f"{int(self.estimated_hours * 0.5)} hours",
            })
        
        # Add discussion/reflection activity
        activities.append({
            'type': 'discussion',
            'description': "Group discussion and reflection",
            'duration': '20 minutes',
        })
        
        return activities


class Class(BaseAcademicModel):
    """Enhanced Class management with comprehensive academic configuration and CBC support."""
    
    # Basic Information
    name = models.CharField(max_length=100, verbose_name=_("Class Name"))
    grade_level = models.CharField(
        max_length=20, 
        choices=GRADE_LEVEL_CHOICES,
        verbose_name=_("Grade Level")
    )
    section = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        verbose_name=_("Section")
    )
    stream = models.CharField(
        max_length=15, 
        choices=STREAM_CHOICES, 
        blank=True, 
        null=True,
        verbose_name=_("Stream")
    )
    room_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_("Room Number")
    )
    
    # Academic Context
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='classes',
        verbose_name=_("Academic Year")
    )
    
    class_teacher = models.ForeignKey(
        'teachers.TeacherProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_classes',
        verbose_name=_("Class Teacher")
    )
    
    # CBC-Specific Fields
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVELS,
        default='middle_school',
        verbose_name=_("Education Level")
    )
    
    cbc_pathway = models.CharField(
        max_length=20,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    senior_track = models.CharField(
        max_length=30,
        choices=SENIOR_SCHOOL_TRACKS,
        blank=True,
        null=True,
        verbose_name=_("Senior School Track")
    )
    
    # Curriculum Information
    primary_curriculum = models.CharField(
        max_length=20,
        choices=CURRICULUM_CHOICES,
        verbose_name=_("Primary Curriculum")
    )
    additional_curriculums = models.JSONField(
        default=list, 
        blank=True,
        verbose_name=_("Additional Curriculums")
    )
    
    # Class Configuration
    capacity = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("Capacity")
    )
    current_strength = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Current Strength")
    )
    
    # Schedule Information
    schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Class timetable/schedule"),
        verbose_name=_("Schedule")
    )
    
    # CBC Assessment Configuration
    portfolio_required = models.BooleanField(
        default=False,
        verbose_name=_("Portfolio Required"),
        help_text=_("Whether students need to maintain portfolios")
    )
    
    project_work_required = models.BooleanField(
        default=False,
        verbose_name=_("Project Work Required"),
        help_text=_("Whether project work is mandatory")
    )
    
    community_service_hours = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        help_text=_("Required community service hours per term"),
        verbose_name=_("Community Service Hours")
    )
    
    # Academic Configuration
    assessment_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Class-specific assessment configuration"),
        verbose_name=_("Assessment Configuration")
    )
    
    # Additional Information
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Description")
    )
    class_rules = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Class rules and expectations"),
        verbose_name=_("Class Rules")
    )
    class_color = models.CharField(
        max_length=7, 
        default='#3B82F6',
        help_text=_("Color code for class identification"),
        verbose_name=_("Class Color")
    )
    
    # Facilities Information
    facilities = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Available facilities for this class"),
        verbose_name=_("Facilities")
    )
    
    # Academic Performance Tracking
    average_performance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Average Performance")
    )
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Attendance Rate")
    )
    
    # Parent Engagement
    parent_engagement_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Engagement'),
            ('medium', 'Medium Engagement'),
            ('high', 'High Engagement'),
            ('structured', 'Structured Program'),
        ],
        default='medium',
        verbose_name=_("Parent Engagement Level")
    )
    
    # Technology Integration
    technology_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Technology'),
            ('intermediate', 'Intermediate Technology'),
            ('advanced', 'Advanced Technology'),
            ('digital_classroom', 'Digital Classroom'),
        ],
        default='basic',
        verbose_name=_("Technology Level")
    )
    
    # Special Programs
    special_programs = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Special programs for this class"),
        verbose_name=_("Special Programs")
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata for the class"),
        verbose_name=_("Metadata")
    )

    objects = ClassManager()

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
        unique_together = ['name', 'academic_year', 'section']
        ordering = ['academic_year', 'grade_level', 'section']
        indexes = [
            models.Index(fields=['academic_year', 'grade_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['stream']),
            models.Index(fields=['class_teacher']),
            models.Index(fields=['grade_level', 'section']),
            models.Index(fields=['education_level']),
            models.Index(fields=['cbc_pathway']),
            models.Index(fields=['senior_track']),
        ]

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        """Update current strength and auto-configure CBC settings."""
        # Update current strength based on enrollments
        if self.pk:
            try:
                from students.models import StudentEnrollment
                self.current_strength = StudentEnrollment.objects.filter(
                    class_enrolled=self, 
                    status='active'
                ).count()
            except ImportError:
                pass
        
        # Auto-configure CBC settings
        if not self.education_level:
            self.education_level = self._auto_determine_education_level()
        
        if self.academic_year.is_cbc and not self.portfolio_required:
            # Set portfolio requirements based on education level
            if self.education_level in ['middle_school', 'senior_school']:
                self.portfolio_required = True
        
        # Auto-set primary curriculum from academic year
        if not self.primary_curriculum:
            if self.academic_year.curriculum_system == 'cbc_kenya':
                self.primary_curriculum = 'cbc'
            elif self.academic_year.curriculum_system == '8-4-4_kenya':
                self.primary_curriculum = '8-4-4'
        
        self.clean()
        super().save(*args, **kwargs)

    def _auto_determine_education_level(self):
        """Auto-determine education level based on grade level."""
        grade_map = {
            'pre_primary_1': 'early_years',
            'pre_primary_2': 'early_years',
            'grade_1': 'early_years',
            'grade_2': 'early_years',
            'grade_3': 'early_years',
            'grade_4': 'middle_school',
            'grade_5': 'middle_school',
            'grade_6': 'middle_school',
            'grade_7': 'middle_school',
            'grade_8': 'middle_school',
            'grade_9': 'middle_school',
            'grade_10': 'senior_school',
            'grade_11': 'senior_school',
            'grade_12': 'senior_school',
        }
        return grade_map.get(self.grade_level, 'middle_school')

    def clean(self):
        """Validate class data."""
        errors = {}
        
        # Section validation
        if self.section and not self.section.isalnum():
            errors['section'] = _("Section must be alphanumeric")
        
        # Capacity validation
        if self.current_strength > self.capacity:
            errors['current_strength'] = _("Current strength cannot exceed capacity")
        
        # CBC-specific validation
        if self.academic_year.is_cbc:
            # Validate pathway for senior school
            if self.education_level == 'senior_school' and not self.cbc_pathway:
                errors['cbc_pathway'] = _("CBC pathway is required for Senior School classes")
            
            # Validate senior track for pathways
            if self.cbc_pathway and not self.senior_track:
                errors['senior_track'] = _("Senior track is required when pathway is specified")
        
        # Grade level validation for senior tracks
        if self.senior_track and self.education_level != 'senior_school':
            errors['senior_track'] = _("Senior tracks are only applicable to Senior School classes")
        
        if errors:
            raise ValidationError(errors)

    # ============ PROPERTIES ============

    @property
    def display_name(self):
        """Get formatted class name with section and stream."""
        parts = [self.name]
        if self.section:
            parts.append(f"Section {self.section}")
        if self.stream:
            parts.append(f"({self.get_stream_display()})")
        
        # Add CBC pathway if available
        if self.cbc_pathway:
            parts.append(f"- {self.get_cbc_pathway_display()}")
        
        return ' '.join(parts)

    @property
    def available_seats(self):
        """Get number of available seats."""
        return max(0, self.capacity - self.current_strength)

    @property
    def is_full(self):
        """Check if class is full."""
        return self.current_strength >= self.capacity

    @property
    def occupancy_rate(self):
        """Calculate class occupancy rate."""
        if self.capacity == 0:
            return 0
        return round((self.current_strength / self.capacity) * 100, 2)

    @property
    def is_cbc_class(self):
        """Check if this is a CBC class."""
        return self.academic_year.is_cbc or self.primary_curriculum == 'cbc'

    @property
    def cbc_info(self):
        """Get CBC-specific information for this class."""
        info = {
            'education_level': self.get_education_level_display(),
            'is_senior_school': self.education_level == 'senior_school',
            'requires_portfolio': self.portfolio_required,
            'requires_project': self.project_work_required,
            'community_service_hours': self.community_service_hours,
        }
        
        if self.cbc_pathway:
            info['pathway'] = self.get_cbc_pathway_display()
        if self.senior_track:
            info['senior_track'] = self.get_senior_track_display()
            
        return info

    @property
    def class_code(self):
        """Generate class code."""
        year_code = self.academic_year.code[:4] if self.academic_year.code else 'AY'
        grade_code = self.grade_level.split('_')[-1].upper() if '_' in self.grade_level else self.grade_level[:3].upper()
        section_code = self.section.upper() if self.section else 'A'
        return f"{year_code}{grade_code}{section_code}"

    @property
    def academic_info(self):
        """Get comprehensive academic information."""
        return {
            'grade_level': self.get_grade_level_display(),
            'education_level': self.get_education_level_display(),
            'curriculum': self.get_primary_curriculum_display(),
            'is_cbc': self.is_cbc_class,
            'academic_year': self.academic_year.name,
            'term': self.get_current_term_info(),
        }

    # ============ STUDENT RELATED METHODS ============

    @property
    def student_list(self):
        """Get list of students in this class."""
        try:
            from students.models import StudentEnrollment
            return StudentEnrollment.objects.filter(
                class_enrolled=self,
                status='active'
            ).select_related('student__user').order_by('roll_number')
        except ImportError:
            return StudentEnrollment.objects.none()

    def get_students_by_gender(self):
        """Get student count by gender."""
        try:
            from students.models import StudentProfile
            student_ids = self.student_list.values_list('student_id', flat=True)
            return StudentProfile.objects.filter(
                id__in=student_ids
            ).values('gender').annotate(count=models.Count('id'))
        except ImportError:
            return []

    def get_students_by_pathway(self):
        """Get student distribution by CBC pathway (for Senior School)."""
        if not self.is_cbc_class or self.education_level != 'senior_school':
            return {}
        
        try:
            from .models import PathwaySelection
            student_ids = self.student_list.values_list('student_id', flat=True)
            selections = PathwaySelection.objects.filter(
                student_id__in=student_ids,
                academic_year=self.academic_year,
                is_approved=True
            )
            
            distribution = {}
            for selection in selections:
                pathway = selection.get_preferred_pathway_display()
                distribution[pathway] = distribution.get(pathway, 0) + 1
            
            return distribution
        except ImportError:
            return {}

    def add_student(self, student, roll_number=None):
        """Add a student to this class."""
        try:
            from students.models import StudentEnrollment
            
            if self.is_full:
                raise ValidationError(_("Class is full. Cannot add more students."))
            
            enrollment, created = StudentEnrollment.objects.get_or_create(
                student=student,
                academic_year=self.academic_year,
                defaults={
                    'class_enrolled': self,
                    'roll_number': roll_number or self._get_next_roll_number(),
                    'status': 'active',
                }
            )
            
            if not created:
                enrollment.class_enrolled = self
                if roll_number:
                    enrollment.roll_number = roll_number
                enrollment.save()
            
            # Update current strength
            self.current_strength = StudentEnrollment.objects.filter(
                class_enrolled=self, 
                status='active'
            ).count()
            self.save()
            
            return enrollment
        except ImportError:
            return None

    def _get_next_roll_number(self):
        """Get next available roll number."""
        from students.models import StudentEnrollment
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=self,
            academic_year=self.academic_year
        ).exclude(roll_number=None).order_by('-roll_number')
        
        if enrollments.exists():
            return enrollments.first().roll_number + 1
        return 1

    def remove_student(self, student):
        """Remove a student from this class."""
        try:
            from students.models import StudentEnrollment
            
            enrollment = StudentEnrollment.objects.filter(
                student=student,
                class_enrolled=self,
                academic_year=self.academic_year,
                status='active'
            ).first()
            
            if enrollment:
                enrollment.status = 'transferred'
                enrollment.save()
                
                # Update current strength
                self.current_strength = StudentEnrollment.objects.filter(
                    class_enrolled=self, 
                    status='active'
                ).count()
                self.save()
            
            return enrollment
        except ImportError:
            return None

    # ============ SUBJECT RELATED METHODS ============

    def get_subjects(self):
        """Get subjects taught in this class."""
        assignments = self.subject_assignments.filter(is_active=True)
        return Subject.objects.filter(
            id__in=assignments.values('subject')
        ).distinct()

    def get_subjects_by_category(self):
        """Get subjects grouped by category."""
        subjects = self.get_subjects()
        categories = {}
        
        for subject in subjects:
            category = subject.get_category_display()
            if category not in categories:
                categories[category] = []
            categories[category].append(subject)
        
        return categories

    def get_cbc_core_subjects(self):
        """Get CBC core subjects for this class."""
        subjects = self.get_subjects()
        return subjects.filter(is_cbc_core=True)

    def get_subjects_by_pathway(self):
        """Get subjects by CBC pathway alignment."""
        if not self.cbc_pathway:
            return {}
        
        subjects = self.get_subjects()
        pathway_subjects = {
            'core': subjects.filter(cbc_pathway=self.cbc_pathway, is_cbc_core=True),
            'elective': subjects.filter(cbc_pathway=self.cbc_pathway, is_cbc_core=False),
            'general': subjects.filter(cbc_pathway__isnull=True),
        }
        
        return pathway_subjects

    def assign_subject(self, subject, teacher, periods_per_week=5):
        """Assign a subject to this class with a teacher."""
        try:
            from .models import SubjectAssignment
            
            assignment, created = SubjectAssignment.objects.get_or_create(
                subject=subject,
                teacher=teacher,
                class_assigned=self,
                academic_year=self.academic_year,
                defaults={
                    'periods_per_week': periods_per_week,
                }
            )
            
            if not created:
                assignment.periods_per_week = periods_per_week
                assignment.save()
            
            return assignment
        except ImportError:
            return None

    # ============ TEACHER RELATED METHODS ============

    def get_teachers(self):
        """Get teachers assigned to this class."""
        try:
            from teachers.models import TeacherProfile
            assignments = self.subject_assignments.filter(is_active=True)
            teacher_ids = assignments.values('teacher').distinct()
            return TeacherProfile.objects.filter(id__in=teacher_ids).distinct()
        except ImportError:
            return TeacherProfile.objects.none()

    def get_teachers_by_subject(self):
        """Get teachers grouped by subject."""
        teachers_by_subject = {}
        
        for assignment in self.subject_assignments.filter(is_active=True):
            subject_name = assignment.subject.name
            if subject_name not in teachers_by_subject:
                teachers_by_subject[subject_name] = []
            
            teachers_by_subject[subject_name].append({
                'teacher': assignment.teacher,
                'periods_per_week': assignment.periods_per_week,
                'is_class_teacher': assignment.is_class_teacher,
            })
        
        return teachers_by_subject

    def set_class_teacher(self, teacher):
        """Set or update class teacher."""
        try:
            # Remove class teacher flag from all assignments
            self.subject_assignments.filter(is_class_teacher=True).update(is_class_teacher=False)
            
            # Find or create assignment for this teacher
            assignment = self.subject_assignments.filter(
                teacher=teacher,
                is_active=True
            ).first()
            
            if assignment:
                assignment.is_class_teacher = True
                assignment.save()
            
            self.class_teacher = teacher
            self.save()
            
            return True
        except Exception as e:
            logger.error(f"Error setting class teacher: {e}")
            return False

    # ============ ASSESSMENT RELATED METHODS ============

    def get_assessment_config(self):
        """Get assessment configuration for this class."""
        default_config = {
            'continuous_assessment_weight': 40,
            'term_exam_weight': 60,
            'practical_weight': self._get_average_practical_weight(),
            'project_required': self.project_work_required,
            'portfolio_required': self.portfolio_required,
        }
        
        if self.assessment_config:
            default_config.update(self.assessment_config)
        
        return default_config

    def _get_average_practical_weight(self):
        """Calculate average practical weight for subjects in this class."""
        subjects = self.get_subjects()
        if not subjects.exists():
            return 0
        
        total_weight = sum(subject.practical_weight for subject in subjects)
        return total_weight / subjects.count()

    def get_assessment_schedule(self, term=None):
        """Get assessment schedule for this class."""
        try:
            from .models import AcademicTerm
            current_term = term or AcademicTerm.objects.filter(
                academic_year=self.academic_year,
                is_current=True
            ).first()
            
            if not current_term:
                return []
            
            # Get assessments from the syllabus
            schedule = []
            for subject in self.get_subjects():
                subject_assessments = subject.assessment_methods or []
                for assessment in subject_assessments:
                    schedule.append({
                        'subject': subject.name,
                        'type': assessment.get('type', 'assessment'),
                        'description': assessment.get('description', ''),
                        'weight': assessment.get('weight', 0),
                        'due_date': assessment.get('due_date'),
                    })
            
            return schedule
        except ImportError:
            return []

    # ============ TIMETABLE/SCHEDULE METHODS ============

    def get_timetable(self):
        """Get class timetable."""
        if self.schedule:
            return self.schedule
        
        # Generate default timetable if not set
        return self._generate_default_timetable()

    def _generate_default_timetable(self):
        """Generate default timetable based on grade level."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        timetable = {}
        for day in days:
            timetable[day] = {}
            for period in periods:
                timetable[day][period] = {
                    'subject': None,
                    'teacher': None,
                    'room': self.room_number or 'TBD',
                    'type': 'theory',
                }
        
        return timetable

    def update_schedule(self, day, period, subject, teacher, room=None, type='theory'):
        """Update schedule for specific day and period."""
        if not self.schedule:
            self.schedule = self._generate_default_timetable()
        
        if day in self.schedule and period in self.schedule[day]:
            self.schedule[day][period] = {
                'subject': subject.name if hasattr(subject, 'name') else subject,
                'teacher': teacher.full_name if hasattr(teacher, 'full_name') else teacher,
                'room': room or self.room_number or 'TBD',
                'type': type,
            }
            
            self.save()
            return True
        
        return False

    # ============ PERFORMANCE TRACKING METHODS ============

    def update_performance_metrics(self):
        """Update performance metrics for this class."""
        try:
            from grading.models import Grade
            
            # Calculate average performance
            grades = Grade.objects.filter(
                enrollment__class_enrolled=self,
                enrollment__status='active',
                academic_year=self.academic_year,
                is_active=True
            )
            
            if grades.exists():
                self.average_performance = grades.aggregate(
                    avg_score=models.Avg('score')
                )['avg_score']
            
            # Calculate attendance rate
            from attendance.models import StudentAttendance
            attendance_records = StudentAttendance.objects.filter(
                enrollment__class_enrolled=self,
                enrollment__status='active',
                academic_year=self.academic_year
            )
            
            if attendance_records.exists():
                present_count = attendance_records.filter(status='present').count()
                total_count = attendance_records.count()
                self.attendance_rate = (present_count / total_count) * 100 if total_count > 0 else 0
            
            self.save()
            return True
        except ImportError:
            return False

    def get_performance_trend(self, term_count=3):
        """Get performance trend over multiple terms."""
        try:
            from grading.models import Grade
            from .models import AcademicTerm
            
            terms = AcademicTerm.objects.filter(
                academic_year=self.academic_year
            ).order_by('-term_order')[:term_count]
            
            trend_data = []
            for term in terms:
                grades = Grade.objects.filter(
                    enrollment__class_enrolled=self,
                    academic_year=self.academic_year,
                    term=term,
                    is_active=True
                )
                
                if grades.exists():
                    avg_score = grades.aggregate(avg=models.Avg('score'))['avg']
                    trend_data.append({
                        'term': term.get_name_display(),
                        'average_score': avg_score,
                        'term_order': term.term_order,
                    })
            
            return sorted(trend_data, key=lambda x: x['term_order'])
        except ImportError:
            return []

    # ============ CBC SPECIFIC METHODS ============

    def get_cbc_requirements(self):
        """Get CBC requirements for this class."""
        if not self.is_cbc_class:
            return None
        
        requirements = {
            'education_level': self.education_level,
            'portfolio_required': self.portfolio_required,
            'project_work_required': self.project_work_required,
            'community_service_hours': self.community_service_hours,
            'parent_engagement_level': self.parent_engagement_level,
        }
        
        if self.cbc_pathway:
            requirements['pathway'] = self.cbc_pathway
            requirements['pathway_display'] = self.get_cbc_pathway_display()
        
        if self.senior_track:
            requirements['senior_track'] = self.senior_track
            requirements['track_display'] = self.get_senior_track_display()
        
        return requirements

    def get_competency_focus_areas(self):
        """Get primary competency focus areas for this class."""
        subjects = self.get_subjects()
        competencies = {}
        
        for subject in subjects:
            if subject.cbc_competency_area:
                competency = subject.get_cbc_competency_area_display()
                competencies[competency] = competencies.get(competency, 0) + 1
        
        # Sort by frequency
        sorted_competencies = sorted(
            competencies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [comp[0] for comp in sorted_competencies[:3]]

    def get_portfolio_stats(self):
        """Get portfolio statistics for CBC classes."""
        if not self.portfolio_required:
            return None
        
        try:
            from .models import CBCPortfolio
            portfolios = CBCPortfolio.objects.filter(
                student__enrollments__class_enrolled=self,
                academic_year=self.academic_year,
                is_active=True
            )
            
            total_portfolios = portfolios.count()
            completed_portfolios = portfolios.filter(is_complete=True).count()
            
            return {
                'total_portfolios': total_portfolios,
                'completed_portfolios': completed_portfolios,
                'completion_rate': (completed_portfolios / total_portfolios * 100) if total_portfolios > 0 else 0,
                'average_artifacts': portfolios.aggregate(avg=models.Avg('artifacts_count'))['avg'] or 0,
            }
        except ImportError:
            return None

    # ============ STATISTICS AND REPORTS ============

    def get_class_statistics(self):
        """Get comprehensive class statistics."""
        try:
            from students.models import StudentEnrollment
            from attendance.models import StudentAttendance
            
            total_students = self.current_strength
            active_enrollments = StudentEnrollment.objects.filter(
                class_enrolled=self,
                status='active'
            )
            
            # Calculate attendance rate
            attendance_stats = StudentAttendance.objects.filter(
                enrollment__in=active_enrollments
            ).aggregate(
                total_days=models.Count('id'),
                present_days=models.Count('id', filter=Q(status='present'))
            )
            
            attendance_rate = 0
            if attendance_stats['total_days'] and attendance_stats['total_days'] > 0:
                attendance_rate = (attendance_stats['present_days'] / attendance_stats['total_days']) * 100
            
            stats = {
                'total_students': total_students,
                'attendance_rate': round(attendance_rate, 2),
                'occupancy_rate': self.occupancy_rate,
                'available_seats': self.available_seats,
                'subjects_count': self.get_subjects().count(),
                'teachers_count': self.get_teachers().count(),
                'average_performance': self.average_performance or 0,
            }
            
            # Add CBC-specific statistics
            if self.is_cbc_class:
                cbc_stats = {
                    'cbc_pathway': self.get_cbc_pathway_display() if self.cbc_pathway else 'General',
                    'portfolio_required': self.portfolio_required,
                    'project_required': self.project_work_required,
                    'competency_focus': self.get_competency_focus_areas(),
                }
                stats.update(cbc_stats)
                
                portfolio_stats = self.get_portfolio_stats()
                if portfolio_stats:
                    stats.update({'portfolio_stats': portfolio_stats})
            
            return stats
        except ImportError:
            return {}

    def generate_class_report(self):
        """Generate comprehensive class report."""
        report = {
            'basic_info': {
                'class_name': self.display_name,
                'class_code': self.class_code,
                'grade_level': self.get_grade_level_display(),
                'education_level': self.get_education_level_display(),
                'academic_year': self.academic_year.name,
                'room': self.room_number,
            },
            'academic_info': self.academic_info,
            'statistics': self.get_class_statistics(),
            'subjects': {
                'total': self.get_subjects().count(),
                'list': [subject.name for subject in self.get_subjects()],
                'by_category': self.get_subjects_by_category(),
            },
            'teachers': {
                'class_teacher': self.class_teacher.full_name if self.class_teacher else 'Not Assigned',
                'total': self.get_teachers().count(),
                'list': [teacher.full_name for teacher in self.get_teachers()],
            },
            'students': {
                'total': self.current_strength,
                'capacity': self.capacity,
                'occupancy_rate': f"{self.occupancy_rate}%",
            },
        }
        
        if self.is_cbc_class:
            report['cbc_info'] = self.cbc_info
            report['cbc_requirements'] = self.get_cbc_requirements()
        
        return report

    def get_current_term_info(self):
        """Get current term information."""
        try:
            from .models import AcademicTerm
            current_term = AcademicTerm.objects.filter(
                academic_year=self.academic_year,
                is_current=True
            ).first()
            
            if current_term:
                return {
                    'name': current_term.get_name_display(),
                    'start_date': current_term.start_date,
                    'end_date': current_term.end_date,
                    'progress': current_term.progress_percentage,
                    'weeks_completed': int(current_term.teaching_weeks * (current_term.progress_percentage / 100)),
                }
        except ImportError:
            pass
        
        return None

    # ============ HELPER METHODS ============

    def is_eligible_for_pathway(self, pathway):
        """Check if class is eligible for a specific CBC pathway."""
        if not self.is_cbc_class or self.education_level != 'senior_school':
            return False
        
        # Check if class has subjects in the pathway
        pathway_subjects = self.get_subjects().filter(cbc_pathway=pathway)
        return pathway_subjects.exists()

    def can_accommodate_more_students(self, count=1):
        """Check if class can accommodate more students."""
        return self.available_seats >= count

    def get_resource_requirements(self):
        """Get resource requirements for this class."""
        requirements = {
            'facilities': self.facilities,
            'technology_level': self.get_technology_level_display(),
            'special_programs': self.special_programs,
        }
        
        # Add subject-specific requirements
        subject_requirements = []
        for subject in self.get_subjects():
            if subject.resources_required:
                subject_requirements.extend(subject.resources_required)
        
        requirements['subject_resources'] = list(set(subject_requirements))
        
        return requirements

    def clone_for_next_year(self, next_academic_year):
        """Clone this class for the next academic year."""
        try:
            # Create new class with same configuration
            new_class = Class.objects.create(
                name=self.name,
                grade_level=self._get_next_grade_level(),
                section=self.section,
                stream=self.stream,
                room_number=self.room_number,
                academic_year=next_academic_year,
                education_level=self.education_level,
                cbc_pathway=self.cbc_pathway,
                senior_track=self.senior_track,
                primary_curriculum=self.primary_curriculum,
                additional_curriculums=self.additional_curriculums,
                capacity=self.capacity,
                portfolio_required=self.portfolio_required,
                project_work_required=self.project_work_required,
                community_service_hours=self.community_service_hours,
                description=self.description,
                class_rules=self.class_rules,
                class_color=self.class_color,
                facilities=self.facilities,
                parent_engagement_level=self.parent_engagement_level,
                technology_level=self.technology_level,
                special_programs=self.special_programs,
                created_by=self.created_by,
            )
            
            # Clone subject assignments
            for assignment in self.subject_assignments.filter(is_active=True):
                SubjectAssignment.objects.create(
                    subject=assignment.subject,
                    teacher=assignment.teacher,
                    class_assigned=new_class,
                    academic_year=next_academic_year,
                    periods_per_week=assignment.periods_per_week,
                    is_class_teacher=assignment.is_class_teacher,
                    created_by=assignment.created_by,
                )
            
            return new_class
        except Exception as e:
            logger.error(f"Error cloning class: {e}")
            return None

    def _get_next_grade_level(self):
        """Get next grade level."""
        grade_order = [choice[0] for choice in GRADE_LEVEL_CHOICES]
        try:
            current_index = grade_order.index(self.grade_level)
            if current_index < len(grade_order) - 1:
                return grade_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        
        return self.grade_level


class SubjectAssignment(BaseAcademicModel):
    """Enhanced Teacher subject assignments with teaching load management and CBC support."""
    
    # Core Relationships
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='subject_assignments',
        verbose_name=_("Subject")
    )
    teacher = models.ForeignKey(
        'teachers.TeacherProfile', 
        on_delete=models.CASCADE, 
        related_name='subject_assignments',
        verbose_name=_("Teacher")
    )
    class_assigned = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='subject_assignments',
        verbose_name=_("Class")
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='subject_assignments',
        verbose_name=_("Academic Year")
    )
    
    # Teaching Configuration
    periods_per_week = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Periods per Week")
    )
    
    # Role and Responsibilities
    is_class_teacher = models.BooleanField(
        default=False, 
        verbose_name=_("Is Class Teacher")
    )
    
    role_type = models.CharField(
        max_length=20,
        choices=[
            ('main_teacher', 'Main Teacher'),
            ('assistant', 'Assistant Teacher'),
            ('co_teacher', 'Co-Teacher'),
            ('substitute', 'Substitute Teacher'),
            ('specialist', 'Subject Specialist'),
        ],
        default='main_teacher',
        verbose_name=_("Role Type")
    )
    
    # CBC-Specific Teaching Requirements
    cbc_competency_focus = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific CBC competencies this teacher focuses on"),
        verbose_name=_("CBC Competency Focus")
    )
    
    project_supervision_required = models.BooleanField(
        default=False,
        verbose_name=_("Project Supervision Required")
    )
    
    portfolio_assessment_duty = models.BooleanField(
        default=False,
        verbose_name=_("Portfolio Assessment Duty")
    )
    
    # Schedule Information
    teaching_schedule = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific teaching schedule for this assignment"),
        verbose_name=_("Teaching Schedule")
    )
    
    # Assessment Responsibilities
    assessment_responsibilities = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific assessment responsibilities"),
        verbose_name=_("Assessment Responsibilities")
    )
    
    # Additional Information
    additional_responsibilities = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Additional Responsibilities")
    )
    
    responsibility_allowance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text=_("Additional allowance for responsibilities"),
        verbose_name=_("Responsibility Allowance")
    )
    
    # Status and Dates
    assigned_date = models.DateField(
        auto_now_add=True, 
        verbose_name=_("Assigned Date")
    )
    effective_from = models.DateField(
        default=timezone.now,
        verbose_name=_("Effective From")
    )
    effective_until = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Effective Until")
    )
    
    # Performance Tracking
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Performance Rating")
    )
    
    last_performance_review = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Performance Review")
    )
    
    # Status
    assignment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('temporary', 'Temporary'),
            ('substitute', 'Substitute'),
            ('completed', 'Completed'),
            ('terminated', 'Terminated'),
        ],
        default='active',
        verbose_name=_("Assignment Status")
    )
    
    # Metadata
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Subject Assignment")
        verbose_name_plural = _("Subject Assignments")
        unique_together = ['subject', 'teacher', 'class_assigned', 'academic_year']
        ordering = ['class_assigned', 'subject']
        indexes = [
            models.Index(fields=['teacher', 'is_active']),
            models.Index(fields=['class_assigned', 'subject']),
            models.Index(fields=['is_class_teacher']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['assignment_status']),
            models.Index(fields=['role_type']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.subject.name} - {self.class_assigned.display_name}"

    def save(self, *args, **kwargs):
        """Custom save with validation and auto-configuration."""
        # Auto-set some CBC fields based on class
        if self.class_assigned.is_cbc_class and not self.cbc_competency_focus:
            if self.subject.cbc_competency_area:
                self.cbc_competency_focus = [self.subject.cbc_competency_area]
        
        # Set project supervision if class requires it
        if self.class_assigned.project_work_required:
            self.project_supervision_required = True
        
        # Set portfolio assessment if class requires it
        if self.class_assigned.portfolio_required:
            self.portfolio_assessment_duty = True
        
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate assignment data."""
        errors = {}
        
        # Check if teacher is not overloaded
        current_assignments = SubjectAssignment.objects.filter(
            teacher=self.teacher,
            academic_year=self.academic_year,
            is_active=True,
            assignment_status='active'
        ).exclude(pk=self.pk)
        
        total_periods = sum(assign.periods_per_week for assign in current_assignments) + self.periods_per_week
        
        # Maximum periods per week based on teacher's contract
        max_periods = 40  # Default maximum
        if self.teacher.employment_type == 'full_time':
            max_periods = 40
        elif self.teacher.employment_type == 'part_time':
            max_periods = 20
        
        if total_periods > max_periods:
            errors['periods_per_week'] = _(
                f"Teacher would be overloaded. Maximum {max_periods} periods allowed. "
                f"Currently assigned {total_periods - self.periods_per_week} periods."
            )
        
        # Check for date validity
        if self.effective_until and self.effective_from > self.effective_until:
            errors['effective_until'] = _("Effective until date must be after effective from date")
        
        # Check for schedule conflicts
        if self._has_schedule_conflict():
            errors['teaching_schedule'] = _("Teaching schedule conflicts with existing assignments")
        
        if errors:
            raise ValidationError(errors)

    def _has_schedule_conflict(self):
        """Check if there are schedule conflicts with other assignments."""
        if not self.teaching_schedule:
            return False
        
        # Get all other active assignments for this teacher
        other_assignments = SubjectAssignment.objects.filter(
            teacher=self.teacher,
            academic_year=self.academic_year,
            is_active=True,
            assignment_status='active'
        ).exclude(pk=self.pk)
        
        for assignment in other_assignments:
            if assignment.teaching_schedule:
                # Simple conflict detection (can be enhanced)
                for slot in self.teaching_schedule:
                    if slot in assignment.teaching_schedule:
                        return True
        
        return False

    # ============ PROPERTIES ============

    @property
    def teaching_load_hours(self):
        """Calculate weekly teaching load in hours."""
        return round(self.periods_per_week * 45 / 60, 1)  # Assuming 45-minute periods

    @property
    def is_current(self):
        """Check if this assignment is currently effective."""
        today = timezone.now().date()
        
        if today < self.effective_from:
            return False
        
        if self.effective_until:
            return today <= self.effective_until
        
        return True

    @property
    def assignment_duration_days(self):
        """Calculate assignment duration in days."""
        if not self.effective_from:
            return 0
        
        end_date = self.effective_until or timezone.now().date()
        return max(0, (end_date - self.effective_from).days)

    @property
    def is_cbc_assignment(self):
        """Check if this is a CBC assignment."""
        return self.class_assigned.is_cbc_class

    @property
    def competency_info(self):
        """Get competency information for CBC assignments."""
        if not self.is_cbc_assignment:
            return None
        
        return {
            'competency_focus': self.cbc_competency_focus,
            'subject_competency': self.subject.cbc_competency_area,
            'requires_project_supervision': self.project_supervision_required,
            'requires_portfolio_assessment': self.portfolio_assessment_duty,
        }

    @property
    def workload_score(self):
        """Calculate workload score."""
        base_score = self.periods_per_week / 40 * 100  # Base on periods
        
        # Adjust for additional responsibilities
        if self.is_class_teacher:
            base_score += 10
        
        if self.additional_responsibilities:
            base_score += 5
        
        if self.project_supervision_required:
            base_score += 15
        
        if self.portfolio_assessment_duty:
            base_score += 10
        
        return min(100, base_score)

    # ============ METHODS ============

    def get_assignment_summary(self):
        """Get comprehensive assignment summary."""
        summary = {
            'teacher': self.teacher.full_name,
            'subject': self.subject.name,
            'class': self.class_assigned.display_name,
            'periods_per_week': self.periods_per_week,
            'teaching_hours': self.teaching_load_hours,
            'is_class_teacher': self.is_class_teacher,
            'role_type': self.get_role_type_display(),
            'assignment_status': self.get_assignment_status_display(),
            'is_current': self.is_current,
            'duration_days': self.assignment_duration_days,
        }
        
        if self.is_cbc_assignment:
            summary['cbc_info'] = self.competency_info
        
        return summary

    def calculate_workload_distribution(self):
        """Calculate workload distribution across different responsibilities."""
        workload = {
            'teaching': self.periods_per_week * 45,  # minutes
            'preparation': self.periods_per_week * 30,  # 30 min prep per period
            'assessment': self.periods_per_week * 15,  # 15 min assessment per period
            'additional': 0,
        }
        
        # Add additional workload based on responsibilities
        if self.is_class_teacher:
            workload['additional'] += 300  # 5 hours for class teacher duties
        
        if self.project_supervision_required:
            workload['additional'] += 120  # 2 hours for project supervision
        
        if self.portfolio_assessment_duty:
            workload['additional'] += 180  # 3 hours for portfolio assessment
        
        # Convert to hours
        for key in workload:
            workload[key] = round(workload[key] / 60, 1)
        
        return workload

    def update_performance_rating(self, rating, review_date=None):
        """Update performance rating."""
        if 1 <= rating <= 5:
            self.performance_rating = rating
            self.last_performance_review = review_date or timezone.now().date()
            self.save()
            return True
        return False

    def get_student_count(self):
        """Get number of students in the assigned class."""
        return self.class_assigned.current_strength

    def get_assessment_responsibilities_summary(self):
        """Get summary of assessment responsibilities."""
        if not self.assessment_responsibilities:
            return {
                'total_assessments': 0,
                'types': [],
                'estimated_time': 0,
            }
        
        types = set()
        total_time = 0
        
        for responsibility in self.assessment_responsibilities:
            if 'type' in responsibility:
                types.add(responsibility['type'])
            if 'estimated_time' in responsibility:
                total_time += responsibility['estimated_time']
        
        return {
            'total_assessments': len(self.assessment_responsibilities),
            'types': list(types),
            'estimated_time': total_time,
        }

    def extend_assignment(self, new_effective_until):
        """Extend assignment end date."""
        if new_effective_until > self.effective_from:
            self.effective_until = new_effective_until
            self.save()
            return True
        return False

    def terminate_assignment(self, termination_date=None, reason=None):
        """Terminate assignment."""
        self.assignment_status = 'terminated'
        self.effective_until = termination_date or timezone.now().date()
        if reason:
            self.notes = f"{self.notes or ''}\nTermination: {reason}"
        self.save()
        return True

    def clone_for_next_year(self, next_academic_year):
        """Clone assignment for next academic year."""
        try:
            new_assignment = SubjectAssignment.objects.create(
                subject=self.subject,
                teacher=self.teacher,
                class_assigned=self.class_assigned.clone_for_next_year(next_academic_year),
                academic_year=next_academic_year,
                periods_per_week=self.periods_per_week,
                is_class_teacher=self.is_class_teacher,
                role_type=self.role_type,
                cbc_competency_focus=self.cbc_competency_focus,
                project_supervision_required=self.project_supervision_required,
                portfolio_assessment_duty=self.portfolio_assessment_duty,
                teaching_schedule=self.teaching_schedule,
                assessment_responsibilities=self.assessment_responsibilities,
                additional_responsibilities=self.additional_responsibilities,
                responsibility_allowance=self.responsibility_allowance,
                effective_from=next_academic_year.start_date,
                created_by=self.created_by,
            )
            return new_assignment
        except Exception as e:
            logger.error(f"Error cloning subject assignment: {e}")
            return None


class LessonPlan(BaseAcademicModel):
    """Model for teacher lesson plans."""
    
    # Basic Information
    title = models.CharField(max_length=200, verbose_name=_("Lesson Title"))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_("Subject"))
    sub_topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, verbose_name=_("Sub Topic"))
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name=_("Class"))
    
    # Teacher Information
    teacher = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.CASCADE,
        verbose_name=_("Teacher")
    )
    
    # Lesson Details
    date = models.DateField(verbose_name=_("Lesson Date"))
    duration_minutes = models.IntegerField(
        default=40,
        validators=[MinValueValidator(5), MaxValueValidator(120)],
        verbose_name=_("Duration (minutes)")
    )
    
    # Lesson Components
    learning_objectives = models.JSONField(
        default=list,
        verbose_name=_("Learning Objectives")
    )
    
    materials_needed = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Materials Needed")
    )
    
    introduction = models.TextField(verbose_name=_("Introduction"))
    development = models.TextField(verbose_name=_("Development Activities"))
    conclusion = models.TextField(verbose_name=_("Conclusion/Summary"))
    
    # Assessment
    assessment_methods = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Assessment Methods")
    )
    
    differentiation_strategies = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Differentiation Strategies")
    )
    
    # Homework/Follow-up
    homework_assignment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Homework Assignment")
    )
    
    next_lesson_preview = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Next Lesson Preview")
    )
    
    # Status
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    actual_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Actual Duration (minutes)")
    )
    
    # Reflection
    teacher_reflection = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Teacher Reflection")
    )
    
    class Meta:
        verbose_name = _("Lesson Plan")
        verbose_name_plural = _("Lesson Plans")
        ordering = ['-date', 'class_assigned']
        indexes = [
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['subject', 'class_assigned']),
            models.Index(fields=['is_completed']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.class_assigned.display_name} - {self.date}"
    
    @property
    def lesson_duration_hours(self):
        """Get lesson duration in hours."""
        return round(self.duration_minutes / 60, 1)
    
    def mark_completed(self, actual_duration=None, reflection=None):
        """Mark lesson plan as completed."""
        self.is_completed = True
        if actual_duration:
            self.actual_duration_minutes = actual_duration
        if reflection:
            self.teacher_reflection = reflection
        self.save()


class Syllabus(BaseAcademicModel):
    """Model for subject syllabus and curriculum standards."""
    
    # Basic Information
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='syllabi',
        verbose_name=_("Subject")
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='syllabi',
        verbose_name=_("Academic Year")
    )
    
    # Syllabus Details
    title = models.CharField(max_length=200, verbose_name=_("Syllabus Title"))
    version = models.CharField(max_length=20, default='1.0', verbose_name=_("Version"))
    
    # Curriculum Standards
    curriculum_standards = models.JSONField(
        default=list,
        help_text=_("Curriculum standards and benchmarks"),
        verbose_name=_("Curriculum Standards")
    )
    
    # Content Outline
    topics = models.JSONField(
        default=list,
        help_text=_("Topics and sub-topics with time allocation"),
        verbose_name=_("Topics")
    )
    
    # Learning Resources
    recommended_books = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Recommended textbooks and references"),
        verbose_name=_("Recommended Books")
    )
    
    teaching_resources = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Teaching aids and resources"),
        verbose_name=_("Teaching Resources")
    )
    
    # Assessment Framework
    assessment_framework = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Assessment types, weights, and schedule"),
        verbose_name=_("Assessment Framework")
    )
    
    # Competency Mapping
    competency_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Mapping of topics to competencies"),
        verbose_name=_("Competency Mapping")
    )
    
    # CBC Specific Fields
    cbc_competencies = models.JSONField(
        default=list,
        blank=True,
        help_text=_("CBC competencies addressed"),
        verbose_name=_("CBC Competencies")
    )
    
    project_requirements = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Project requirements for CBC"),
        verbose_name=_("Project Requirements")
    )
    
    # Additional Information
    objectives = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Learning Objectives")
    )
    
    methodology = models.TextField(
        blank=True,
        null=True,
        help_text=_("Recommended teaching methodology"),
        verbose_name=_("Teaching Methodology")
    )
    
    # Status
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_syllabi',
        verbose_name=_("Approved By")
    )
    
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Approval Date")
    )
    
    # Metadata
    syllabus_file = models.FileField(
        upload_to='syllabi/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Syllabus File")
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )

    class Meta:
        verbose_name = _("Syllabus")
        verbose_name_plural = _("Syllabi")
        unique_together = ['subject', 'academic_year', 'version']
        ordering = ['subject', 'academic_year', 'version']
        indexes = [
            models.Index(fields=['subject', 'academic_year']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.academic_year.name} - v{self.version}"
    
    def save(self, *args, **kwargs):
        """Auto-generate version if not provided."""
        if not self.version:
            # Find latest version for this subject and academic year
            latest = Syllabus.objects.filter(
                subject=self.subject,
                academic_year=self.academic_year
            ).order_by('-version').first()
            
            if latest and latest.version:
                try:
                    version_num = float(latest.version)
                    self.version = f"{version_num + 0.1:.1f}"
                except ValueError:
                    self.version = '1.0'
            else:
                self.version = '1.0'
        
        super().save(*args, **kwargs)
    
    @property
    def total_topics(self):
        """Get total number of topics."""
        return len(self.topics) if self.topics else 0
    
    @property
    def total_weeks(self):
        """Calculate total weeks based on time allocation."""
        if not self.topics:
            return 0
        
        total_hours = sum(topic.get('estimated_hours', 0) for topic in self.topics)
        return round(total_hours / self.subject.weekly_hours) if self.subject.weekly_hours > 0 else 0
    
    def get_competency_coverage(self):
        """Get competency coverage analysis."""
        if not self.competency_mapping:
            return {}
        
        coverage = {}
        for topic in self.topics:
            if 'competencies' in topic:
                for competency in topic['competencies']:
                    coverage[competency] = coverage.get(competency, 0) + 1
        
        return coverage


class AcademicEvent(BaseAcademicModel):
    """Model for academic events and calendar entries."""
    
    # Basic Information
    title = models.CharField(max_length=200, verbose_name=_("Event Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Event Details
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name=_("Event Type")
    )
    
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    
    # Location
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Location")
    )
    
    # Academic Context
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='academic_events',
        verbose_name=_("Academic Year")
    )
    
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name=_("Term")
    )
    
    # Participants
    target_audience = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Target audience (students, teachers, parents, etc.)"),
        verbose_name=_("Target Audience")
    )
    
    # Status
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))
    is_cancelled = models.BooleanField(default=False, verbose_name=_("Is Cancelled"))
    
    # Priority
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_("Priority")
    )
    
    # Organizer
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
        verbose_name=_("Organizer")
    )
    
    # Resources
    resources = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Event resources and materials"),
        verbose_name=_("Resources")
    )
    
    # Attendance Tracking
    requires_attendance = models.BooleanField(
        default=False,
        verbose_name=_("Requires Attendance")
    )
    
    # Reminders
    reminder_days_before = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        verbose_name=_("Reminder Days Before")
    )
    
    class Meta:
        verbose_name = _("Academic Event")
        verbose_name_plural = _("Academic Events")
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['academic_year', 'term']),
            models.Index(fields=['is_published']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"
    
    def clean(self):
        """Validate event dates."""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_("End date must be after start date"))
    
    @property
    def duration_hours(self):
        """Calculate event duration in hours."""
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return duration.total_seconds() / 3600
        return 0
    
    @property
    def is_upcoming(self):
        """Check if event is upcoming."""
        return self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        """Check if event is currently ongoing."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def is_past(self):
        """Check if event is in the past."""
        return self.end_date < timezone.now()


class Stream(BaseAcademicModel):
    """Model for academic streams/tracks."""
    
    name = models.CharField(max_length=100, verbose_name=_("Stream Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Stream Code"))
    
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Academic Information
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVELS,
        verbose_name=_("Education Level")
    )
    
    curriculum = models.CharField(
        max_length=20,
        choices=CURRICULUM_CHOICES,
        default='cbc',
        verbose_name=_("Curriculum")
    )
    
    # Pathway Information
    pathway = models.CharField(
        max_length=20,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    # Requirements
    minimum_requirements = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Minimum academic requirements"),
        verbose_name=_("Minimum Requirements")
    )
    
    # Subjects
    core_subjects = models.ManyToManyField(
        Subject,
        related_name='core_in_streams',
        blank=True,
        verbose_name=_("Core Subjects")
    )
    
    elective_subjects = models.ManyToManyField(
        Subject,
        related_name='elective_in_streams',
        blank=True,
        verbose_name=_("Elective Subjects")
    )
    
    # Career Pathways
    career_pathways = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Related career pathways"),
        verbose_name=_("Career Pathways")
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    class Meta:
        verbose_name = _("Stream")
        verbose_name_plural = _("Streams")
        ordering = ['education_level', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['education_level', 'pathway']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_education_level_display()})"


class StudentEnrollment(BaseAcademicModel):
    """Enhanced Student enrollment management with comprehensive tracking and CBC support."""
    
    # Core Relationships
    student = models.ForeignKey(
        'students.StudentProfile', 
        on_delete=models.CASCADE, 
        related_name='academics_enrollments_new',
        verbose_name=_("Student")
    )
    class_enrolled = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='enrollments_academics',
        verbose_name=_("Class")
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='enrollments_academics_1',
        verbose_name=_("Academic Year")
    )
    
    # Enrollment Information
    enrollment_date = models.DateField(
        default=timezone.now, 
        verbose_name=_("Enrollment Date")
    )
    enrollment_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name=_("Enrollment Number")
    )
    
    # Status Information
    status = models.CharField(
        max_length=20, 
        choices=ENROLLMENT_STATUS, 
        default='active',
        verbose_name=_("Status")
    )
    
    status_changed_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Status Changed Date")
    )
    status_reason = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Status Reason")
    )
    
    # Academic Information
    roll_number = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_("Roll Number")
    )
    
    # CBC-Specific Information
    cbc_pathway_selection = models.CharField(
        max_length=20,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway Selection")
    )
    
    senior_track_selection = models.CharField(
        max_length=30,
        choices=SENIOR_SCHOOL_TRACKS,
        blank=True,
        null=True,
        verbose_name=_("Senior Track Selection")
    )
    
    portfolio_status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('submitted', 'Submitted'),
            ('reviewed', 'Reviewed'),
            ('completed', 'Completed'),
        ],
        default='not_started',
        verbose_name=_("Portfolio Status")
    )
    
    community_service_hours_completed = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Community Service Hours Completed")
    )
    
    # House and Extracurricular
    house = models.CharField(
        max_length=20, 
        choices=HOUSE_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name=_("House")
    )
    
    extracurricular_activities = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Extracurricular Activities")
    )
    
    # Previous School Information
    previous_school = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_("Previous School")
    )
    
    transfer_certificate = models.FileField(
        upload_to='transfer_certificates/%Y/%m/', 
        blank=True, 
        null=True,
        verbose_name=_("Transfer Certificate")
    )
    
    previous_performance = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Previous Performance")
    )
    
    # Financial Information
    fee_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Fully Paid'),
            ('partial', 'Partially Paid'),
            ('unpaid', 'Unpaid'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
        ],
        default='unpaid',
        verbose_name=_("Fee Status")
    )
    
    fee_arrears = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Fee Arrears")
    )
    
    # Parent/Guardian Information
    parent_engagement_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Engagement'),
            ('medium', 'Medium Engagement'),
            ('high', 'High Engagement'),
            ('very_high', 'Very High Engagement'),
        ],
        default='medium',
        verbose_name=_("Parent Engagement Level")
    )
    
    # Special Needs and Support
    special_needs = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Special Needs")
    )
    
    support_services = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Support Services")
    )
    
    # Academic Support
    academic_support_level = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Support Needed'),
            ('minimal', 'Minimal Support'),
            ('moderate', 'Moderate Support'),
            ('intensive', 'Intensive Support'),
        ],
        default='none',
        verbose_name=_("Academic Support Level")
    )
    
    # Performance Tracking
    average_performance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Average Performance")
    )
    
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Attendance Percentage")
    )
    
    # Metadata
    remarks = models.TextField(blank=True, null=True, verbose_name=_("Remarks"))
    
    enrollment_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Enrollment Metadata")
    )

    class Meta:
        verbose_name = _("Student Enrollment")
        verbose_name_plural = _("Student Enrollments")
        unique_together = ['student', 'academic_year']
        ordering = ['class_enrolled', 'roll_number']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['enrollment_number']),
            models.Index(fields=['status']),
            models.Index(fields=['house']),
            models.Index(fields=['class_enrolled']),
            models.Index(fields=['cbc_pathway_selection']),
            models.Index(fields=['senior_track_selection']),
            models.Index(fields=['portfolio_status']),
            models.Index(fields=['fee_status']),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.class_enrolled.display_name}"

    def save(self, *args, **kwargs):
        """Generate enrollment number and update status dates."""
        if not self.enrollment_number:
            self.enrollment_number = self._generate_enrollment_number()
        
        if self.pk:
            original = StudentEnrollment.objects.get(pk=self.pk)
            if original.status != self.status:
                self.status_changed_date = timezone.now().date()
        else:
            self.status_changed_date = timezone.now().date()
            
        # Auto-set roll number if not provided
        if not self.roll_number:
            self.roll_number = self._get_next_roll_number()
        
        # Auto-set CBC pathway from class if not specified
        if self.class_enrolled.is_cbc_class and not self.cbc_pathway_selection:
            if self.class_enrolled.cbc_pathway:
                self.cbc_pathway_selection = self.class_enrolled.cbc_pathway
            if self.class_enrolled.senior_track:
                self.senior_track_selection = self.class_enrolled.senior_track
        
        super().save(*args, **kwargs)

    def _generate_enrollment_number(self):
        """Generate unique enrollment number."""
        year = self.enrollment_date.year
        student_initials = self.student.initials if hasattr(self.student, 'initials') else 'ST'
        
        # Find last enrollment for this year
        last_enrollment = StudentEnrollment.objects.filter(
            enrollment_date__year=year
        ).order_by('-enrollment_number').first()
        
        if last_enrollment and last_enrollment.enrollment_number:
            try:
                last_num = int(last_enrollment.enrollment_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"ENR-{year}-{student_initials}-{new_num:04d}"

    def _get_next_roll_number(self):
        """Get next available roll number for the class."""
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=self.class_enrolled,
            academic_year=self.academic_year
        ).exclude(roll_number=None).order_by('-roll_number')
        
        if enrollments.exists():
            return enrollments.first().roll_number + 1
        return 1

    def clean(self):
        """Validate enrollment data."""
        errors = {}
        
        # Check for duplicate enrollment in same academic year
        duplicate_enrollment = StudentEnrollment.objects.filter(
            student=self.student, 
            academic_year=self.academic_year
        ).exclude(pk=self.pk).exists()
        
        if duplicate_enrollment:
            errors['academic_year'] = _('Student is already enrolled for this academic year.')
        
        # Check for duplicate roll number in same class
        if self.roll_number:
            duplicate_roll = StudentEnrollment.objects.filter(
                academic_year=self.academic_year,
                class_enrolled=self.class_enrolled,
                roll_number=self.roll_number
            ).exclude(pk=self.pk).exists()
            
            if duplicate_roll:
                errors['roll_number'] = _('Roll number must be unique within the class for this academic year.')
        
        # Validate CBC pathway for senior school
        if (self.class_enrolled.is_cbc_class and 
            self.class_enrolled.education_level == 'senior_school' and 
            not self.cbc_pathway_selection):
            errors['cbc_pathway_selection'] = _('CBC pathway selection is required for Senior School enrollment.')
        
        # Validate community service hours
        if self.community_service_hours_completed < 0:
            errors['community_service_hours_completed'] = _('Community service hours cannot be negative.')
        
        if errors:
            raise ValidationError(errors)

    # ============ PROPERTIES ============

    @property
    def is_current(self):
        """Check if this is the current enrollment."""
        return self.status == 'active' and self.academic_year.is_current

    @property
    def enrollment_duration(self):
        """Calculate enrollment duration in days."""
        if self.status in ['transferred', 'withdrawn', 'graduated'] and self.status_changed_date:
            end_date = self.status_changed_date
        else:
            end_date = timezone.now().date()
        
        return max(0, (end_date - self.enrollment_date).days)

    @property
    def is_cbc_enrollment(self):
        """Check if this is a CBC enrollment."""
        return self.class_enrolled.is_cbc_class

    @property
    def cbc_info(self):
        """Get CBC-specific information."""
        if not self.is_cbc_enrollment:
            return None
        
        info = {
            'pathway': self.get_cbc_pathway_selection_display() if self.cbc_pathway_selection else 'Not Selected',
            'senior_track': self.get_senior_track_selection_display() if self.senior_track_selection else 'Not Selected',
            'portfolio_status': self.get_portfolio_status_display(),
            'community_service_hours': {
                'completed': self.community_service_hours_completed,
                'required': self.class_enrolled.community_service_hours,
                'remaining': max(0, self.class_enrolled.community_service_hours - self.community_service_hours_completed),
            },
            'requires_portfolio': self.class_enrolled.portfolio_required,
            'requires_project': self.class_enrolled.project_work_required,
        }
        
        return info

    @property
    def academic_progress(self):
        """Get academic progress information."""
        try:
            from grading.models import Grade
            
            grades = Grade.objects.filter(
                enrollment=self,
                is_active=True
            )
            
            if grades.exists():
                avg_score = grades.aggregate(avg=models.Avg('score'))['avg']
                total_grades = grades.count()
                passing_grades = grades.filter(score__gte=40).count()
                
                return {
                    'average_score': round(avg_score, 2) if avg_score else 0,
                    'total_grades': total_grades,
                    'passing_grades': passing_grades,
                    'pass_rate': round((passing_grades / total_grades * 100), 2) if total_grades > 0 else 0,
                }
        except ImportError:
            pass
        
        return None

    @property
    def enrollment_summary(self):
        """Get enrollment summary."""
        summary = {
            'student': self.student.full_name,
            'class': self.class_enrolled.display_name,
            'academic_year': self.academic_year.name,
            'enrollment_date': self.enrollment_date,
            'enrollment_number': self.enrollment_number,
            'status': self.get_status_display(),
            'roll_number': self.roll_number,
            'enrollment_duration_days': self.enrollment_duration,
            'is_current': self.is_current,
        }
        
        if self.is_cbc_enrollment:
            summary['cbc_info'] = self.cbc_info
        
        return summary

    # ============ METHODS ============

    def update_portfolio_status(self, new_status, notes=None):
        """Update portfolio status."""
        valid_statuses = [choice[0] for choice in self._meta.get_field('portfolio_status').choices]
        
        if new_status in valid_statuses:
            self.portfolio_status = new_status
            if notes:
                self.remarks = f"{self.remarks or ''}\nPortfolio Update: {notes}"
            self.save()
            return True
        return False

    def add_community_service_hours(self, hours, activity_description=None):
        """Add community service hours."""
        if hours > 0:
            self.community_service_hours_completed += hours
            
            if activity_description:
                activity_record = {
                    'date': timezone.now().date().isoformat(),
                    'hours': hours,
                    'activity': activity_description,
                    'verified_by': None,  # Could be set by supervisor
                }
                
                # Add to extracurricular activities
                if not self.extracurricular_activities:
                    self.extracurricular_activities = []
                self.extracurricular_activities.append(activity_record)
            
            self.save()
            return True
        return False

    def get_required_community_service_hours(self):
        """Get required community service hours."""
        if self.is_cbc_enrollment:
            return self.class_enrolled.community_service_hours
        return 0

    def get_subject_enrollments(self):
        """Get subject enrollments for this student."""
        try:
            from .models import StudentClassAssignment
            return StudentClassAssignment.objects.filter(
                student=self.student,
                class_assigned=self.class_enrolled,
                academic_year=self.academic_year,
                status='active'
            )
        except ImportError:
            return StudentClassAssignment.objects.none()

    def calculate_fee_balance(self, total_fee_amount):
        """Calculate fee balance."""
        # This would typically integrate with a fee payment system
        # For now, return basic calculation
        if self.fee_status == 'paid':
            return 0
        elif self.fee_status == 'partial':
            return total_fee_amount - (total_fee_amount * 0.5)  # Assuming 50% paid
        else:
            return total_fee_amount

    def update_academic_performance(self):
        """Update academic performance metrics."""
        progress = self.academic_progress
        if progress:
            self.average_performance = progress['average_score']
            self.save()
            return True
        return False

    def get_attendance_summary(self):
        """Get attendance summary."""
        try:
            from attendance.models import StudentAttendance
            
            attendance_records = StudentAttendance.objects.filter(
                enrollment=self
            )
            
            if attendance_records.exists():
                total_days = attendance_records.count()
                present_days = attendance_records.filter(status='present').count()
                absent_days = attendance_records.filter(status='absent').count()
                late_days = attendance_records.filter(status='late').count()
                
                attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                self.attendance_percentage = attendance_rate
                self.save()
                
                return {
                    'total_days': total_days,
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'late_days': late_days,
                    'attendance_rate': round(attendance_rate, 2),
                }
        except ImportError:
            pass
        
        return None

    def promote_to_next_class(self, next_academic_year):
        """Promote student to next class."""
        try:
            # Find next class based on current class
            next_grade = self._get_next_grade_level()
            next_class = Class.objects.filter(
                academic_year=next_academic_year,
                grade_level=next_grade,
                is_active=True
            ).first()
            
            if next_class:
                # Create new enrollment for next year
                new_enrollment = StudentEnrollment.objects.create(
                    student=self.student,
                    class_enrolled=next_class,
                    academic_year=next_academic_year,
                    previous_school=self.class_enrolled.name,
                    remarks=f"Promoted from {self.class_enrolled.display_name}",
                    created_by=self.created_by,
                )
                
                # Update current enrollment status
                self.status = 'graduated' if next_grade == 'grade_12' else 'transferred'
                self.save()
                
                return new_enrollment
        except Exception as e:
            logger.error(f"Error promoting student: {e}")
        
        return None

    def _get_next_grade_level(self):
        """Get next grade level."""
        grade_order = [choice[0] for choice in GRADE_LEVEL_CHOICES]
        try:
            current_index = grade_order.index(self.class_enrolled.grade_level)
            if current_index < len(grade_order) - 1:
                return grade_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        
        return self.class_enrolled.grade_level

    def generate_enrollment_certificate_data(self):
        """Generate data for enrollment certificate."""
        return {
            'student_name': self.student.full_name,
            'student_admission_number': self.student.admission_number,
            'class': self.class_enrolled.display_name,
            'academic_year': self.academic_year.name,
            'enrollment_date': self.enrollment_date.strftime('%B %d, %Y'),
            'enrollment_number': self.enrollment_number,
            'roll_number': self.roll_number,
            'principal_signature': None,  # Would be added by system
            'date_issued': timezone.now().date().strftime('%B %d, %Y'),
        }


class StudentClassAssignment(BaseAcademicModel):
    """Enhanced Student assignment to specific classes or subjects with CBC support."""
    
    # Core Relationships
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='class_assignments',
        verbose_name=_("Student")
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='student_assignments',
        verbose_name=_("Class")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_assignments',
        verbose_name=_("Subject")
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='student_class_assignments',
        verbose_name=_("Academic Year")
    )
    
    # Assignment Details
    assignment_date = models.DateField(
        default=timezone.now, 
        verbose_name=_("Assignment Date")
    )
    effective_from = models.DateField(
        default=timezone.now,
        verbose_name=_("Effective From")
    )
    effective_until = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Effective Until")
    )
    
    # Status Information
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
            ('transferred', 'Transferred'),
            ('withdrawn', 'Withdrawn'),
            ('suspended', 'Suspended'),
        ],
        default='active',
        verbose_name=_("Status")
    )
    
    status_changed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Status Changed Date")
    )
    
    # Academic Information
    seating_position = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Seating Position")
    )
    
    locker_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Locker Number")
    )
    
    desk_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Desk Number")
    )
    
    # CBC-Specific Information
    is_core_subject = models.BooleanField(
        default=False,
        verbose_name=_("Is Core Subject")
    )
    
    is_elective_subject = models.BooleanField(
        default=False,
        verbose_name=_("Is Elective Subject")
    )
    
    competency_tracking_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Competency Tracking Enabled")
    )
    
    project_work_assigned = models.BooleanField(
        default=False,
        verbose_name=_("Project Work Assigned")
    )
    
    # Performance Tracking
    performance_level = models.CharField(
        max_length=20,
        choices=[
            ('beginning', 'Beginning'),
            ('developing', 'Developing'),
            ('proficient', 'Proficient'),
            ('advanced', 'Advanced'),
            ('exemplary', 'Exemplary'),
        ],
        blank=True,
        null=True,
        verbose_name=_("Performance Level")
    )
    
    last_assessment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Assessment Date")
    )
    
    # Teacher Information
    assigned_teacher = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_assignments',
        verbose_name=_("Assigned Teacher")
    )
    
    # Additional Information
    learning_style = models.CharField(
        max_length=20,
        choices=[
            ('visual', 'Visual Learner'),
            ('auditory', 'Auditory Learner'),
            ('kinesthetic', 'Kinesthetic Learner'),
            ('reading_writing', 'Reading/Writing Learner'),
            ('mixed', 'Mixed Learning Style'),
        ],
        blank=True,
        null=True,
        verbose_name=_("Learning Style")
    )
    
    special_accommodations = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Special Accommodations")
    )
    
    # Metadata
    remarks = models.TextField(blank=True, null=True, verbose_name=_("Remarks"))
    
    assignment_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Assignment Metadata")
    )

    class Meta:
        verbose_name = _("Student Class Assignment")
        verbose_name_plural = _("Student Class Assignments")
        unique_together = ['student', 'class_assigned', 'subject', 'academic_year']
        ordering = ['class_assigned', 'student']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['class_assigned', 'subject']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_teacher']),
            models.Index(fields=['is_core_subject']),
            models.Index(fields=['performance_level']),
        ]

    def __str__(self):
        if self.subject:
            return f"{self.student.full_name} - {self.class_assigned.display_name} - {self.subject.name}"
        return f"{self.student.full_name} - {self.class_assigned.display_name}"

    def save(self, *args, **kwargs):
        """Set default effective_from if not provided and validate dates."""
        if not self.effective_from:
            self.effective_from = timezone.now().date()
        
        # Update status changed date if status changed
        if self.pk:
            original = StudentClassAssignment.objects.get(pk=self.pk)
            if original.status != self.status:
                self.status_changed_date = timezone.now().date()
        else:
            self.status_changed_date = timezone.now().date()
        
        # Auto-set subject type flags
        if self.subject:
            self.is_core_subject = self.subject.is_cbc_core or self.subject.is_compulsory
            self.is_elective_subject = not self.is_core_subject
        
        # Auto-set competency tracking for CBC subjects
        if self.subject and self.subject.is_cbc_subject:
            self.competency_tracking_enabled = True
        
        super().save(*args, **kwargs)

    def clean(self):
        """Validate assignment dates."""
        errors = {}
        
        # Check if dates exist before comparing
        if self.effective_from and self.effective_until:
            if self.effective_from > self.effective_until:
                errors['effective_from'] = _("Effective from date must be before effective until date")
                errors['effective_until'] = _("Effective until date must be after effective from date")
        
        # Check for duplicate assignments
        if self.subject:
            duplicate_assignment = StudentClassAssignment.objects.filter(
                student=self.student,
                class_assigned=self.class_assigned,
                subject=self.subject,
                academic_year=self.academic_year,
                status='active'
            ).exclude(pk=self.pk).exists()
            
            if duplicate_assignment:
                errors['subject'] = _('Student already has an active assignment for this subject.')
        
        if errors:
            raise ValidationError(errors)

    # ============ PROPERTIES ============

    @property
    def is_current(self):
        """Check if assignment is currently active."""
        today = timezone.now().date()
        
        # Check if effective_from exists (should always exist after save)
        if not self.effective_from:
            return False
        
        # Check if we're after the effective_from date
        if today < self.effective_from:
            return False
        
        # Check if effective_until exists and we're before it
        if self.effective_until:
            return today <= self.effective_until
        
        # If no effective_until, return True if we're after effective_from
        return True

    @property
    def assignment_duration(self):
        """Calculate assignment duration in days."""
        if not self.effective_from:
            return 0
        
        end_date = self.effective_until or timezone.now().date()
        return max(0, (end_date - self.effective_from).days)

    @property
    def is_cbc_assignment(self):
        """Check if this is a CBC assignment."""
        return self.subject and self.subject.is_cbc_subject

    @property
    def subject_info(self):
        """Get subject information."""
        if not self.subject:
            return None
        
        info = {
            'name': self.subject.name,
            'code': self.subject.code,
            'category': self.subject.get_category_display(),
            'credits': float(self.subject.credits),
            'periods_per_week': self.subject.periods_per_week,
            'weekly_hours': self.subject.weekly_hours,
            'is_core': self.is_core_subject,
            'is_elective': self.is_elective_subject,
        }
        
        if self.is_cbc_assignment:
            info.update({
                'cbc_competency_area': self.subject.get_cbc_competency_area_display() if self.subject.cbc_competency_area else None,
                'cbc_pathway': self.subject.get_cbc_pathway_display() if self.subject.cbc_pathway else None,
                'practical_weight': self.subject.practical_weight,
                'project_based': self.subject.project_based,
            })
        
        return info

    @property
    def assignment_summary(self):
        """Get assignment summary."""
        summary = {
            'student': self.student.full_name,
            'class': self.class_assigned.display_name,
            'subject': self.subject.name if self.subject else 'General Class Assignment',
            'academic_year': self.academic_year.name,
            'assignment_date': self.assignment_date,
            'status': self.get_status_display(),
            'is_current': self.is_current,
            'assignment_duration_days': self.assignment_duration,
        }
        
        if self.assigned_teacher:
            summary['teacher'] = self.assigned_teacher.full_name
        
        return summary

    # ============ METHODS ============

    def update_status(self, new_status, reason=None):
        """Update assignment status."""
        valid_statuses = [choice[0] for choice in self._meta.get_field('status').choices]
        
        if new_status in valid_statuses:
            self.status = new_status
            self.status_changed_date = timezone.now().date()
            
            if reason:
                self.remarks = f"{self.remarks or ''}\nStatus Change: {new_status} - {reason}"
            
            self.save()
            return True
        return False

    def assign_teacher(self, teacher):
        """Assign teacher to this student assignment."""
        self.assigned_teacher = teacher
        self.save()
        return True

    def update_performance_level(self, level, assessment_date=None):
        """Update performance level."""
        valid_levels = [choice[0] for choice in self._meta.get_field('performance_level').choices]
        
        if level in valid_levels:
            self.performance_level = level
            self.last_assessment_date = assessment_date or timezone.now().date()
            self.save()
            return True
        return False

    def get_competency_progress(self):
        """Get competency progress for CBC assignments."""
        if not self.competency_tracking_enabled or not self.subject:
            return None
        
        try:
            from .models import CompetencyTracking
            
            competencies = CompetencyTracking.objects.filter(
                student=self.student,
                academic_year=self.academic_year,
                competency_area=self.subject.cbc_competency_area
            )
            
            if competencies.exists():
                competency = competencies.first()
                return {
                    'competency_area': competency.get_competency_area_display(),
                    'current_level': competency.get_current_level_display(),
                    'target_level': competency.get_target_level_display(),
                    'has_improved': competency.has_improved,
                    'last_assessed': competency.last_assessed,
                }
        except ImportError:
            pass
        
        return None

    def assign_project_work(self, project_title, description=None):
        """Assign project work to student."""
        if self.is_cbc_assignment and self.subject.project_based:
            self.project_work_assigned = True
            
            project_data = {
                'title': project_title,
                'description': description,
                'assigned_date': timezone.now().date().isoformat(),
                'status': 'assigned',
                'subject': self.subject.name,
            }
            
            # Add to assignment metadata
            if 'projects' not in self.assignment_metadata:
                self.assignment_metadata['projects'] = []
            
            self.assignment_metadata['projects'].append(project_data)
            self.save()
            return True
        
        return False

    def get_assessment_history(self):
        """Get assessment history for this assignment."""
        try:
            from grading.models import Grade
            
            grades = Grade.objects.filter(
                student=self.student,
                subject=self.subject,
                class_assigned=self.class_assigned,
                academic_year=self.academic_year,
                is_active=True
            ).order_by('-assessment_date')
            
            assessments = []
            for grade in grades:
                assessments.append({
                    'assessment_type': grade.get_assessment_type_display(),
                    'score': float(grade.score),
                    'max_score': float(grade.max_score),
                    'percentage': grade.percentage,
                    'assessment_date': grade.assessment_date,
                    'teacher': grade.teacher.full_name if grade.teacher else None,
                })
            
            return assessments
        except ImportError:
            return []

    def calculate_performance_trend(self):
        """Calculate performance trend over time."""
        assessments = self.get_assessment_history()
        
        if not assessments:
            return None
        
        # Group by month for trend analysis
        monthly_performance = {}
        for assessment in assessments:
            month_key = assessment['assessment_date'].strftime('%Y-%m')
            if month_key not in monthly_performance:
                monthly_performance[month_key] = []
            monthly_performance[month_key].append(assessment['percentage'])
        
        # Calculate monthly averages
        trend_data = []
        for month, scores in sorted(monthly_performance.items()):
            avg_score = sum(scores) / len(scores)
            trend_data.append({
                'month': month,
                'average_percentage': round(avg_score, 2),
                'assessment_count': len(scores),
            })
        
        return trend_data

    def get_learning_resources(self):
        """Get learning resources for this assignment."""
        resources = []
        
        if self.subject:
            # Add subject resources
            if self.subject.resources_required:
                resources.extend(self.subject.resources_required)
            
            # Add syllabus resources if available
            try:
                from .models import Syllabus
                syllabus = Syllabus.objects.filter(
                    subject=self.subject,
                    academic_year=self.academic_year,
                    is_active=True
                ).first()
                
                if syllabus and syllabus.recommended_books:
                    resources.extend([
                        {'type': 'book', 'name': book, 'category': 'recommended'}
                        for book in syllabus.recommended_books
                    ])
            except ImportError:
                pass
        
        # Add special accommodations as resources
        if self.special_accommodations:
            resources.extend([
                {'type': 'accommodation', 'name': accommodation, 'category': 'special'}
                for accommodation in self.special_accommodations
            ])
        
        return resources

    def clone_for_next_year(self, next_academic_year, next_class=None):
        """Clone assignment for next academic year."""
        try:
            # Determine next class
            target_class = next_class or self.class_assigned.clone_for_next_year(next_academic_year)
            
            if not target_class:
                return None
            
            # Create new assignment
            new_assignment = StudentClassAssignment.objects.create(
                student=self.student,
                class_assigned=target_class,
                subject=self.subject,
                academic_year=next_academic_year,
                assignment_date=timezone.now().date(),
                effective_from=next_academic_year.start_date,
                status='pending',
                is_core_subject=self.is_core_subject,
                is_elective_subject=self.is_elective_subject,
                competency_tracking_enabled=self.competency_tracking_enabled,
                learning_style=self.learning_style,
                special_accommodations=self.special_accommodations,
                remarks=f"Cloned from previous year assignment",
                created_by=self.created_by,
            )
            
            return new_assignment
        except Exception as e:
            logger.error(f"Error cloning student class assignment: {e}")
            return None

    def generate_progress_report(self):
        """Generate progress report for this assignment."""
        report = {
            'assignment_info': self.assignment_summary,
            'subject_info': self.subject_info,
            'performance': {
                'current_level': self.get_performance_level_display() if self.performance_level else 'Not Assessed',
                'last_assessment': self.last_assessment_date,
                'trend': self.calculate_performance_trend(),
            },
            'assessments': self.get_assessment_history(),
            'resources': self.get_learning_resources(),
            'competency_progress': self.get_competency_progress(),
            'project_work': {
                'assigned': self.project_work_assigned,
                'projects': self.assignment_metadata.get('projects', []) if self.project_work_assigned else [],
            },
        }
        
        return report


# ============================================================================
# CBC-SPECIFIC MODELS
# ============================================================================

class CBCAssessment(BaseAcademicModel):
    """Model for tracking CBC-specific assessments."""
    
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='cbc_assessments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='cbc_assessments'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='cbc_assessments'
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='cbc_assessments'
    )
    
    # Assessment details
    assessment_type = models.CharField(
        max_length=20,
        choices=ASSESSMENT_TYPES,
        verbose_name=_("Assessment Type")
    )
    
    assessment_date = models.DateField(verbose_name=_("Assessment Date"))
    
    # Competency-based scores
    competency_scores = models.JSONField(
        default=dict,
        help_text=_("Scores for different competencies"),
        verbose_name=_("Competency Scores")
    )
    
    practical_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Practical Score")
    )
    
    theory_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Theory Score")
    )
    
    project_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Project Score")
    )
    
    # CBC descriptors
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('exceeding', 'Exceeding Expectations'),
            ('meeting', 'Meeting Expectations'),
            ('approaching', 'Approaching Expectations'),
            ('beginning', 'Beginning to Develop'),
        ],
        verbose_name=_("Proficiency Level")
    )
    
    teacher_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Teacher Comments")
    )
    
    portfolio_evidence = models.FileField(
        upload_to='cbc_portfolio/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Portfolio Evidence")
    )
    
    class Meta:
        verbose_name = _("CBC Assessment")
        verbose_name_plural = _("CBC Assessments")
        unique_together = ['student', 'subject', 'academic_year', 'assessment_type']
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['assessment_type']),
            models.Index(fields=['proficiency_level']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.get_assessment_type_display()}"
    
    @property
    def total_score(self):
        """Calculate total score based on assessment type."""
        if self.assessment_type == 'practical':
            return self.practical_score
        elif self.assessment_type == 'project':
            return self.project_score
        else:
            return self.theory_score
    
    @property
    def is_national_exam(self):
        """Check if this is a national exam assessment."""
        return self.assessment_type in ['knec', 'kpsea', 'kjsea', 'kcse']


class CBCPortfolio(BaseAcademicModel):
    """Model for tracking student portfolios in CBC."""
    
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='cbc_portfolios'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='cbc_portfolios'
    )
    
    portfolio_title = models.CharField(max_length=200, verbose_name=_("Portfolio Title"))
    portfolio_type = models.CharField(
        max_length=30,
        choices=[
            ('academic', 'Academic Portfolio'),
            ('talent', 'Talent Portfolio'),
            ('project', 'Project Portfolio'),
            ('reflection', 'Reflection Portfolio'),
        ],
        verbose_name=_("Portfolio Type")
    )
    
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    artifacts = models.JSONField(
        default=list,
        help_text=_("List of portfolio artifacts with metadata"),
        verbose_name=_("Artifacts")
    )
    
    skills_demonstrated = models.JSONField(
        default=list,
        help_text=_("Skills demonstrated in this portfolio"),
        verbose_name=_("Skills Demonstrated")
    )
    
    reflection = models.TextField(blank=True, null=True, verbose_name=_("Student Reflection"))
    teacher_feedback = models.TextField(blank=True, null=True, verbose_name=_("Teacher Feedback"))
    
    submission_date = models.DateField(auto_now_add=True, verbose_name=_("Submission Date"))
    is_complete = models.BooleanField(default=False, verbose_name=_("Is Complete"))
    
    class Meta:
        verbose_name = _("CBC Portfolio")
        verbose_name_plural = _("CBC Portfolios")
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['portfolio_type']),
            models.Index(fields=['is_complete']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.portfolio_title}"
    
    @property
    def artifacts_count(self):
        """Count of artifacts in portfolio."""
        return len(self.artifacts) if self.artifacts else 0


class PathwaySelection(BaseAcademicModel):
    """Model for tracking student pathway selections in CBC."""
    
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='pathway_selections'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='pathway_selections'
    )
    
    # Pathways
    preferred_pathway = models.CharField(
        max_length=30,
        choices=CBC_PATHWAY_CHOICES,
        verbose_name=_("Preferred Pathway")
    )
    
    alternative_pathway = models.CharField(
        max_length=30,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Alternative Pathway")
    )
    
    senior_track = models.CharField(
        max_length=30,
        choices=SENIOR_SCHOOL_TRACKS,
        blank=True,
        null=True,
        verbose_name=_("Senior School Track")
    )
    
    # Selection details
    selection_date = models.DateField(default=timezone.now, verbose_name=_("Selection Date"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_pathways',
        verbose_name=_("Approved By")
    )
    approval_date = models.DateField(null=True, blank=True, verbose_name=_("Approval Date"))
    
    # Rationale
    student_statement = models.TextField(
        blank=True,
        null=True,
        help_text=_("Student's statement about why they chose this pathway"),
        verbose_name=_("Student Statement")
    )
    
    parent_consent = models.BooleanField(default=False, verbose_name=_("Parent Consent"))
    teacher_recommendation = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Teacher Recommendation")
    )
    
    # Career aspirations
    career_interests = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Career interests related to pathway"),
        verbose_name=_("Career Interests")
    )
    
    class Meta:
        verbose_name = _("Pathway Selection")
        verbose_name_plural = _("Pathway Selections")
        unique_together = ['student', 'academic_year']
        ordering = ['-selection_date']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['preferred_pathway']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_preferred_pathway_display()}"


class CompetencyTracking(BaseAcademicModel):
    """Model for tracking student competencies across curriculum."""
    
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='competency_tracking'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='competency_tracking'
    )
    
    competency_area = models.CharField(
        max_length=50,
        choices=[
            ('communication', 'Communication and Collaboration'),
            ('critical_thinking', 'Critical Thinking and Problem Solving'),
            ('creativity', 'Creativity and Imagination'),
            ('citizenship', 'Citizenship'),
            ('digital_literacy', 'Digital Literacy'),
            ('learning_to_learn', 'Learning to Learn'),
            ('self_efficacy', 'Self-efficacy'),
        ],
        verbose_name=_("Competency Area")
    )
    
    # Assessment levels
    baseline_level = models.CharField(
        max_length=20,
        choices=[
            ('beginning', 'Beginning'),
            ('developing', 'Developing'),
            ('proficient', 'Proficient'),
            ('advanced', 'Advanced'),
        ],
        null=True,
        blank=True,
        verbose_name=_("Baseline Level")
    )
    
    current_level = models.CharField(
        max_length=20,
        choices=[
            ('beginning', 'Beginning'),
            ('developing', 'Developing'),
            ('proficient', 'Proficient'),
            ('advanced', 'Advanced'),
        ],
        verbose_name=_("Current Level")
    )
    
    target_level = models.CharField(
        max_length=20,
        choices=[
            ('beginning', 'Beginning'),
            ('developing', 'Developing'),
            ('proficient', 'Proficient'),
            ('advanced', 'Advanced'),
        ],
        verbose_name=_("Target Level")
    )
    
    # Evidence and tracking
    evidence = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Evidence of competency development"),
        verbose_name=_("Evidence")
    )
    
    teacher_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Teacher Comments")
    )
    
    last_assessed = models.DateField(null=True, blank=True, verbose_name=_("Last Assessed"))
    next_review = models.DateField(null=True, blank=True, verbose_name=_("Next Review"))
    
    class Meta:
        verbose_name = _("Competency Tracking")
        verbose_name_plural = _("Competency Tracking")
        unique_together = ['student', 'academic_year', 'competency_area']
        ordering = ['competency_area']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['competency_area', 'current_level']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_competency_area_display()}"
    
    @property
    def has_improved(self):
        """Check if student has improved from baseline."""
        if not self.baseline_level:
            return None
        
        levels = ['beginning', 'developing', 'proficient', 'advanced']
        try:
            baseline_index = levels.index(self.baseline_level)
            current_index = levels.index(self.current_level)
            return current_index > baseline_index
        except ValueError:
            return None


class CurriculumMapping(BaseAcademicModel):
    """Model for mapping curriculum standards and competencies."""
    
    curriculum_system = models.CharField(
        max_length=30,
        choices=AcademicYear.CURRICULUM_SYSTEMS,
        verbose_name=_("Curriculum System")
    )
    
    grade_level = models.CharField(
        max_length=20,
        choices=GRADE_LEVEL_CHOICES,
        verbose_name=_("Grade Level")
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='curriculum_mappings',
        verbose_name=_("Subject")
    )
    
    # Standards mapping
    standard_code = models.CharField(max_length=50, verbose_name=_("Standard Code"))
    standard_description = models.TextField(verbose_name=_("Standard Description"))
    
    # Competency alignment
    aligned_competencies = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Competencies aligned with this standard"),
        verbose_name=_("Aligned Competencies")
    )
    
    # Learning outcomes
    learning_outcomes = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific learning outcomes"),
        verbose_name=_("Learning Outcomes")
    )
    
    # Assessment criteria
    assessment_criteria = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Assessment criteria for this standard"),
        verbose_name=_("Assessment Criteria")
    )
    
    # Resources and links
    resources = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Recommended resources"),
        verbose_name=_("Resources")
    )
    
    # International alignment
    international_equivalents = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Equivalent standards in other curricula"),
        verbose_name=_("International Equivalents")
    )
    
    class Meta:
        verbose_name = _("Curriculum Mapping")
        verbose_name_plural = _("Curriculum Mappings")
        unique_together = ['curriculum_system', 'grade_level', 'subject', 'standard_code']
        ordering = ['curriculum_system', 'grade_level', 'subject']
        indexes = [
            models.Index(fields=['curriculum_system', 'grade_level']),
            models.Index(fields=['subject', 'standard_code']),
        ]
    
    def __str__(self):
        return f"{self.get_curriculum_system_display()} - {self.get_grade_level_display()} - {self.standard_code}"