# accounts/serializers.py - REFACTORED AND ORGANIZED VERSION

from datetime import date
import logging
import re
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    LoginHistory, LoginSession, OTPToken, TwoFactorAuth, User, UserProfile,
    # Import specific choices
    TwoFAMethodChoices, TokenTypeChoices, LoginStatusChoices, SessionStatusChoices,
    UserRole, GenderChoices, CurriculumChoices, HouseChoices, BloodGroupChoices
)

logger = logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_email_domain(email):
    """Validate email domain"""
    if email:
        # Add any domain-specific validation here
        # For example, check if email is from allowed domains
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'delvok.ac.ke']
        domain = email.split('@')[-1].lower()
        
        # Check if it's a test domain
        if domain in ['test.com', 'example.com']:
            return False, _("Test/example email domains are not allowed")
            
        return True, ""
    return False, _("Invalid email address")


# ============================================================================
# BASE SERIALIZERS (Define these first to avoid circular imports)
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'user_role',
            'bio', 'website', 'social_links', 'notifications_enabled',
            'email_notifications', 'sms_notifications', 'push_notifications',
            'language', 'timezone', 'hobbies', 'achievements', 'skills',
            'education_background', 'profile_visibility', 'contact_preference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_social_links(self, value):
        """Validate social links format"""
        if value and isinstance(value, dict):
            for platform, url in value.items():
                if url and not isinstance(url, str):
                    raise serializers.ValidationError(
                        _("Social links must be URLs in string format.")
                    )
        return value
    
    def validate_achievements(self, value):
        """Validate achievements format"""
        if value and isinstance(value, list):
            for achievement in value:
                if not isinstance(achievement, dict):
                    raise serializers.ValidationError(
                        _("Achievements must be a list of objects.")
                    )
                if 'title' not in achievement:
                    raise serializers.ValidationError(
                        _("Each achievement must have a title.")
                    )
        return value
    
    def validate_skills(self, value):
        """Validate skills format"""
        if value and isinstance(value, list):
            for skill in value:
                if not isinstance(skill, dict):
                    raise serializers.ValidationError(
                        _("Skills must be a list of objects.")
                    )
                if 'name' not in skill:
                    raise serializers.ValidationError(
                        _("Each skill must have a name.")
                    )
        return value


