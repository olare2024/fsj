# accounts/models.py - COMPLETE CORRECTED VERSION

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import uuid
from datetime import date, timedelta
import pyotp
import qrcode
import base64
from io import BytesIO
from django.core.cache import cache
from django.conf import settings
import secrets
from django.urls import reverse
from django.db.models import Q
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


# ============================================================================
# MANAGERS
# ============================================================================

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'), 
]




class CustomUserManager(BaseUserManager):
    """Custom manager for User model with email as username field"""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        
        # Set defaults
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', False)
        extra_fields.setdefault('is_approved', False)
        
        # Set role-specific defaults
        role = extra_fields.get('role', 'student')
        if role == 'student':
            extra_fields.setdefault('is_staff', False)
        elif role in ['admin', 'teacher', 'head_teacher', 'curriculum_coordinator']:
            extra_fields.setdefault('is_staff', True)
        
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        return self.get(email=email)


# ============================================================================
# BASE MODEL
# ============================================================================

class BaseModel(models.Model):
    """Abstract base model with common fields and methods"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Override save to include validation"""
        try:
            self.full_clean()
        except ValidationError as e:
            logger.error(f"Validation error saving {self.__class__.__name__}: {e}")
            raise
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_objects(cls):
        """Get all active objects"""
        return cls.objects.filter(is_active=True)


# ============================================================================
# MIXINS
# ============================================================================

class ContactInfoMixin(models.Model):
    """Mixin for contact information fields"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("Phone Number")
    )
    alternative_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("Alternative Phone")
    )
    address = models.TextField(blank=True, verbose_name=_("Residential Address"))
    city = models.CharField(max_length=50, blank=True, verbose_name=_("City"))
    country = models.CharField(max_length=50, default='Kenya', verbose_name=_("Country"))
    
    class Meta:
        abstract = True


class EmergencyContactMixin(models.Model):
    """Mixin for emergency contact information"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    
    emergency_contact_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Emergency Contact Name")
    )
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        verbose_name=_("Emergency Contact Phone")
    )
    emergency_contact_relationship = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name=_("Relationship")
    )
    emergency_contact_address = models.TextField(
        blank=True, 
        verbose_name=_("Emergency Contact Address")
    )
    
    class Meta:
        abstract = True


class MedicalInfoMixin(models.Model):
    """Mixin for medical information"""
    class BloodGroup(models.TextChoices):
        A_POSITIVE = 'a_positive', _('A+')
        A_NEGATIVE = 'a_negative', _('A-')
        B_POSITIVE = 'b_positive', _('B+')
        B_NEGATIVE = 'b_negative', _('B-')
        AB_POSITIVE = 'ab_positive', _('AB+')
        AB_NEGATIVE = 'ab_negative', _('AB-')
        O_POSITIVE = 'o_positive', _('O+')
        O_NEGATIVE = 'o_negative', _('O-')
    
    blood_group = models.CharField(
        max_length=15, 
        choices=BloodGroup.choices, 
        blank=True,
        verbose_name=_("Blood Group")
    )
    medical_info = models.TextField(blank=True, verbose_name=_("Medical Information"))
    allergies = models.TextField(blank=True, verbose_name=_("Allergies"))
    chronic_conditions = models.TextField(blank=True, verbose_name=_("Chronic Conditions"))
    current_medications = models.TextField(blank=True, verbose_name=_("Current Medications"))
    doctor_name = models.CharField(max_length=100, blank=True, verbose_name=_("Doctor Name"))
    doctor_phone = models.CharField(max_length=17, blank=True, verbose_name=_("Doctor Phone"))
    
    class Meta:
        abstract = True


# ============================================================================
# MAIN USER MODEL
# ============================================================================

