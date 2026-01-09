# teachers/models.py - OPTIMIZED KENYAN TEACHER MODEL
from datetime import timedelta
from io import BytesIO
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import uuid
import logging
from decimal import Decimal
from accounts.models import User, BaseModel
from django.db.models import Q
from import_export import resources
from django.conf import settings
import re
import random
import string


logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM FILE STORAGE FOR TEACHER DOCUMENTS
# ============================================================================
teacher_document_storage = FileSystemStorage(
    location=settings.MEDIA_ROOT / 'teacher_documents',
    base_url='/media/teacher_documents/'
)


# ============================================================================
# DEPARTMENT MODEL
# ============================================================================

class Department(BaseModel):
    """Department model aligned with TSC and CBC structure"""
    
   
    TSC_CATEGORY_CHOICES = [
        ('primary', _('Primary School')),
        ('junior_secondary', _('Junior Secondary School')),
        ('senior_secondary', _('Senior Secondary School')),
        ('special_needs', _('Special Needs Education')),
        ('technical', _('Technical/Vocational')),
        ('ecde', _('Early Childhood Development Education')),
    ]
    
    CBC_PATHWAY_CHOICES = [
        ('stem', _('STEM Pathway')),
        ('social_sciences', _('Social Sciences Pathway')),
        ('arts_sports', _('Arts & Sports Pathway')),
        ('general', _('General Pathway')),
        ('applied', _('Applied Pathway')),
        ('technical', _('Technical Pathway')),
    ]
    """Department model aligned with TSC and CBC structure"""
    name = models.CharField(max_length=100, verbose_name=_("Department Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Department Code"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # TSC Classification
    tsc_category = models.CharField(
        max_length=50,
        choices=TSC_CATEGORY_CHOICES,  
        default='junior_secondary',
        verbose_name=_("TSC Category")
    )
    
    # CBC Alignment
    cbc_pathway = models.CharField(
        max_length=50,
        choices=CBC_PATHWAY_CHOICES,  
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    # Head of Department
    hod = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_headed',
        verbose_name=_("Head of Department")
    )
    
    # Location Information
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    building = models.CharField(max_length=100, blank=True, verbose_name=_("Building"))
    room_number = models.CharField(max_length=20, blank=True, verbose_name=_("Room Number"))
    
    # Academic Information
    academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Academic Year")
    )
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['tsc_category']),
            models.Index(fields=['cbc_pathway']),
            models.Index(fields=['academic_year']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def teacher_count(self):
        """Get number of active teachers in this department"""
        return self.teachers.filter(is_active=True, teacher__is_active=True).count()
    
    @property
    def student_count(self):
        """Get number of students in this department's classes"""
        from academics.models import Class
        classes = Class.objects.filter(department=self)
        return sum(cls.students.count() for cls in classes)
    
    def get_active_teachers(self):
        """Get all active teachers in this department"""
        return self.teachers.filter(is_active=True, teacher__is_active=True)


# ============================================================================
# TEACHER PROFILE MODEL
# ============================================================================

class TeacherProfile(BaseModel):
    """
    Enhanced teacher profile model aligned with TSC and CBC requirements
    Integrates with accounts.User model
    """
    
    # ====================
    # EMPLOYMENT TYPES (TSC CATEGORIES)
    # ====================
    class EmploymentType(models.TextChoices):
        PERMANENT_TSC = 'permanent_tsc', _('Permanent Teacher (TSC)')
        CONTRACT_TSC = 'contract_tsc', _('Contract Teacher (TSC)')
        BOM = 'bom', _('BOM Teacher')
        PTA = 'pta', _('PTA Teacher')
        INTERN = 'intern', _('TSC Intern')
        VOLUNTEER = 'volunteer', _('Volunteer Teacher')
        PART_TIME = 'part_time', _('Part-time Teacher')
        SUBSTITUTE = 'substitute', _('Substitute Teacher')
    
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ON_LEAVE = 'on_leave', _('On Leave')
        STUDY_LEAVE = 'study_leave', _('On Study Leave')
        MATERNITY_LEAVE = 'maternity_leave', _('On Maternity Leave')
        PATERNITY_LEAVE = 'paternity_leave', _('On Paternity Leave')
        SICK_LEAVE = 'sick_leave', _('On Sick Leave')
        SUSPENDED = 'suspended', _('Suspended')
        TERMINATED = 'terminated', _('Terminated')
        RETIRED = 'retired', _('Retired')
        RESIGNED = 'resigned', _('Resigned')
        TRANSFERRED = 'transferred', _('Transferred')
        DECEASED = 'deceased', _('Deceased')
    
    # ====================
    # TEACHING LEVELS (TSC CLASSIFICATION)
    # ====================
    class TeachingLevel(models.TextChoices):
        PRIMARY = 'primary', _('Primary School (Grade 1-6)')
        JUNIOR_SECONDARY = 'junior_secondary', _('Junior Secondary (Grade 7-9)')
        SENIOR_SECONDARY = 'senior_secondary', _('Senior Secondary (Grade 10-12)')
        ECDE = 'ecde', _('Early Childhood Development Education')
        SPECIAL_NEEDS = 'special_needs', _('Special Needs Education')
        TECHNICAL = 'technical', _('Technical/Vocational')
        TVET = 'tvet', _('TVET Institution')
        UNIVERSITY = 'university', _('University')
    
    # ====================
    # TSC REGISTRATION STATUS
    # ====================
    class TSCStatus(models.TextChoices):
        REGISTERED = 'registered', _('TSC Registered')
        PROVISIONAL = 'provisional', _('Provisional Registration')
        PENDING = 'pending', _('Registration Pending')
        INTERN = 'intern', _('TSC Intern')
        NOT_REGISTERED = 'not_registered', _('Not Registered')
        EXPIRED = 'expired', _('Registration Expired')
        SUSPENDED = 'suspended', _('Registration Suspended')
        REVOKED = 'revoked', _('Registration Revoked')
    
    # ====================
    # CORE IDENTIFICATION
    # ====================
    teacher = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_("Teacher User Account"),
        help_text=_("Links to the main user account")
    )
    
    # ====================
    # TSC REGISTRATION INFORMATION (MANDATORY)
    # ====================
    tsc_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("TSC Number"),
        help_text=_("Teacher Service Commission registration number")
    )
    
    tsc_registration_date = models.DateField(
        verbose_name=_("TSC Registration Date"),
        help_text=_("Date teacher was registered by TSC")
    )
    
    tsc_status = models.CharField(
        max_length=20,
        choices=TSCStatus.choices,
        default=TSCStatus.REGISTERED,
        verbose_name=_("TSC Status")
    )
    
    tsc_category = models.CharField(
        max_length=50,
        choices=[
            ('classroom_teacher', _('Classroom Teacher')),
            ('head_teacher', _('Head Teacher')),
            ('deputy_head_teacher', _('Deputy Head Teacher')),
            ('senior_teacher', _('Senior Teacher')),
            ('senior_master', _('Senior Master')),
            ('principal', _('Principal')),
            ('deputy_principal', _('Deputy Principal')),
        ],
        default='classroom_teacher',
        verbose_name=_("TSC Category")
    )
    
    tsc_payroll_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("TSC Payroll Number"),
        help_text=_("TSC payroll number for permanent teachers")
    )
    
    # ====================
    # ACADEMIC QUALIFICATIONS (TSC REQUIREMENTS)
    # ====================
    highest_qualification = models.CharField(
        max_length=50,
        choices=[
            ('certificate', _('Certificate in Education')),
            ('diploma_primary', _('Diploma in Primary Teacher Education (DPTE)')),
            ('diploma_secondary', _('Diploma in Secondary Teacher Education (DSTE)')),
            ('bachelor_education', _("Bachelor's Degree in Education (B.Ed)")),
            ('bachelor_arts', _("Bachelor of Arts with Education (BA.Ed)")),
            ('bachelor_science', _("Bachelor of Science with Education (BSc.Ed)")),
            ('postgraduate_diploma', _('Postgraduate Diploma in Education (PGDE)')),
            ('masters_education', _("Master's Degree in Education")),
            ('masters_other', _("Master's Degree in Other Field")),
            ('phd_education', _('PhD in Education')),
            ('phd_other', _('PhD in Other Field')),
        ],
        verbose_name=_("Highest Qualification")
    )
    
    qualification_institution = models.CharField(
        max_length=200,
        verbose_name=_("Institution of Highest Qualification"),
        help_text=_("University/College where highest qualification was obtained")
    )
    
    year_of_graduation = models.IntegerField(
        validators=[MinValueValidator(1970), MaxValueValidator(timezone.now().year)],
        verbose_name=_("Year of Graduation"),
        help_text=_("Year highest qualification was awarded")
    )
    
    # KCSE GRADES (Required for TSC registration)
    kcse_mean_grade = models.CharField(
        max_length=5,
        choices=[
            ('A', 'A'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B', 'B'),
            ('B-', 'B-'),
            ('C+', 'C+'),
            ('C', 'C'),
            ('C-', 'C-'),
            ('D+', 'D+'),
            ('D', 'D'),
            ('D-', 'D-'),
            ('E', 'E'),
        ],
        verbose_name=_("KCSE Mean Grade")
    )
    
    kcse_index_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("KCSE Index Number")
    )
    
    kcse_year = models.IntegerField(
        validators=[MinValueValidator(1989), MaxValueValidator(timezone.now().year)],
        null=True,
        blank=True,
        verbose_name=_("KCSE Year")
    )
    
    # TEACHING SUBJECTS
    teaching_subjects = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Teaching Subjects"),
        help_text=_("List of subjects teacher is qualified to teach")
    )
    
    # ====================
    # EMPLOYMENT INFORMATION
    # ====================
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.PERMANENT_TSC,
        verbose_name=_("Employment Type")
    )
    
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        verbose_name=_("Employment Status")
    )
    
    teaching_level = models.CharField(
        max_length=20,
        choices=TeachingLevel.choices,
        default=TeachingLevel.JUNIOR_SECONDARY,
        verbose_name=_("Teaching Level")
    )
    
    # ====================
    # PROFESSIONAL INFORMATION
    # ====================
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        verbose_name=_("Department")
    )
    
    designation = models.CharField(
        max_length=100,
        choices=[
            ('classroom_teacher', _('Classroom Teacher')),
            ('senior_teacher', _('Senior Teacher')),
            ('head_of_department', _('Head of Department')),
            ('deputy_head_teacher', _('Deputy Head Teacher')),
            ('head_teacher', _('Head Teacher')),
            ('deputy_principal', _('Deputy Principal')),
            ('principal', _('Principal')),
            ('director_studies', _('Director of Studies')),
            ('curriculum_coordinator', _('Curriculum Coordinator')),
            ('guidance_counselor', _('Guidance and Counseling Teacher')),
            ('games_master', _('Games Master/Mistress')),
            ('lab_technician', _('Laboratory Technician')),
            ('librarian', _('Librarian')),
        ],
        default='classroom_teacher',
        verbose_name=_("Designation")
    )
    
    # ====================
    # CBC-SPECIFIC QUALIFICATIONS
    # ====================
    cbc_trained = models.BooleanField(
        default=False,
        verbose_name=_("CBC Trained"),
        help_text=_("Has completed Competency-Based Curriculum training")
    )
    
    cbc_training_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("CBC Training Date")
    )
    
    cbc_training_level = models.CharField(
        max_length=50,
        choices=[
            ('foundation', _('Foundation Level (Grade 1-3)')),
            ('lower_primary', _('Lower Primary (Grade 4-6)')),
            ('junior_school', _('Junior School (Grade 7-9)')),
            ('senior_school', _('Senior School (Grade 10-12)')),
            ('all_levels', _('All Levels')),
        ],
        blank=True,
        verbose_name=_("CBC Training Level")
    )
    
    # ====================
    # ADDITIONAL PROFESSIONAL INFORMATION
    # ====================
    teacher_registration_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Teacher Registration Number")
    )
    
    knec_registration_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("KNEC Registration Number")
    )
    
    sacco_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("SACCO Name")
    )
    
    sacco_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("SACCO Number")
    )
    
    blood_group = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        verbose_name=_("Blood Group")
    )
    
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Bank Name")
    )
    
    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Bank Account Number")
    )
    
    bank_branch = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Bank Branch")
    )
    
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Emergency Contact Name")
    )
    
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Emergency Contact Phone")
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Relationship")
    )
    
    # ====================
    # TPD MODULES (Teacher Professional Development)
    # ====================
    tpd_current_module = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name=_("Current TPD Module"),
        help_text=_("Current Teacher Professional Development module (1-6)")
    )
    
    tpd_last_completed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last TPD Completion Date")
    )
    
    tpd_next_renewal_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("TPD License Renewal Date"),
        help_text=_("Next renewal date (every 5 years)")
    )
    
    tpd_license_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("TPD License Number")
    )
    
    # ====================
    # DATES
    # ====================
    employment_date = models.DateField(
        verbose_name=_("Employment Date"),
        help_text=_("Date of first employment in current school")
    )
    
    confirmation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Confirmation Date")
    )
    
    retirement_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Planned Retirement Date")
    )
    
    last_promotion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Promotion Date")
    )
    
    # ====================
    # TEACHING LOAD & SCHEDULE
    # ====================
    weekly_periods = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name=_("Weekly Periods"),
        help_text=_("Number of teaching periods per week (max 50)")
    )
    
    teaching_load_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Teaching Load Hours"),
        help_text=_("Weekly teaching hours")
    )
    
    # ====================
    # PERFORMANCE TRACKING
    # ====================
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.00), MaxValueValidator(5.00)],
        verbose_name=_("Performance Rating"),
        help_text=_("Overall performance rating (1.00-5.00)")
    )
    
    last_appraisal_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Appraisal Date")
    )
    
    next_appraisal_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Next Appraisal Date")
    )
    
    appraisal_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Last Appraisal Score")
    )
    
    # ====================
    # SALARY INFORMATION
    # ====================
    salary_scale = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('b5', _('B5 - Classroom Teacher')),
            ('c1', _('C1 - Senior Teacher')),
            ('c2', _('C2 - Senior Master I')),
            ('c3', _('C3 - Senior Master II')),
            ('c4', _('C4 - Senior Master III')),
            ('c5', _('C5 - Senior Master IV')),
            ('d1', _('D1 - Deputy Principal III')),
            ('d2', _('D2 - Deputy Principal II')),
            ('d3', _('D3 - Deputy Principal I')),
            ('d4', _('D4 - Principal')),
            ('d5', _('D5 - Senior Principal')),
        ],
        verbose_name=_("Salary Scale")
    )
    
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Basic Salary")
    )
    
    house_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("House Allowance")
    )
    
    commuter_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Commuter Allowance")
    )
    
    # ====================
    # ADDITIONAL INFORMATION
    # ====================
    subjects = models.ManyToManyField(
        'academics.Subject',
        related_name='teachers',
        blank=True,
        verbose_name=_("Subjects Currently Teaching")
    )
    
    classes = models.ManyToManyField(
        'academics.Class',
        related_name='teachers',
        blank=True,
        verbose_name=_("Classes Currently Teaching")
    )
    
    # Role Flags
    is_class_teacher = models.BooleanField(
        default=False,
        verbose_name=_("Class Teacher")
    )
    
    is_head_of_department = models.BooleanField(
        default=False,
        verbose_name=_("Head of Department")
    )
    
    is_deputy_principal = models.BooleanField(
        default=False,
        verbose_name=_("Deputy Principal")
    )
    
    is_principal = models.BooleanField(
        default=False,
        verbose_name=_("Principal")
    )
    
    is_curriculum_coordinator = models.BooleanField(
        default=False,
        verbose_name=_("Curriculum Coordinator")
    )
    
    is_guidance_counselor = models.BooleanField(
        default=False,
        verbose_name=_("Guidance and Counseling Teacher")
    )
    
    is_games_master = models.BooleanField(
        default=False,
        verbose_name=_("Games Master/Mistress")
    )
    
    # ====================
    # ADMINISTRATIVE
    # ====================
    notes = models.TextField(
        blank=True,
        verbose_name=_("Administrative Notes")
    )
    
    achievements = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Achievements"),
        help_text=_("List of teacher's achievements/awards")
    )
    
    class Meta:
        verbose_name = _("Teacher Profile")
        verbose_name_plural = _("Teacher Profiles")
        ordering = ['teacher__last_name', 'teacher__first_name']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['tsc_number']),
            models.Index(fields=['tsc_status']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['teaching_level']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['cbc_trained']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['designation']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - TSC: {self.tsc_number}"
    
    def clean(self):
        """Validate TSC requirements based on teaching level"""
        errors = {}
        
        # Validate TSC number format
        if self.tsc_number and not self.tsc_number.startswith('TSC/'):
            errors['tsc_number'] = _("TSC number should start with 'TSC/'")
        
        # Validate KCSE grades based on teaching level
        if self.teaching_level in [self.TeachingLevel.JUNIOR_SECONDARY,
                                  self.TeachingLevel.SENIOR_SECONDARY]:
            
            # Secondary teachers require minimum C+ in KCSE
            if self.kcse_mean_grade < 'C+':
                errors['kcse_mean_grade'] = _(
                    f"Secondary school teachers require minimum KCSE grade of C+. "
                    f"Current: {self.get_kcse_mean_grade_display()}"
                )
        
        # Primary teachers require minimum C in KCSE
        elif self.teaching_level == self.TeachingLevel.PRIMARY:
            if self.kcse_mean_grade < 'C':
                errors['kcse_mean_grade'] = _(
                    f"Primary school teachers require minimum KCSE grade of C. "
                    f"Current: {self.get_kcse_mean_grade_display()}"
                )
        
        # ECDE teachers require minimum C- in KCSE
        elif self.teaching_level == self.TeachingLevel.ECDE:
            if self.kcse_mean_grade < 'C-':
                errors['kcse_mean_grade'] = _(
                    f"ECDE teachers require minimum KCSE grade of C-. "
                    f"Current: {self.get_kcse_mean_grade_display()}"
                )
        
        # Validate TPD renewal date
        if self.tpd_next_renewal_date and self.tpd_last_completed_date:
            years_diff = (self.tpd_next_renewal_date - self.tpd_last_completed_date).days / 365
            if years_diff > 5:
                errors['tpd_next_renewal_date'] = _(
                    "TPD renewal should be within 5 years of last completion"
                )
        
        # Validate CBC training for Junior Secondary teachers
        if (self.teaching_level == self.TeachingLevel.JUNIOR_SECONDARY and
            not self.cbc_trained):
            errors['cbc_trained'] = _(
                "Junior Secondary teachers must be CBC trained"
            )
        
        # Validate employment dates
        if self.employment_date:
            if self.employment_date > timezone.now().date():
                errors['employment_date'] = _("Employment date cannot be in the future")
            
            if self.confirmation_date and self.confirmation_date < self.employment_date:
                errors['confirmation_date'] = _("Confirmation date must be after employment date")
            
            if self.retirement_date and self.retirement_date < self.employment_date:
                errors['retirement_date'] = _("Retirement date must be after employment date")
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Custom save logic with validation and calculations"""
        self.full_clean()
        
        # Calculate teaching load hours (assuming 40 minutes per period)
        if self.weekly_periods:
            self.teaching_load_hours = Decimal(self.weekly_periods * 40 / 60)
        
        # Update user role if teacher has special designation
        if self.is_principal:
            self.teacher.role = User.Role.HEAD_TEACHER
        elif self.is_deputy_principal or self.is_head_of_department:
            self.teacher.role = User.Role.CURRICULUM_COORDINATOR
        else:
            self.teacher.role = User.Role.TEACHER
        
        # Update user staff_id if not set
        if not self.teacher.staff_id and self.tsc_number:
            self.teacher.staff_id = self.tsc_number
        
        self.teacher.save()
        super().save(*args, **kwargs)
    
    def validate_tsc_requirements(self):
        """Comprehensive TSC requirements validation"""
        errors = []
        warnings = []
        
        # Age requirements
        age = self.age
        if age and age < 21:
            errors.append(_("Teacher must be at least 21 years old"))
        
        # Qualifications based on teaching level
        if self.teaching_level == self.TeachingLevel.SENIOR_SECONDARY:
            # Senior secondary requires degree minimum
            if 'bachelor' not in self.highest_qualification:
                errors.append(_("Senior Secondary teachers require at least a Bachelor's degree"))
        
        # Subject combination validation
        if self.teaching_subjects:
            # Check for approved subject combinations
            invalid_combinations = self._get_invalid_subject_combinations()
            if invalid_combinations:
                warnings.append(_("Invalid subject combinations: {}".format(invalid_combinations)))
        
        return {'errors': errors, 'warnings': warnings}
    
    def _get_invalid_subject_combinations(self):
        """Return invalid subject combinations based on TSC guidelines"""
        invalid_combos = []
        subjects = self.teaching_subjects
        
        # Example: Chemistry and History is unusual combination
        if 'Chemistry' in subjects and 'History' in subjects:
            invalid_combos.append("Chemistry-History")
        
        return invalid_combos
    
    # ====================
    # PROPERTIES
    # ====================
    
    @property
    def full_name(self):
        """Get teacher's full name"""
        return self.teacher.get_full_name()
    
    @property
    def email(self):
        """Get teacher's email"""
        return self.teacher.email
    
    @property
    def phone_number(self):
        """Get teacher's phone number"""
        return self.teacher.phone_number
    
    @property
    def tsc_compliant(self):
        """Check if teacher meets all TSC requirements"""
        checks = [
            bool(self.tsc_number),
            self.tsc_status in [self.TSCStatus.REGISTERED, self.TSCStatus.PROVISIONAL],
            bool(self.highest_qualification),
        ]
        
        # Additional checks based on teaching level
        if self.teaching_level == self.TeachingLevel.JUNIOR_SECONDARY:
            checks.append(self.cbc_trained)
        
        # Check TPD status
        if self.tpd_next_renewal_date:
            checks.append(timezone.now().date() <= self.tpd_next_renewal_date)
        
        return all(checks)
    
    @property
    def years_of_service(self):
        """Calculate years of service from employment date"""
        if self.employment_date:
            today = timezone.now().date()
            years = today.year - self.employment_date.year
            if (today.month, today.day) < (self.employment_date.month, self.employment_date.day):
                years -= 1
            return years
        return 0
    
    @property
    def months_to_retirement(self):
        """Calculate months until retirement"""
        if self.retirement_date:
            today = timezone.now().date()
            if self.retirement_date > today:
                months = (self.retirement_date.year - today.year) * 12
                months += self.retirement_date.month - today.month
                return months
        return None
    
    @property
    def age(self):
        """Calculate teacher's age"""
        return self.teacher.age
    
    @property
    def total_salary(self):
        """Calculate total salary with allowances"""
        total = Decimal('0.00')
        if self.basic_salary:
            total += self.basic_salary
        if self.house_allowance:
            total += self.house_allowance
        if self.commuter_allowance:
            total += self.commuter_allowance
        return total
    
    @property
    def tsc_summary(self):
        """Get TSC compliance summary"""
        return {
            'tsc_number': self.tsc_number,
            'tsc_status': self.get_tsc_status_display(),
            'registration_date': self.tsc_registration_date,
            'teaching_level': self.get_teaching_level_display(),
            'highest_qualification': self.get_highest_qualification_display(),
            'cbc_trained': self.cbc_trained,
            'tpd_current': self.tpd_current_module,
            'tpd_renewal_due': self.tpd_next_renewal_date,
            'is_tsc_compliant': self.tsc_compliant,
            'tsc_category': self.get_tsc_category_display(),
            'payroll_number': self.tsc_payroll_number,
        }
    
    @property
    def qualification_summary(self):
        """Get qualification summary"""
        return {
            'highest_qualification': self.get_highest_qualification_display(),
            'institution': self.qualification_institution,
            'year_of_graduation': self.year_of_graduation,
            'kcse_mean_grade': self.get_kcse_mean_grade_display(),
            'kcse_index_number': self.kcse_index_number,
            'kcse_year': self.kcse_year,
            'teaching_subjects': self.teaching_subjects,
        }
    
    @property
    def employment_summary(self):
        """Get employment summary"""
        return {
            'employment_type': self.get_employment_type_display(),
            'employment_status': self.get_employment_status_display(),
            'employment_date': self.employment_date,
            'years_of_service': self.years_of_service,
            'department': str(self.department) if self.department else None,
            'designation': self.get_designation_display(),
            'salary_scale': self.salary_scale,
            'basic_salary': self.basic_salary,
            'total_salary': self.total_salary,
        }
    
    # ====================
    # CLASS METHODS
    # ====================
    
    @classmethod
    def get_teachers_by_subject(cls, subject_name):
        """Get all teachers qualified to teach a specific subject"""
        return cls.objects.filter(
            teaching_subjects__contains=[subject_name],
            is_active=True,
            employment_status='active'
        )
    
    @classmethod
    def get_available_cover_teachers(cls, date, period_count=1):
        """Get teachers available for cover duties on specific date"""
        # Teachers who are present, not on leave, and have capacity
        from datetime import timedelta
        
        # Get teachers on leave that day
        on_leave = cls.objects.filter(
            leave_applications__start_date__lte=date,
            leave_applications__end_date__gte=date,
            leave_applications__status='approved'
        ).values_list('id', flat=True)
        
        # Get available teachers (present, not on leave, with capacity)
        return cls.objects.filter(
            is_active=True,
            employment_status='active'
        ).exclude(
            id__in=on_leave
        ).filter(
            weekly_periods__lt=40  # Has capacity for more periods
        )
    
    # ====================
    # METHODS
    # ====================
    
    def update_tpd_module(self, new_module, completion_date=None):
        """Update TPD module and set renewal date"""
        if 1 <= new_module <= 6:
            self.tpd_current_module = new_module
            self.tpd_last_completed_date = completion_date or timezone.now().date()
            
            # Set next renewal date (5 years from completion)
            self.tpd_next_renewal_date = self.tpd_last_completed_date.replace(
                year=self.tpd_last_completed_date.year + 5
            )
            
            self.save()
            return True
        return False
    
    def mark_cbc_trained(self, training_date=None, certificate_file=None):
        """Mark teacher as CBC trained"""
        self.cbc_trained = True
        self.cbc_training_date = training_date or timezone.now().date()
        
        if certificate_file:
            # In a real implementation, you would save the file
            pass
        
        self.save()
        return True
    
    def generate_tsc_report(self):
        """Generate comprehensive TSC report"""
        return {
            'personal_info': {
                'name': self.full_name,
                'tsc_number': self.tsc_number,
                'id_number': self.teacher.id_number,
                'date_of_birth': self.teacher.date_of_birth,
                'gender': self.teacher.get_gender_display(),
                'nationality': self.teacher.nationality,
            },
            'qualifications': self.qualification_summary,
            'employment': self.employment_summary,
            'compliance': {
                'tsc_compliant': self.tsc_compliant,
                'requirements_met': self._check_tsc_requirements(),
                'documents_verified': self._get_verified_documents(),
            },
            'professional_development': {
                'tpd_module': self.tpd_current_module,
                'last_tpd_date': self.tpd_last_completed_date,
                'next_renewal': self.tpd_next_renewal_date,
                'cbc_trained': self.cbc_trained,
                'cbc_training_date': self.cbc_training_date,
                'cbc_training_level': self.get_cbc_training_level_display() if self.cbc_training_level else None,
            },
            'performance': {
                'rating': self.performance_rating,
                'last_appraisal': self.last_appraisal_date,
                'next_appraisal': self.next_appraisal_date,
                'appraisal_score': self.appraisal_score,
            }
        }
    
    def _check_tsc_requirements(self):
        """Check specific TSC requirements"""
        requirements = {
            'tsc_registration': bool(self.tsc_number) and self.tsc_status in [self.TSCStatus.REGISTERED, self.TSCStatus.PROVISIONAL],
            'academic_qualifications': bool(self.highest_qualification),
            'kcse_requirements': self._check_kcse_requirements(),
            'professional_certification': bool(self.teacher.id_number),  # Assuming ID is required
        }
        
        if self.teaching_level == self.TeachingLevel.JUNIOR_SECONDARY:
            requirements['cbc_training'] = self.cbc_trained
        
        if self.employment_type in [self.EmploymentType.PERMANENT_TSC, self.EmploymentType.CONTRACT_TSC]:
            requirements['tpd_current'] = self.tpd_current_module >= 1
            requirements['tpd_valid'] = not self.tpd_next_renewal_date or timezone.now().date() <= self.tpd_next_renewal_date
        
        return requirements
    
    def _check_kcse_requirements(self):
        """Check KCSE requirements based on teaching level"""
        if self.teaching_level in [self.TeachingLevel.JUNIOR_SECONDARY,
                                  self.TeachingLevel.SENIOR_SECONDARY]:
            return self.kcse_mean_grade >= 'C+'
        elif self.teaching_level == self.TeachingLevel.PRIMARY:
            return self.kcse_mean_grade >= 'C'
        elif self.teaching_level == self.TeachingLevel.ECDE:
            return self.kcse_mean_grade >= 'C-'
        return True
    
    def _get_verified_documents(self):
        """Get list of verified documents"""
        # This would check TeacherDocument model
        return {
            'tsc_certificate': False,
            'good_conduct': False,
            'academic_certificates': False,
            'id_copy': bool(self.teacher.id_number),
        }
    
    def get_current_classes(self):
        """Get classes currently assigned to teacher"""
        return self.classes.filter(is_active=True)
    
    def get_current_subjects(self):
        """Get subjects currently taught by teacher"""
        return self.subjects.filter(is_active=True)
    
    def calculate_workload(self):
        """Calculate teacher's current workload"""
        classes_count = self.get_current_classes().count()
        subjects_count = self.get_current_subjects().count()
        periods_per_week = self.weekly_periods or 0
        
        return {
            'classes': classes_count,
            'subjects': subjects_count,
            'periods_per_week': periods_per_week,
            'teaching_hours': self.teaching_load_hours,
            'workload_percentage': (periods_per_week / 45 * 100) if periods_per_week else 0,  # 45 is max recommended
        }


# ============================================================================
# PROFESSIONAL STANDING MODEL
# ============================================================================

class ProfessionalStanding(BaseModel):
    """Track teacher's professional standing and disciplinary records"""
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='professional_standings'
    )
    
    record_type = models.CharField(
        max_length=30,
        choices=[
            ('disciplinary', _('Disciplinary Action')),
            ('warning', _('Warning Letter')),
            ('commendation', _('Commendation')),
            ('promotion', _('Promotion Recommendation')),
            ('transfer', _('Transfer Recommendation')),
            ('other', _('Other Record')),
        ]
    )
    
    date = models.DateField()
    description = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='active')
    resolution_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # File attachments
    document = models.FileField(upload_to='professional_records/', null=True, blank=True)
    
    class Meta:
        ordering = ['-date']