class TwoFactorAuthSerializer(serializers.ModelSerializer):
    """Serializer for TwoFactorAuth model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    qr_code = serializers.SerializerMethodField()
    provisioning_uri = serializers.SerializerMethodField()
    unused_backup_codes = serializers.SerializerMethodField()
    
    class Meta:
        model = TwoFactorAuth
        fields = [
            'id', 'user', 'user_email', 'user_full_name',
            'is_enabled', 'primary_method', 'qr_code',
            'provisioning_uri', 'unused_backup_codes',
            'recovery_email', 'recovery_phone',
            'last_used', 'last_backup_code_generated',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'qr_code', 'provisioning_uri',
            'unused_backup_codes', 'last_used',
            'last_backup_code_generated', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'secret_key': {'write_only': True},
            'backup_codes': {'write_only': True},
            'pending_session_token': {'write_only': True},
            'pending_session_expiry': {'write_only': True},
            'pending_redirect_url': {'write_only': True},
        }
    
    def get_qr_code(self, obj):
        """Get QR code as base64"""
        if obj.is_enabled and obj.primary_method == TwoFAMethodChoices.AUTHENTICATOR:
            return obj.generate_qr_code()
        return ""
    
    def get_provisioning_uri(self, obj):
        """Get provisioning URI for authenticator app"""
        if obj.is_enabled and obj.primary_method == TwoFAMethodChoices.AUTHENTICATOR:
            return obj.generate_provisioning_uri()
        return ""
    
    def get_unused_backup_codes(self, obj):
        """Get unused backup codes"""
        if obj.is_enabled:
            return obj.get_unused_backup_codes()
        return []
    
    def validate_primary_method(self, value):
        """Validate 2FA method"""
        user = self.instance.user if self.instance else None
        if not user and self.context.get('request'):
            user = self.context['request'].user
        
        if user:
            if value == TwoFAMethodChoices.EMAIL and not user.email:
                raise serializers.ValidationError(
                    _("Email is required for email-based 2FA.")
                )
            
            if value == TwoFAMethodChoices.SMS and not user.phone_number:
                raise serializers.ValidationError(
                    _("Phone number is required for SMS-based 2FA.")
                )
        
        return value

class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for LoginHistory model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'user', 'user_email', 'user_full_name',
            'ip_address', 'location', 'country', 'city',
            'user_agent', 'device_type', 'browser', 'platform',
            'login_status', 'status_display', 'failure_reason',
            'is_suspicious', 'two_fa_method', 'created_at'
        ]
        read_only_fields = fields
    
    def get_status_display(self, obj):
        return obj.get_login_status_display()


class OTPTokenSerializer(serializers.ModelSerializer):
    """Serializer for OTPToken model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_valid = serializers.SerializerMethodField()
    expires_in_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = OTPToken
        fields = [
            'id', 'user', 'user_email', 'token', 'token_type',
            'purpose', 'is_used', 'is_valid', 'expires_in_minutes',
            'created_at', 'expires_at', 'used_at', 'ip_address',
            'user_agent', 'login_session'
        ]
        read_only_fields = fields
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_expires_in_minutes(self, obj):
        if obj.expires_at:
            delta = obj.expires_at - timezone.now()
            return max(0, int(delta.total_seconds() // 60))
        return 0


class LoginSessionSerializer(serializers.ModelSerializer):
    """Serializer for LoginSession model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_active = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    otp_is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = LoginSession
        fields = [
            'id', 'user', 'user_email', 'user_full_name',
            'session_token', 'status', 'ip_address',
            'user_agent', 'device_info', 'is_active',
            'is_expired', 'otp_is_valid', 'otp_sent_at',
            'otp_verified_at', 'expires_at', 'last_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_is_active(self, obj):
        return obj.is_active
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_otp_is_valid(self, obj):
        return obj.otp_is_valid

# ============================================================================
# CORE USER SERIALIZERS
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Base User serializer with all fields"""
    
    full_name = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    profile_completion_percentage = serializers.SerializerMethodField()
    dashboard_url = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    feature_flags = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        exclude = [
            'password', 'last_login', 'is_superuser', 
            'groups', 'user_permissions', 'is_admin'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login',
            'email_verified', 'phone_verified', 'is_verified',
            'login_count', 'failed_login_attempts', 'password_changed_at',
            'last_profile_update', 'profile_completion_date',
            'account_locked_until', 'last_activity', 'admission_number',
            'staff_id', 'is_staff', 'is_suspended'
        ]
        extra_kwargs = {
            'email': {'required': True, 'validators': [EmailValidator()]},
            'first_name': {'required': True, 'min_length': 2},
            'last_name': {'required': True, 'min_length': 2},
            'password': {'write_only': True, 'required': False},
            'profile_picture': {'required': False},
            'date_of_birth': {'required': False},
            'phone_number': {'required': False},
            'role': {'required': True},
        }

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_initials(self, obj):
        return obj.get_initials()

    def get_age(self, obj):
        return obj.age

    def get_profile_completion_percentage(self, obj):
        return obj.profile_completion_percentage

    def get_dashboard_url(self, obj):
        return obj.get_dashboard_url()

    def get_permissions(self, obj):
        return obj.get_permissions()

    def get_feature_flags(self, obj):
        return obj.get_feature_flags()

    def validate_email(self, value):
        """Validate email with domain checking"""
        # Clean email
        value = value.strip().lower()
        
        # Check domain
        is_valid, message = validate_email_domain(value)
        if not is_valid:
            raise serializers.ValidationError(message)
        
        # Check for existing user (excluding current user if updating)
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            existing = User.objects.filter(email=value).exclude(pk=user.pk).first()
        else:
            existing = User.objects.filter(email=value).first()
            
        if existing:
            raise serializers.ValidationError(_("A user with this email already exists."))
        
        return value

    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            # Check if date is in the future
            if value > date.today():
                raise serializers.ValidationError(_("Date of birth cannot be in the future."))
            
            # Calculate age
            age = (date.today() - value).days // 365
            
            # Validate age based on role
            role = self.initial_data.get('role', getattr(self.instance, 'role', None))
            
            if role == UserRole.STUDENT:
                if age < 3:
                    raise serializers.ValidationError(_("Student must be at least 3 years old."))
                if age > 25:
                    raise serializers.ValidationError(_("Student age seems unrealistic."))
            elif role in [UserRole.TEACHER, UserRole.HEAD_TEACHER, UserRole.CURRICULUM_COORDINATOR]:
                if age < 21:
                    raise serializers.ValidationError(_("Staff must be at least 21 years old."))
        
        return value

    def validate_password(self, value):
        """Validate password strength"""
        if value:
            try:
                # Use Django's built-in password validators
                validate_password(value)
                
                # Additional custom validation
                if len(value) < 8:
                    raise serializers.ValidationError(_("Password must be at least 8 characters long"))
                if not any(char.isdigit() for char in value):
                    raise serializers.ValidationError(_("Password must contain at least one number"))
                if not any(char.isupper() for char in value):
                    raise serializers.ValidationError(_("Password must contain at least one uppercase letter"))
                if not any(char.islower() for char in value):
                    raise serializers.ValidationError(_("Password must contain at least one lowercase letter"))
                if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in value):
                    raise serializers.ValidationError(_("Password must contain at least one special character"))
                    
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
        
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        errors = {}
        
        # Check role-specific requirements
        role = attrs.get('role', getattr(self.instance, 'role', None))
        
        if role == UserRole.STUDENT:
            # Students should not have staff_id
            if attrs.get('staff_id'):
                errors['staff_id'] = _("Students cannot have staff ID.")
            
            # Validate parent information
            if not attrs.get('parent_email') and not getattr(self.instance, 'parent_email', None):
                errors['parent_email'] = _("Student must have parent/guardian email.")
        
        elif role in [UserRole.TEACHER, UserRole.HEAD_TEACHER, 
                     UserRole.CURRICULUM_COORDINATOR, UserRole.ADMIN,
                     UserRole.ACCOUNTANT, UserRole.IT_SUPPORT,
                     UserRole.COUNSELOR, UserRole.LIBRARIAN,
                     UserRole.OFFICE_STAFF]:
            # Staff should not have admission_number
            if attrs.get('admission_number'):
                errors['admission_number'] = _("Staff cannot have admission number.")
        
        # Validate phone number format
        phone_number = attrs.get('phone_number')
        if phone_number:
            # Basic phone validation
            phone_regex = r'^\+?1?\d{9,15}$'
            if not re.match(phone_regex, phone_number):
                errors['phone_number'] = _("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

    def create(self, validated_data):
        """Create a new user with proper role handling"""
        # Extract password if provided
        password = validated_data.pop('password', None)
        
        # Create user
        user = User(**validated_data)
        
        # Set password if provided
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        # Save user (this will trigger auto-generation of admission_number/staff_id)
        user.save()
        
        # Create associated profile
        UserProfile.objects.create(user=user)
        
        # Create 2FA settings if required
        if user.requires_2fa_setup:
            TwoFactorAuth.objects.create(user=user)
        
        return user

    def update(self, instance, validated_data):
        """Update user instance"""
        # Handle password update separately
        password = validated_data.pop('password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password if provided
        if password:
            instance.set_password(password)
        
        # Save the instance
        instance.save()
        
        # Clear caches
        from django.core.cache import cache
        cache.delete(f"profile_completion_{instance.id}")
        cache.delete(f"user_permissions_{instance.id}")
        cache.delete(f"feature_flags_{instance.id}")
        
        return instance

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation (registration)"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'middle_name',
            'password', 'confirm_password', 'role', 'phone_number',
            'date_of_birth', 'gender', 'nationality', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True, 'min_length': 2},
            'last_name': {'required': True, 'min_length': 2},
            'role': {'required': True},
        }

    def validate(self, attrs):
        """Validate registration data"""
        errors = {}
        
        # Check password confirmation
        if attrs.get('password') != attrs.get('confirm_password'):
            errors['confirm_password'] = _("Passwords do not match.")
        
        # Validate email domain
        email = attrs.get('email')
        if email:
            is_valid, message = validate_email_domain(email)
            if not is_valid:
                errors['email'] = message
        
        # Check for existing user with this email
        if email and User.objects.filter(email=email).exists():
            errors['email'] = _("A user with this email already exists.")
        
        # Role-specific validation
        role = attrs.get('role')
        if role == User.UserRole.STUDENT:
            # Students must provide date of birth
            if not attrs.get('date_of_birth'):
                errors['date_of_birth'] = _("Date of birth is required for students.")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        # Remove confirm_password from validated data
        attrs.pop('confirm_password', None)
        
        return attrs

    def create(self, validated_data):
        """Create new user with automatic identifier generation"""
        try:
            # Create user instance
            user = User.objects.create_user(**validated_data)
            
            # Create associated profile
            UserProfile.objects.create(user=user)
            
            # Log the registration
            logger.info(f"New user registered: {user.email} ({user.role})")
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise serializers.ValidationError(_("Failed to create user. Please try again."))


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    profile_completion_percentage = serializers.SerializerMethodField()
    missing_profile_fields = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'middle_name',
            'phone_number', 'alternative_phone', 'address',
            'city', 'country', 'date_of_birth', 'gender',
            'nationality', 'id_number', 'profile_picture',
            'blood_group', 'medical_info', 'allergies',
            'chronic_conditions', 'current_medications',
            'doctor_name', 'doctor_phone',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'emergency_contact_address',
            'primary_curriculum', 'grade_level', 'current_class',
            'house', 'department', 'qualification',
            'specialization', 'designation', 'years_of_experience',
            'parent_name', 'parent_email', 'parent_phone',
            'parent_occupation', 'previous_school',
            'transfer_certificate', 'birth_certificate',
            'recommendation_letter', 'profile_completed',
            'profile_completion_percentage', 'missing_profile_fields',
            'preferred_dashboard_view', 'dashboard_widgets',
            'theme_preference', 'last_profile_update'
        ]
        read_only_fields = [
            'id', 'profile_completed', 'profile_completion_percentage',
            'missing_profile_fields', 'last_profile_update'
        ]
        extra_kwargs = {
            'profile_picture': {'required': False},
            'transfer_certificate': {'required': False},
            'birth_certificate': {'required': False},
            'recommendation_letter': {'required': False},
        }

    def get_profile_completion_percentage(self, obj):
        return obj.profile_completion_percentage

    def get_missing_profile_fields(self, obj):
        return obj.get_missing_profile_fields()

    def validate(self, attrs):
        """Validate profile update"""
        user = self.context['request'].user
        
        # Check if user can update certain fields
        if 'role' in attrs and attrs['role'] != user.role:
            raise serializers.ValidationError({
                'role': _("You cannot change your role.")
            })
        
        # Validate date of birth
        date_of_birth = attrs.get('date_of_birth', user.date_of_birth)
        if date_of_birth:
            if date_of_birth > date.today():
                raise serializers.ValidationError({
                    'date_of_birth': _("Date of birth cannot be in the future.")
                })
        
        return attrs

    def update(self, instance, validated_data):
        """Update user profile"""
        # Track if profile was completed
        was_profile_completed = instance.profile_completed
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update last_profile_update timestamp
        instance.last_profile_update = timezone.now()
        
        # Save and check profile completion
        instance.save()
        
        # Check if profile is now completed
        if not was_profile_completed and instance.profile_completed:
            logger.info(f"User {instance.email} completed their profile")
        
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user listing (minimal fields for performance)"""
    
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'role_display',
            'profile_picture', 'is_active', 'is_verified',
            'is_approved', 'profile_completed', 'is_suspended',
            'last_login', 'created_at', 'is_online'
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role_display(self, obj):
        return obj.get_role_display()

    def get_is_online(self, obj):
        return obj.is_online


class UserDetailSerializer(UserSerializer):
    """Detailed user serializer with related data"""
    
    user_profile = serializers.SerializerMethodField()
    two_factor_auth = serializers.SerializerMethodField()
    login_history = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    parents = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            # All fields from User model except sensitive ones
            'id', 'email', 'first_name', 'last_name', 'middle_name',
            'role', 'gender', 'nationality', 'date_of_birth',
            'phone_number', 'alternative_phone', 'address', 'city', 'country',
            'id_number', 'profile_picture', 'blood_group', 'medical_info',
            'allergies', 'chronic_conditions', 'current_medications',
            'doctor_name', 'doctor_phone', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'emergency_contact_address', 'admission_number', 'staff_id',
            'primary_curriculum', 'grade_level', 'current_class', 'house',
            'academic_year', 'department', 'qualification', 'specialization',
            'designation', 'years_of_experience', 'parent_name',
            'parent_email', 'parent_phone', 'parent_occupation',
            'previous_school', 'transfer_certificate', 'birth_certificate',
            'recommendation_letter', 'is_staff', 'is_active',
            'email_verified', 'phone_verified', 'is_verified',
            'is_approved', 'is_suspended', 'is_on_leave',
            'profile_completed', 'preferred_dashboard_view',
            'dashboard_widgets', 'theme_preference',
            'date_joined', 'enrollment_date', 'employment_date',
            'last_login', 'last_login_ip', 'login_count',
            'failed_login_attempts', 'password_changed_at',
            'last_profile_update', 'profile_completion_date',
            'account_locked_until', 'last_activity',
            'created_at', 'updated_at',
            # Computed fields from UserSerializer
            'full_name', 'initials', 'age', 'profile_completion_percentage',
            'dashboard_url', 'permissions', 'feature_flags',
            # Additional fields for UserDetailSerializer
            'user_profile', 'two_factor_auth', 'login_history',
            'children', 'parents'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login',
            'email_verified', 'phone_verified', 'is_verified',
            'login_count', 'failed_login_attempts', 'password_changed_at',
            'last_profile_update', 'profile_completion_date',
            'account_locked_until', 'last_activity', 'admission_number',
            'staff_id', 'is_staff', 'is_suspended'
        ]
        extra_kwargs = {
            'email': {'required': True, 'validators': [EmailValidator()]},
            'first_name': {'required': True, 'min_length': 2},
            'last_name': {'required': True, 'min_length': 2},
            'profile_picture': {'required': False},
            'date_of_birth': {'required': False},
            'phone_number': {'required': False},
            'role': {'required': True},
        }

    def get_user_profile(self, obj):
        try:
            profile = obj.user_profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None

    def get_two_factor_auth(self, obj):
        try:
            two_fa = obj.two_factor_auth
            return TwoFactorAuthSerializer(two_fa).data
        except TwoFactorAuth.DoesNotExist:
            return None

    def get_login_history(self, obj):
        login_history = obj.login_history.all()[:10]  # Last 10 logins
        return LoginHistorySerializer(login_history, many=True).data

    def get_children(self, obj):
        if obj.role == User.UserRole.PARENT:
            children = obj.get_children()
            return UserListSerializer(children, many=True).data
        return []

    def get_parents(self, obj):
        if obj.role == User.UserRole.STUDENT:
            parents = obj.get_parents()
            return UserListSerializer(parents, many=True).data
        return []



class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for dropdowns and basic info"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'profile_picture']
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()


# ============================================================================
# AUTHENTICATION SERIALIZERS
# ============================================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with enhanced user data"""
    
    def validate(self, attrs):
        """Validate credentials and return enhanced token data"""
        data = super().validate(attrs)
        
        user = self.user
        
        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError(_("Account is inactive."))
        
        # Check if account is suspended
        if user.is_suspended:
            raise serializers.ValidationError(_("Account is suspended."))
        
        # Check if account is locked
        if user.is_account_locked():
            raise serializers.ValidationError(_("Account is temporarily locked. Please try again later."))
        
        # Check if account needs approval
        if not user.is_approved and user.requires_approval():
            raise serializers.ValidationError(_("Account pending approval. Please contact administrator."))
        
        # Record successful login
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        user_agent = request.META.get('HTTP_USER_AGENT') if request else None
        
        user.record_successful_login(ip_address, user_agent)
        
        # Add user data to token
        refresh = self.get_token(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Add user information
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.role,
            'role_display': user.get_role_display(),
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'dashboard_url': user.get_dashboard_url(),
            'permissions': user.get_permissions(),
            'feature_flags': user.get_feature_flags(),
            'profile_completed': user.profile_completed,
            'requires_2fa': user.requires_2fa_setup,
            'has_2fa_enabled': user.has_2fa_enabled(),
            'profile_completion_percentage': user.profile_completion_percentage,
        }
        
        # Check if 2FA is required
        if user.requires_2fa_setup and not user.has_2fa_enabled():
            data['requires_2fa_setup'] = True
        
        return data
    
    @classmethod
    def get_token(cls, user):
        """Create token with custom claims"""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        token['profile_completed'] = user.profile_completed
        token['is_verified'] = user.is_verified
        token['is_approved'] = user.is_approved
        
        return token


