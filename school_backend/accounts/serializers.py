# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.validators import UniqueValidator
from .models import User, UserProfile, TwoFactorAuth, OTPToken, LoginHistory
import re
from datetime import date


# ============================================================================
# USER SERIALIZERS
# ============================================================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        error_messages={
            'min_length': _('Password must be at least 8 characters long.')
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'middle_name',
            'password', 'password_confirm', 'role', 'phone_number',
            'date_of_birth', 'gender'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True}
        }

    def validate(self, data):
        """Validate registration data"""
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _('Passwords do not match.')
            })

        # Validate password strength
        password = data['password']
        errors = []
        
        if len(password) < 8:
            errors.append(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'[0-9]', password):
            errors.append(_('Password must contain at least one number.'))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>?]', password):
            errors.append(_('Password must contain at least one special character.'))
        
        if errors:
            raise serializers.ValidationError({'password': errors})

        # Validate role-specific requirements
        role = data.get('role')
        if role == User.Role.STUDENT:
            if not data.get('date_of_birth'):
                raise serializers.ValidationError({
                    'date_of_birth': _('Date of birth is required for students.')
                })
            
            # Validate student age
            dob = data.get('date_of_birth')
            if dob:
                age = self._calculate_age(dob)
                if age < 3:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student must be at least 3 years old.')
                    })
                if age > 25:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student age seems unrealistic.')
                    })

        # Remove password_confirm from validated data
        data.pop('password_confirm')
        
        return data

    def _calculate_age(self, dob):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def create(self, validated_data):
        """Create user with hashed password"""
        # Extract password
        password = validated_data.pop('password')
        
        # Create user
        user = User(**validated_data)
        user.set_password(password)
        
        # Set additional fields
        user.is_active = True
        user.is_verified = False
        user.is_approved = False
        user.profile_completed = False
        
        # Save user
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    remember_me = serializers.BooleanField(default=False)
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False)

    def validate(self, data):
        """Validate login credentials"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError(_('Email and password are required.'))
        
        # Authenticate user
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        
        if not user:
            # Record failed login attempt
            try:
                user_obj = User.objects.get(email=email)
                user_obj.record_failed_login(
                    ip_address=data.get('ip_address'),
                    user_agent=data.get('user_agent'),
                    reason="Invalid credentials"
                )
            except User.DoesNotExist:
                pass
            
            raise serializers.ValidationError(_('Invalid email or password.'))
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(_('Your account is deactivated. Please contact support.'))
        
        # Check if user is suspended
        if user.is_suspended:
            raise serializers.ValidationError(_('Your account has been suspended. Please contact support.'))
        
        # Check if account is locked
        if user.is_account_locked():
            raise serializers.ValidationError(_('Your account is temporarily locked. Please try again later.'))
        
        # Check if password is expired
        if user.is_password_expired():
            raise serializers.ValidationError(_('Your password has expired. Please reset your password.'))
        
        # Record successful login
        user.record_successful_login(
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent')
        )
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Base user serializer for read operations"""
    full_name = serializers.SerializerMethodField()
    profile_completion_percentage = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'middle_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'gender', 'nationality',
            'admission_number', 'staff_id', 'profile_picture', 'is_active',
            'is_verified', 'is_approved', 'is_suspended', 'profile_completed',
            'profile_completion_percentage', 'age', 'is_online', 'user_profile'
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get full name"""
        return obj.get_full_name()

    def get_profile_completion_percentage(self, obj):
        """Get profile completion percentage"""
        return obj.profile_completion_percentage

    def get_age(self, obj):
        """Get age"""
        return obj.age

    def get_is_online(self, obj):
        """Get online status"""
        return obj.is_online

    def get_user_profile(self, obj):
        """Get user profile data"""
        try:
            profile = obj.user_profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None


class UserDetailSerializer(UserSerializer):
    """Detailed user serializer with all fields"""
    years_of_service = serializers.SerializerMethodField()
    requires_2fa_setup = serializers.SerializerMethodField()
    dashboard_url = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    feature_flags = serializers.SerializerMethodField()
    missing_profile_fields = serializers.SerializerMethodField()
    identifier = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'address', 'city', 'country', 'id_number',
            'grade_level', 'current_class', 'house', 'academic_year',
            'primary_curriculum', 'department', 'designation',
            'qualification', 'specialization', 'years_of_experience',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'emergency_contact_address',
            'medical_info', 'allergies', 'chronic_conditions',
            'current_medications', 'doctor_name', 'doctor_phone',
            'blood_group', 'previous_school', 'years_of_service',
            'requires_2fa_setup', 'dashboard_url', 'permissions',
            'feature_flags', 'missing_profile_fields', 'identifier',
            'email_verified', 'phone_verified', 'is_on_leave',
            'enrollment_date', 'employment_date', 'date_joined',
            'last_login', 'login_count', 'failed_login_attempts',
            'last_profile_update', 'preferred_dashboard_view',
            'dashboard_widgets', 'theme_preference'
        )
        read_only_fields = fields

    def get_years_of_service(self, obj):
        """Get years of service"""
        return obj.years_of_service

    def get_requires_2fa_setup(self, obj):
        """Check if 2FA setup is required"""
        return obj.requires_2fa_setup

    def get_dashboard_url(self, obj):
        """Get dashboard URL"""
        return obj.get_dashboard_url()

    def get_permissions(self, obj):
        """Get user permissions"""
        return obj.get_permissions()

    def get_feature_flags(self, obj):
        """Get user feature flags"""
        return obj.get_feature_flags()

    def get_missing_profile_fields(self, obj):
        """Get missing profile fields"""
        return obj.get_missing_profile_fields()

    def get_identifier(self, obj):
        """Get user identifier"""
        return obj.identifier


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        help_text=_('Required when changing password')
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        min_length=8
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'middle_name',
            'phone_number', 'alternative_phone',
            'address', 'city', 'country',
            'date_of_birth', 'gender', 'nationality',
            'profile_picture', 'id_number',
            'grade_level', 'current_class', 'house',
            'department', 'designation',
            'qualification', 'specialization',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'emergency_contact_address',
            'medical_info', 'allergies', 'chronic_conditions',
            'current_medications', 'doctor_name', 'doctor_phone',
            'blood_group', 'previous_school',
            'current_password', 'new_password', 'confirm_password',
            'preferred_dashboard_view', 'theme_preference', 'dashboard_widgets'
        )
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
        }

    def validate(self, data):
        """Validate update data"""
        # Validate password change
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        current_password = data.get('current_password')

        if new_password or confirm_password:
            if not current_password:
                raise serializers.ValidationError({
                    'current_password': _('Current password is required to change password.')
                })
            
            if new_password != confirm_password:
                raise serializers.ValidationError({
                    'confirm_password': _('New passwords do not match.')
                })
            
            # Validate new password strength
            errors = []
            if len(new_password) < 8:
                errors.append(_('Password must be at least 8 characters long.'))
            if not re.search(r'[A-Z]', new_password):
                errors.append(_('Password must contain at least one uppercase letter.'))
            if not re.search(r'[a-z]', new_password):
                errors.append(_('Password must contain at least one lowercase letter.'))
            if not re.search(r'[0-9]', new_password):
                errors.append(_('Password must contain at least one number.'))
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>?]', new_password):
                errors.append(_('Password must contain at least one special character.'))
            
            if errors:
                raise serializers.ValidationError({'new_password': errors})
        
        # Validate student-specific fields
        user = self.instance
        if user.role == User.Role.STUDENT:
            if 'date_of_birth' in data and data['date_of_birth']:
                age = self._calculate_age(data['date_of_birth'])
                if age < 3:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student must be at least 3 years old.')
                    })
                if age > 25:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student age seems unrealistic.')
                    })
        
        return data

    def _calculate_age(self, dob):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def update(self, instance, validated_data):
        """Update user instance"""
        # Handle password change
        new_password = validated_data.pop('new_password', None)
        current_password = validated_data.pop('current_password', None)
        validated_data.pop('confirm_password', None)
        
        if new_password and current_password:
            # Verify current password
            if not instance.check_password(current_password):
                raise serializers.ValidationError({
                    'current_password': _('Current password is incorrect.')
                })
            
            # Set new password
            instance.set_password(new_password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update profile completion status
        instance.check_profile_completion()
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (minimal data)"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'role', 'role_display',
            'profile_picture', 'is_active', 'is_verified',
            'profile_completion', 'date_joined'
        )

    def get_full_name(self, obj):
        """Get full name"""
        return obj.get_full_name()

    def get_role_display(self, obj):
        """Get role display name"""
        return obj.get_role_display()

    def get_profile_completion(self, obj):
        """Get profile completion percentage"""
        return obj.profile_completion_percentage



# Add this to your accounts/serializers.py file, around line 400 (after UserListSerializer)

class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for basic user information"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'role', 'role_display',
            'profile_picture', 'admission_number', 'staff_id',
            'grade_level', 'current_class', 'department',
            'designation', 'phone_number'
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get full name"""
        return obj.get_full_name()

    def get_role_display(self, obj):
        """Get role display name"""
        return obj.get_role_display()