# ============================================================================
# PERFORMANCE INDICATOR MODEL - FIXED
# ============================================================================

class PerformanceIndicator(BaseModel):  # FIXED: Now inherits from BaseModel
    """Track teacher performance indicators"""
    
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='performance_indicators')
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.Term', on_delete=models.CASCADE, null=True, blank=True)
    
    # Academic performance
    student_performance_average = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    improvement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Professional conduct
    punctuality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    lesson_preparation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    record_keeping_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Student engagement
    student_engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    parent_satisfaction_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Professional development
    pd_completion_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    innovation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Overall
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    evaluation_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Performance Indicator")
        verbose_name_plural = _("Performance Indicators")
        ordering = ['-evaluation_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['overall_score']),
            models.Index(fields=['is_active']),  # Now has is_active from BaseModel
        ]


# ============================================================================
# TEACHER TRANSFER MODEL
# ============================================================================

class TeacherTransfer(BaseModel):
    """Track teacher transfers between schools"""
    
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    
    transfer_type = models.CharField(
        max_length=30,
        choices=[
            ('inter_school', _('Inter-School Transfer')),
            ('intra_school', _('Intra-School Transfer')),
            ('promotional', _('Promotional Transfer')),
            ('requested', _('Requested Transfer')),
            ('disciplinary', _('Disciplinary Transfer')),
        ]
    )
    
    from_school = models.ForeignKey('institutions.School', on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_school = models.ForeignKey('institutions.School', on_delete=models.CASCADE, related_name='incoming_transfers')
    
    effective_date = models.DateField()
    reason = models.TextField()
    
    # Approval workflow
    applied_date = models.DateField(auto_now_add=True)
    approved_by_sending = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_sending_transfers')
    approved_by_receiving = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_receiving_transfers')
    approved_by_tsc = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_tsc_transfers')
    
    # Transfer details
    handover_completed = models.BooleanField(default=False)
    handover_date = models.DateField(null=True, blank=True)
    handover_notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', _('Draft')),
            ('pending', _('Pending Approval')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('completed', _('Completed')),
        ],
        default='draft'
    )
    
    class Meta:
        verbose_name = _("Teacher Transfer")
        verbose_name_plural = _("Teacher Transfers")
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['transfer_type']),
            models.Index(fields=['status']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['is_active']),
        ]