class LoginSerializer(serializers.Serializer):
    """Serializer for login with username/password"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    remember_me = serializers.BooleanField(default=False, required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Invalid email or password."))
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(_("Account is inactive."))
        
        # Check if user is suspended
        if user.is_suspended:
            raise serializers.ValidationError(_("Account is suspended."))
        
        # Check if account is locked
        if user.is_account_locked():
            lock_time = user.account_locked_until
            if lock_time:
                time_left = lock_time - timezone.now()
                minutes_left = max(0, int(time_left.total_seconds() // 60))
                raise serializers.ValidationError(
                    _("Account is temporarily locked. Try again in %(minutes)d minutes.") % 
                    {'minutes': minutes_left}
                )
        
        # Check password
        if not user.check_password(password):
            # Record failed login attempt
            request = self.context.get('request')
            ip_address = request.META.get('REMOTE_ADDR') if request else None
            user_agent = request.META.get('HTTP_USER_AGENT') if request else None
            
            user.record_failed_login(ip_address, user_agent, "Invalid password")
            
            # Check if account is now locked
            if user.is_account_locked():
                raise serializers.ValidationError(_("Too many failed attempts. Account locked for 30 minutes."))
            
            raise serializers.ValidationError(_("Invalid email or password."))
        
        # Check if account needs approval
        if not user.is_approved and user.requires_approval():
            raise serializers.ValidationError(_("Account pending approval. Please contact administrator."))
        
        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email and check if user exists"""
        value = value.strip().lower()
        
        try:
            user = User.objects.get(email=value)
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(_("Account is inactive."))
            
            # Check if user is suspended
            if user.is_suspended:
                raise serializers.ValidationError(_("Account is suspended."))
            
            return value
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist for security
            return value
    
    def save(self):
        """Initiate password reset process"""
        email = self.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Delete existing unused password reset tokens
            user.otp_tokens.filter(
                token_type=OTPToken.TokenTypeChoices.PASSWORD_RESET,
                is_used=False
            ).update(is_used=True)
            
            # Create new password reset token
            request = self.context.get('request')
            ip_address = request.META.get('REMOTE_ADDR') if request else None
            user_agent = request.META.get('HTTP_USER_AGENT') if request else None
            
            token = OTPToken.create_otp(
                user=user,
                token_type=OTPToken.TokenTypeChoices.PASSWORD_RESET,
                purpose="Password reset",
                ip_address=ip_address,
                user_agent=user_agent,
                validity_minutes=30
            )
            
            # Send password reset email
            user.initiate_password_reset(request)
            
            logger.info(f"Password reset requested for {email}")
            
            return token
            
        except User.DoesNotExist:
            # For security, don't reveal if user exists
            return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': _("Passwords do not match.")
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        # Verify token
        try:
            otp_token = OTPToken.objects.get(
                token=token,
                token_type=OTPToken.TokenTypeChoices.PASSWORD_RESET,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            # Check if user is active
            user = otp_token.user
            if not user.is_active:
                raise serializers.ValidationError(_("Account is inactive."))
            
            if user.is_suspended:
                raise serializers.ValidationError(_("Account is suspended."))
            
            attrs['otp_token'] = otp_token
            attrs['user'] = user
            
            return attrs
            
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': _("Invalid or expired reset token.")
            })
    
    def save(self):
        """Reset password and mark token as used"""
        otp_token = self.validated_data['otp_token']
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        otp_token.mark_used()
        
        # Record in login history
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        user_agent = request.META.get('HTTP_USER_AGENT') if request else None
        
        LoginHistory.record_login_attempt(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            status=LoginHistory.LoginStatusChoices.PASSWORD_RESET
        )
        
        logger.info(f"Password reset completed for {user.email}")
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password while logged in"""
    
    current_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        
        if not user.check_password(value):
            raise serializers.ValidationError(_("Current password is incorrect."))
        
        return value
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': _("Passwords do not match.")
            })
        
        # Check if new password is same as current
        current_password = attrs.get('current_password')
        if new_password == current_password:
            raise serializers.ValidationError({
                'new_password': _("New password must be different from current password.")
            })
        
        return attrs
    
    def save(self):
        """Change password"""
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Record the change
        logger.info(f"Password changed for {user.email}")
        
        return user


# ============================================================================
# TWO-FACTOR AUTHENTICATION SERIALIZERS
# ============================================================================

class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for setting up 2FA"""
    
    method = serializers.ChoiceField(
        choices=TwoFAMethodChoices.choices,
        required=True
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required if selecting SMS method and no phone number is set"
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Required if selecting EMAIL method and no email is set"
    )
    
    def validate(self, attrs):
        user = self.context['request'].user
        method = attrs.get('method')
        
        # Check if 2FA is already enabled
        try:
            two_fa = user.two_factor_auth
            if two_fa.is_enabled:
                raise serializers.ValidationError(
                    _("Two-factor authentication is already enabled.")
                )
        except TwoFactorAuth.DoesNotExist:
            pass
        
        # Validate method requirements
        if method == TwoFactorAuth.TwoFAMethodChoices.EMAIL:
            email = attrs.get('email') or user.email
            if not email:
                raise serializers.ValidationError({
                    'email': _("Email is required for email-based 2FA. Please provide an email address.")
                })
            # Validate email format if provided
            if attrs.get('email'):
                # Django's EmailValidator is already used by EmailField
                # Additional custom validation can be added here if needed
                pass
        
        if method == TwoFactorAuth.TwoFAMethodChoices.SMS:
            phone_number = attrs.get('phone_number') or user.phone_number
            if not phone_number:
                raise serializers.ValidationError({
                    'phone_number': _("Phone number is required for SMS-based 2FA. Please provide a phone number.")
                })
            # Validate phone number format if provided
            if attrs.get('phone_number'):
                if not self._is_valid_phone_number(phone_number):
                    raise serializers.ValidationError({
                        'phone_number': _("Invalid phone number format. Please use a valid phone number.")
                    })
                # Check if phone number is already used by another user
                if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
                    raise serializers.ValidationError({
                        'phone_number': _("This phone number is already registered to another account.")
                    })
        
        return attrs
    
    def _is_valid_phone_number(self, phone_number):
        """Basic phone number validation"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        # Basic validation - adjust based on your requirements
        return len(digits) >= 10 and len(digits) <= 15
    
    @transaction.atomic
    def save(self):
        """Setup 2FA for user"""
        user = self.context['request'].user
        method = self.validated_data['method']
        
        # Update user contact info if provided
        update_fields = []
        
        if method == TwoFactorAuth.TwoFAMethodChoices.SMS and 'phone_number' in self.validated_data:
            phone_number = self.validated_data.get('phone_number')
            if phone_number:  # Only update if a value was provided
                user.phone_number = phone_number
                update_fields.append('phone_number')
        
        if method == TwoFactorAuth.TwoFAMethodChoices.EMAIL and 'email' in self.validated_data:
            email = self.validated_data.get('email')
            if email:  # Only update if a value was provided
                user.email = email
                update_fields.append('email')
        
        if update_fields:
            user.save(update_fields=update_fields)
        
        # Get or create 2FA settings
        two_fa, created = TwoFactorAuth.objects.get_or_create(user=user)
        
        # Update primary method
        two_fa.primary_method = method
        
        # Generate secret key if using authenticator
        if method == TwoFactorAuth.TwoFAMethodChoices.AUTHENTICATOR and not two_fa.secret_key:
            two_fa.generate_secret()
        
        # Generate backup codes
        backup_codes = two_fa.generate_backup_codes()
        
        two_fa.save()
        
        # Prepare response data
        response_data = {
            'two_fa': TwoFactorAuthSerializer(two_fa).data,
            'backup_codes': backup_codes,
            'message': _("Two-factor authentication has been successfully set up.")
        }
        
        # Add method-specific data
        if method == TwoFactorAuth.TwoFAMethodChoices.AUTHENTICATOR:
            # Include QR code URI for authenticator setup
            response_data['qr_code_uri'] = two_fa.generate_provisioning_uri()
        
        return response_data


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for verifying 2FA setup"""
    
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate(self, attrs):
        user = self.context['request'].user
        otp = attrs.get('otp')
        
        try:
            two_fa = user.two_factor_auth
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(
                _("Two-factor authentication is not set up.")
            )
        
        # Verify OTP
        if not two_fa.verify_otp(otp):
            raise serializers.ValidationError({
                'otp': _("Invalid OTP code.")
            })
        
        attrs['two_fa'] = two_fa
        return attrs
    
    def save(self):
        """Enable 2FA after verification"""
        two_fa = self.validated_data['two_fa']
        
        # Enable 2FA
        two_fa.is_enabled = True
        two_fa.save()
        
        logger.info(f"2FA enabled for {two_fa.user.email}")
        
        return two_fa