# ============================================================================
# USER PROFILE SERIALIZERS
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_email', 'user_full_name',
            'bio', 'website', 'social_links', 'hobbies',
            'notifications_enabled', 'email_notifications',
            'sms_notifications', 'push_notifications',
            'language', 'timezone', 'profile_visibility',
            'contact_preference', 'achievements', 'skills',
            'education_background'
        )
        read_only_fields = ('id',)

    def get_user_full_name(self, obj):
        """Get user full name"""
        return obj.user.get_full_name()

    def validate_social_links(self, value):
        """Validate social links"""
        if not isinstance(value, dict):
            raise serializers.ValidationError(_('Social links must be a dictionary.'))
        
        # Validate URLs in social links
        for key, url in value.items():
            if not url.startswith(('http://', 'https://')):
                raise serializers.ValidationError({
                    'social_links': _('URLs must start with http:// or https://')
                })
        
        return value

    def validate_achievements(self, value):
        """Validate achievements array"""
        if not isinstance(value, list):
            raise serializers.ValidationError(_('Achievements must be a list.'))
        
        for achievement in value:
            if not isinstance(achievement, dict):
                raise serializers.ValidationError(_('Each achievement must be a dictionary.'))
            
            if 'title' not in achievement:
                raise serializers.ValidationError(_('Each achievement must have a title.'))
        
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = UserProfile
        fields = (
            'bio', 'website', 'social_links', 'hobbies',
            'notifications_enabled', 'email_notifications',
            'sms_notifications', 'push_notifications',
            'language', 'timezone', 'profile_visibility',
            'contact_preference'
        )

    def validate_social_links(self, value):
        """Validate social links"""
        if not isinstance(value, dict):
            raise serializers.ValidationError(_('Social links must be a dictionary.'))
        
        for key, url in value.items():
            if not url.startswith(('http://', 'https://')):
                raise serializers.ValidationError({
                    'social_links': _('URLs must start with http:// or https://')
                })
        
        return value


