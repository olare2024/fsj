# accounts/models.py - REFACTORED AND ORGANIZED VERSION

import base64
import logging
import secrets
import uuid
from datetime import date, timedelta
from io import BytesIO

import pyotp
import qrcode
import requests
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import (EmailValidator, MinLengthValidator,
                                    RegexValidator)
from django.db import models, transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS AND ENUMS
# ============================================================================

class GenderChoices(models.TextChoices):
    """Gender choices for users"""
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHER = 'other', _('Other')
    PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')
GENDER_CHOICES = GenderChoices

class UserRole(models.TextChoices):
    """User role choices"""
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


# Dashboard URL mappings - defined separately
USER_ROLE_DASHBOARDS = {
    UserRole.ADMIN: '/admin/admin-portal',
    UserRole.HEAD_TEACHER: '/head-teacher/headteacher-portal',
    UserRole.CURRICULUM_COORDINATOR: '/curriculum/curriculum-portal',
    UserRole.TEACHER: '/teacher/teacher-portal',
    UserRole.OFFICE_STAFF: '/staff/staff-portal',
    UserRole.STUDENT: '/student/student-portal',
    UserRole.PARENT: '/parent/parent-portal',
    UserRole.LIBRARIAN: '/library/library-portal',
    UserRole.ACCOUNTANT: '/finance/finance-portal',
    UserRole.IT_SUPPORT: '/it/it-portal',
    UserRole.COUNSELOR: '/counselor/counselor-portal',
}


def get_dashboard_url(role):
    """Get dashboard URL for a given role"""
    return USER_ROLE_DASHBOARDS.get(role, '/dashboard')


class CurriculumChoices(models.TextChoices):
    """Curriculum choices"""
    CBC = 'cbc', _('CBC - Competency Based Curriculum')
    ICSE = 'icse', _('ICSE - Indian Certificate of Secondary Education')
    AMERICAN = 'american', _('American Curriculum')
    BRITISH = 'british', _('British Curriculum')
    MONTESSORI = 'montessori', _('Montessori')
    COMBINED = 'combined', _('Combined Curriculum')
    IGCSE = 'igcse', _('IGCSE')
    IB = 'ib', _('International Baccalaureate')


class HouseChoices(models.TextChoices):
    """House system choices"""
    UNITY = 'unity', _('Unity House')
    COURAGE = 'courage', _('Courage House')
    WISDOM = 'wisdom', _('Wisdom House')
    SUCCESS = 'success', _('Success House')
    EXCELLENCE = 'excellence', _('Excellence House')
    INTEGRITY = 'integrity', _('Integrity House')
    BRAVERY = 'bravery', _('Bravery House')
    HONOR = 'honor', _('Honor House')


class BloodGroupChoices(models.TextChoices):
    """Blood group choices"""
    A_POSITIVE = 'a_positive', _('A+')
    A_NEGATIVE = 'a_negative', _('A-')
    B_POSITIVE = 'b_positive', _('B+')
    B_NEGATIVE = 'b_negative', _('B-')
    AB_POSITIVE = 'ab_positive', _('AB+')
    AB_NEGATIVE = 'ab_negative', _('AB-')
    O_POSITIVE = 'o_positive', _('O+')
    O_NEGATIVE = 'o_negative', _('O-')


class TwoFAMethodChoices(models.TextChoices):
    """2FA method choices"""
    EMAIL = 'email', _('Email')
    AUTHENTICATOR = 'authenticator', _('Authenticator App')
    SMS = 'sms', _('SMS')
    VOICE = 'voice', _('Voice Call')


class TokenTypeChoices(models.TextChoices):
    """OTP token type choices"""
    EMAIL_VERIFICATION = 'email_verification', _('Email Verification')
    PHONE_VERIFICATION = 'phone_verification', _('Phone Verification')
    PASSWORD_RESET = 'password_reset', _('Password Reset')
    LOGIN_VERIFICATION = 'login_verification', _('Login Verification')
    ACCOUNT_RECOVERY = 'account_recovery', _('Account Recovery')
    TWO_FACTOR_BACKUP = 'two_factor_backup', _('2FA Backup')
    ACCOUNT_APPROVAL = 'account_approval', _('Account Approval')