class TwoFactorDisableSerializer(serializers.Serializer):
    """Serializer for disabling 2FA"""
    
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('password')
        
        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': _("Password is incorrect.")
            })
        
        # Check if 2FA is enabled
        try:
            two_fa = user.two_factor_auth
            if not two_fa.is_enabled:
                raise serializers.ValidationError(
                    _("Two-factor authentication is not enabled.")
                )
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(
                _("Two-factor authentication is not set up.")
            )
        
        attrs['two_fa'] = two_fa
        return attrs
    
    def save(self):
        """Disable 2FA"""
        two_fa = self.validated_data['two_fa']
        
        # Disable 2FA
        two_fa.disable_2fa()
        
        logger.info(f"2FA disabled for {two_fa.user.email}")
        
        return two_fa


class TwoFactorBackupCodeSerializer(serializers.Serializer):
    """Serializer for verifying 2FA backup code"""
    
    backup_code = serializers.CharField(
        required=True,
        max_length=8,
        min_length=8,
        help_text="8-character backup code"
    )
    
    def validate(self, attrs):
        user = self.context['request'].user
        backup_code = attrs.get('backup_code')
        
        try:
            two_fa = user.two_factor_auth
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(
                _("Two-factor authentication is not set up.")
            )
        
        # Verify backup code
        if not two_fa.verify_backup_code(backup_code):
            raise serializers.ValidationError({
                'backup_code': _("Invalid backup code.")
            })
        
        attrs['two_fa'] = two_fa
        return attrs