# ============================================================================
# AUTHENTICATION SERIALIZERS
# ============================================================================

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)
    captcha = serializers.CharField(required=False)

    def validate_email(self, value):
        """Validate email exists"""
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError(_('This account is deactivated.'))
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email address.'))


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validate password reset data"""
        # Check if passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': _('Passwords do not match.')
            })

        # Validate password strength
        password = data['new_password']
        errors = []
        
        if len(password) < 8:
            errors.append(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'[0-9]', password):
            errors.append(_('Password must contain at least one number.'))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>?]', password):
            errors.append(_('Password must contain at least one special character.'))
        
        if errors:
            raise serializers.ValidationError({'new_password': errors})

        # Validate token
        token = data['token']
        try:
            otp = OTPToken.objects.get(
                token=token,
                token_type=OTPToken.TokenType.PASSWORD_RESET,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            data['otp'] = otp
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': _('Invalid or expired reset token.')
            })

        return data

    def save(self):
        """Reset password"""
        otp = self.validated_data['otp']
        new_password = self.validated_data['new_password']
        
        # Update password
        user = otp.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        otp.mark_used()
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password while logged in"""
    current_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    confirm_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validate password change data"""
        user = self.context['request'].user
        
        # Check current password
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError({
                'current_password': _('Current password is incorrect.')
            })

        # Check if passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': _('Passwords do not match.')
            })

        # Check if new password is same as current
        if user.check_password(data['new_password']):
            raise serializers.ValidationError({
                'new_password': _('New password must be different from current password.')
            })

        # Validate password strength
        password = data['new_password']
        errors = []
        
        if len(password) < 8:
            errors.append(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'[0-9]', password):
            errors.append(_('Password must contain at least one number.'))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>?]', password):
            errors.append(_('Password must contain at least one special character.'))
        
        if errors:
            raise serializers.ValidationError({'new_password': errors})

        return data

    def save(self):
        """Change password"""
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField(required=True)

    def validate(self, data):
        """Validate verification token"""
        token = data['token']
        
        try:
            otp = OTPToken.objects.get(
                token=token,
                token_type=OTPToken.TokenType.EMAIL_VERIFICATION,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            data['otp'] = otp
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': _('Invalid or expired verification token.')
            })

        return data

    def save(self):
        """Verify email"""
        otp = self.validated_data['otp']
        user = otp.user
        
        # Mark email as verified
        user.email_verified = True
        user.is_verified = True
        
        # Auto-approve certain roles
        if user.role in [User.Role.STUDENT, User.Role.PARENT]:
            user.is_approved = True
        
        user.save()
        
        # Mark token as used
        otp.mark_used()
        
        return user


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email"""
        try:
            user = User.objects.get(email=value)
            if user.email_verified:
                raise serializers.ValidationError(_('Email is already verified.'))
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email address.'))