# ============================================================================
# TEACHER DOCUMENT MODEL
# ============================================================================

class TeacherDocument(BaseModel):
    """Model for storing teacher documents required by TSC and school administration"""
    
    DOCUMENT_TYPES = [
        ('tsc_certificate', _('TSC Certificate')),
        ('good_conduct', _('Certificate of Good Conduct')),
        ('academic_certificate', _('Academic Certificate')),
        ('transcript', _('Academic Transcript')),
        ('cbc_certificate', _('CBC Training Certificate')),
        ('tpd_certificate', _('TPD Certificate')),
        ('id_copy', _('National ID/Passport Copy')),
        ('kra_pin', _('KRA PIN Certificate')),
        ('nssf_card', _('NSSF Card')),
        ('nhif_card', _('NHIF Card')),
        ('appointment_letter', _('Appointment Letter')),
        ('confirmation_letter', _('Confirmation Letter')),
        ('promotion_letter', _('Promotion Letter')),
        ('transfer_letter', _('Transfer Letter')),
        ('medical_report', _('Medical Report')),
        ('birth_certificate', _('Birth Certificate')),
        ('marriage_certificate', _('Marriage Certificate')),
        ('police_clearance', _('Police Clearance Certificate')),
        ('cv_resume', _('CV/Resume')),
        ('reference_letter', _('Reference Letter')),
        ('performance_appraisal', _('Performance Appraisal Form')),
        ('leave_document', _('Leave Application/Approval')),
        ('disciplinary', _('Disciplinary Document')),
        ('other', _('Other Document')),
    ]
    
    DOCUMENT_STATUS = [
        ('pending', _('Pending Review')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
        ('missing', _('Missing')),
        ('under_review', _('Under Review')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Teacher")
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES,
        verbose_name=_("Document Type")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Document Title")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    document_file = models.FileField(
        upload_to='teacher_documents/%Y/%m/%d/',
        storage=teacher_document_storage,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        verbose_name=_("Document File")
    )
    
    file_size = models.BigIntegerField(
        default=0,
        verbose_name=_("File Size (bytes)")
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Upload Date")
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Expiry Date")
    )
    
    status = models.CharField(
        max_length=20,
        choices=DOCUMENT_STATUS,
        default='pending',
        verbose_name=_("Status")
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        verbose_name=_("Verified By")
    )
    
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Verification Date")
    )
    
    verification_notes = models.TextField(
        blank=True,
        verbose_name=_("Verification Notes")
    )
    
    is_required = models.BooleanField(
        default=True,
        verbose_name=_("Required Document")
    )
    
    is_archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived")
    )
    
    class Meta:
        verbose_name = _("Teacher Document")
        verbose_name_plural = _("Teacher Documents")
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['is_required']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'document_type'],
                condition=models.Q(is_active=True),
                name='unique_active_document_type_per_teacher'
            )
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_document_type_display()}"
    
    def clean(self):
        """Validate document requirements"""
        errors = {}
        
        # Check file size (max 10MB)
        if self.document_file and self.document_file.size > 10 * 1024 * 1024:
            errors['document_file'] = _("File size cannot exceed 10MB")
        
        # Check expiry date
        if self.expiry_date and self.expiry_date < timezone.now().date():
            if self.status != 'expired':
                errors['expiry_date'] = _("Document has expired. Please update status to 'Expired'")
        
        # Validate document type based on teacher's employment type
        if self.teacher and self.document_type == 'tsc_certificate':
            if self.teacher.employment_type in ['permanent_tsc', 'contract_tsc', 'intern']:
                self.is_required = True
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Save document with file size calculation"""
        if self.document_file:
            self.file_size = self.document_file.size
        
        # Set title if not provided
        if not self.title:
            self.title = f"{self.get_document_type_display()} - {self.teacher.full_name}"
        
        super().save(*args, **kwargs)
    
    @property
    def file_url(self):
        """Get document URL"""
        if self.document_file:
            return self.document_file.url
        return None
    
    @property
    def file_extension(self):
        """Get file extension"""
        if self.document_file:
            return self.document_file.name.split('.')[-1].lower()
        return None
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def days_to_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            today = timezone.now().date()
            if self.expiry_date >= today:
                return (self.expiry_date - today).days
        return None
    
    def verify_document(self, user, status='verified', notes=''):
        """Verify or reject a document"""
        if user and user.is_staff:
            self.status = status
            self.verified_by = user
            self.verification_date = timezone.now()
            self.verification_notes = notes
            self.save()
            return True
        return False
    
    def archive_document(self):
        """Archive document (soft delete)"""
        self.is_archived = True
        self.is_active = False
        self.save()


# ============================================================================
# TEACHER QUALIFICATION MODEL
# ============================================================================

class TeacherQualification(BaseModel):
    """Model for storing teacher's academic and professional qualifications"""
    
    QUALIFICATION_TYPES = [
        ('primary', _('Primary Education Certificate')),
        ('secondary', _('Secondary Education Certificate')),
        ('certificate', _('Certificate')),
        ('diploma', _('Diploma')),
        ('bachelor', _("Bachelor's Degree")),
        ('postgraduate_diploma', _('Postgraduate Diploma')),
        ('masters', _("Master's Degree")),
        ('phd', _('Doctorate (PhD)')),
        ('professional', _('Professional Certification')),
        ('training', _('Training Certificate')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='qualifications',
        verbose_name=_("Teacher")
    )
    
    qualification_type = models.CharField(
        max_length=30,
        choices=QUALIFICATION_TYPES,
        verbose_name=_("Qualification Type")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Qualification Title")
    )
    
    institution = models.CharField(
        max_length=200,
        verbose_name=_("Institution")
    )
    
    institution_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Institution Location")
    )
    
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Field of Study")
    )
    
    grade_classification = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Grade/Classification")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Completion Date")
    )
    
    is_completed = models.BooleanField(
        default=True,
        verbose_name=_("Completed")
    )
    
    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Certificate Number")
    )
    
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('not_verified', _('Not Verified')),
            ('pending', _('Verification Pending')),
            ('verified', _('Verified')),
            ('rejected', _('Verification Rejected')),
        ],
        default='not_verified',
        verbose_name=_("Verification Status")
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_qualifications',
        verbose_name=_("Verified By")
    )
    
    verification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Verification Date")
    )
    
    verification_notes = models.TextField(
        blank=True,
        verbose_name=_("Verification Notes")
    )
    
    document = models.ForeignKey(
        TeacherDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qualifications',
        verbose_name=_("Supporting Document")
    )
    
    class Meta:
        verbose_name = _("Teacher Qualification")
        verbose_name_plural = _("Teacher Qualifications")
        ordering = ['-end_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['qualification_type']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.title}"
    
    def clean(self):
        """Validate qualification dates"""
        errors = {}
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            if self.completion_date:
                if self.completion_date < self.start_date:
                    errors['completion_date'] = _("Completion date cannot be before start date")
                if self.completion_date > self.end_date:
                    errors['completion_date'] = _("Completion date cannot be after end date")
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def duration_years(self):
        """Calculate duration in years"""
        if self.start_date and self.end_date:
            years = self.end_date.year - self.start_date.year
            if (self.end_date.month, self.end_date.day) < (self.start_date.month, self.start_date.day):
                years -= 1
            return years
        return None
    
    @property
    def is_current(self):
        """Check if qualification is currently ongoing"""
        if not self.is_completed and self.end_date:
            return self.end_date >= timezone.now().date()
        return False
    
    def verify_qualification(self, user, status='verified', notes=''):
        """Verify qualification"""
        if user and user.is_staff:
            self.verification_status = status
            self.verified_by = user
            self.verification_date = timezone.now().date()
            self.verification_notes = notes
            self.save()
            return True
        return False


# ============================================================================
# TEACHER TRAINING MODEL
# ============================================================================

class TeacherTraining(BaseModel):
    """Model for tracking teacher professional development and training"""
    
    TRAINING_TYPES = [
        ('cbc', _('CBC Training')),
        ('tpd', _('Teacher Professional Development')),
        ('subject_specific', _('Subject-Specific Training')),
        ('pedagogy', _('Pedagogical Training')),
        ('technology', _('Technology Integration')),
        ('leadership', _('Leadership Training')),
        ('special_needs', _('Special Needs Education')),
        ('assessment', _('Assessment & Evaluation')),
        ('classroom_management', _('Classroom Management')),
        ('guidance_counseling', _('Guidance & Counseling')),
        ('health_safety', _('Health & Safety')),
        ('other', _('Other Training')),
    ]
    
    TRAINING_MODES = [
        ('online', _('Online')),
        ('in_person', _('In-Person')),
        ('hybrid', _('Hybrid')),
        ('workshop', _('Workshop')),
        ('seminar', _('Seminar')),
        ('conference', _('Conference')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='trainings',
        verbose_name=_("Teacher")
    )
    
    training_type = models.CharField(
        max_length=50,
        choices=TRAINING_TYPES,
        verbose_name=_("Training Type")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Training Title")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    organizer = models.CharField(
        max_length=200,
        verbose_name=_("Organizing Institution")
    )
    
    training_mode = models.CharField(
        max_length=20,
        choices=TRAINING_MODES,
        default='in_person',
        verbose_name=_("Training Mode")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Duration (Hours)")
    )
    
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name=_("Mandatory Training")
    )
    
    is_certified = models.BooleanField(
        default=True,
        verbose_name=_("Certified")
    )
    
    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Certificate Number")
    )
    
    certificate_issued_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Certificate Issue Date")
    )
    
    certificate_validity_years = models.IntegerField(
        default=5,
        verbose_name=_("Certificate Validity (Years)")
    )
    
    assessment_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Assessment Score")
    )
    
    feedback = models.TextField(
        blank=True,
        verbose_name=_("Feedback")
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('registered', _('Registered')),
            ('in_progress', _('In Progress')),
            ('completed', _('Completed')),
            ('cancelled', _('Cancelled')),
            ('failed', _('Failed')),
        ],
        default='registered',
        verbose_name=_("Status")
    )
    
    document = models.ForeignKey(
        TeacherDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainings',
        verbose_name=_("Training Certificate")
    )
    
    class Meta:
        verbose_name = _("Teacher Training")
        verbose_name_plural = _("Teacher Trainings")
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['training_type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_mandatory']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.title}"
    
    def clean(self):
        """Validate training dates"""
        errors = {}
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if training is in the future
            if self.start_date > timezone.now().date() and self.status == 'completed':
                errors['status'] = _("Cannot mark training as completed before it starts")
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def is_current(self):
        """Check if training is currently ongoing"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'in_progress'
    
    @property
    def certificate_expiry_date(self):
        """Calculate certificate expiry date"""
        if self.certificate_issued_date and self.certificate_validity_years:
            return self.certificate_issued_date.replace(
                year=self.certificate_issued_date.year + self.certificate_validity_years
            )
        return None
    
    @property
    def is_certificate_valid(self):
        """Check if certificate is still valid"""
        expiry_date = self.certificate_expiry_date
        if expiry_date:
            return timezone.now().date() <= expiry_date
        return False
    
    def complete_training(self, score=None, feedback=''):
        """Mark training as completed"""
        self.status = 'completed'
        if score:
            self.assessment_score = score
        if feedback:
            self.feedback = feedback
        if not self.certificate_issued_date:
            self.certificate_issued_date = timezone.now().date()
        self.save()
        
        # Update teacher's CBC status if applicable
        if self.training_type == 'cbc' and 'CBC' in self.title:
            self.teacher.mark_cbc_trained(self.certificate_issued_date)
        
        return True


# ============================================================================
# TEACHER ASSIGNMENT MODEL
# ============================================================================

class TeacherAssignment(BaseModel):
    """Model for tracking teacher assignments to classes and subjects"""
    
    ASSIGNMENT_TYPES = [
        ('teaching', _('Teaching Assignment')),
        ('administrative', _('Administrative Duty')),
        ('committee', _('Committee Membership')),
        ('co_curricular', _('Co-curricular Activity')),
        ('pastoral', _('Pastoral Duty')),
        ('supervisory', _('Supervisory Duty')),
        ('other', _('Other Assignment')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_("Teacher")
    )
    
    assignment_type = models.CharField(
        max_length=30,
        choices=ASSIGNMENT_TYPES,
        default='teaching',
        verbose_name=_("Assignment Type")
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Assignment Title")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    
    academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.CASCADE,
        verbose_name=_("Academic Year")
    )
    
    term = models.ForeignKey(
        'academics.Term',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Term")
    )
    
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Subject")
    )
    
    class_assigned = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Class")
    )
    
    stream = models.ForeignKey(
        'academics.Stream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Stream")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    weekly_periods = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name=_("Weekly Periods")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    is_primary_assignment = models.BooleanField(
        default=False,
        verbose_name=_("Primary Assignment")
    )
    
    workload_factor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.01), MaxValueValidator(5.00)],
        verbose_name=_("Workload Factor")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_assignments',
        verbose_name=_("Approved By")
    )
    
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Approval Date")
    )
    
    class Meta:
        verbose_name = _("Teacher Assignment")
        verbose_name_plural = _("Teacher Assignments")
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['assignment_type']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['subject']),
            models.Index(fields=['class_assigned']),
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'subject', 'class_assigned', 'academic_year'],
                condition=models.Q(is_active=True),
                name='unique_active_assignment'
            )
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.title}"
    
    def clean(self):
        """Validate assignment details"""
        errors = {}
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if assignment overlaps with academic year
            if self.academic_year:
                if self.start_date < self.academic_year.start_date:
                    errors['start_date'] = _("Assignment cannot start before academic year")
                if self.end_date > self.academic_year.end_date:
                    errors['end_date'] = _("Assignment cannot end after academic year")
        
        # Validate teaching assignment requirements
        if self.assignment_type == 'teaching':
            if not self.subject:
                errors['subject'] = _("Teaching assignment requires a subject")
            if not self.class_assigned:
                errors['class_assigned'] = _("Teaching assignment requires a class")
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Save assignment with updates to teacher's workload"""
        super().save(*args, **kwargs)
        
        # Update teacher's total weekly periods if this is a teaching assignment
        if self.assignment_type == 'teaching' and self.is_active:
            self._update_teacher_workload()
    
    def _update_teacher_workload(self):
        """Update teacher's total workload"""
        active_teaching_assignments = TeacherAssignment.objects.filter(
            teacher=self.teacher,
            assignment_type='teaching',
            is_active=True,
            academic_year=self.academic_year
        )
        
        total_periods = sum(assignment.weekly_periods for assignment in active_teaching_assignments)
        
        # Update teacher's weekly periods
        if total_periods != self.teacher.weekly_periods:
            self.teacher.weekly_periods = total_periods
            self.teacher.save()
    
    @property
    def duration_weeks(self):
        """Calculate duration in weeks"""
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            return max(1, days // 7)
        return None
    
    @property
    def workload_hours(self):
        """Calculate workload hours (40 minutes per period)"""
        return Decimal(self.weekly_periods * 40 / 60)
    
    @property
    def adjusted_workload_hours(self):
        """Calculate adjusted workload hours with factor"""
        return self.workload_hours * self.workload_factor
    
    def activate_assignment(self):
        """Activate assignment"""
        self.is_active = True
        self.save()
    
    def deactivate_assignment(self):
        """Deactivate assignment"""
        self.is_active = False
        self.save()
        self._update_teacher_workload()


# ============================================================================
# TEACHER ATTENDANCE MODEL
# ============================================================================

class TeacherAttendance(BaseModel):
    """Model for tracking teacher attendance"""
    
    ATTENDANCE_STATUS = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('late', _('Late')),
        ('half_day', _('Half Day')),
        ('leave', _('On Leave')),
        ('off_duty', _('Off Duty')),
        ('training', _('On Training')),
        ('sick', _('Sick')),
        ('emergency', _('Emergency Leave')),
        ('other', _('Other')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("Teacher")
    )
    
    date = models.DateField(
        verbose_name=_("Date")
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
    
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='present',
        verbose_name=_("Status")
    )
    
    is_late = models.BooleanField(
        default=False,
        verbose_name=_("Late Arrival")
    )
    
    late_minutes = models.IntegerField(
        default=0,
        verbose_name=_("Late Minutes")
    )
    
    is_early_departure = models.BooleanField(
        default=False,
        verbose_name=_("Early Departure")
    )
    
    early_departure_minutes = models.IntegerField(
        default=0,
        verbose_name=_("Early Departure Minutes")
    )
    
    working_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Working Hours")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Verified By")
    )
    
    verification_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Verification Time")
    )
    
    class Meta:
        verbose_name = _("Teacher Attendance")
        verbose_name_plural = _("Teacher Attendance Records")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'date'],
                name='unique_attendance_per_teacher_per_day'
            )
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        """Validate attendance data"""
        errors = {}
        
        # Check if date is in the future
        if self.date > timezone.now().date():
            errors['date'] = _("Attendance date cannot be in the future")
        
        # Check if check-out is before check-in
        if self.check_in_time and self.check_out_time:
            if self.check_out_time <= self.check_in_time:
                errors['check_out_time'] = _("Check-out time must be after check-in time")
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Calculate working hours and late status"""
        # Calculate working hours
        if self.check_in_time and self.check_out_time:
            # Convert times to minutes
            check_in_minutes = self.check_in_time.hour * 60 + self.check_in_time.minute
            check_out_minutes = self.check_out_time.hour * 60 + self.check_out_time.minute
            
            working_minutes = check_out_minutes - check_in_minutes
            self.working_hours = Decimal(working_minutes / 60)
            
            # Check for early departure (before 4:00 PM)
            if check_out_minutes < (16 * 60):  # 4:00 PM
                self.is_early_departure = True
                self.early_departure_minutes = (16 * 60) - check_out_minutes
            
            # Check for late arrival (after 8:00 AM)
            if check_in_minutes > (8 * 60):  # 8:00 AM
                self.is_late = True
                self.late_minutes = check_in_minutes - (8 * 60)
        
        super().save(*args, **kwargs)
    
    @property
    def is_full_day(self):
        """Check if teacher worked a full day"""
        return self.working_hours >= Decimal('7.5')
    
    @property
    def is_absent(self):
        """Check if teacher was absent"""
        return self.status in ['absent', 'sick', 'leave']
    
    @property
    def attendance_summary(self):
        """Get attendance summary"""
        return {
            'date': self.date,
            'status': self.get_status_display(),
            'check_in': self.check_in_time,
            'check_out': self.check_out_time,
            'working_hours': float(self.working_hours),
            'is_late': self.is_late,
            'late_minutes': self.late_minutes,
            'is_early_departure': self.is_early_departure,
            'early_departure_minutes': self.early_departure_minutes,
            'is_full_day': self.is_full_day,
        }


# ============================================================================
# TEACHER LEAVE MODEL
# ============================================================================

class TeacherLeave(BaseModel):
    """Model for tracking teacher leave applications"""
    
    LEAVE_TYPES = [
        ('annual', _('Annual Leave')),
        ('sick', _('Sick Leave')),
        ('maternity', _('Maternity Leave')),
        ('paternity', _('Paternity Leave')),
        ('study', _('Study Leave')),
        ('compassionate', _('Compassionate Leave')),
        ('emergency', _('Emergency Leave')),
        ('unpaid', _('Unpaid Leave')),
        ('other', _('Other Leave')),
    ]
    
    LEAVE_STATUS = [
        ('draft', _('Draft')),
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
        ('in_progress', _('Leave in Progress')),
        ('completed', _('Completed')),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        verbose_name=_("Teacher")
    )
    
    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPES,
        verbose_name=_("Leave Type")
    )
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    days_requested = models.IntegerField(
        verbose_name=_("Days Requested")
    )
    
    reason = models.TextField(
        verbose_name=_("Reason for Leave")
    )
    
    contact_address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Contact Address During Leave")
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Contact Phone During Leave")
    )
    
    emergency_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Emergency Contact")
    )
    
    status = models.CharField(
        max_length=20,
        choices=LEAVE_STATUS,
        default='draft',
        verbose_name=_("Status")
    )
    
    applied_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("Applied Date")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name=_("Approved By")
    )
    
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Approval Date")
    )
    
    approval_notes = models.TextField(
        blank=True,
        verbose_name=_("Approval Notes")
    )
    
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_leaves',
        verbose_name=_("Rejected By")
    )
    
    rejection_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Rejection Date")
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_("Rejection Reason")
    )
    
    documents = models.ManyToManyField(
        TeacherDocument,
        blank=True,
        related_name='leave_applications',
        verbose_name=_("Supporting Documents")
    )
    
    cover_teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='covered_leaves',
        verbose_name=_("Cover Teacher")
    )
    
    handover_notes = models.TextField(
        blank=True,
        verbose_name=_("Handover Notes")
    )
    
    class Meta:
        verbose_name = _("Teacher Leave")
        verbose_name_plural = _("Teacher Leaves")
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['leave_type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_leave_type_display()} - {self.start_date}"
    
    def clean(self):
        """Validate leave application"""
        errors = {}
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if leave is in the past
            if self.start_date < timezone.now().date() and self.status not in ['completed', 'in_progress']:
                errors['start_date'] = _("Cannot apply for leave in the past")
            
            # Calculate days requested
            days = (self.end_date - self.start_date).days + 1
            if days != self.days_requested:
                self.days_requested = days
        
        # Validate leave type constraints
        if self.leave_type == 'maternity':
            if self.teacher.teacher.gender != 'female':
                errors['leave_type'] = _("Maternity leave is only for female teachers")
            if self.days_requested > 90:
                errors['days_requested'] = _("Maternity leave cannot exceed 90 days")
        
        elif self.leave_type == 'paternity':
            if self.teacher.teacher.gender != 'male':
                errors['leave_type'] = _("Paternity leave is only for male teachers")
            if self.days_requested > 14:
                errors['days_requested'] = _("Paternity leave cannot exceed 14 days")
        
        elif self.leave_type == 'sick':
            if self.days_requested > 30:
                errors['days_requested'] = _("Sick leave without medical certificate cannot exceed 30 days")
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def is_current(self):
        """Check if leave is currently active"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'approved'
    
    @property
    def days_remaining(self):
        """Calculate days remaining in leave"""
        if self.is_current:
            today = timezone.now().date()
            return (self.end_date - today).days + 1
        return 0
    
    @property
    def leave_summary(self):
        """Get leave summary"""
        return {
            'teacher': self.teacher.full_name,
            'leave_type': self.get_leave_type_display(),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'days_requested': self.days_requested,
            'status': self.get_status_display(),
            'is_current': self.is_current,
            'days_remaining': self.days_remaining,
            'approved_by': self.approved_by.get_full_name() if self.approved_by else None,
            'approval_date': self.approval_date,
        }
    
    def submit_for_approval(self):
        """Submit leave for approval"""
        if self.status == 'draft':
            self.status = 'pending'
            self.save()
            return True
        return False
    
    def approve_leave(self, user, notes=''):
        """Approve leave application"""
        if user and user.is_staff:
            self.status = 'approved'
            self.approved_by = user
            self.approval_date = timezone.now().date()
            self.approval_notes = notes
            self.save()
            
            # Create attendance records for leave period
            self._create_leave_attendance_records()
            
            return True
        return False
    
    def reject_leave(self, user, reason=''):
        """Reject leave application"""
        if user and user.is_staff:
            self.status = 'rejected'
            self.rejected_by = user
            self.rejection_date = timezone.now().date()
            self.rejection_reason = reason
            self.save()
            return True
        return False
    
    def _create_leave_attendance_records(self):
        """Create attendance records for leave period"""
        current_date = self.start_date
        while current_date <= self.end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday-Friday
                TeacherAttendance.objects.get_or_create(
                    teacher=self.teacher,
                    date=current_date,
                    defaults={
                        'status': 'leave',
                        'notes': f"{self.get_leave_type_display()} - {self.reason}"
                    }
                )
            current_date += timedelta(days=1)