# ============================================================================
# OTP & VERIFICATION SERIALIZERS
# ============================================================================

class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email"""
        value = value.strip().lower()
        
        try:
            user = User.objects.get(email=value)
            
            # Check if already verified
            if user.email_verified:
                raise serializers.ValidationError(
                    _("Email is already verified.")
                )
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    _("Account is inactive.")
                )
            
            return value
            
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("User with this email does not exist.")
            )
    
    def save(self):
        """Send verification email"""
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        request = self.context.get('request')
        
        # Send verification email
        token = user.send_verification_email(request)
        
        logger.info(f"Verification email sent to {email}")
        
        return token


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for verifying email with token"""
    
    token = serializers.CharField(required=True)
    
    def validate(self, attrs):
        token = attrs.get('token')
        
        try:
            otp_token = OTPToken.objects.get(
                token=token,
                token_type=OTPToken.TokenTypeChoices.EMAIL_VERIFICATION,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            user = otp_token.user
            
            # Check if already verified
            if user.email_verified:
                raise serializers.ValidationError(
                    _("Email is already verified.")
                )
            
            attrs['otp_token'] = otp_token
            attrs['user'] = user
            
            return attrs
            
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': _("Invalid or expired verification token.")
            })
    
    def save(self):
        """Verify email and mark token as used"""
        otp_token = self.validated_data['otp_token']
        user = self.validated_data['user']
        
        # Mark email as verified
        user.email_verified = True
        
        # Also mark as verified if this was the last verification needed
        if not user.is_verified and (user.phone_verified or not user.phone_number):
            user.is_verified = True
        
        user.save()
        
        # Mark token as used
        otp_token.mark_used()
        
        logger.info(f"Email verified for {user.email}")
        
        return user