class User(AbstractBaseUser, PermissionsMixin, BaseModel, 
           ContactInfoMixin, EmergencyContactMixin, MedicalInfoMixin):
    """
    Enhanced Custom User Model for Delvok Academy Management System
    with Dashboard Redirection Support
    """
    
    # Role Constants with Dashboard URLs
    class Role(models.TextChoices):
        ADMIN = 'admin', _('System Administrator')
        HEAD_TEACHER = 'head_teacher', _('Head Teacher')
        CURRICULUM_COORDINATOR = 'curriculum_coordinator', _('Curriculum Coordinator')
        TEACHER = 'teacher', _('Teacher')
        OFFICE_STAFF = 'office_staff', _('Office Staff')
        STUDENT = 'student', _('Student')
        PARENT = 'parent', _('Parent')
        LIBRARIAN = 'librarian', _('Librarian')
        ACCOUNTANT = 'accountant', _('Accountant')
        IT_SUPPORT = 'it_support', _('IT Support')
        COUNSELOR = 'counselor', _('School Counselor')
    
    # Dashboard URL mappings
    DASHBOARD_URLS = {
        Role.ADMIN: '/admin/admin-portal',
        Role.HEAD_TEACHER: '/head-teacher/headteacher-portal',
        Role.CURRICULUM_COORDINATOR: '/curriculum/curriculum-portal',
        Role.TEACHER: '/teacher/teacher-portal',
        Role.OFFICE_STAFF: '/staff/staff-portal',
        Role.STUDENT: '/student/student-portal',
        Role.PARENT: '/parent/parent-portal',
        Role.LIBRARIAN: '/library/library-portal',
        Role.ACCOUNTANT: '/finance/finance-portal',
        Role.IT_SUPPORT: '/it/it-portal',
        Role.COUNSELOR: '/counselor/counselor-portal',
    }
    
    class Curriculum(models.TextChoices):
        CBC = 'cbc', _('CBC - Competency Based Curriculum')
        ICSE = 'icse', _('ICSE - Indian Certificate of Secondary Education')
        AMERICAN = 'american', _('American Curriculum')
        BRITISH = 'british', _('British Curriculum')
        MONTESSORI = 'montessori', _('Montessori')
        COMBINED = 'combined', _('Combined Curriculum')
        IGCSE = 'igcse', _('IGCSE')
        IB = 'ib', _('International Baccalaureate')
    
    class House(models.TextChoices):
        UNITY = 'unity', _('Unity House')
        COURAGE = 'courage', _('Courage House')
        WISDOM = 'wisdom', _('Wisdom House')
        SUCCESS = 'success', _('Success House')
        EXCELLENCE = 'excellence', _('Excellence House')
        INTEGRITY = 'integrity', _('Integrity House')
        BRAVERY = 'bravery', _('Bravery House')
        HONOR = 'honor', _('Honor House')
    
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')
    
    # === Core Identification Fields ===
    email = models.EmailField(
        verbose_name=_("Email Address"),
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        help_text=_("Required. Must be a valid email address.")
    )
    first_name = models.CharField(
        max_length=50, 
        verbose_name=_("First Name"),
        validators=[MinLengthValidator(2)]
    )
    last_name = models.CharField(
        max_length=50, 
        verbose_name=_("Last Name"),
        validators=[MinLengthValidator(2)]
    )
    middle_name = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name=_("Middle Name")
    )
    
    # === Academy Identifiers ===
    admission_number = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name=_("Admission Number"),
        help_text=_("Automatically generated for students")
    )
    staff_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name=_("Staff ID"),
        help_text=_("Automatically generated for staff")
    )
    
    # === Role and Access Control ===
    role = models.CharField(
        max_length=25, 
        choices=Role.choices, 
        default=Role.STUDENT, 
        verbose_name=_("User Role")
    )
    is_staff = models.BooleanField(default=False, verbose_name=_("Staff Status"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Administrator"))
    
    # === Personal Information ===
    date_of_birth = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Date of Birth")
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name=_("Profile Picture"),
        max_length=500
    )
    gender = models.CharField(
        max_length=20, 
        choices=Gender.choices, 
        blank=True,
        verbose_name=_("Gender")
    )
    nationality = models.CharField(
        max_length=50, 
        default='Kenyan',
        verbose_name=_("Nationality")
    )
    id_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_("National ID/Passport")
    )
    
    # === Profile Completion Tracking ===
    profile_completed = models.BooleanField(
        default=False, 
        verbose_name=_("Profile Completed")
    )
    profile_completion_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Profile Completion Date")
    )
    profile_requirements_met = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Profile Requirements Met")
    )
    
    # === Academic Information ===
    primary_curriculum = models.CharField(
        max_length=15, 
        choices=Curriculum.choices, 
        blank=True, 
        null=True,
        verbose_name=_("Primary Curriculum")
    )
    grade_level = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_("Grade Level")
    )
    current_class = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_("Current Class")
    )
    house = models.CharField(
        max_length=20, 
        choices=House.choices, 
        blank=True, 
        null=True,
        verbose_name=_("House")
    )
    academic_year = models.CharField(
        max_length=9, 
        blank=True, 
        verbose_name=_("Academic Year")
    )
    
    # === Status and Verification ===
    is_verified = models.BooleanField(default=False, verbose_name=_("Verified Account"))
    is_suspended = models.BooleanField(default=False, verbose_name=_("Suspended"))
    is_on_leave = models.BooleanField(default=False, verbose_name=_("On Leave"))
    email_verified = models.BooleanField(default=False, verbose_name=_("Email Verified"))
    phone_verified = models.BooleanField(default=False, verbose_name=_("Phone Verified"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Approved Account"))
    
    # === Timestamps ===
    last_login = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Last Login")
    )
    date_joined = models.DateTimeField(
        default=timezone.now, 
        verbose_name=_("Date Joined")
    )
    enrollment_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Enrollment Date")
    )
    employment_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Employment Date")
    )
    last_profile_update = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Last Profile Update")
    )
    
    # === Professional Information ===
    department = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Department")
    )
    qualification = models.TextField(
        blank=True, 
        verbose_name=_("Qualifications")
    )
    specialization = models.TextField(
        blank=True, 
        verbose_name=_("Specialization")
    )
    designation = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Designation")
    )
    years_of_experience = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Years of Experience")
    )
    
    # === Student-Specific Information ===
    parent_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Parent/Guardian Name")
    )
    parent_email = models.EmailField(
        blank=True, 
        verbose_name=_("Parent/Guardian Email")
    )
    parent_phone = models.CharField(
        max_length=17, 
        blank=True, 
        verbose_name=_("Parent/Guardian Phone")
    )
    parent_occupation = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Parent Occupation")
    )
    
    # === Additional Information ===
    previous_school = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("Previous School")
    )
    transfer_certificate = models.FileField(
        upload_to='transfer_certificates/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name=_("Transfer Certificate"),
        max_length=500
    )
    birth_certificate = models.FileField(
        upload_to='birth_certificates/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name=_("Birth Certificate"),
        max_length=500
    )
    recommendation_letter = models.FileField(
        upload_to='recommendation_letters/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name=_("Recommendation Letter"),
        max_length=500
    )
    
    # === Login & Session Management ===
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name=_("Last Login IP")
    )
    last_login_user_agent = models.TextField(
        blank=True, 
        verbose_name=_("Last Login User Agent")
    )
    last_activity = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Last Activity")
    )
    login_count = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Login Count")
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Failed Login Attempts")
    )
    account_locked_until = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Account Locked Until")
    )
    password_changed_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Password Changed At")
    )
    
    # === Dashboard Preferences ===
    preferred_dashboard_view = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('overview', _('Overview')),
            ('detailed', _('Detailed View')),
            ('minimal', _('Minimal View')),
            ('custom', _('Custom Layout'))
        ],
        default='overview',
        verbose_name=_("Preferred Dashboard View")
    )
    dashboard_widgets = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Dashboard Widgets"),
        help_text=_("User's preferred dashboard widget configuration")
    )
    theme_preference = models.CharField(
        max_length=20,
        choices=[
            ('light', _('Light')),
            ('dark', _('Dark')),
            ('auto', _('Auto'))
        ],
        default='light',
        verbose_name=_("Theme Preference")
    )
    
    # === System Fields ===
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['profile_completed']),
            models.Index(fields=['admission_number']),
            models.Index(fields=['staff_id']),
            models.Index(fields=['grade_level']),
            models.Index(fields=['last_login']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_suspended']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_user_email'
            ),
            models.UniqueConstraint(
                fields=['admission_number'],
                condition=Q(admission_number__isnull=False),
                name='unique_admission_number'
            ),
            models.UniqueConstraint(
                fields=['staff_id'],
                condition=Q(staff_id__isnull=False),
                name='unique_staff_id'
            ),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    # === Core User Methods ===
    def get_full_name(self):
        """Return the full name of the user"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name for the user (first name)"""
        return self.first_name

    def get_initials(self):
        """Return user initials"""
        initials = self.first_name[0] if self.first_name else ''
        if self.last_name:
            initials += self.last_name[0]
        return initials.upper()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send email to this user"""
        html_message = kwargs.pop('html_message', None)
        try:
            send_mail(
                subject, 
                message, 
                from_email or settings.DEFAULT_FROM_EMAIL, 
                [self.email], 
                html_message=html_message, 
                **kwargs
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {self.email}: {e}")
            return False

    def validate_password_strength(self, password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append(_("Password must be at least 8 characters long"))
        if not any(char.isdigit() for char in password):
            errors.append(_("Password must contain at least one number"))
        if not any(char.isupper() for char in password):
            errors.append(_("Password must contain at least one uppercase letter"))
        if not any(char.islower() for char in password):
            errors.append(_("Password must contain at least one lowercase letter"))
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
            errors.append(_("Password must contain at least one special character"))
            
        if errors:
            raise ValidationError(errors)
        return True

    # === Profile Completion Methods ===
    def check_profile_completion(self):
        """Check if user has completed profile requirements"""
        if self.profile_completed:
            return True
        
        required_fields = self._get_required_fields_for_role()
        
        requirements_met = {}
        all_requirements_met = True
        
        for field in required_fields:
            value = getattr(self, field, None)
            is_met = bool(value and (not isinstance(value, str) or value.strip()))
            requirements_met[field] = {
                'met': is_met,
                'value': str(value)[:50] + '...' if value else None,
                'required': True,
                'display_name': self._get_field_display_name(field)
            }
            
            if not is_met:
                all_requirements_met = False
        
        self.profile_requirements_met = requirements_met
        
        if all_requirements_met:
            self.mark_profile_completed()
            return True
        
        return False

    def _get_required_fields_for_role(self):
        """Get required fields based on user role"""
        required_fields = ['first_name', 'last_name', 'email', 'phone_number']
        
        if self.role == self.Role.STUDENT:
            required_fields.extend([
                'admission_number', 'grade_level', 'current_class', 
                'date_of_birth', 'parent_name', 'parent_phone'
            ])
        elif self.role in [self.Role.TEACHER, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR]:
            required_fields.extend(['staff_id', 'department', 'designation'])
        elif self.role == self.Role.PARENT:
            required_fields.extend(['parent_name', 'parent_phone'])
        
        return required_fields

    def _get_field_display_name(self, field_name):
        """Get display name for a field"""
        field_display_names = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'phone_number': _('Phone Number'),
            'admission_number': _('Admission Number'),
            'staff_id': _('Staff ID'),
            'grade_level': _('Grade Level'),
            'current_class': _('Current Class'),
            'date_of_birth': _('Date of Birth'),
            'department': _('Department'),
            'designation': _('Designation'),
            'parent_name': _('Parent Name'),
            'parent_phone': _('Parent Phone'),
        }
        return field_display_names.get(field_name, field_name.replace('_', ' ').title())

    def mark_profile_completed(self):
        """Mark profile as completed"""
        self.profile_completed = True
        self.profile_completion_date = timezone.now()
        
        if not self.profile_requirements_met:
            self.check_profile_completion()
        
        self.save(update_fields=[
            'profile_completed', 
            'profile_completion_date',
            'profile_requirements_met'
        ])

    def get_missing_profile_fields(self):
        """Get list of missing required profile fields"""
        if self.profile_completed:
            return []
        
        self.check_profile_completion()
        
        missing_fields = []
        for field, data in self.profile_requirements_met.items():
            if data.get('required', True) and not data.get('met', False):
                missing_fields.append({
                    'field': field,
                    'display_name': data.get('display_name', field)
                })
        
        return missing_fields

    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        if self.profile_completed:
            return 100
        
        if not self.profile_requirements_met:
            self.check_profile_completion()
        
        total_required = 0
        completed = 0
        
        for field, data in self.profile_requirements_met.items():
            if data.get('required', True):
                total_required += 1
                if data.get('met', False):
                    completed += 1
        
        if total_required == 0:
            return 100
        
        return int((completed / total_required) * 100)

    # === Dashboard & Redirection Methods ===
    def get_dashboard_url(self):
        """Get the appropriate dashboard URL based on user role"""
        return self.DASHBOARD_URLS.get(self.role, '/dashboard')

    def get_redirect_url_after_login(self):
        """
        Get redirect URL after successful login/2FA verification
        """
        # Check if user needs to complete profile
        if not self.profile_completed:
            return '/complete-profile'
        
        # Check if user is suspended
        if self.is_suspended:
            return '/account-suspended'
        
        # Check if user needs approval
        if not self.is_approved and self.requires_approval():
            return '/pending-approval'
        
        # Check if password is expired
        if self.is_password_expired():
            return '/change-password?expired=true'
        
        # Check if 2FA setup is required but not enabled
        if self.requires_2fa_setup and not self.has_2fa_enabled():
            return '/setup-2fa'
        
        # Return role-specific dashboard
        return self.get_dashboard_url()

    def requires_approval(self):
        """Check if user role requires manual approval"""
        return self.role in [
            self.Role.TEACHER, 
            self.Role.HEAD_TEACHER, 
            self.Role.CURRICULUM_COORDINATOR,
            self.Role.ACCOUNTANT,
            self.Role.IT_SUPPORT,
            self.Role.COUNSELOR
        ]

    # === Authentication & Security Methods ===
    def record_successful_login(self, ip_address, user_agent):
        """Record successful login attempt"""
        self.last_login = timezone.now()
        self.last_login_ip = ip_address
        self.last_login_user_agent = user_agent
        self.login_count += 1
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_activity = timezone.now()
        self.save(update_fields=[
            'last_login', 'last_login_ip', 'last_login_user_agent',
            'login_count', 'failed_login_attempts', 'account_locked_until',
            'last_activity'
        ])
        
        # Record login history
        LoginHistory.record_login_attempt(
            user=self,
            ip_address=ip_address,
            user_agent=user_agent,
            status=LoginHistory.LoginStatus.SUCCESS
        )

    def record_failed_login(self, ip_address=None, user_agent=None, reason=""):
        """Record failed login attempt and lock account if necessary"""
        self.failed_login_attempts += 1
        self.last_activity = timezone.now()
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save(update_fields=[
            'failed_login_attempts', 'last_activity', 'account_locked_until'
        ])
        
        # Record failed login history
        if ip_address:
            LoginHistory.record_login_attempt(
                user=self,
                ip_address=ip_address,
                user_agent=user_agent or '',
                status=LoginHistory.LoginStatus.FAILED,
                failure_reason=reason or "Invalid credentials"
            )

    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                # Auto-unlock if lock time has passed
                self.unlock_account()
        return False

    def unlock_account(self):
        """Unlock user account"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def set_password(self, raw_password):
        """Override set_password to track password change"""
        # Validate password strength
        self.validate_password_strength(raw_password)
        
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
        self.save(update_fields=['password', 'password_changed_at'])

    def is_password_expired(self):
        """Check if password needs to be changed (90 days)"""
        if self.password_changed_at:
            return timezone.now() > self.password_changed_at + timedelta(days=90)
        return False

    # === Email Verification Methods ===
    def send_verification_email(self, request=None):
        """Send email verification link"""
        token = OTPToken.create_otp(
            user=self,
            token_type=OTPToken.TokenType.EMAIL_VERIFICATION,
            purpose="Email verification"
        )
        
        # Create verification URL
        from django.urls import reverse
        verification_url = reverse('verify-email', kwargs={'token': token.token})
        if request:
            from django.http import HttpRequest
            if isinstance(request, HttpRequest):
                from django.urls import reverse
                verification_url = request.build_absolute_uri(verification_url)
        
        # Send email
        subject = _("Verify your email address - Delvok Academy")
        html_message = render_to_string('accounts/email_verification.html', {
            'user': self,
            'verification_url': verification_url,
            'token': token.token,
            'expiry_hours': 24
        })
        plain_message = strip_tags(html_message)
        
        self.email_user(subject, plain_message, html_message=html_message)
        return token

    # === Password Reset Methods ===
    def initiate_password_reset(self, request=None):
        """Initiate password reset process"""
        # Delete existing password reset tokens
        self.otp_tokens.filter(
            token_type=OTPToken.TokenType.PASSWORD_RESET,
            is_used=False
        ).update(is_used=True)
        
        # Create new token
        token = OTPToken.create_otp(
            user=self,
            token_type=OTPToken.TokenType.PASSWORD_RESET,
            purpose="Password reset",
            validity_minutes=30
        )
        
        # Create reset URL
        from django.urls import reverse
        reset_url = reverse('password-reset-confirm', kwargs={'token': token.token})
        if request:
            from django.http import HttpRequest
            if isinstance(request, HttpRequest):
                reset_url = request.build_absolute_uri(reset_url)
        
        # Send email
        subject = _("Password Reset Request - Delvok Academy")
        html_message = render_to_string('accounts/password_reset_email.html', {
            'user': self,
            'reset_url': reset_url,
            'token': token.token,
            'expiry_minutes': 30
        })
        plain_message = strip_tags(html_message)
        
        self.email_user(subject, plain_message, html_message=html_message)
        return token

    # === Permission & Role Methods ===
    def get_permissions(self):
        """Get user permissions for frontend AuthContext"""
        permissions = []
        
        # Role-based permissions
        if self.role == self.Role.ADMIN:
            permissions.extend(['*', 'users.manage', 'system.manage', 'finance.manage', 'reports.manage'])
        elif self.role == self.Role.ACCOUNTANT:
            permissions.extend(['finance.view', 'finance.manage', 'reports.view', 'reports.generate'])
        elif self.role == self.Role.TEACHER:
            permissions.extend(['students.view', 'attendance.manage', 'grades.manage', 'lessons.manage'])
        elif self.role == self.Role.STUDENT:
            permissions.extend(['profile.view', 'grades.view', 'attendance.view', 'courses.view'])
        elif self.role == self.Role.PARENT:
            permissions.extend(['profile.view', 'children.view', 'grades.view', 'attendance.view'])
        elif self.role == self.Role.HEAD_TEACHER:
            permissions.extend(['students.manage', 'teachers.manage', 'attendance.manage', 'grades.manage', 'reports.view'])
        elif self.role == self.Role.IT_SUPPORT:
            permissions.extend(['system.view', 'users.manage', 'tickets.manage'])
        
        return permissions

    def get_feature_flags(self):
        """Get feature flags for frontend AuthContext"""
        flags = {
            'canViewDashboard': True,
            'canExportData': self.role in [self.Role.ADMIN, self.Role.ACCOUNTANT, self.Role.HEAD_TEACHER],
            'canManageStudents': self.role in [self.Role.ADMIN, self.Role.TEACHER, self.Role.HEAD_TEACHER],
            'canManageFinance': self.role in [self.Role.ADMIN, self.Role.ACCOUNTANT],
            'canGenerateReports': self.role in [self.Role.ADMIN, self.Role.ACCOUNTANT, self.Role.HEAD_TEACHER],
            'canManageUsers': self.role in [self.Role.ADMIN, self.Role.HEAD_TEACHER],
            'canManageSystem': self.role in [self.Role.ADMIN, self.Role.IT_SUPPORT],
            'canManageCurriculum': self.role in [self.Role.ADMIN, self.Role.CURRICULUM_COORDINATOR, self.Role.HEAD_TEACHER],
            'canViewAnalytics': self.role in [self.Role.ADMIN, self.Role.HEAD_TEACHER, self.Role.ACCOUNTANT],
            'canSendNotifications': self.role in [self.Role.ADMIN, self.Role.HEAD_TEACHER, self.Role.TEACHER],
            'canUploadDocuments': self.role in [self.Role.ADMIN, self.Role.TEACHER, self.Role.STUDENT, self.Role.PARENT],
        }
        return flags

    # === Utility Methods ===
    def clean(self):
        """Custom validation for the model"""
        errors = {}
        
        # Email validation
        if self.email:
            existing_user = User.objects.filter(email=self.email)
            if self.pk:  # If updating, exclude self
                existing_user = existing_user.exclude(pk=self.pk)
            if existing_user.exists():
                errors['email'] = _('A user with this email already exists.')
        
        # Role-specific validation
        if self.pk:  # Only for existing users
            if self.role == self.Role.STUDENT and not self.admission_number:
                errors['admission_number'] = _('Admission number is required for students.')
            
            if self.role in [self.Role.TEACHER, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR] and not self.staff_id:
                errors['staff_id'] = _('Staff ID is required for staff members.')
        
        # Age validation for students
        if self.role == self.Role.STUDENT and self.date_of_birth:
            age = self.age
            if age and age < 3:
                errors['date_of_birth'] = _('Student must be at least 3 years old.')
            if age and age > 25:
                errors['date_of_birth'] = _('Student age seems unrealistic.')
        
        # Password validation if provided
        if self.password and len(self.password) > 0:
            try:
                self.validate_password_strength(self.password)
            except ValidationError as e:
                errors['password'] = e.messages
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save method to handle automatic field population"""
        is_new = self._state.adding
        
        # Auto-generate identifiers if needed for new users
        if is_new:
            if self.role == self.Role.STUDENT and not self.admission_number:
                self.admission_number = self.generate_admission_number()
            
            if self.role in [self.Role.TEACHER, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR, 
                            self.Role.ACCOUNTANT, self.Role.IT_SUPPORT, self.Role.COUNSELOR,
                            self.Role.LIBRARIAN, self.Role.OFFICE_STAFF] and not self.staff_id:
                self.staff_id = self.generate_staff_id()
        
        # Set is_staff based on role
        if not self.is_staff:
            self.is_staff = self.role in [
                self.Role.ADMIN, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR,
                self.Role.TEACHER, self.Role.ACCOUNTANT, self.Role.IT_SUPPORT, self.Role.COUNSELOR,
                self.Role.LIBRARIAN, self.Role.OFFICE_STAFF
            ]
        
        # Set academic year if not set (for students)
        if self.role == self.Role.STUDENT and not self.academic_year:
            self.academic_year = self.get_current_academic_year()
        
        # Track profile updates for existing users
        if not is_new:
            try:
                original = User.objects.get(pk=self.pk)
                # Check if any profile fields changed
                profile_fields = ['first_name', 'last_name', 'middle_name', 'phone_number', 'address']
                for field in profile_fields:
                    if getattr(original, field) != getattr(self, field):
                        self.last_profile_update = timezone.now()
                        break
            except User.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    def generate_admission_number(self):
        """Generate unique admission number"""
        year = timezone.now().year
        last_student = User.objects.filter(
            role=self.Role.STUDENT,
            admission_number__isnull=False
        ).order_by('-admission_number').first()
        
        new_number = 1
        if last_student and last_student.admission_number:
            try:
                # Extract the number part from format like DEL-STU-2024-0001
                parts = last_student.admission_number.split('-')
                if len(parts) == 4:
                    last_number = int(parts[-1])
                    new_number = last_number + 1
            except (ValueError, IndexError):
                pass
            
        return f"DEL-STU-{year}-{new_number:04d}"

    def generate_staff_id(self):
        """Generate unique staff ID"""
        year = timezone.now().year
        role_prefix = {
            self.Role.TEACHER: 'TCH',
            self.Role.HEAD_TEACHER: 'HT',
            self.Role.CURRICULUM_COORDINATOR: 'CC',
            self.Role.ACCOUNTANT: 'ACC',
            self.Role.ADMIN: 'ADM',
            self.Role.IT_SUPPORT: 'IT',
            self.Role.COUNSELOR: 'COU',
            self.Role.LIBRARIAN: 'LIB',
            self.Role.OFFICE_STAFF: 'OFF'
        }.get(self.role, 'EMP')
        
        last_staff = User.objects.filter(
            role__in=[
                self.Role.TEACHER, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR,
                self.Role.ACCOUNTANT, self.Role.ADMIN, self.Role.IT_SUPPORT, self.Role.COUNSELOR,
                self.Role.LIBRARIAN, self.Role.OFFICE_STAFF
            ],
            staff_id__isnull=False
        ).order_by('-staff_id').first()
        
        new_number = 1
        if last_staff and last_staff.staff_id:
            try:
                parts = last_staff.staff_id.split('-')
                if len(parts) == 4:
                    last_number = int(parts[-1])
                    new_number = last_number + 1
            except (ValueError, IndexError):
                pass
            
        return f"DEL-{role_prefix}-{year}-{new_number:04d}"

    def get_current_academic_year(self):
        """Get current academic year in format YYYY-YYYY"""
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Academic year typically runs from September to August
        if current_month >= 9:  # September to December
            return f"{current_year}-{current_year + 1}"
        else:  # January to August
            return f"{current_year - 1}-{current_year}"

    # === Session Management ===
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    # === Data Export & GDPR Compliance ===
    def export_data(self, include_sensitive=False):
        """Export user data for GDPR compliance"""
        data = {
            'basic_info': {
                'name': self.get_full_name(),
                'email': self.email,
                'role': self.get_role_display(),
                'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            },
            'profile_info': {
                'phone': self.phone_number,
                'address': self.address,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'gender': self.get_gender_display() if self.gender else None,
                'nationality': self.nationality,
            }
        }
        
        if include_sensitive:
            data['academic_info'] = {
                'admission_number': self.admission_number,
                'staff_id': self.staff_id,
                'grade_level': self.grade_level,
                'current_class': self.current_class,
                'house': self.get_house_display() if self.house else None,
                'academic_year': self.academic_year,
            }
            data['activity'] = {
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'login_count': self.login_count,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            }
            data['system_info'] = {
                'is_active': self.is_active,
                'is_verified': self.is_verified,
                'is_approved': self.is_approved,
                'profile_completed': self.profile_completed,
                'profile_completion_date': self.profile_completion_date.isoformat() if self.profile_completion_date else None,
            }
        
        return data

    # === Parent-Child Relationship Methods ===
    def get_children(self):
        """Get children for parent users"""
        if self.role == self.Role.PARENT:
            return User.objects.filter(
                role=self.Role.STUDENT,
                parent_email=self.email
            )
        return User.objects.none()

    def get_parents(self):
        """Get parents for student users"""
        if self.role == self.Role.STUDENT and self.parent_email:
            return User.objects.filter(
                role=self.Role.PARENT,
                email=self.parent_email
            )
        return User.objects.none()

    # === Bulk Operations ===
    @classmethod
    def bulk_update_status(cls, user_ids, status_field, status_value):
        """Bulk update user status"""
        with transaction.atomic():
            users = cls.objects.filter(id__in=user_ids)
            update_count = users.update(**{status_field: status_value})
            
            # Log the action
            logger.info(f"Bulk updated {update_count} users: {status_field}={status_value}")
            
            return update_count

    # === Property Methods ===
    @property
    def age(self):
        """Calculate current age"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def display_name(self):
        """Get display name with role"""
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def identifier(self):
        """Get primary identifier"""
        return self.admission_number or self.staff_id or self.email

    @property
    def years_of_service(self):
        """Calculate years of service for staff"""
        if self.employment_date:
            today = date.today()
            return today.year - self.employment_date.year - (
                (today.month, today.day) < (self.employment_date.month, self.employment_date.day)
            )
        return None

    @property
    def requires_2fa_setup(self):
        """Check if user should setup 2FA (admins and accountants)"""
        return self.role in [self.Role.ADMIN, self.Role.ACCOUNTANT, self.Role.IT_SUPPORT]

    @property
    def is_online(self):
        """Check if user is currently online (active in last 15 minutes)"""
        if self.last_activity:
            return timezone.now() - self.last_activity < timedelta(minutes=15)
        return False

    @property
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        return self.get_profile_completion_percentage()
    
    @property
    def is_teacher(self):
        """Check if user is a teacher or has teacher privileges"""
        return self.role in [
            self.Role.TEACHER,
            self.Role.HEAD_TEACHER,
            self.Role.CURRICULUM_COORDINATOR,
            self.Role.ADMIN
        ]
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == self.Role.STUDENT
    
    @property
    def is_parent(self):
        """Check if user is a parent"""
        return self.role == self.Role.PARENT
    
    @property
    def is_staff_member(self):
        """Check if user is any type of staff"""
        return self.role in [
            self.Role.ADMIN,
            self.Role.HEAD_TEACHER,
            self.Role.CURRICULUM_COORDINATOR,
            self.Role.TEACHER,
            self.Role.OFFICE_STAFF,
            self.Role.LIBRARIAN,
            self.Role.ACCOUNTANT,
            self.Role.IT_SUPPORT,
            self.Role.COUNSELOR
        ]
    
    @property
    def is_finance_user(self):
        """Check if user has finance access"""
        return self.role in [self.Role.ADMIN, self.Role.ACCOUNTANT]
    
    @property
    def is_management(self):
        """Check if user is in management role"""
        return self.role in [self.Role.ADMIN, self.Role.HEAD_TEACHER, self.Role.CURRICULUM_COORDINATOR]
    
    @property
    def has_document_upload_access(self):
        """Check if user can upload documents"""
        return self.role in [
            self.Role.ADMIN,
            self.Role.TEACHER,
            self.Role.HEAD_TEACHER,
            self.Role.STUDENT,
            self.Role.PARENT
        ]