# ============================================================================
# QUERY MANAGERS
# ============================================================================

class TeacherProfileQuerySet(models.QuerySet):
    """Custom QuerySet for TeacherProfile"""
    
    def active_teachers(self):
        """Get all active teachers"""
        return self.filter(
            is_active=True,  # From BaseModel inheritance
            employment_status='active',
            teacher__is_active=True  # From User model
        )
    
    def tsc_registered(self):
        """Get all TSC registered teachers"""
        return self.filter(
            tsc_status__in=['registered', 'provisional', 'intern'],
            is_active=True
        )
    
    def cbc_trained(self):
        """Get all CBC trained teachers"""
        return self.filter(
            cbc_trained=True,
            is_active=True
        )
    
    def by_department(self, department_id):
        """Get teachers by department"""
        return self.filter(
            department_id=department_id,
            is_active=True,
            department__is_active=True
        )
    
    def by_teaching_level(self, level):
        """Get teachers by teaching level"""
        return self.filter(
            teaching_level=level,
            is_active=True
        )
    
    def with_expiring_tpd(self, days=30):
        """Get teachers with TPD expiring within specified days"""
        today = timezone.now().date()
        expiry_date = today + timedelta(days=days)
        
        return self.filter(
            tpd_next_renewal_date__range=[today, expiry_date],
            is_active=True
        )
    
    def on_leave(self):
        """Get teachers currently on leave"""
        return self.filter(
            employment_status__in=['on_leave', 'study_leave', 'maternity_leave', 'paternity_leave', 'sick_leave'],
            is_active=True
        )
    