class PhoneVerificationSerializer(serializers.Serializer):
    """Serializer for phone verification"""
    
    phone_number = serializers.CharField(required=True)
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        # Clean phone number
        value = value.strip().replace(' ', '')
        
        # Basic phone validation
        phone_regex = r'^\+?1?\d{9,15}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                _("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        
        # Check if user exists with this phone number
        user = self.context['request'].user
        
        # Check if phone number is already verified
        if user.phone_verified and user.phone_number == value:
            raise serializers.ValidationError(
                _("Phone number is already verified.")
            )
        
        return value
    
    def save(self):
        """Send phone verification OTP"""
        user = self.context['request'].user
        phone_number = self.validated_data['phone_number']
        
        # Update phone number if different
        if user.phone_number != phone_number:
            user.phone_number = phone_number
            user.phone_verified = False
            user.save()
        
        # Create OTP for phone verification
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        user_agent = request.META.get('HTTP_USER_AGENT') if request else None
        
        token = OTPToken.create_otp(
            user=user,
            token_type=OTPToken.TokenTypeChoices.PHONE_VERIFICATION,
            purpose="Phone verification",
            ip_address=ip_address,
            user_agent=user_agent,
            validity_minutes=10
        )
        
        # TODO: Send SMS with OTP
        # This would integrate with an SMS service provider
        
        logger.info(f"Phone verification OTP sent to {phone_number}")
        
        return token