# ============================================================================
# PROFILE MODELS
# ============================================================================

class UserProfile(BaseModel):
    """Enhanced User profile model for additional user information"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_profile'
    )
    bio = models.TextField(blank=True, verbose_name=_("Biography"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    social_links = models.JSONField(default=dict, blank=True, verbose_name=_("Social Links"))
    notifications_enabled = models.BooleanField(default=True, verbose_name=_("Notifications Enabled"))
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email Notifications"))
    sms_notifications = models.BooleanField(default=False, verbose_name=_("SMS Notifications"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Push Notifications"))
    language = models.CharField(max_length=10, default='en', verbose_name=_("Preferred Language"))
    timezone = models.CharField(max_length=50, default='UTC', verbose_name=_("Timezone"))
    
    # Additional profile fields
    hobbies = models.TextField(blank=True, verbose_name=_("Hobbies & Interests"))
    achievements = models.JSONField(default=list, blank=True, verbose_name=_("Achievements"))
    skills = models.JSONField(default=list, blank=True, verbose_name=_("Skills"))
    education_background = models.JSONField(default=list, blank=True, verbose_name=_("Education Background"))
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', _('Public')),
            ('school_only', _('School Only')),
            ('private', _('Private'))
        ],
        default='school_only',
        verbose_name=_("Profile Visibility")
    )
    
    # Communication preferences
    contact_preference = models.CharField(
        max_length=20,
        choices=[
            ('email', _('Email')),
            ('phone', _('Phone')),
            ('both', _('Both'))
        ],
        default='email',
        verbose_name=_("Preferred Contact Method")
    )

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"

    def add_achievement(self, title, description, date_achieved, category=None):
        """Add an achievement to user profile"""
        achievement = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'date_achieved': date_achieved.isoformat() if hasattr(date_achieved, 'isoformat') else str(date_achieved),
            'category': category,
            'created_at': timezone.now().isoformat()
        }
        
        if not self.achievements:
            self.achievements = []
        
        self.achievements.append(achievement)
        self.save()

    def add_skill(self, skill_name, proficiency_level='intermediate', category=None):
        """Add a skill to user profile"""
        skill = {
            'id': str(uuid.uuid4()),
            'name': skill_name,
            'proficiency_level': proficiency_level,
            'category': category,
            'added_at': timezone.now().isoformat()
        }
        
        if not self.skills:
            self.skills = []
        
        self.skills.append(skill)
        self.save()


# ============================================================================
# AUTHENTICATION & SECURITY MODELS
# ============================================================================

class TwoFactorAuth(BaseModel):
    """Enhanced 2FA model with session management for dashboard redirection"""
    
    class Method(models.TextChoices):
        EMAIL = 'email', _('Email')
        AUTHENTICATOR = 'authenticator', _('Authenticator App')
        SMS = 'sms', _('SMS')
        VOICE = 'voice', _('Voice Call')

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='two_factor_auth'
    )
    secret_key = models.CharField(max_length=32, blank=True)
    is_enabled = models.BooleanField(default=False)
    primary_method = models.CharField(
        max_length=20, 
        choices=Method.choices, 
        default=Method.EMAIL
    )
    backup_codes = models.JSONField(default=list, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    recovery_email = models.EmailField(blank=True)
    recovery_phone = models.CharField(max_length=17, blank=True)
    last_backup_code_generated = models.DateTimeField(null=True, blank=True)

    # Session management for OTP verification flow
    pending_session_token = models.CharField(max_length=100, blank=True)
    pending_session_expiry = models.DateTimeField(null=True, blank=True)
    pending_redirect_url = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _("Two Factor Authentication")
        verbose_name_plural = _("Two Factor Authentications")
        indexes = [
            models.Index(fields=['user', 'is_enabled']),
        ]

    def __str__(self):
        return f"2FA for {self.user.email}"

    def save(self, *args, **kwargs):
        """Override save to generate secret key if not set"""
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()
        super().save(*args, **kwargs)

    def generate_secret(self):
        """Generate a new secret key"""
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key

    def create_pending_session(self, session_token, redirect_url=None):
        """Create a pending session for OTP verification"""
        self.pending_session_token = session_token
        self.pending_session_expiry = timezone.now() + timedelta(minutes=10)
        self.pending_redirect_url = redirect_url or self.user.get_dashboard_url()
        self.save()

    def verify_pending_session(self, session_token, otp_code):
        """Verify OTP and pending session"""
        if (not self.pending_session_token or 
            self.pending_session_token != session_token or
            timezone.now() > self.pending_session_expiry):
            return False, "Invalid or expired session"
        
        if not self.verify_otp(otp_code):
            return False, "Invalid OTP code"
        
        # Session verified successfully
        redirect_url = self.pending_redirect_url
        self.clear_pending_session()
        
        return True, redirect_url

    def clear_pending_session(self):
        """Clear pending session data"""
        self.pending_session_token = ""
        self.pending_session_expiry = None
        self.pending_redirect_url = ""
        self.save()

    def generate_provisioning_uri(self):
        """Generate URI for QR code"""
        if not self.secret_key:
            self.generate_secret()
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email, 
            issuer_name="Delvok Academy"
        )

    def generate_qr_code(self):
        """Generate QR code as base64"""
        try:
            uri = self.generate_provisioning_uri()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return ""

    def verify_otp(self, otp, window=2):
        """Verify OTP code with extended window for time sync issues"""
        if not self.is_enabled:
            return True
            
        if not self.secret_key:
            return False
            
        totp = pyotp.TOTP(self.secret_key)
        is_valid = totp.verify(otp, valid_window=window)
        if is_valid:
            self.last_used = timezone.now()
            self.save(update_fields=['last_used'])
        return is_valid

    def generate_backup_codes(self, count=10):
        """Generate backup codes with timestamp"""
        backup_codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = [
            {
                'code': code, 
                'used': False, 
                'generated_at': timezone.now().isoformat()
            } for code in backup_codes
        ]
        self.last_backup_code_generated = timezone.now()
        self.save()
        return backup_codes

    def verify_backup_code(self, code):
        """Verify backup code and mark as used"""
        for backup_code in self.backup_codes:
            if backup_code['code'] == code and not backup_code['used']:
                backup_code['used'] = True
                backup_code['used_at'] = timezone.now().isoformat()
                self.save()
                return True
        return False

    def get_unused_backup_codes(self):
        """Get list of unused backup codes"""
        return [bc for bc in self.backup_codes if not bc.get('used', False)]

    def disable_2fa(self):
        """Disable 2FA and clear all data"""
        self.is_enabled = False
        self.secret_key = ""
        self.backup_codes = []
        self.pending_session_token = ""
        self.pending_session_expiry = None
        self.pending_redirect_url = ""
        self.last_backup_code_generated = None
        self.save()


class OTPToken(BaseModel):
    """Enhanced OTP Token model for email/SMS verification and password reset"""
    
    class TokenType(models.TextChoices):
        EMAIL_VERIFICATION = 'email_verification', _('Email Verification')
        PHONE_VERIFICATION = 'phone_verification', _('Phone Verification')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
        LOGIN_VERIFICATION = 'login_verification', _('Login Verification')
        ACCOUNT_RECOVERY = 'account_recovery', _('Account Recovery')
        TWO_FACTOR_BACKUP = 'two_factor_backup', _('2FA Backup')
        ACCOUNT_APPROVAL = 'account_approval', _('Account Approval')
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='otp_tokens'
    )
    token = models.CharField(max_length=6, verbose_name=_("OTP Token"))
    token_type = models.CharField(
        max_length=20, 
        choices=TokenType.choices, 
        verbose_name=_("Token Type")
    )
    purpose = models.CharField(max_length=100, blank=True, verbose_name=_("Purpose"))
    is_used = models.BooleanField(default=False, verbose_name=_("Is Used"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Used At"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Request IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    
    class Meta:
        verbose_name = _("OTP Token")
        verbose_name_plural = _("OTP Tokens")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used', 'expires_at']),
            models.Index(fields=['user', 'token_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"OTP {self.token} for {self.user.email} ({self.token_type})"
    
    def is_valid(self):
        """Check if OTP token is valid and not expired"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def clean(self):
        """Validate token expiration"""
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError(_("Expiration time must be in the future"))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def create_otp(cls, user, token_type, purpose="", ip_address=None, user_agent="", validity_minutes=10):
        """Create a new OTP token"""
        # Clean up expired tokens
        cls.objects.filter(
            user=user, 
            expires_at__lt=timezone.now()
        ).delete()
        
        # Generate random 6-digit token
        token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        otp = cls.objects.create(
            user=user,
            token=token,
            token_type=token_type,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=validity_minutes),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return otp

    @classmethod
    def verify_otp(cls, user, token, token_type):
        """Verify OTP token"""
        try:
            otp = cls.objects.get(
                user=user,
                token=token,
                token_type=token_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            otp.mark_used()
            return True, "OTP verified successfully"
        except cls.DoesNotExist:
            return False, "Invalid or expired OTP"


class LoginHistory(BaseModel):
    """Enhanced Login history tracking for security monitoring"""
    
    class LoginStatus(models.TextChoices):
        SUCCESS = 'success', _('Success')
        FAILED = 'failed', _('Failed')
        LOCKED = 'locked', _('Locked')
        TWO_FACTOR_REQUIRED = 'two_factor_required', _('2FA Required')
        TWO_FACTOR_VERIFIED = 'two_factor_verified', _('2FA Verified')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
        ACCOUNT_RECOVERY = 'account_recovery', _('Account Recovery')
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_history'
    )
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Location"))
    device_type = models.CharField(max_length=50, blank=True, verbose_name=_("Device Type"))
    browser = models.CharField(max_length=50, blank=True, verbose_name=_("Browser"))
    platform = models.CharField(max_length=50, blank=True, verbose_name=_("Platform"))
    login_status = models.CharField(
        max_length=20, 
        choices=LoginStatus.choices, 
        verbose_name=_("Login Status")
    )
    failure_reason = models.CharField(max_length=100, blank=True, verbose_name=_("Failure Reason"))
    session_key = models.CharField(max_length=100, blank=True, verbose_name=_("Session Key"))
    two_fa_method = models.CharField(
        max_length=20, 
        blank=True, 
        choices=TwoFactorAuth.Method.choices, 
        verbose_name=_("2FA Method")
    )
    country = models.CharField(max_length=50, blank=True, verbose_name=_("Country"))
    city = models.CharField(max_length=50, blank=True, verbose_name=_("City"))
    is_suspicious = models.BooleanField(default=False, verbose_name=_("Suspicious Activity"))
    
    class Meta:
        verbose_name = _("Login History")
        verbose_name_plural = _("Login History")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'login_status']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_suspicious']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.login_status} - {self.created_at}"
    
    @classmethod
    def record_login_attempt(cls, user, ip_address, user_agent, status, failure_reason='', session_key='', two_fa_method=''):
        """Record login attempt with enhanced location detection"""
        # Parse user agent for device information
        device_info = cls.parse_user_agent(user_agent)
        
        # Get location from IP (simplified version)
        location_info = cls.get_location_from_ip(ip_address)
        
        # Check for suspicious activity
        is_suspicious = cls.detect_suspicious_activity(user, ip_address, location_info)
        
        return cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location_info.get('location', ''),
            country=location_info.get('country', ''),
            city=location_info.get('city', ''),
            device_type=device_info.get('device_type', ''),
            browser=device_info.get('browser', ''),
            platform=device_info.get('platform', ''),
            login_status=status,
            failure_reason=failure_reason,
            session_key=session_key,
            two_fa_method=two_fa_method,
            is_suspicious=is_suspicious
        )
    
    @staticmethod
    def parse_user_agent(user_agent):
        """Enhanced user agent parsing"""
        info = {
            'device_type': 'Desktop',
            'browser': 'Unknown',
            'platform': 'Unknown'
        }
        
        if not user_agent:
            return info
            
        user_agent_lower = user_agent.lower()
        
        # Detect device type
        if 'mobile' in user_agent_lower:
            info['device_type'] = 'Mobile'
        elif 'tablet' in user_agent_lower:
            info['device_type'] = 'Tablet'
        elif 'tv' in user_agent_lower:
            info['device_type'] = 'TV'
        elif 'bot' in user_agent_lower or 'crawler' in user_agent_lower:
            info['device_type'] = 'Bot'
        
        # Detect browser
        if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
            info['browser'] = 'Chrome'
        elif 'firefox' in user_agent_lower:
            info['browser'] = 'Firefox'
        elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            info['browser'] = 'Safari'
        elif 'edg' in user_agent_lower:
            info['browser'] = 'Edge'
        elif 'opera' in user_agent_lower:
            info['browser'] = 'Opera'
        elif 'brave' in user_agent_lower:
            info['browser'] = 'Brave'
        
        # Detect platform
        if 'windows' in user_agent_lower:
            info['platform'] = 'Windows'
        elif 'mac' in user_agent_lower:
            info['platform'] = 'macOS'
        elif 'linux' in user_agent_lower:
            info['platform'] = 'Linux'
        elif 'android' in user_agent_lower:
            info['platform'] = 'Android'
        elif 'ios' in user_agent_lower:
            info['platform'] = 'iOS'
        elif 'cros' in user_agent_lower:
            info['platform'] = 'Chrome OS'
        
        return info
    
    @staticmethod
    def get_location_from_ip(ip_address):
        """Get location from IP address - simplified version"""
        location_info = {
            'location': '',
            'country': '',
            'city': ''
        }
        
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            location_info['location'] = 'Localhost'
            return location_info
        
        # For production, integrate with a proper IP geolocation service
        # This is a simplified version
        location_info['location'] = 'Unknown'
        location_info['country'] = 'Unknown'
        location_info['city'] = 'Unknown'
            
        return location_info
    
    @staticmethod
    def detect_suspicious_activity(user, ip_address, location_info):
        """Detect potentially suspicious login activity"""
        # Check if this is a new location for the user
        recent_logins = LoginHistory.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).exclude(ip_address=ip_address)
        
        if recent_logins.exists():
            # User has logged in from different IPs recently
            unique_ips = recent_logins.values('ip_address').distinct().count()
            if unique_ips >= 3:  # Logged in from 3+ different IPs in 30 days
                return True
        
        # Check if location is very different from usual
        usual_country = recent_logins.exclude(country='').values('country').annotate(
            count=models.Count('country')
        ).order_by('-count').first()
        
        if (usual_country and 
            location_info.get('country') and 
            location_info.get('country') != 'Unknown' and
            location_info.get('country') != usual_country['country']):
            return True
            
        return False