class LoginStatusChoices(models.TextChoices):
    """Login status choices"""
    SUCCESS = 'success', _('Success')
    FAILED = 'failed', _('Failed')
    LOCKED = 'locked', _('Locked')
    TWO_FACTOR_REQUIRED = 'two_factor_required', _('2FA Required')
    TWO_FACTOR_VERIFIED = 'two_factor_verified', _('2FA Verified')
    PASSWORD_RESET = 'password_reset', _('Password Reset')
    ACCOUNT_RECOVERY = 'account_recovery', _('Account Recovery')


class SessionStatusChoices(models.TextChoices):
    """Login session status choices"""
    PENDING_OTP = 'pending_otp', _('Pending OTP Verification')
    VERIFIED = 'verified', _('OTP Verified')
    EXPIRED = 'expired', _('Expired')
    FAILED = 'failed', _('OTP Verification Failed')
    REVOKED = 'revoked', _('Session Revoked')


# ============================================================================
# BASE CLASSES AND MIXINS
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
    
    @classmethod
    def bulk_update_status(cls, ids, field, value):
        """Bulk update status of objects"""
        with transaction.atomic():
            updated = cls.objects.filter(id__in=ids).update(**{field: value})
            logger.info(f"Bulk updated {updated} {cls.__name__} objects: {field}={value}")
            return updated


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
    
    @property
    def formatted_phone(self):
        """Get formatted phone number"""
        if self.phone_number:
            return f"+{self.phone_number}" if not self.phone_number.startswith('+') else self.phone_number
        return None


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
    
    blood_group = models.CharField(
        max_length=15, 
        choices=BloodGroupChoices.choices, 
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
# MANAGERS
# ============================================================================

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
        role = extra_fields.get('role', UserRole.STUDENT)
        if role in [UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR, 
                   UserRole.TEACHER, UserRole.ACCOUNTANT, UserRole.IT_SUPPORT]:
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
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        return self.get(email=email)
    
    def get_active_users(self):
        """Get all active users"""
        return self.filter(is_active=True)
    
    def get_users_by_role(self, role):
        """Get users by role"""
        return self.filter(role=role, is_active=True)
    
    def get_staff_members(self):
        """Get all staff members"""
        staff_roles = [
            UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR,
            UserRole.TEACHER, UserRole.OFFICE_STAFF, UserRole.LIBRARIAN,
            UserRole.ACCOUNTANT, UserRole.IT_SUPPORT, UserRole.COUNSELOR
        ]
        return self.filter(role__in=staff_roles, is_active=True)
    
    def get_students(self):
        """Get all students"""
        return self.filter(role=UserRole.STUDENT, is_active=True)
    
    def get_parents(self):
        """Get all parents"""
        return self.filter(role=UserRole.PARENT, is_active=True)


# ============================================================================
# MAIN USER MODEL
# ============================================================================

class User(AbstractBaseUser, PermissionsMixin, BaseModel, 
           ContactInfoMixin, EmergencyContactMixin, MedicalInfoMixin):
    """
    Enhanced Custom User Model for Delvok Academy Management System
    with Dashboard Redirection Support
    """
    
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
        choices=UserRole.choices, 
        default=UserRole.STUDENT, 
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
        choices=GenderChoices.choices, 
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
        choices=CurriculumChoices.choices, 
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
        choices=HouseChoices.choices, 
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
        null=True, 
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

    # ====================
    # CORE USER METHODS
    # ====================
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
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
    
    # ====================
    # VALIDATION METHODS
    # ====================
    
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
        
        # Age validation for students
        if self.role == UserRole.STUDENT and self.date_of_birth:
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
    
    # ====================
    # PROFILE COMPLETION
    # ====================
    
    def check_profile_completion(self, force_check=False):
        """Check if user has completed profile requirements"""
        if self.profile_completed and not force_check:
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
        

        try:
            import json

            #Test if it's valid JSON
            json.dumps(requirements_met)
            self.profile_requirements_met = requirements_met
        except (TypeError, ValueError):
            self.profile_requirements_met = {}
        
        if all_requirements_met:
            self.mark_profile_completed()
            return True
        
        return False
    
    def _get_required_fields_for_role(self):
        """Get required fields based on user role"""
        required_fields = ['first_name', 'last_name', 'email', 'phone_number']
        
        if self.role == UserRole.STUDENT:
            required_fields.extend([
                'admission_number', 'grade_level', 'current_class', 
                'date_of_birth', 'parent_name', 'parent_phone'
            ])
        elif self.role in [UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR]:
            required_fields.extend(['staff_id', 'department', 'designation'])
        elif self.role == UserRole.PARENT:
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
        cache_key = f"profile_completion_{self.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        if self.profile_completed:
            result = 100
        else:
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
                result = 100
            else:
                result = int((completed / total_required) * 100)
        
        cache.set(cache_key, result, 300)
        return result
    
    def update_profile_completion_status(self):
        """Update profile completion status and return missing fields"""
        was_completed = self.profile_completed
        
        self.check_profile_completion(force_check=True)
        
        missing_fields = []
        for field, data in self.profile_requirements_met.items():
            if data.get('required', True) and not data.get('met', False):
                missing_fields.append({
                    'field': field,
                    'display_name': data.get('display_name', field),
                    'required': True
                })
        
        if not was_completed and self.profile_completed:
            self.profile_completion_date = timezone.now()
            self.save(update_fields=['profile_completion_date'])
        
        return {
            'profile_completed': self.profile_completed,
            'completion_percentage': self.get_profile_completion_percentage(),
            'missing_fields': missing_fields,
            'requirements_met': self.profile_requirements_met,
            'just_completed': not was_completed and self.profile_completed
        }
    
    # ====================
    # DASHBOARD & REDIRECTION
    # ====================
    
    def get_dashboard_url(self):
        """Get the appropriate dashboard URL based on user role"""
        return get_dashboard_url(self.role)
    
    def get_redirect_url_after_login(self):
        """Get redirect URL after successful login/2FA verification"""
        if not self.profile_completed:
            return '/complete-profile'
        
        if self.is_suspended:
            return '/account-suspended'
        
        if not self.is_approved and self.requires_approval():
            return '/pending-approval'
        
        if self.is_password_expired():
            return '/change-password?expired=true'
        
        if self.requires_2fa_setup and not self.has_2fa_enabled():
            return '/setup-2fa'
        
        return self.get_dashboard_url()
    
    def requires_approval(self):
        """Check if user role requires manual approval"""
        return self.role in [
            UserRole.TEACHER, 
            UserRole.HEAD_TEACHER, 
            UserRole.CURRICULUM_COORDINATOR,
            UserRole.ACCOUNTANT,
            UserRole.IT_SUPPORT,
            UserRole.COUNSELOR
        ]
    
    # ====================
    # AUTHENTICATION & SECURITY
    # ====================
    
    def record_successful_login(self, ip_address, user_agent):
        """Record successful login attempt"""
        self.last_login = timezone.now()
        self.last_login_ip = ip_address or '0.0.0.0'
        self.last_login_user_agent = user_agent or ''
        self.login_count += 1
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_activity = timezone.now()
        self.save(update_fields=[
            'last_login', 'last_login_ip', 'last_login_user_agent',
            'login_count', 'failed_login_attempts', 'account_locked_until',
            'last_activity'
        ])
        
        LoginHistory.record_login_attempt(
            user=self,
            ip_address=ip_address or '0.0.0.0',
            user_agent=user_agent or '',
            status=LoginStatusChoices.SUCCESS
        )
        
        cache.delete(f"profile_completion_{self.id}")
    
    def record_failed_login(self, ip_address=None, user_agent=None, reason=""):
        """Record failed login attempt and lock account if necessary"""
        self.failed_login_attempts += 1
        self.last_activity = timezone.now()
        
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save(update_fields=[
            'failed_login_attempts', 'last_activity', 'account_locked_until'
        ])
        
        if ip_address:
            LoginHistory.record_login_attempt(
                user=self,
                ip_address=ip_address or '0.0.0.0',
                user_agent=user_agent or '',
                status=LoginStatusChoices.FAILED,
                failure_reason=reason or "Invalid credentials"
            )
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                self.unlock_account()
        return False
    
    def unlock_account(self):
        """Unlock user account"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def set_password(self, raw_password):
        """Override set_password to track password change"""
        self.validate_password_strength(raw_password)
        
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
        self.save(update_fields=['password', 'password_changed_at'])
    
    def is_password_expired(self):
        """Check if password needs to be changed (90 days)"""
        if self.password_changed_at:
            return timezone.now() > self.password_changed_at + timedelta(days=90)
        return False
    
    # ====================
    # EMAIL VERIFICATION
    # ====================
    
    def send_verification_email(self, request=None):
        """Send email verification link"""
        from django.urls import reverse
        
        token = OTPToken.create_otp(
            user=self,
            token_type=TokenTypeChoices.EMAIL_VERIFICATION,
            purpose="Email verification"
        )
        
        verification_url = reverse('verify-email', kwargs={'token': token.token})
        if request:
            from django.http import HttpRequest
            if isinstance(request, HttpRequest):
                verification_url = request.build_absolute_uri(verification_url)
        
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
    
    # ====================
    # PASSWORD RESET
    # ====================
    
    def initiate_password_reset(self, request=None):
        """Initiate password reset process"""
        from django.urls import reverse
        
        self.otp_tokens.filter(
            token_type=TokenTypeChoices.PASSWORD_RESET,
            is_used=False
        ).update(is_used=True)
        
        token = OTPToken.create_otp(
            user=self,
            token_type=TokenTypeChoices.PASSWORD_RESET,
            purpose="Password reset",
            validity_minutes=30
        )
        
        reset_url = reverse('password-reset-confirm', kwargs={'token': token.token})
        if request:
            from django.http import HttpRequest
            if isinstance(request, HttpRequest):
                reset_url = request.build_absolute_uri(reset_url)
        
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
    
    # ====================
    # PERMISSIONS & ROLES
    # ====================
    
    def get_permissions(self):
        """Get user permissions for frontend AuthContext"""
        cache_key = f"user_permissions_{self.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        permissions = []
        
        if self.role == UserRole.ADMIN:
            permissions.extend(['*', 'users.manage', 'system.manage', 'finance.manage', 'reports.manage'])
        elif self.role == UserRole.ACCOUNTANT:
            permissions.extend(['finance.view', 'finance.manage', 'reports.view', 'reports.generate'])
        elif self.role == UserRole.TEACHER:
            permissions.extend(['students.view', 'attendance.manage', 'grades.manage', 'lessons.manage'])
        elif self.role == UserRole.STUDENT:
            permissions.extend(['profile.view', 'grades.view', 'attendance.view', 'courses.view'])
        elif self.role == UserRole.PARENT:
            permissions.extend(['profile.view', 'children.view', 'grades.view', 'attendance.view'])
        elif self.role == UserRole.HEAD_TEACHER:
            permissions.extend(['students.manage', 'teachers.manage', 'attendance.manage', 'grades.manage', 'reports.view'])
        elif self.role == UserRole.IT_SUPPORT:
            permissions.extend(['system.view', 'users.manage', 'tickets.manage'])
        
        cache.set(cache_key, permissions, 300)
        return permissions
    
    def get_feature_flags(self):
        """Get feature flags for frontend AuthContext"""
        cache_key = f"feature_flags_{self.id}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        flags = {
            'canViewDashboard': True,
            'canExportData': self.role in [UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.HEAD_TEACHER],
            'canManageStudents': self.role in [UserRole.ADMIN, UserRole.TEACHER, UserRole.HEAD_TEACHER],
            'canManageFinance': self.role in [UserRole.ADMIN, UserRole.ACCOUNTANT],
            'canGenerateReports': self.role in [UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.HEAD_TEACHER],
            'canManageUsers': self.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER],
            'canManageSystem': self.role in [UserRole.ADMIN, UserRole.IT_SUPPORT],
            'canManageCurriculum': self.role in [UserRole.ADMIN, UserRole.CURRICULUM_COORDINATOR, UserRole.HEAD_TEACHER],
            'canViewAnalytics': self.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.ACCOUNTANT],
            'canSendNotifications': self.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.TEACHER],
            'canUploadDocuments': self.role in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT, UserRole.PARENT],
        }
        
        cache.set(cache_key, flags, 300)
        return flags
    
    def has_permission(self, permission_codename):
        """Check if user has specific permission"""
        if self.is_superuser or self.role == UserRole.ADMIN:
            return True
        
        permissions = self.get_permissions()
        return permission_codename in permissions or '*' in permissions
    
    def can_access_feature(self, feature_name):
        """Check if user can access specific feature"""
        feature_flags = self.get_feature_flags()
        return feature_flags.get(feature_name, False)
    
    # ====================
    # SAVE METHOD
    # ====================
    
    def save(self, *args, **kwargs):
        """Override save method to handle automatic field population"""
        is_new = self._state.adding
        
        # Auto-generate identifiers BEFORE validation for new users
        if is_new:
            if self.role == UserRole.STUDENT and not self.admission_number:
                self.admission_number = self.generate_admission_number()
            
            staff_roles = [
                UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR,
                UserRole.ACCOUNTANT, UserRole.IT_SUPPORT, UserRole.COUNSELOR,
                UserRole.LIBRARIAN, UserRole.OFFICE_STAFF, UserRole.ADMIN
            ]
            if self.role in staff_roles and not self.staff_id:
                self.staff_id = self.generate_staff_id()
        
        # For existing users, ensure required identifiers exist
        if not is_new:
            if self.role == UserRole.STUDENT and not self.admission_number:
                self.admission_number = self.generate_admission_number()
            
            staff_roles = [
                UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR,
                UserRole.ACCOUNTANT, UserRole.IT_SUPPORT, UserRole.COUNSELOR,
                UserRole.LIBRARIAN, UserRole.OFFICE_STAFF, UserRole.ADMIN
            ]
            if self.role in staff_roles and not self.staff_id:
                self.staff_id = self.generate_staff_id()
        
        # Set is_staff based on role
        if not self.is_staff:
            self.is_staff = self.role in [
                UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR,
                UserRole.TEACHER, UserRole.ACCOUNTANT, UserRole.IT_SUPPORT, UserRole.COUNSELOR,
                UserRole.LIBRARIAN, UserRole.OFFICE_STAFF
            ]
        
        # Set academic year if not set (for students)
        if self.role == UserRole.STUDENT and not self.academic_year:
            self.academic_year = self.get_current_academic_year()
        
        # Track profile updates for existing users
        if not is_new:
            try:
                original = User.objects.get(pk=self.pk)
                profile_fields = ['first_name', 'last_name', 'middle_name', 'phone_number', 'address']
                for field in profile_fields:
                    if getattr(original, field) != getattr(self, field):
                        self.last_profile_update = timezone.now()
                        break
            except User.DoesNotExist:
                pass
        
        # Run validation
        try:
            self.full_clean()
        except ValidationError as e:
            logger.error(f"Validation error saving User: {e}")
            raise
        
        super().save(*args, **kwargs)
        
        # Clear relevant caches
        cache.delete(f"profile_completion_{self.id}")
        cache.delete(f"user_permissions_{self.id}")
        cache.delete(f"feature_flags_{self.id}")
    
    # ====================
    # UTILITY METHODS
    # ====================
    
    def generate_admission_number(self):
        """Generate unique admission number"""
        year = timezone.now().year
        last_student = User.objects.filter(
            role=UserRole.STUDENT,
            admission_number__isnull=False
        ).order_by('-admission_number').first()
        
        new_number = 1
        if last_student and last_student.admission_number:
            try:
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
            UserRole.TEACHER: 'TCH',
            UserRole.HEAD_TEACHER: 'HT',
            UserRole.CURRICULUM_COORDINATOR: 'CC',
            UserRole.ACCOUNTANT: 'ACC',
            UserRole.ADMIN: 'ADM',
            UserRole.IT_SUPPORT: 'IT',
            UserRole.COUNSELOR: 'COU',
            UserRole.LIBRARIAN: 'LIB',
            UserRole.OFFICE_STAFF: 'OFF'
        }.get(self.role, 'EMP')
        
        last_staff = User.objects.filter(
            role__in=[
                UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR,
                UserRole.ACCOUNTANT, UserRole.ADMIN, UserRole.IT_SUPPORT, UserRole.COUNSELOR,
                UserRole.LIBRARIAN, UserRole.OFFICE_STAFF
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
        
        if current_month >= 9:  # September to December
            return f"{current_year}-{current_year + 1}"
        else:  # January to August
            return f"{current_year - 1}-{current_year}"
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
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
    
    def get_children(self):
        """Get children for parent users"""
        if self.role == UserRole.PARENT:
            return User.objects.filter(
                role=UserRole.STUDENT,
                parent_email=self.email
            )
        return User.objects.none()
    
    def get_parents(self):
        """Get parents for student users"""
        if self.role == UserRole.STUDENT and self.parent_email:
            return User.objects.filter(
                role=UserRole.PARENT,
                email=self.parent_email
            )
        return User.objects.none()
    
    def get_dashboard_data(self):
        """Get dashboard data for frontend"""
        dashboard_data = {
            'user': {
                'id': str(self.id),
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role,
                'role_display': self.get_role_display(),
                'profile_picture': self.profile_picture.url if self.profile_picture else None,
                'profile_completed': self.profile_completed,
                'is_verified': self.is_verified,
                'is_approved': self.is_approved,
            },
            'dashboard_url': self.get_dashboard_url(),
            'permissions': self.get_permissions(),
            'feature_flags': self.get_feature_flags(),
        }
        
        # Add role-specific data
        if self.role == UserRole.STUDENT:
            dashboard_data['student_info'] = {
                'admission_number': self.admission_number,
                'grade_level': self.grade_level,
                'current_class': self.current_class,
                'house': self.house,
                'academic_year': self.academic_year,
            }
        elif self.role in [UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR]:
            dashboard_data['teacher_info'] = {
                'staff_id': self.staff_id,
                'department': self.department,
                'designation': self.designation,
                'years_of_experience': self.years_of_experience,
            }
        
        return dashboard_data
    
    # ====================
    # PROPERTIES
    # ====================
    
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
        return self.role in [UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.IT_SUPPORT]
    
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
            UserRole.TEACHER,
            UserRole.HEAD_TEACHER,
            UserRole.CURRICULUM_COORDINATOR,
            UserRole.ADMIN
        ]
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == UserRole.STUDENT
    
    @property
    def is_parent(self):
        """Check if user is a parent"""
        return self.role == UserRole.PARENT
    
    @property
    def is_staff_member(self):
        """Check if user is any type of staff"""
        return self.role in [
            UserRole.ADMIN,
            UserRole.HEAD_TEACHER,
            UserRole.CURRICULUM_COORDINATOR,
            UserRole.TEACHER,
            UserRole.OFFICE_STAFF,
            UserRole.LIBRARIAN,
            UserRole.ACCOUNTANT,
            UserRole.IT_SUPPORT,
            UserRole.COUNSELOR
        ]
    
    @property
    def is_finance_user(self):
        """Check if user has finance access"""
        return self.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]
    
    @property
    def is_management(self):
        """Check if user is in management role"""
        return self.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR]
    
    @property
    def has_document_upload_access(self):
        """Check if user can upload documents"""
        return self.role in [
            UserRole.ADMIN,
            UserRole.TEACHER,
            UserRole.HEAD_TEACHER,
            UserRole.STUDENT,
            UserRole.PARENT
        ]
    
    def has_2fa_enabled(self):
        """Check if user has 2FA enabled"""
        try:
            return self.two_factor_auth.is_enabled
        except TwoFactorAuth.DoesNotExist:
            return False
    
    @property
    def cached_permissions(self):
        """Get cached permissions"""
        return self.get_permissions()
    
    @property
    def cached_feature_flags(self):
        """Get cached feature flags"""
        return self.get_feature_flags()


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
# AUTHENTICATION MODELS
# ============================================================================

class TwoFactorAuth(BaseModel):
    """Enhanced 2FA model with session management for dashboard redirection"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='two_factor_auth'
    )
    secret_key = models.CharField(max_length=32, blank=True)
    is_enabled = models.BooleanField(default=False)
    primary_method = models.CharField(
        max_length=20, 
        choices=TwoFAMethodChoices.choices, 
        default=TwoFAMethodChoices.EMAIL
    )
    backup_codes = models.JSONField(default=list, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    recovery_email = models.EmailField(blank=True)
    recovery_phone = models.CharField(max_length=17, blank=True)
    last_backup_code_generated = models.DateTimeField(null=True, blank=True)
    
    # Session management for OTP verification flow
    pending_session_token = models.CharField(max_length=300, blank=True)
    pending_session_expiry = models.DateTimeField(null=True, blank=True)
    pending_redirect_url = models.CharField(max_length=500, blank=True)

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


class LoginSession(BaseModel):
    """Model to track login sessions with OTP verification"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_sessions'
    )
    session_token = models.CharField(
        max_length=64, 
        unique=True, 
        verbose_name=_("Session Token")
    )
    status = models.CharField(
        max_length=20, 
        choices=SessionStatusChoices.choices, 
        default=SessionStatusChoices.PENDING_OTP,
        verbose_name=_("Status")
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name=_("IP Address")
    )
    user_agent = models.TextField(
        blank=True, 
        verbose_name=_("User Agent")
    )
    device_info = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Device Information")
    )
    otp_sent_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("OTP Sent At")
    )
    otp_verified_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("OTP Verified At")
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At")
    )
    last_activity = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Last Activity")
    )
    jwt_refresh_token = models.TextField(
        blank=True, 
        verbose_name=_("JWT Refresh Token")
    )
    jwt_access_token = models.TextField(
        blank=True, 
        verbose_name=_("JWT Access Token")
    )
    
    class Meta:
        verbose_name = _("Login Session")
        verbose_name_plural = _("Login Sessions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.status} - {self.created_at}"
    
    @property
    def is_active(self):
        """Check if session is active"""
        return (
            self.status == SessionStatusChoices.VERIFIED and 
            timezone.now() < self.expires_at
        )
    
    @property
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() >= self.expires_at
    
    @property
    def otp_is_valid(self):
        """Check if OTP is still valid"""
        if not self.otp_sent_at:
            return False
        return timezone.now() < self.otp_sent_at + timedelta(minutes=5)
    
    def generate_session_token(self):
        """Generate a unique session token"""
        self.session_token = secrets.token_urlsafe(48)
        return self.session_token
    
    def send_otp(self, method='email'):
        """Send OTP for this login session"""
        otp_token = OTPToken.create_otp(
            user=self.user,
            token_type=TokenTypeChoices.LOGIN_VERIFICATION,
            purpose="Login verification",
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            validity_minutes=5
        )
        
        self.otp_sent_at = timezone.now()
        self.save()
        
        if method == 'email':
            self._send_otp_email(otp_token)
        elif method == 'sms':
            self._send_otp_sms(otp_token)
        
        return otp_token
    
    def _send_otp_email(self, otp_token):
        """Send OTP via email"""
        subject = _("Login Verification Code - Delvok Academy")
        html_message = render_to_string('accounts/login_otp_email.html', {
            'user': self.user,
            'otp': otp_token.token,
            'expiry_minutes': 5,
            'device_info': self.device_info,
            'ip_address': self.ip_address
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                html_message=html_message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
    
    def _send_otp_sms(self, otp_token):
        """Send OTP via SMS"""
        # Implement SMS sending logic here
        pass
    
    def verify_otp(self, otp_code):
        """Verify OTP code"""
        if not self.otp_is_valid:
            self.status = SessionStatusChoices.EXPIRED
            self.save()
            return False, _("OTP has expired. Please request a new one.")
        
        try:
            otp_token = OTPToken.objects.get(
                user=self.user,
                token=otp_code,
                token_type=TokenTypeChoices.LOGIN_VERIFICATION,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            otp_token.mark_used()
            
            self.status = SessionStatusChoices.VERIFIED
            self.otp_verified_at = timezone.now()
            self.expires_at = timezone.now() + timedelta(hours=12)
            self.save()
            
            return True, _("OTP verified successfully.")
            
        except OTPToken.DoesNotExist:
            self.record_failed_attempt()
            return False, _("Invalid OTP code.")
    
    def record_failed_attempt(self):
        """Record failed OTP attempt"""
        pass
    
    def revoke(self):
        """Revoke this login session"""
        self.status = SessionStatusChoices.REVOKED
        self.save()
    
    @classmethod
    def create_pending_session(cls, user, ip_address, user_agent, device_info=None):
        """Create a new pending login session"""
        cls.objects.filter(
            user=user,
            status=SessionStatusChoices.PENDING_OTP,
            expires_at__lt=timezone.now()
        ).update(status=SessionStatusChoices.EXPIRED)
        
        session = cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info or {},
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        session.generate_session_token()
        session.save()
        
        return session


class OTPToken(BaseModel):
    """Enhanced OTP Token model for email/SMS verification and password reset"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='otp_tokens'
    )
    token = models.CharField(max_length=6, verbose_name=_("OTP Token"))
    token_type = models.CharField(
        max_length=20, 
        choices=TokenTypeChoices.choices, 
        verbose_name=_("Token Type")
    )
    purpose = models.CharField(max_length=100, blank=True, verbose_name=_("Purpose"))
    is_used = models.BooleanField(default=False, verbose_name=_("Is Used"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Used At"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Request IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    login_session = models.ForeignKey(
        'LoginSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='otp_tokens'
    )
    
    class Meta:
        verbose_name = _("OTP Token")
        verbose_name_plural = _("OTP Tokens")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used', 'expires_at']),
            models.Index(fields=['user', 'token_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['login_session']),
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
    def create_otp(cls, user, token_type, purpose="", ip_address=None, user_agent="", validity_minutes=10, login_session=None):
        """Create a new OTP token"""
        cls.objects.filter(
            user=user, 
            expires_at__lt=timezone.now()
        ).delete()
        
        token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        otp = cls.objects.create(
            user=user,
            token=token,
            token_type=token_type,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=validity_minutes),
            ip_address=ip_address,
            user_agent=user_agent,
            login_session=login_session
        )
        
        return otp
    
    @classmethod
    def verify_otp(cls, user, token, token_type, login_session=None):
        """Verify OTP token"""
        try:
            query_params = {
                'user': user,
                'token': token,
                'token_type': token_type,
                'is_used': False,
                'expires_at__gt': timezone.now()
            }
            
            if login_session:
                query_params['login_session'] = login_session
            
            otp = cls.objects.get(**query_params)
            otp.mark_used()
            return True, "OTP verified successfully"
        except cls.DoesNotExist:
            return False, "Invalid or expired OTP"


class LoginHistory(BaseModel):
    """Enhanced Login history tracking for security monitoring"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_history'
    )
    ip_address = models.GenericIPAddressField(null=True,blank=True,verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Location"))
    device_type = models.CharField(max_length=50, blank=True, verbose_name=_("Device Type"))
    browser = models.CharField(max_length=50, blank=True, verbose_name=_("Browser"))
    platform = models.CharField(max_length=50, blank=True, verbose_name=_("Platform"))
    login_status = models.CharField(
        max_length=20, 
        choices=LoginStatusChoices.choices, 
        verbose_name=_("Login Status")
    )
    failure_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Failure Reason"))
    session_key = models.CharField(max_length=100, blank=True, verbose_name=_("Session Key"))
    two_fa_method = models.CharField(
        max_length=20, 
        blank=True, 
        choices=TwoFAMethodChoices.choices, 
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
        if ip_address is None:
            ip_address = '0.0.0.0'

        device_info = cls.parse_user_agent(user_agent)
        location_info = cls.get_location_from_ip(ip_address)
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
        """Get location from IP address using external service"""
        location_info = {
            'location': '',
            'country': '',
            'city': '',
            'region': '',
            'timezone': ''
        }
        
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            location_info['location'] = 'Localhost'
            location_info['country'] = 'Local'
            return location_info
        
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
            if response.status_code == 200:
                data = response.json()
                
                country = data.get('country_name', '')
                city = data.get('city', '')
                region = data.get('region', '')
                
                location_info['country'] = country or 'Unknown'
                location_info['city'] = city or 'Unknown'
                location_info['region'] = region or 'Unknown'
                location_info['timezone'] = data.get('timezone', '')
                
                parts = []
                if city:
                    parts.append(city)
                if region:
                    parts.append(region)
                if country:
                    parts.append(country)
                
                location_info['location'] = ', '.join(parts) if parts else 'Unknown'
                
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {e}")
            location_info['location'] = 'Unknown'
            location_info['country'] = 'Unknown'
            location_info['city'] = 'Unknown'
        
        return location_info
    
    @staticmethod
    def detect_suspicious_activity(user, ip_address, location_info):
        """Detect potentially suspicious login activity"""
        recent_logins = LoginHistory.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).exclude(ip_address=ip_address)
        
        if recent_logins.exists():
            unique_ips = recent_logins.values('ip_address').distinct().count()
            if unique_ips >= 3:
                return True
        
        usual_country = recent_logins.exclude(country='').values('country').annotate(
            count=models.Count('country')
        ).order_by('-count').first()
        
        if (usual_country and 
            location_info.get('country') and 
            location_info.get('country') != 'Unknown' and
            location_info.get('country') != usual_country['country']):
            return True
            
        return False


class EmailVerification(BaseModel):
    """Model for email verification tokens"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='email_verifications'
    )
    token = models.CharField(
        max_length=64, 
        unique=True, 
        verbose_name=_("Verification Token")
    )
    is_used = models.BooleanField(default=False, verbose_name=_("Is Used"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    used_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Used At")
    )
    
    class Meta:
        verbose_name = _("Email Verification")
        verbose_name_plural = _("Email Verifications")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Email verification for {self.user.email}"
    
    @property
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    @classmethod
    def create_verification_token(cls, user):
        """Create a new email verification token"""
        cls.objects.filter(user=user).delete()
        
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    @classmethod
    def verify_token(cls, token):
        """Verify email verification token"""
        try:
            verification = cls.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            verification.mark_used()
            
            user = verification.user
            user.email_verified = True
            user.is_verified = user.is_verified or True
            user.save()
            
            return True, user, _("Email verified successfully")
            
        except cls.DoesNotExist:
            return False, None, _("Invalid or expired verification token")


class OTPSession(models.Model):
    """Store OTP sessions in database instead of cache"""
    session_token = models.UUIDField(unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_valid(self):
        return not self.verified and timezone.now() < self.expires_at
    
    def mark_verified(self):
        self.verified = True
        self.save()