# ============================================================================
# TWO-FACTOR AUTHENTICATION SERIALIZERS
# ============================================================================

class TwoFactorSetupSerializer(serializers.ModelSerializer):
    """Serializer for 2FA setup"""
    qr_code = serializers.SerializerMethodField()
    secret_key = serializers.SerializerMethodField()
    provisioning_uri = serializers.SerializerMethodField()

    class Meta:
        model = TwoFactorAuth
        fields = ('primary_method', 'qr_code', 'secret_key', 'provisioning_uri')
        read_only_fields = ('qr_code', 'secret_key', 'provisioning_uri')

    def get_qr_code(self, obj):
        """Get QR code"""
        return obj.generate_qr_code()

    def get_secret_key(self, obj):
        """Get secret key"""
        return obj.secret_key

    def get_provisioning_uri(self, obj):
        """Get provisioning URI"""
        return obj.generate_provisioning_uri()

    def create(self, validated_data):
        """Create 2FA setup"""
        user = self.context['request'].user
        two_fa, created = TwoFactorAuth.objects.get_or_create(user=user)
        
        if created or not two_fa.secret_key:
            two_fa.generate_secret()
        
        two_fa.primary_method = validated_data.get('primary_method', two_fa.primary_method)
        two_fa.save()
        
        return two_fa


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for verifying 2FA setup"""
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text=_('6-digit OTP code from authenticator app')
    )
    backup_code = serializers.CharField(
        required=False,
        help_text=_('Backup code (if OTP is not available)')
    )

    def validate(self, data):
        """Validate 2FA verification"""
        user = self.context['request'].user
        otp_code = data.get('otp')
        backup_code = data.get('backup_code')
        
        try:
            two_fa = user.two_factor_auth
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(_('2FA is not setup for this account.'))
        
        # Try OTP first
        if otp_code and two_fa.verify_otp(otp_code):
            data['verified'] = True
            return data
        
        # Try backup code
        if backup_code and two_fa.verify_backup_code(backup_code):
            data['verified'] = True
            return data
        
        raise serializers.ValidationError(_('Invalid OTP or backup code.'))

    def save(self):
        """Enable 2FA after verification"""
        user = self.context['request'].user
        two_fa = user.two_factor_auth
        
        two_fa.is_enabled = True
        two_fa.save()
        
        # Generate backup codes
        backup_codes = two_fa.generate_backup_codes()
        
        return {
            'two_fa': two_fa,
            'backup_codes': backup_codes
        }


class TwoFactorLoginSerializer(serializers.Serializer):
    """Serializer for 2FA during login"""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6
    )
    remember_device = serializers.BooleanField(default=False)

    def validate(self, data):
        """Validate 2FA login"""
        email = data['email']
        otp_code = data['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Invalid user.'))
        
        try:
            two_fa = user.two_factor_auth
            if not two_fa.is_enabled:
                raise serializers.ValidationError(_('2FA is not enabled for this account.'))
            
            if not two_fa.verify_otp(otp_code):
                raise serializers.ValidationError(_('Invalid OTP code.'))
            
            data['user'] = user
            return data
            
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(_('2FA is not setup for this account.'))


class TwoFactorDisableSerializer(serializers.Serializer):
    """Serializer for disabling 2FA"""
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validate password for disabling 2FA"""
        user = self.context['request'].user
        password = data['password']
        
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': _('Password is incorrect.')
            })
        
        return data

    def save(self):
        """Disable 2FA"""
        user = self.context['request'].user
        
        try:
            two_fa = user.two_factor_auth
            two_fa.disable_2fa()
            return two_fa
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(_('2FA is not setup for this account.'))