class TeacherProfileManager(models.Manager):
    """Custom manager for TeacherProfile"""
    
    def get_queryset(self):
        return TeacherProfileQuerySet(self.model, using=self._db)
    
    def active_teachers(self):
        return self.get_queryset().active_teachers()
    
    def tsc_registered(self):
        return self.get_queryset().tsc_registered()
    
    def cbc_trained(self):
        return self.get_queryset().cbc_trained()
    
    def by_department(self, department_id):
        return self.get_queryset().by_department(department_id)
    
    def by_teaching_level(self, level):
        return self.get_queryset().by_teaching_level(level)
    
    def with_expiring_tpd(self, days=30):
        return self.get_queryset().with_expiring_tpd(days)
    
    def on_leave(self):
        return self.get_queryset().on_leave()


# ============================================================================
# SIGNALS & RECEIVERS
# ============================================================================

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save, sender=TeacherProfile)
def update_user_role(sender, instance, created, **kwargs):
    """
    Update user role when teacher profile is created or updated
    """
    if instance.teacher:
        # Update user staff_id from TSC number
        if not instance.teacher.staff_id and instance.tsc_number:
            instance.teacher.staff_id = instance.tsc_number
        
        # Set user role based on teacher designation
        if instance.is_principal:
            instance.teacher.role = User.Role.HEAD_TEACHER
        elif instance.is_deputy_principal:
            instance.teacher.role = User.Role.DEPUTY_PRINCIPAL
        elif instance.is_head_of_department:
            instance.teacher.role = User.Role.CURRICULUM_COORDINATOR
        else:
            instance.teacher.role = User.Role.TEACHER
        
        instance.teacher.save()