class VerifyPhoneSerializer(serializers.Serializer):
    """Serializer for verifying phone with OTP"""
    
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate(self, attrs):
        user = self.context['request'].user
        otp = attrs.get('otp')
        
        # Verify OTP
        try:
            otp_token = OTPToken.objects.get(
                user=user,
                token=otp,
                token_type=OTPToken.TokenTypeChoices.PHONE_VERIFICATION,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            attrs['otp_token'] = otp_token
            return attrs
            
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError({
                'otp': _("Invalid or expired OTP code.")
            })
    
    def save(self):
        """Verify phone and mark token as used"""
        otp_token = self.validated_data['otp_token']
        user = self.context['request'].user
        
        # Mark phone as verified
        user.phone_verified = True
        
        # Also mark as verified if this was the last verification needed
        if not user.is_verified and (user.email_verified or not user.email):
            user.is_verified = True
        
        user.save()
        
        # Mark token as used
        otp_token.mark_used()
        
        logger.info(f"Phone verified for {user.email}")
        
        return user


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class BulkUserUpdateSerializer(serializers.Serializer):
    """Serializer for bulk user updates"""
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of user IDs to update"
    )
    action = serializers.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('approve', 'Approve'),
            ('suspend', 'Suspend'),
            ('unsuspend', 'Unsuspend'),
            ('verify', 'Verify'),
        ],
        required=True
    )
    
    def validate_user_ids(self, value):
        """Validate user IDs exist"""
        users = User.objects.filter(id__in=value)
        if len(users) != len(value):
            raise serializers.ValidationError(
                _("Some user IDs do not exist.")
            )
        return value
    
    def save(self):
        """Perform bulk update"""
        user_ids = self.validated_data['user_ids']
        action = self.validated_data['action']
        
        # Map action to field and value
        action_map = {
            'activate': ('is_active', True),
            'deactivate': ('is_active', False),
            'approve': ('is_approved', True),
            'suspend': ('is_suspended', True),
            'unsuspend': ('is_suspended', False),
            'verify': ('is_verified', True),
        }
        
        field, value = action_map.get(action, (None, None))
        
        if not field:
            raise serializers.ValidationError(_("Invalid action."))
        
        # Perform bulk update
        updated_count = User.bulk_update_status(user_ids, field, value)
        
        return {
            'updated_count': updated_count,
            'action': action
        }


class BulkUserDeleteSerializer(serializers.Serializer):
    """Serializer for bulk user deletion"""
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of user IDs to delete"
    )
    confirm = serializers.BooleanField(
        required=True,
        help_text="Confirm deletion"
    )
    
    def validate(self, attrs):
        if not attrs.get('confirm'):
            raise serializers.ValidationError({
                'confirm': _("Please confirm deletion.")
            })
        
        user_ids = attrs.get('user_ids')
        users = User.objects.filter(id__in=user_ids)
        
        # Check if trying to delete self
        request_user = self.context.get('request').user
        if request_user.id in user_ids:
            raise serializers.ValidationError({
                'user_ids': _("You cannot delete your own account.")
            })
        
        # Check for admin users
        admin_users = users.filter(role=User.UserRole.ADMIN)
        if admin_users.exists():
            raise serializers.ValidationError({
                'user_ids': _("Cannot delete administrator accounts.")
            })
        
        attrs['users'] = users
        return attrs
    
    def save(self):
        """Delete users"""
        users = self.validated_data['users']
        deleted_count = users.count()
        
        # Soft delete users (set is_active=False)
        users.update(is_active=False)
        
        logger.info(f"Bulk deleted {deleted_count} users")
        
        return {
            'deleted_count': deleted_count
        }


# ============================================================================
# DASHBOARD & REDIRECTION SERIALIZERS
# ============================================================================

class DashboardPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for dashboard preferences"""
    
    class Meta:
        model = User
        fields = [
            'preferred_dashboard_view',
            'dashboard_widgets',
            'theme_preference'
        ]
    
    def validate_dashboard_widgets(self, value):
        """Validate dashboard widgets configuration"""
        if value and isinstance(value, dict):
            # Add any widget validation logic here
            pass
        return value
    
    def update(self, instance, validated_data):
        """Update dashboard preferences"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UserRedirectSerializer(serializers.Serializer):
    """Serializer for user redirection information"""
    
    redirect_url = serializers.CharField(read_only=True)
    requires_action = serializers.BooleanField(read_only=True)
    action_type = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    
    def to_representation(self, instance):
        """Get redirection information for user"""
        user = instance
        
        data = {
            'redirect_url': user.get_redirect_url_after_login(),
            'requires_action': False,
            'action_type': None,
            'message': None
        }
        
        # Check if user needs to complete profile
        if not user.profile_completed:
            data['requires_action'] = True
            data['action_type'] = 'complete_profile'
            data['message'] = _("Please complete your profile to continue.")
        
        # Check if user is suspended
        elif user.is_suspended:
            data['requires_action'] = True
            data['action_type'] = 'account_suspended'
            data['message'] = _("Your account is suspended. Please contact administrator.")
        
        # Check if user needs approval
        elif not user.is_approved and user.requires_approval():
            data['requires_action'] = True
            data['action_type'] = 'pending_approval'
            data['message'] = _("Your account is pending approval.")
        
        # Check if password is expired
        elif user.is_password_expired():
            data['requires_action'] = True
            data['action_type'] = 'change_password'
            data['message'] = _("Your password has expired. Please change it.")
        
        # Check if 2FA setup is required
        elif user.requires_2fa_setup and not user.has_2fa_enabled():
            data['requires_action'] = True
            data['action_type'] = 'setup_2fa'
            data['message'] = _("Two-factor authentication is required for your role.")
        
        return data


# ============================================================================
# EXPORT SERIALIZERS
# ============================================================================

class UserExportSerializer(serializers.ModelSerializer):
    """Serializer for user data export (GDPR compliance)"""
    
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    profile_completion_percentage = serializers.SerializerMethodField()
    missing_profile_fields = serializers.SerializerMethodField()
    login_history_count = serializers.SerializerMethodField()
    last_login_location = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role',
            'first_name', 'last_name', 'middle_name',
            'phone_number', 'alternative_phone',
            'address', 'city', 'country',
            'date_of_birth', 'age', 'gender', 'nationality',
            'id_number', 'profile_picture',
            'blood_group', 'medical_info', 'allergies',
            'chronic_conditions', 'current_medications',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'emergency_contact_address',
            'admission_number', 'staff_id',
            'primary_curriculum', 'grade_level', 'current_class',
            'house', 'academic_year',
            'department', 'qualification', 'specialization',
            'designation', 'years_of_experience', 'years_of_service',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'previous_school', 'transfer_certificate', 'birth_certificate',
            'recommendation_letter',
            'is_active', 'is_verified', 'is_approved', 'is_suspended',
            'is_on_leave', 'email_verified', 'phone_verified',
            'profile_completed', 'profile_completion_percentage',
            'missing_profile_fields',
            'date_joined', 'enrollment_date', 'employment_date',
            'last_login', 'last_login_ip', 'login_count',
            'password_changed_at', 'last_profile_update',
            'login_history_count', 'last_login_location',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.age
    
    def get_years_of_service(self, obj):
        return obj.years_of_service
    
    def get_profile_completion_percentage(self, obj):
        return obj.profile_completion_percentage
    
    def get_missing_profile_fields(self, obj):
        return obj.get_missing_profile_fields()
    
    def get_login_history_count(self, obj):
        return obj.login_history.count()
    
    def get_last_login_location(self, obj):
        last_login = obj.login_history.filter(
            login_status=LoginHistory.LoginStatusChoices.SUCCESS
        ).order_by('-created_at').first()
        
        if last_login:
            return {
                'location': last_login.location,
                'country': last_login.country,
                'city': last_login.city,
                'ip_address': last_login.ip_address,
                'date': last_login.created_at
            }
        return None