class BackupCodesSerializer(serializers.Serializer):
    """Serializer for generating backup codes"""
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validate password"""
        user = self.context['request'].user
        password = data['password']
        
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': _('Password is incorrect.')
            })
        
        return data

    def save(self):
        """Generate new backup codes"""
        user = self.context['request'].user
        
        try:
            two_fa = user.two_factor_auth
            if not two_fa.is_enabled:
                raise serializers.ValidationError(_('2FA is not enabled.'))
            
            backup_codes = two_fa.generate_backup_codes()
            return backup_codes
            
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(_('2FA is not setup for this account.'))


# ============================================================================
# ADMIN SERIALIZERS
# ============================================================================

class UserCreateByAdminSerializer(serializers.ModelSerializer):
    """Serializer for creating users by admin"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    send_welcome_email = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'middle_name',
            'password', 'role', 'phone_number', 'date_of_birth',
            'gender', 'nationality', 'is_active', 'is_verified',
            'is_approved', 'send_welcome_email'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True}
        }

    def validate(self, data):
        """Validate user creation by admin"""
        # Validate role-specific requirements
        role = data.get('role')
        
        if role == User.Role.STUDENT:
            if not data.get('date_of_birth'):
                raise serializers.ValidationError({
                    'date_of_birth': _('Date of birth is required for students.')
                })
            
            # Validate student age
            dob = data.get('date_of_birth')
            if dob:
                age = self._calculate_age(dob)
                if age < 3:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student must be at least 3 years old.')
                    })
                if age > 25:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student age seems unrealistic.')
                    })
        
        # Validate password strength
        password = data.get('password')
        errors = []
        
        if len(password) < 8:
            errors.append(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'[0-9]', password):
            errors.append(_('Password must contain at least one number.'))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>?]', password):
            errors.append(_('Password must contain at least one special character.'))
        
        if errors:
            raise serializers.ValidationError({'password': errors})
        
        return data

    def _calculate_age(self, dob):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def create(self, validated_data):
        """Create user by admin"""
        # Extract send_welcome_email flag
        send_welcome_email = validated_data.pop('send_welcome_email', False)
        
        # Extract password
        password = validated_data.pop('password')
        
        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Send welcome email if requested
        if send_welcome_email:
            try:
                user.send_verification_email()
            except Exception as e:
                # Log error but don't fail user creation
                print(f"Failed to send welcome email: {e}")
        
        return user


class UserUpdateByAdminSerializer(serializers.ModelSerializer):
    """Serializer for updating users by admin"""
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'middle_name',
            'phone_number', 'alternative_phone',
            'address', 'city', 'country',
            'date_of_birth', 'gender', 'nationality',
            'id_number', 'profile_picture',
            'grade_level', 'current_class', 'house', 'academic_year',
            'primary_curriculum', 'department', 'designation',
            'qualification', 'specialization', 'years_of_experience',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'emergency_contact_address',
            'medical_info', 'allergies', 'chronic_conditions',
            'current_medications', 'doctor_name', 'doctor_phone',
            'blood_group', 'previous_school',
            'is_active', 'is_verified', 'is_approved', 'is_suspended',
            'is_on_leave', 'email_verified', 'phone_verified',
            'profile_completed', 'enrollment_date', 'employment_date'
        )

    def validate(self, data):
        """Validate admin update"""
        instance = self.instance
        
        # Validate student-specific fields
        if instance.role == User.Role.STUDENT:
            if 'date_of_birth' in data and data['date_of_birth']:
                age = self._calculate_age(data['date_of_birth'])
                if age < 3:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student must be at least 3 years old.')
                    })
                if age > 25:
                    raise serializers.ValidationError({
                        'date_of_birth': _('Student age seems unrealistic.')
                    })
        
        return data

    def _calculate_age(self, dob):
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def update(self, instance, validated_data):
        """Update user by admin"""
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update profile completion status
        instance.check_profile_completion()
        
        instance.save()
        return instance


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user status by admin"""
    class Meta:
        model = User
        fields = ('is_active', 'is_verified', 'is_approved', 'is_suspended', 'is_on_leave')
    
    def update(self, instance, validated_data):
        """Update user status"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