@receiver(pre_save, sender=TeacherDocument)
def check_document_expiry(sender, instance, **kwargs):
    """
    Automatically mark documents as expired
    """
    if instance.expiry_date and instance.expiry_date < timezone.now().date():
        instance.status = 'expired'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_tsc_number():
    """Generate a unique TSC number"""
    while True:
        # Format: TSC/XXXXX/YYYY
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=5))
        tsc_number = f"TSC/{random_part}/{year}"
        
        # Check if number exists
        if not TeacherProfile.objects.filter(tsc_number=tsc_number).exists():
            return tsc_number


def validate_tsc_number(tsc_number):
    """Validate TSC number format"""
    pattern = r'^TSC/\d{5}/\d{4}$'
    return bool(re.match(pattern, tsc_number))


def calculate_teacher_workload(teacher_id):
    """Calculate teacher's total workload"""
    from django.db.models import Sum
    
    assignments = TeacherAssignment.objects.filter(
        teacher_id=teacher_id,
        is_active=True,
        assignment_type='teaching'
    )
    
    total_periods = assignments.aggregate(Sum('weekly_periods'))['weekly_periods__sum'] or 0
    total_hours = total_periods * 40 / 60  # 40 minutes per period
    
    return {
        'total_periods': total_periods,
        'total_hours': total_hours,
        'assignments': assignments.count(),
        'max_recommended_periods': 45,
        'workload_percentage': (total_periods / 45 * 100) if total_periods else 0
    }


def get_teacher_summary(teacher_id):
    """Get comprehensive teacher summary"""
    from django.db.models import Count, Avg
    
    teacher = TeacherProfile.objects.get(id=teacher_id)
    
    # Get attendance summary for current month
    today = timezone.now().date()
    first_day = today.replace(day=1)
    
    monthly_attendance = TeacherAttendance.objects.filter(
        teacher=teacher,
        date__gte=first_day,
        date__lte=today
    )
    
    present_days = monthly_attendance.filter(status='present').count()
    absent_days = monthly_attendance.filter(status='absent').count()
    leave_days = monthly_attendance.filter(status='leave').count()
    
    # Get current assignments
    current_year = timezone.now().year
    current_assignments = TeacherAssignment.objects.filter(
        teacher=teacher,
        is_active=True,
        academic_year__year=current_year
    )
    
    # Get upcoming leaves
    upcoming_leaves = TeacherLeave.objects.filter(
        teacher=teacher,
        status='approved',
        start_date__gte=today
    )[:5]
    
    # Get recent trainings
    recent_trainings = TeacherTraining.objects.filter(
        teacher=teacher,
        status='completed'
    ).order_by('-end_date')[:5]
    
    # Get performance indicators
    performance_indicators = PerformanceIndicator.objects.filter(
        teacher=teacher,
        is_active=True
    ).order_by('-evaluation_date')[:5]
    
    return {
        'teacher': {
            'id': teacher.id,
            'name': teacher.full_name,
            'tsc_number': teacher.tsc_number,
            'department': str(teacher.department) if teacher.department else None,
            'designation': teacher.get_designation_display(),
            'teaching_level': teacher.get_teaching_level_display(),
            'tsc_compliant': teacher.tsc_compliant,
            'cbc_trained': teacher.cbc_trained,
            'tpd_status': {
                'current_module': teacher.tpd_current_module,
                'last_completed': teacher.tpd_last_completed_date,
                'next_renewal': teacher.tpd_next_renewal_date,
                'is_valid': teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date >= today
            }
        },
        'attendance': {
            'month': today.strftime('%B %Y'),
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'attendance_rate': (present_days / today.day * 100) if today.day > 0 else 0
        },
        'workload': teacher.calculate_workload(),
        'assignments': {
            'total': current_assignments.count(),
            'subjects': current_assignments.values('subject').distinct().count(),
            'classes': current_assignments.values('class_assigned').distinct().count(),
            'details': list(current_assignments.values('title', 'weekly_periods', 'subject__name', 'class_assigned__name'))
        },
        'leaves': {
            'upcoming': list(upcoming_leaves.values('leave_type', 'start_date', 'end_date', 'days_requested')),
            'remaining_annual': 21 - teacher.leave_applications.filter(
                leave_type='annual',
                status='approved'
            ).count()
        },
        'professional_development': {
            'recent_trainings': list(recent_trainings.values('title', 'organizer', 'end_date', 'training_type')),
            'tpd_module': teacher.tpd_current_module,
            'next_renewal': teacher.tpd_next_renewal_date
        },
        'performance': {
            'rating': teacher.performance_rating,
            'last_appraisal': teacher.last_appraisal_date,
            'next_appraisal': teacher.next_appraisal_date,
            'appraisal_score': teacher.appraisal_score,
            'recent_indicators': list(performance_indicators.values('evaluation_date', 'overall_score', 'student_performance_average'))
        }
    }


def export_teacher_data(teacher_id, format='pdf'):
    """Export teacher data in specified format"""
    # This would be implemented based on requirements
    # Could generate PDF, Excel, or Word documents
    pass