# ============================================================================
# ADMIN-SPECIFIC SERIALIZERS
# ============================================================================

class UserAdminCreateSerializer(UserCreateSerializer):
    """Admin-only user creation serializer with additional fields"""
    
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + [
            'is_staff', 'is_verified', 'is_approved',
            'is_active', 'profile_completed'
        ]
    
    def validate(self, attrs):
        # Call parent validation
        attrs = super().validate(attrs)
        
        # Admin-specific validation
        request_user = self.context['request'].user
        
        # Only admins can create staff/admin users
        role = attrs.get('role')
        if role in [User.UserRole.ADMIN, User.UserRole.HEAD_TEACHER]:
            if not request_user.is_superuser:
                raise serializers.ValidationError({
                    'role': _("Only superusers can create administrator accounts.")
                })
        
        return attrs


class UserAdminUpdateSerializer(UserUpdateSerializer):
    """Admin-only user update serializer"""
    
    class Meta(UserUpdateSerializer.Meta):
        fields = UserUpdateSerializer.Meta.fields + [
            'role', 'is_staff', 'is_verified', 'is_approved',
            'is_active', 'is_suspended', 'is_on_leave',
            'email_verified', 'phone_verified'
        ]
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        request_user = self.context['request'].user
        
        # Check permissions for role changes
        if 'role' in attrs:
            new_role = attrs['role']
            current_role = self.instance.role
            
            if new_role != current_role:
                # Only admins can change roles
                if not request_user.is_superuser:
                    raise serializers.ValidationError({
                        'role': _("Only administrators can change user roles.")
                    })
                
                # Prevent changing own role away from admin
                if self.instance == request_user and new_role != User.UserRole.ADMIN:
                    raise serializers.ValidationError({
                        'role': _("You cannot change your own role from administrator.")
                    })
        
        return attrs


# ============================================================================
# UTILITY SERIALIZERS
# ============================================================================

class StatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    total_users = serializers.IntegerField(read_only=True)
    active_users = serializers.IntegerField(read_only=True)
    new_users_today = serializers.IntegerField(read_only=True)
    new_users_this_week = serializers.IntegerField(read_only=True)
    verified_users = serializers.IntegerField(read_only=True)
    pending_approval = serializers.IntegerField(read_only=True)
    suspended_users = serializers.IntegerField(read_only=True)
    
    # Role distribution
    role_distribution = serializers.DictField(read_only=True)
    
    # Profile completion
    profiles_completed = serializers.IntegerField(read_only=True)
    profiles_incomplete = serializers.IntegerField(read_only=True)
    
    # Activity
    online_now = serializers.IntegerField(read_only=True)
    logins_today = serializers.IntegerField(read_only=True)


class SearchSerializer(serializers.Serializer):
    """Serializer for user search"""
    
    query = serializers.CharField(required=True, max_length=100)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=False
    )
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    is_approved = serializers.BooleanField(required=False)
    profile_completed = serializers.BooleanField(required=False)


class FilterSerializer(serializers.Serializer):
    """Serializer for user filtering"""
    
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=False
    )
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    is_approved = serializers.BooleanField(required=False)
    is_suspended = serializers.BooleanField(required=False)
    profile_completed = serializers.BooleanField(required=False)
    date_joined_start = serializers.DateField(required=False)
    date_joined_end = serializers.DateField(required=False)
    last_login_start = serializers.DateField(required=False)
    last_login_end = serializers.DateField(required=False)


# ============================================================================
# PAGINATION SERIALIZERS
# ============================================================================

class PaginatedResponseSerializer(serializers.Serializer):
    """Serializer for paginated responses"""
    
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.ListField()


# ============================================================================
# ERROR SERIALIZERS
# ============================================================================

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    
    error = serializers.CharField()
    code = serializers.CharField(required=False)
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()


class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors"""
    
    field = serializers.CharField()
    message = serializers.CharField()
    code = serializers.CharField(required=False)


# ============================================================================
# REGISTRATION MODULE
# ============================================================================

class RegistrationModuleSerializer(serializers.Serializer):
    """Serializer for user registration module data"""
    
    user = UserCreateSerializer(required=True)
    accept_terms = serializers.BooleanField(required=True)
    send_welcome_email = serializers.BooleanField(default=True)
    
    def validate_accept_terms(self, value):
        if not value:
            raise serializers.ValidationError(
                _("You must accept the terms and conditions.")
            )
        return value
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        accept_terms = validated_data.pop('accept_terms')
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        
        # Create user
        user_serializer = UserCreateSerializer(data=user_data, context=self.context)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        # Send welcome email if requested
        if send_welcome_email and user.email:
            try:
                # Import here to avoid circular imports
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                subject = _("Welcome to Delvok Academy!")
                html_message = render_to_string('accounts/welcome_email.html', {
                    'user': user,
                    'school_name': 'Delvok Academy'
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    'noreply@delvok.ac.ke',
                    [user.email],
                    html_message=html_message
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
        
        return {
            'user': user,
            'accept_terms': accept_terms,
            'message': _("Registration successful! Please check your email for verification.")
        }