# ============================================================================
# STATISTICS AND DASHBOARD SERIALIZERS
# ============================================================================

class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    pending_approval = serializers.IntegerField()
    suspended_users = serializers.IntegerField()
    role_distribution = serializers.DictField()
    profile_completion_stats = serializers.DictField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    user_stats = UserStatisticsSerializer()
    login_stats = serializers.DictField()
    activity_stats = serializers.DictField()
    recent_activity = serializers.ListField()


# ============================================================================
# EXPORT SERIALIZERS
# ============================================================================

class UserExportSerializer(serializers.ModelSerializer):
    """Serializer for user data export"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()
    blood_group_display = serializers.SerializerMethodField()
    house_display = serializers.SerializerMethodField()
    curriculum_display = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    profile_completion_percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name',
            'role', 'role_display',
            'admission_number', 'staff_id',
            'phone_number', 'date_of_birth', 'age',
            'gender', 'gender_display',
            'nationality', 'id_number',
            'grade_level', 'current_class',
            'house', 'house_display',
            'primary_curriculum', 'curriculum_display',
            'academic_year', 'enrollment_date',
            'department', 'designation',
            'years_of_experience', 'years_of_service',
            'employment_date', 'parent_name',
            'parent_email', 'parent_phone',
            'address', 'city', 'country',
            'blood_group', 'blood_group_display',
            'is_active', 'is_verified', 'is_approved',
            'is_suspended', 'is_on_leave',
            'profile_completed', 'profile_completion_percentage',
            'date_joined', 'last_login',
            'login_count', 'status'
        )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role_display(self, obj):
        return obj.get_role_display()

    def get_gender_display(self, obj):
        return obj.get_gender_display() if obj.gender else ''

    def get_blood_group_display(self, obj):
        return obj.get_blood_group_display() if obj.blood_group else ''

    def get_house_display(self, obj):
        return obj.get_house_display() if obj.house else ''

    def get_curriculum_display(self, obj):
        return obj.get_primary_curriculum_display() if obj.primary_curriculum else ''

    def get_age(self, obj):
        return obj.age

    def get_years_of_service(self, obj):
        return obj.years_of_service

    def get_profile_completion_percentage(self, obj):
        return obj.profile_completion_percentage

    def get_status(self, obj):
        if obj.is_suspended:
            return 'Suspended'
        elif not obj.is_active:
            return 'Inactive'
        elif not obj.is_verified:
            return 'Unverified'
        elif not obj.is_approved:
            return 'Pending Approval'
        else:
            return 'Active'


# ============================================================================
# SEARCH AND FILTER SERIALIZERS
# ============================================================================

class UserSearchSerializer(serializers.Serializer):
    """Serializer for user search parameters"""
    query = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    is_approved = serializers.BooleanField(required=False)
    profile_completed = serializers.BooleanField(required=False)
    date_joined_start = serializers.DateField(required=False)
    date_joined_end = serializers.DateField(required=False)
    grade_level = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class UserFilterSerializer(serializers.Serializer):
    """Serializer for user filtering"""
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=User.Role.choices),
        required=False
    )
    status = serializers.ChoiceField(
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('suspended', 'Suspended'),
            ('pending', 'Pending Approval')
        ],
        required=False
    )
    profile_completion = serializers.ChoiceField(
        choices=[
            ('complete', 'Complete'),
            ('incomplete', 'Incomplete')
        ],
        required=False
    )
    date_range = serializers.ChoiceField(
        choices=[
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year')
        ],
        required=False
    )
    sort_by = serializers.ChoiceField(
        choices=[
            ('date_joined', 'Date Joined'),
            ('last_login', 'Last Login'),
            ('name', 'Name'),
            ('email', 'Email')
        ],
        default='date_joined'
    )
    sort_order = serializers.ChoiceField(
        choices=[('asc', 'Ascending'), ('desc', 'Descending')],
        default='desc'
    )