def generate_teacher_report_card(teacher_id, academic_year_id):
    """
    Generate comprehensive teacher performance report card
    
    Args:
        teacher_id (int): ID of the teacher
        academic_year_id (int): ID of the academic year
        
    Returns:
        BytesIO: PDF file buffer
    """
    try:
        # Import models
        from academics.models import AcademicYear, Term, Subject, Class
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, KeepTogether, Image
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfgen import canvas
        from reportlab.platypus.flowables import HRFlowable
        from datetime import datetime
        import os
        
        # Get teacher and academic year
        teacher = TeacherProfile.objects.select_related(
            'teacher', 'department'
        ).prefetch_related(
            'subjects', 'classes', 'assignments',
            'attendance_records', 'performance_indicators',
            'trainings', 'qualifications', 'documents'
        ).get(id=teacher_id)
        
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        
        # Get teacher data for the academic year
        current_term = Term.objects.filter(
            academic_year=academic_year,
            start_date__lte=datetime.now(),
            end_date__gte=datetime.now()
        ).first()
        
        # Get performance indicators for the year
        performance_indicators = PerformanceIndicator.objects.filter(
            teacher=teacher,
            academic_year=academic_year,
            is_active=True
        ).order_by('term__order') if current_term else []
        
        # Get attendance records for the academic year
        attendance_records = TeacherAttendance.objects.filter(
            teacher=teacher,
            date__gte=academic_year.start_date,
            date__lte=academic_year.end_date,
            is_active=True
        )
        
        # Get assignments for the academic year
        assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            academic_year=academic_year,
            is_active=True,
            assignment_type='teaching'
        ).select_related('subject', 'class_assigned')
        
        # Get trainings completed in the academic year
        trainings = TeacherTraining.objects.filter(
            teacher=teacher,
            end_date__gte=academic_year.start_date,
            end_date__lte=academic_year.end_date,
            status='completed',
            is_active=True
        )
        
        # Calculate statistics
        total_days = (academic_year.end_date - academic_year.start_date).days + 1
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        leave_days = attendance_records.filter(status='leave').count()
        late_days = attendance_records.filter(status='late').count()
        
        # Generate PDF report
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1*cm,
            rightMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # Custom styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E5A88'),  # Dark blue
            fontName='Helvetica-Bold'
        )
        
        # Header style
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#2E5A88'),
            fontName='Helvetica-Bold',
            borderPadding=5,
            borderColor=colors.HexColor('#2E5A88'),
            borderWidth=1
        )
        
        # Subheader style
        subheader_style = ParagraphStyle(
            'CustomSubheader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=5,
            textColor=colors.HexColor('#4A6572'),
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            leading=12
        )
        
        # Label style
        label_style = ParagraphStyle(
            'CustomLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            fontName='Helvetica-Oblique'
        )
        
        # Value style
        value_style = ParagraphStyle(
            'CustomValue',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.black
        )
        
        # Small text style
        small_style = ParagraphStyle(
            'CustomSmall',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray
        )
        
        # Build story content
        story = []
        
        # ====================
        # COVER PAGE
        # ====================
        
        # School logo and header
        story.append(Spacer(1, 2*cm))
        
        # School name
        school_name = Paragraph(
            "<b>MINISTRY OF EDUCATION - KENYA</b>",
            ParagraphStyle(
                'SchoolName',
                parent=styles['Title'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=10
            )
        )
        story.append(school_name)
        
        # Report title
        report_title = Paragraph(
            "TEACHER PERFORMANCE REPORT CARD",
            title_style
        )
        story.append(report_title)
        
        story.append(Spacer(1, 1*cm))
        
        # Teacher photo placeholder
        story.append(Paragraph("TEACHER PHOTO", ParagraphStyle(
            'PhotoPlaceholder',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.gray,
            borderPadding=20,
            backColor=colors.whitesmoke
        )))
        
        story.append(Spacer(1, 1.5*cm))
        
        # Teacher information table
        teacher_info = [
            ["<b>Teacher Name:</b>", teacher.full_name],
            ["<b>TSC Number:</b>", teacher.tsc_number],
            ["<b>Employee ID:</b>", teacher.teacher.staff_id or "N/A"],
            ["<b>Department:</b>", str(teacher.department) if teacher.department else "N/A"],
            ["<b>Academic Year:</b>", str(academic_year)],
            ["<b>Report Date:</b>", datetime.now().strftime("%B %d, %Y")],
            ["<b>Report Period:</b>", f"{academic_year.start_date.strftime('%b %d, %Y')} to {academic_year.end_date.strftime('%b %d, %Y')}"]
        ]
        
        teacher_table = Table(teacher_info, colWidths=[3*cm, 10*cm])
        teacher_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(teacher_table)
        story.append(Spacer(1, 2*cm))
        
        # Confidential notice
        confidential = Paragraph(
            "<b><i>CONFIDENTIAL - FOR OFFICIAL USE ONLY</i></b>",
            ParagraphStyle(
                'Confidential',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.red
            )
        )
        story.append(confidential)
        
        story.append(PageBreak())
        
        # ====================
        # TABLE OF CONTENTS
        # ====================
        
        story.append(Paragraph("TABLE OF CONTENTS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        toc_items = [
            "1. Personal Information",
            "2. Academic Qualifications",
            "3. Professional Information",
            "4. Teaching Load & Assignments",
            "5. Attendance Record",
            "6. Performance Indicators",
            "7. Professional Development",
            "8. Achievements & Awards",
            "9. TSC Compliance Status",
            "10. Recommendations & Action Plan"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, normal_style))
            story.append(Spacer(1, 0.2*cm))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 1: PERSONAL INFORMATION
        # ====================
        
        story.append(Paragraph("1. PERSONAL INFORMATION", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        personal_info_data = [
            ["Full Name:", teacher.full_name],
            ["TSC Number:", teacher.tsc_number],
            ["Date of Birth:", teacher.teacher.date_of_birth.strftime("%B %d, %Y") if teacher.teacher.date_of_birth else "N/A"],
            ["Gender:", teacher.teacher.get_gender_display()],
            ["Nationality:", teacher.teacher.nationality or "N/A"],
            ["ID/Passport No:", teacher.teacher.id_number or "N/A"],
            ["Phone Number:", teacher.teacher.phone_number or "N/A"],
            ["Email Address:", teacher.teacher.email or "N/A"],
            ["Residence:", teacher.teacher.address or "N/A"]
        ]
        
        personal_table = Table(personal_info_data, colWidths=[4*cm, 8*cm])
        personal_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(personal_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Emergency contact
        story.append(Paragraph("<b>Emergency Contact:</b>", subheader_style))
        
        if teacher.emergency_contact_name:
            emergency_info = f"{teacher.emergency_contact_name} ({teacher.emergency_contact_relationship or 'N/A'}) - {teacher.emergency_contact_phone or 'N/A'}"
            story.append(Paragraph(emergency_info, normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 2: ACADEMIC QUALIFICATIONS
        # ====================
        
        story.append(Paragraph("2. ACADEMIC QUALIFICATIONS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Highest qualification
        qual_data = [
            ["Highest Qualification:", teacher.get_highest_qualification_display()],
            ["Institution:", teacher.qualification_institution or "N/A"],
            ["Year of Graduation:", str(teacher.year_of_graduation) if teacher.year_of_graduation else "N/A"],
            ["KCSE Mean Grade:", teacher.get_kcse_mean_grade_display()],
            ["KCSE Index Number:", teacher.kcse_index_number or "N/A"],
            ["KCSE Year:", str(teacher.kcse_year) if teacher.kcse_year else "N/A"]
        ]
        
        qual_table = Table(qual_data, colWidths=[4*cm, 8*cm])
        qual_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(qual_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Teaching subjects
        if teacher.teaching_subjects:
            story.append(Paragraph("<b>Teaching Subjects:</b>", subheader_style))
            subjects_text = ", ".join(teacher.teaching_subjects)
            story.append(Paragraph(subjects_text, normal_style))
        
        # Additional qualifications
        additional_quals = teacher.qualifications.filter(is_active=True)
        if additional_quals.exists():
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("<b>Additional Qualifications:</b>", subheader_style))
            
            for qual in additional_quals[:5]:  # Show top 5
                qual_info = f"• {qual.title} - {qual.institution} ({qual.end_date.year})"
                story.append(Paragraph(qual_info, normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 3: PROFESSIONAL INFORMATION
        # ====================
        
        story.append(Paragraph("3. PROFESSIONAL INFORMATION", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Employment details
        emp_data = [
            ["Employment Type:", teacher.get_employment_type_display()],
            ["Employment Status:", teacher.get_employment_status_display()],
            ["Teaching Level:", teacher.get_teaching_level_display()],
            ["Designation:", teacher.get_designation_display()],
            ["Date of Employment:", teacher.employment_date.strftime("%B %d, %Y") if teacher.employment_date else "N/A"],
            ["Years of Service:", str(teacher.years_of_service)],
            ["TSC Category:", teacher.get_tsc_category_display()],
            ["TSC Status:", teacher.get_tsc_status_display()]
        ]
        
        if teacher.confirmation_date:
            emp_data.append(["Confirmation Date:", teacher.confirmation_date.strftime("%B %d, %Y")])
        
        if teacher.retirement_date:
            emp_data.append(["Planned Retirement:", teacher.retirement_date.strftime("%B %d, %Y")])
        
        emp_table = Table(emp_data, colWidths=[4*cm, 8*cm])
        emp_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(emp_table)
        story.append(Spacer(1, 0.5*cm))
        
        # CBC Training status
        story.append(Paragraph("<b>CBC Training Status:</b>", subheader_style))
        
        cbc_status = "Trained" if teacher.cbc_trained else "Not Trained"
        cbc_info = f"{cbc_status}"
        
        if teacher.cbc_trained and teacher.cbc_training_date:
            cbc_info += f" (Trained on: {teacher.cbc_training_date.strftime('%B %d, %Y')})"
            if teacher.cbc_training_level:
                cbc_info += f" - Level: {teacher.get_cbc_training_level_display()}"
        
        story.append(Paragraph(cbc_info, normal_style))
        
        # TPD Status
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("<b>TPD Status:</b>", subheader_style))
        
        tpd_info = f"Module {teacher.tpd_current_module}"
        if teacher.tpd_last_completed_date:
            tpd_info += f" (Last completed: {teacher.tpd_last_completed_date.strftime('%B %d, %Y')})"
        
        if teacher.tpd_next_renewal_date:
            days_remaining = (teacher.tpd_next_renewal_date - datetime.now().date()).days
            tpd_info += f" - Renewal due: {teacher.tpd_next_renewal_date.strftime('%B %d, %Y')} ({days_remaining} days remaining)"
        
        story.append(Paragraph(tpd_info, normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 4: TEACHING LOAD & ASSIGNMENTS
        # ====================
        
        story.append(Paragraph("4. TEACHING LOAD & ASSIGNMENTS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Teaching load summary
        workload = teacher.calculate_workload()
        
        load_data = [
            ["Total Periods/Week:", str(teacher.weekly_periods)],
            ["Teaching Hours/Week:", f"{teacher.teaching_load_hours:.2f}"],
            ["Workload Percentage:", f"{workload['workload_percentage']:.1f}%"],
            ["Recommended Maximum:", "45 periods/week"],
            ["Status:", "Optimal" if workload['workload_percentage'] <= 100 else "Overloaded"]
        ]
        
        load_table = Table(load_data, colWidths=[4*cm, 8*cm])
        load_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(load_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Current assignments
        if assignments.exists():
            story.append(Paragraph("<b>Current Assignments:</b>", subheader_style))
            
            assign_data = [["Subject", "Class", "Stream", "Periods/Week", "Status"]]
            
            for assign in assignments:
                assign_data.append([
                    assign.subject.name if assign.subject else "N/A",
                    assign.class_assigned.name if assign.class_assigned else "N/A",
                    assign.stream.name if assign.stream else "N/A",
                    str(assign.weekly_periods),
                    "Active" if assign.is_active else "Inactive"
                ])
            
            assign_table = Table(assign_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm])
            assign_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5A88')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ]))
            
            story.append(assign_table)
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 5: ATTENDANCE RECORD
        # ====================
        
        story.append(Paragraph("5. ATTENDANCE RECORD", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Attendance summary
        att_data = [
            ["Total Working Days:", str(total_days)],
            ["Days Present:", str(present_days)],
            ["Days Absent:", str(absent_days)],
            ["Days on Leave:", str(leave_days)],
            ["Days Late:", str(late_days)],
            ["Attendance Rate:", f"{(present_days/total_days*100):.1f}%" if total_days > 0 else "0%"]
        ]
        
        att_table = Table(att_data, colWidths=[4*cm, 8*cm])
        att_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(att_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Monthly attendance chart
        story.append(Paragraph("<b>Monthly Attendance Breakdown:</b>", subheader_style))
        
        # Calculate monthly attendance (simplified)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Create a simple monthly breakdown table
        month_data = [["Month", "Present", "Absent", "Leave", "Rate"]]
        
        for month_num, month_name in enumerate(months, 1):
            # This would be calculated from actual data in a real implementation
            month_present = present_days // 12  # Simplified
            month_absent = absent_days // 12
            month_leave = leave_days // 12
            month_rate = (month_present / 20 * 100) if 20 > 0 else 0
            
            month_data.append([
                month_name,
                str(month_present),
                str(month_absent),
                str(month_leave),
                f"{month_rate:.1f}%"
            ])
        
        month_table = Table(month_data, colWidths=[2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
        month_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6572')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('ALIGN', (1, 1), (4, -1), 'CENTER'),
        ]))
        
        story.append(month_table)
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 6: PERFORMANCE INDICATORS
        # ====================
        
        story.append(Paragraph("6. PERFORMANCE INDICATORS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        if performance_indicators.exists():
            # Overall performance rating
            if teacher.performance_rating:
                story.append(Paragraph(f"<b>Overall Performance Rating:</b> {teacher.performance_rating}/5.00", subheader_style))
                story.append(Spacer(1, 0.3*cm))
            
            # Performance breakdown by term
            for indicator in performance_indicators:
                if indicator.term:
                    story.append(Paragraph(f"<b>{indicator.term.name} Performance:</b>", subheader_style))
                    
                    perf_data = [
                        ["Indicator", "Score (out of 5)"],
                        ["Student Performance", f"{indicator.student_performance_average:.2f}"],
                        ["Punctuality", f"{indicator.punctuality_score:.2f}"],
                        ["Lesson Preparation", f"{indicator.lesson_preparation_score:.2f}"],
                        ["Student Engagement", f"{indicator.student_engagement_score:.2f}"],
                        ["Professional Development", f"{indicator.pd_completion_score:.2f}"],
                        ["<b>Overall Score</b>", f"<b>{indicator.overall_score:.2f}</b>"]
                    ]
                    
                    perf_table = Table(perf_data, colWidths=[5*cm, 4*cm])
                    perf_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5A88')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                        ('BACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#F0F8FF')),
                    ]))
                    
                    story.append(perf_table)
                    story.append(Spacer(1, 0.5*cm))
            
            # Last appraisal details
            if teacher.last_appraisal_date:
                story.append(Paragraph("<b>Last Appraisal Details:</b>", subheader_style))
                appr_data = [
                    ["Appraisal Date:", teacher.last_appraisal_date.strftime("%B %d, %Y")],
                    ["Appraisal Score:", f"{teacher.appraisal_score:.2f}" if teacher.appraisal_score else "N/A"],
                    ["Next Appraisal:", teacher.next_appraisal_date.strftime("%B %d, %Y") if teacher.next_appraisal_date else "N/A"]
                ]
                
                appr_table = Table(appr_data, colWidths=[4*cm, 8*cm])
                appr_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ]))
                
                story.append(appr_table)
        else:
            story.append(Paragraph("No performance indicators available for this academic year.", normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 7: PROFESSIONAL DEVELOPMENT
        # ====================
        
        story.append(Paragraph("7. PROFESSIONAL DEVELOPMENT", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        if trainings.exists():
            story.append(Paragraph("<b>Trainings Completed This Year:</b>", subheader_style))
            
            train_data = [["Training Title", "Organizer", "Duration", "Date", "Score"]]
            
            for training in trainings[:10]:  # Show top 10
                train_data.append([
                    training.title[:30] + "..." if len(training.title) > 30 else training.title,
                    training.organizer[:20] + "..." if len(training.organizer) > 20 else training.organizer,
                    f"{training.duration_hours} hrs",
                    training.end_date.strftime("%b %Y"),
                    f"{training.assessment_score:.1f}" if training.assessment_score else "N/A"
                ])
            
            train_table = Table(train_data, colWidths=[4*cm, 3*cm, 2*cm, 2*cm, 2*cm])
            train_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6572')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('ALIGN', (2, 1), (4, -1), 'CENTER'),
            ]))
            
            story.append(train_table)
            story.append(Spacer(1, 0.5*cm))
        
        # Professional memberships
        story.append(Paragraph("<b>Professional Memberships:</b>", subheader_style))
        memberships = []
        
        if teacher.sacco_name:
            memberships.append(f"• {teacher.sacco_name} (SACCO)")
        
        if teacher.teacher_registration_number:
            memberships.append("• Registered Teacher")
        
        if teacher.knec_registration_number:
            memberships.append("• KNEC Registered")
        
        if memberships:
            for membership in memberships:
                story.append(Paragraph(membership, normal_style))
        else:
            story.append(Paragraph("No professional memberships recorded.", normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 8: ACHIEVEMENTS & AWARDS
        # ====================
        
        story.append(Paragraph("8. ACHIEVEMENTS & AWARDS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        if teacher.achievements and isinstance(teacher.achievements, list) and len(teacher.achievements) > 0:
            for achievement in teacher.achievements[:10]:  # Show top 10
                if isinstance(achievement, dict):
                    title = achievement.get('title', 'Achievement')
                    date = achievement.get('date', '')
                    description = achievement.get('description', '')
                    
                    story.append(Paragraph(f"<b>• {title}</b> {date}", subheader_style))
                    if description:
                        story.append(Paragraph(description, normal_style))
                    story.append(Spacer(1, 0.2*cm))
                else:
                    story.append(Paragraph(f"• {achievement}", normal_style))
        else:
            story.append(Paragraph("No achievements recorded for this period.", normal_style))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 9: TSC COMPLIANCE STATUS
        # ====================
        
        story.append(Paragraph("9. TSC COMPLIANCE STATUS", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Compliance checklist
        tsc_requirements = [
            ["Requirement", "Status", "Details"],
            ["TSC Registration", "✓ Compliant" if teacher.tsc_status in ['registered', 'provisional'] else "✗ Non-compliant", teacher.get_tsc_status_display()],
            ["Academic Qualifications", "✓ Compliant" if teacher.highest_qualification else "✗ Non-compliant", teacher.get_highest_qualification_display()],
            ["KCSE Requirements", "✓ Compliant" if teacher._check_kcse_requirements() else "✗ Non-compliant", teacher.get_kcse_mean_grade_display()],
            ["TPD Status", "✓ Compliant" if teacher.tpd_current_module >= 1 and (not teacher.tpd_next_renewal_date or teacher.tpd_next_renewal_date >= datetime.now().date()) else "⚠ Needs attention", f"Module {teacher.tpd_current_module}"],
            ["CBC Training", "✓ Compliant" if teacher.cbc_trained or teacher.teaching_level != TeacherProfile.TeachingLevel.JUNIOR_SECONDARY else "✗ Non-compliant", "Trained" if teacher.cbc_trained else "Not Required/Not Trained"],
            ["Teaching Certificate", "✓ On File" if teacher.documents.filter(document_type='tsc_certificate', status='verified').exists() else "⚠ Not Verified", ""],
            ["Good Conduct", "✓ On File" if teacher.documents.filter(document_type='good_conduct', status='verified').exists() else "⚠ Not Verified", ""],
            ["ID Copy", "✓ On File" if teacher.teacher.id_number else "⚠ Not Provided", ""]
        ]
        
        tsc_table = Table(tsc_requirements, colWidths=[5*cm, 3*cm, 4*cm])
        tsc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5A88')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        
        story.append(tsc_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Overall compliance status
        story.append(Paragraph(f"<b>Overall TSC Compliance:</b> {'✓ COMPLIANT' if teacher.tsc_compliant else '✗ NON-COMPLIANT'}", 
                              ParagraphStyle(
                                  'ComplianceStatus',
                                  parent=styles['Normal'],
                                  fontSize=12,
                                  textColor=colors.green if teacher.tsc_compliant else colors.red,
                                  fontName='Helvetica-Bold'
                              )))
        
        story.append(PageBreak())
        
        # ====================
        # SECTION 10: RECOMMENDATIONS & ACTION PLAN
        # ====================
        
        story.append(Paragraph("10. RECOMMENDATIONS & ACTION PLAN", header_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Generate recommendations based on performance
        recommendations = []
        
        # Workload recommendations
        workload_percentage = workload['workload_percentage']
        if workload_percentage > 100:
            recommendations.append("Reduce teaching workload to recommended levels (max 45 periods/week)")
        elif workload_percentage < 70:
            recommendations.append("Consider additional teaching assignments or administrative duties")
        
        # Attendance recommendations
        attendance_rate = (present_days/total_days*100) if total_days > 0 else 0
        if attendance_rate < 90:
            recommendations.append("Improve attendance and punctuality")
        
        # TPD recommendations
        if teacher.tpd_next_renewal_date and (teacher.tpd_next_renewal_date - datetime.now().date()).days < 90:
            recommendations.append("Complete next TPD module before renewal date")
        
        # CBC training recommendations
        if teacher.teaching_level == TeacherProfile.TeachingLevel.JUNIOR_SECONDARY and not teacher.cbc_trained:
            recommendations.append("Complete mandatory CBC training for Junior Secondary")
        
        # Performance recommendations
        if teacher.performance_rating and teacher.performance_rating < 3.0:
            recommendations.append("Participate in performance improvement program")
        
        # Add standard recommendations
        recommendations.extend([
            "Participate in at least 2 professional development activities annually",
            "Maintain updated teaching portfolio and lesson plans",
            "Engage in peer observation and collaborative teaching",
            "Participate in school committees and extracurricular activities"
        ])
        
        # Display recommendations
        for i, recommendation in enumerate(recommendations[:8], 1):  # Show top 8
            story.append(Paragraph(f"{i}. {recommendation}", normal_style))
            story.append(Spacer(1, 0.2*cm))
        
        story.append(Spacer(1, 1*cm))
        
        # Action plan table
        story.append(Paragraph("<b>Proposed Action Plan for Next Term:</b>", subheader_style))
        
        action_data = [
            ["Action Item", "Responsible", "Timeline", "Success Indicators"],
            ["Complete TPD Module", teacher.full_name, "Next 3 months", "Certificate of completion"],
            ["Improve attendance", teacher.full_name, "Immediate", "95%+ attendance rate"],
            ["Attend CBC training", "School Admin", "Next term", "Training certificate"],
            ["Reduce workload if needed", "HOD/Principal", "Next term", "Max 45 periods/week"]
        ]
        
        action_table = Table(action_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
        action_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6572')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(action_table)
        
        story.append(Spacer(1, 1.5*cm))
        
        # ====================
        # SIGNATURE SECTION
        # ====================
        
        signature_data = [
            ["Prepared by:", "___________________________", "Date: ________________"],
            ["", "Curriculum Coordinator", ""],
            ["", "", ""],
            ["Reviewed by:", "___________________________", "Date: ________________"],
            ["", "Head of Department", ""],
            ["", "", ""],
            ["Approved by:", "___________________________", "Date: ________________"],
            ["", "Principal/Head Teacher", ""],
            ["", "", ""],
            ["Teacher's Acknowledgment:", "___________________________", "Date: ________________"],
            ["", teacher.full_name, ""]
        ]
        
        signature_table = Table(signature_data, colWidths=[4*cm, 6*cm, 4*cm])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(signature_table)
        
        # ====================
        # FOOTER
        # ====================
        
        story.append(Spacer(1, 1*cm))
        
        footer = Paragraph(
            "This report is generated by the School Management System. All information is confidential and for official use only.",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.gray
            )
        )
        story.append(footer)
        
        # Build the PDF
        doc.build(story, onFirstPage=lambda c, d: add_page_number(c, d, 1),
                         onLaterPages=lambda c, d: add_page_number(c, d, 1))
        
        buffer.seek(0)
        return buffer
        
    except TeacherProfile.DoesNotExist:
        raise ValueError(f"Teacher with ID {teacher_id} not found")
    except AcademicYear.DoesNotExist:
        raise ValueError(f"Academic Year with ID {academic_year_id} not found")
    except Exception as e:
        logger.error(f"Error generating teacher report card: {str(e)}")
        raise


def add_page_number(canvas, doc, start_number):
    """
    Add page numbers to PDF
    """
    page_num = canvas.getPageNumber() + start_number - 1
    text = f"Page {page_num}"
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(doc.pagesize[0] - 20, 20, text)


def generate_teacher_summary_report(teacher_ids, academic_year_id):
    """
    Generate summary report for multiple teachers
    """
    # Similar implementation but for multiple teachers
    pass


def export_teacher_report_to_excel(teacher_id, academic_year_id):
    """
    Export teacher report to Excel format
    """
    # Implementation for Excel export
    pass


# Add to TeacherProfile model methods
def get_performance_report(self, academic_year_id):
    """Get performance report for teacher"""
    return generate_teacher_report_card(self.id, academic_year_id)


# Add the method to TeacherProfile
TeacherProfile.get_performance_report = get_performance_report

def calculate_teacher_capacity(teacher_id):
    """Calculate teacher's teaching capacity and utilization"""
    teacher = TeacherProfile.objects.get(id=teacher_id)
    
    # Maximum recommended periods (TSC guidelines)
    max_periods = 45 if teacher.teaching_level == TeacherProfile.TeachingLevel.SENIOR_SECONDARY else 40
    
    # Current utilization
    utilization = (teacher.weekly_periods / max_periods * 100) if max_periods > 0 else 0
    
    # Available capacity
    available_periods = max_periods - teacher.weekly_periods
    
    return {
        'current_periods': teacher.weekly_periods,
        'max_recommended': max_periods,
        'utilization_percentage': utilization,
        'available_periods': available_periods,
        'capacity_status': 'overloaded' if utilization > 100 else 'optimal' if utilization > 80 else 'underutilized'
    }


# Add bulk operations class
class TeacherBulkOperations:
    
    @staticmethod
    def bulk_update_tpd_module(teacher_ids, new_module):
        """Update TPD module for multiple teachers"""
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids)
        updated = []
        
        for teacher in teachers:
            if teacher.update_tpd_module(new_module):
                updated.append(teacher.id)
        
        return updated
    
    @staticmethod
    def bulk_mark_cbc_trained(teacher_ids, training_date=None):
        """Mark multiple teachers as CBC trained"""
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids)
        updated = []
        
        for teacher in teachers:
            if teacher.mark_cbc_trained(training_date):
                updated.append(teacher.id)
        
        return updated
    
    @staticmethod
    def calculate_workload_for_all():
        """Recalculate workload for all active teachers"""
        from django.db.models import Sum
        
        teachers = TeacherProfile.objects.filter(is_active=True)
        
        for teacher in teachers:
            assignments = TeacherAssignment.objects.filter(
                teacher=teacher,
                is_active=True,
                assignment_type='teaching'
            )
            total_periods = assignments.aggregate(
                Sum('weekly_periods')
            )['weekly_periods__sum'] or 0
            
            teacher.weekly_periods = total_periods
            teacher.teaching_load_hours = Decimal(total_periods * 40 / 60)
        
        TeacherProfile.objects.bulk_update(
            teachers,
            ['weekly_periods', 'teaching_load_hours']
        )




# ============================================================================
# INITIALIZE CUSTOM MANAGER
# ============================================================================

TeacherProfile.add_to_class('objects', TeacherProfileManager())