# teachers/serializers.py - COMPLETE IMPROVED VERSION

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import re

from .models import (
    Department, TeacherProfile, TeacherDocument, TeacherQualification,
    TeacherTraining, TeacherAssignment, TeacherAttendance, TeacherLeave,
    ProfessionalStanding, PerformanceIndicator, TeacherTransfer
)
from accounts.models import User, GENDER_CHOICES
from academics.models import Subject, Class, AcademicYear, AcademicTerm


# ============================================================================
# VALIDATORS
# ============================================================================

def validate_tsc_number(value):
    """Validate TSC number format"""
    if not value:
        return value
    
    pattern = r'^TSC/\d{5}/\d{4}$'
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            _("Invalid TSC number format. Expected format: TSC/XXXXX/YYYY")
        )
    return value


def validate_kcse_grade(value):
    """Validate KCSE grade format"""
    if not value:
        return value
    
    valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']
    if value not in valid_grades:
        raise serializers.ValidationError(
            _("Invalid KCSE grade. Valid grades are: A, A-, B+, B, B-, C+, C, C-, D+, D, D-, E")
        )
    return value


def validate_phone_number(value):
    """Validate Kenyan phone number"""
    if not value:
        return value
    
    # Clean the number
    value = value.strip().replace(' ', '')
    
    # Check Kenyan formats
    patterns = [
        r'^\+254[17]\d{8}$',  # +2547XXXXXXXX or +2541XXXXXXXX
        r'^0[17]\d{8}$',      # 07XXXXXXXX or 01XXXXXXXX
        r'^254[17]\d{8}$',    # 2547XXXXXXXX or 2541XXXXXXXX
    ]
    
    if not any(re.match(pattern, value) for pattern in patterns):
        raise serializers.ValidationError(
            _("Invalid phone number format. Use +254XXXXXXXXX, 07XXXXXXXX or 01XXXXXXXX")
        )
    return value


def validate_id_number(value):
    """Validate Kenyan ID number"""
    if not value:
        return value
    
    # Remove any whitespace
    value = value.strip()
    
    if not value.isdigit() or len(value) != 8:
        raise serializers.ValidationError(
            _("Invalid ID number. Must be 8 digits.")
        )
    
    # Validate using Kenyan ID algorithm (simple version)
    # First 7 digits for birth date and gender validation
    year_prefix = int(value[:2])
    if year_prefix < 0 or year_prefix > 99:
        raise serializers.ValidationError(_("Invalid ID number year prefix"))
    
    return value


def validate_date_not_future(value):
    """Validate date is not in the future"""
    if value and value > timezone.now().date():
        raise serializers.ValidationError(_("Date cannot be in the future"))
    return value


# ============================================================================
# HELPER FUNCTIONS & SERIALIZERS
# ============================================================================

def get_active_teacherprofiles():
    """Safely get active TeacherProfile queryset"""
    from .models import TeacherProfile  # Import here to avoid circular import
    return TeacherProfile.objects.filter(
        employment_status='active',
        is_active=True
    ).select_related('teacher', 'department')


def get_department_queryset():
    """Get department queryset with prefetching"""
    from .models import Department
    return Department.objects.filter(is_active=True).select_related('hod')


class DepartmentMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Department"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'tsc_category', 'is_active']
        read_only_fields = ['id', 'is_active']


class SubjectMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Subject"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'category', 'is_active']
        read_only_fields = ['id', 'is_active']


class ClassMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Class"""
    
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'grade_level', 'stream', 'stream_name', 'is_active']
        read_only_fields = ['id', 'stream_name', 'is_active']


class UserNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for User model"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 
            'phone_number', 'id_number', 'date_of_birth', 'gender', 
            'nationality', 'is_active'
        ]
        read_only_fields = ['id', 'full_name', 'is_active']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# ============================================================================
# DEPARTMENT SERIALIZERS
# ============================================================================

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    hod = serializers.PrimaryKeyRelatedField(
        queryset=TeacherProfile.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    hod_details = serializers.SerializerMethodField(read_only=True)
    
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    
    academic_year_details = serializers.SerializerMethodField(read_only=True)
    
    teacher_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    subject_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'tsc_category', 'cbc_pathway',
            'hod', 'hod_details', 'location', 'building', 'room_number', 
            'academic_year', 'academic_year_details', 'teacher_count', 
            'student_count', 'subject_count', 'is_active', 'created_at', 
            'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_count', 'student_count', 'subject_count',
            'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset dynamically to avoid circular imports
        from .models import TeacherProfile
        self.fields['hod'].queryset = TeacherProfile.objects.filter(
            employment_status='active',
            is_active=True
        ).select_related('teacher', 'department')
    
    def validate_code(self, value):
        """Validate department code"""
        if not value:
            return value
        
        # Allow more flexible format: ABC-123, ABCD-123, or just ABC123
        pattern = r'^[A-Z]{3,4}([-_])?\d{3}$'
        if not re.match(pattern, value, re.IGNORECASE):
            raise serializers.ValidationError(
                _("Invalid department code format. Expected: ABC-123 or ABC123")
            )
        
        # Convert to uppercase for consistency
        return value.upper()
    
    def validate(self, data):
        """Validate department data"""
        errors = {}
        
        # Check if HOD is assigned to another department
        hod = data.get('hod')
        if hod:
            # Check if this HOD is already assigned to another active department
            existing_dept = Department.objects.filter(
                hod=hod,
                is_active=True
            ).exclude(id=self.instance.id if self.instance else None).first()
            
            if existing_dept:
                errors['hod'] = _(
                    f"This teacher is already the HOD of {existing_dept.name}. "
                    f"Please reassign them first."
                )
            
            # Check if HOD is active
            if not hod.is_active:
                errors['hod'] = _("Selected HOD is not active")
            
            # Check if HOD has active employment status
            if hod.employment_status != 'active':
                errors['hod'] = _("Selected HOD does not have active employment status")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def get_hod_details(self, obj):
        if obj.hod:
            return {
                'id': obj.hod.id,
                'full_name': obj.hod.full_name,
                'tsc_number': obj.hod.tsc_number,
                'email': obj.hod.email,
                'phone_number': obj.hod.phone_number,
                'designation': obj.hod.get_designation_display(),
                'teaching_level': obj.hod.get_teaching_level_display()
            }
        return None
    
    def get_academic_year_details(self, obj):
        if obj.academic_year:
            return {
                'id': obj.academic_year.id,
                'name': str(obj.academic_year),
                'start_date': obj.academic_year.start_date,
                'end_date': obj.academic_year.end_date,
                'is_current': obj.academic_year.is_current
            }
        return None
    
    def to_representation(self, instance):
        """Custom representation to include calculated fields"""
        representation = super().to_representation(instance)
        
        # Add additional computed fields
        representation['teachers'] = instance.teacher_count
        representation['active_teachers'] = instance.teachers.filter(
            is_active=True, 
            employment_status='active'
        ).count()
        
        # Add department statistics
        from academics.models import Subject, Class
        representation['total_subjects'] = Subject.objects.filter(
            department=instance,
            is_active=True
        ).count()
        
        representation['total_classes'] = Class.objects.filter(
            department=instance,
            is_active=True
        ).count()
        
        return representation
    
    def create(self, validated_data):
        """Create department with additional validation"""
        hod = validated_data.get('hod')
        
        if hod:
            # Set HOD's department if not already set
            if hod.department != validated_data.get('department'):
                hod.department = validated_data.get('department')
                hod.is_head_of_department = True
                hod.save()
        
        department = super().create(validated_data)
        
        # Update department statistics cache
        department.refresh_from_db()
        
        return department
    
    def update(self, instance, validated_data):
        """Update department with HOD management"""
        old_hod = instance.hod
        new_hod = validated_data.get('hod')
        
        # Remove HOD flag from old HOD if changing
        if old_hod and old_hod != new_hod:
            old_hod.is_head_of_department = False
            old_hod.save()
        
        # Update new HOD
        if new_hod:
            new_hod.is_head_of_department = True
            new_hod.department = instance
            new_hod.save()
        
        department = super().update(instance, validated_data)
        
        return department

# ============================================================================
# TEACHER PROFILE SERIALIZERS
# ============================================================================

class TeacherProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TeacherProfile (includes User creation)"""
    
    # User fields (required for creation)
    first_name = serializers.CharField(
        max_length=50, 
        required=True,
        help_text="Teacher's first name"
    )
    last_name = serializers.CharField(
        max_length=50, 
        required=True,
        help_text="Teacher's last name"
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_("A user with this email already exists.")
            )
        ]
    )
    phone_number = serializers.CharField(
        max_length=20, 
        required=True,
        validators=[validate_phone_number],
        help_text="Format: +2547XXXXXXXX or 07XXXXXXXX"
    )
    id_number = serializers.CharField(
        max_length=20, 
        required=True,
        validators=[validate_id_number],
        help_text="8-digit Kenyan ID number"
    )
    date_of_birth = serializers.DateField(
        required=True,
        validators=[validate_date_not_future]
    )
    gender = serializers.ChoiceField(
        choices=GENDER_CHOICES,
        required=True
    )
    nationality = serializers.CharField(
        max_length=50, 
        default='Kenyan', 
        required=False
    )
    
    # TSC validation
    tsc_number = serializers.CharField(
        max_length=20,
        required=True,
        validators=[
            validate_tsc_number,
            UniqueValidator(
                queryset=TeacherProfile.objects.all(),
                message=_("A teacher with this TSC number already exists.")
            )
        ],
        help_text="Format: TSC/XXXXX/YYYY"
    )
    
    # KCSE validation
    kcse_mean_grade = serializers.CharField(
        max_length=5, 
        required=True,
        validators=[validate_kcse_grade]
    )
    
    # Department
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=get_department_queryset(),
        source='department',
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = TeacherProfile
        fields = [
            # User fields
            'first_name', 'last_name', 'email', 'phone_number', 'id_number',
            'date_of_birth', 'gender', 'nationality',
            
            # Teacher fields
            'tsc_number', 'tsc_registration_date', 'tsc_status', 'tsc_category',
            'tsc_payroll_number', 'highest_qualification', 'qualification_institution',
            'year_of_graduation', 'kcse_mean_grade', 'kcse_index_number',
            'kcse_year', 'teaching_subjects', 'employment_type', 'employment_status',
            'teaching_level', 'department_id', 'designation', 'cbc_trained',
            'cbc_training_date', 'cbc_training_level', 'teacher_registration_number',
            'knec_registration_number', 'sacco_name', 'sacco_number', 'blood_group',
            'bank_name', 'bank_account_number', 'bank_branch', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship', 'tpd_current_module',
            'tpd_last_completed_date', 'tpd_next_renewal_date', 'tpd_license_number',
            'employment_date', 'confirmation_date', 'retirement_date', 'last_promotion_date',
            'weekly_periods', 'teaching_load_hours', 'performance_rating',
            'last_appraisal_date', 'next_appraisal_date', 'appraisal_score',
            'salary_scale', 'basic_salary', 'house_allowance', 'commuter_allowance',
            'is_class_teacher', 'is_head_of_department', 'is_deputy_principal',
            'is_principal', 'is_curriculum_coordinator', 'is_guidance_counselor',
            'is_games_master', 'notes', 'achievements'
        ]
    
    def validate(self, data):
        """Validate teacher profile data"""
        errors = {}
        
        # Validate dates
        employment_date = data.get('employment_date')
        if employment_date:
            validate_date_not_future(employment_date)
        
        tsc_registration_date = data.get('tsc_registration_date')
        if tsc_registration_date:
            validate_date_not_future(tsc_registration_date)
        
        # Validate KCSE year
        kcse_year = data.get('kcse_year')
        if kcse_year:
            current_year = timezone.now().year
            if kcse_year < 1989 or kcse_year > current_year:
                errors['kcse_year'] = _("KCSE year must be between 1989 and current year")
        
        # Validate graduation year
        year_of_graduation = data.get('year_of_graduation')
        if year_of_graduation:
            current_year = timezone.now().year
            if year_of_graduation < 1970 or year_of_graduation > current_year:
                errors['year_of_graduation'] = _("Graduation year must be between 1970 and current year")
        
        # Validate TPD dates
        tpd_last_completed_date = data.get('tpd_last_completed_date')
        tpd_next_renewal_date = data.get('tpd_next_renewal_date')
        
        if tpd_last_completed_date and tpd_next_renewal_date:
            if tpd_next_renewal_date <= tpd_last_completed_date:
                errors['tpd_next_renewal_date'] = _("TPD renewal date must be after completion date")
            
            # Check if renewal is within 5 years
            days_diff = (tpd_next_renewal_date - tpd_last_completed_date).days
            years_diff = days_diff / 365.25
            if years_diff > 5:
                errors['tpd_next_renewal_date'] = _("TPD renewal should be within 5 years of completion")
        
        # Validate CBC training for Junior Secondary teachers
        teaching_level = data.get('teaching_level')
        cbc_trained = data.get('cbc_trained', False)
        
        if teaching_level == 'junior_secondary' and not cbc_trained:
            errors['cbc_trained'] = _("Junior Secondary teachers must be CBC trained")
        
        # Validate salary fields
        basic_salary = data.get('basic_salary')
        if basic_salary is not None and basic_salary < 0:
            errors['basic_salary'] = _("Basic salary cannot be negative")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create User and TeacherProfile with transaction"""
        # Extract User data
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone_number': validated_data.pop('phone_number'),
            'id_number': validated_data.pop('id_number'),
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'nationality': validated_data.pop('nationality', 'Kenyan'),
        }
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(**user_data)
                # Generate temporary password (user should reset on first login)
                temp_password = f"{user.id}@Teach{timezone.now().year}!"
                user.set_password(temp_password)
                user.role = User.Role.TEACHER
                user.is_active = True  # Activate immediately or based on school policy
                user.save()
                
                # Create TeacherProfile
                teacher_profile = TeacherProfile.objects.create(
                    teacher=user,
                    **validated_data
                )
                
                return teacher_profile
                
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': _("Failed to create teacher profile. Error: {}").format(str(e))
            })


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for TeacherProfile (read and update)"""
    
    teacher = UserNestedSerializer(read_only=True)
    
    department = DepartmentMinimalSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=get_department_queryset(),
        source='department',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Many-to-many relationships
    subjects = SubjectMinimalSerializer(many=True, read_only=True)
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.filter(is_active=True),
        source='subjects',
        many=True,
        write_only=True,
        required=False
    )
    
    classes = ClassMinimalSerializer(many=True, read_only=True)
    class_ids = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.filter(is_active=True),
        source='classes',
        many=True,
        write_only=True,
        required=False
    )
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    years_of_service = serializers.SerializerMethodField()
    tsc_compliant = serializers.BooleanField(read_only=True)
    total_salary = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    workload_percentage = serializers.SerializerMethodField()
    workload_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'teacher', 'full_name', 'email', 'phone_number', 'age',
            'tsc_number', 'tsc_registration_date', 'tsc_status', 'tsc_category',
            'tsc_payroll_number', 'highest_qualification', 'qualification_institution',
            'year_of_graduation', 'kcse_mean_grade', 'kcse_index_number',
            'kcse_year', 'teaching_subjects', 'employment_type', 'employment_status',
            'teaching_level', 'department', 'department_id', 'designation',
            'cbc_trained', 'cbc_training_date', 'cbc_training_level',
            'teacher_registration_number', 'knec_registration_number',
            'sacco_name', 'sacco_number', 'blood_group', 'bank_name',
            'bank_account_number', 'bank_branch', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'tpd_current_module', 'tpd_last_completed_date', 'tpd_next_renewal_date',
            'tpd_license_number', 'employment_date', 'confirmation_date',
            'retirement_date', 'last_promotion_date', 'weekly_periods',
            'teaching_load_hours', 'performance_rating', 'last_appraisal_date',
            'next_appraisal_date', 'appraisal_score', 'salary_scale',
            'basic_salary', 'house_allowance', 'commuter_allowance',
            'total_salary', 'subjects', 'subject_ids', 'classes', 'class_ids',
            'is_class_teacher', 'is_head_of_department', 'is_deputy_principal',
            'is_principal', 'is_curriculum_coordinator', 'is_guidance_counselor',
            'is_games_master', 'years_of_service', 'tsc_compliant', 
            'workload_percentage', 'workload_status', 'notes', 'achievements', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher', 'full_name', 'email', 'phone_number', 'age',
            'years_of_service', 'tsc_compliant', 'total_salary', 
            'workload_percentage', 'workload_status', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_email(self, obj):
        return obj.email
    
    def get_phone_number(self, obj):
        return obj.phone_number
    
    def get_years_of_service(self, obj):
        return obj.years_of_service
    
    def get_workload_percentage(self, obj):
        return obj.workload_percentage
    
    def get_workload_status(self, obj):
        percentage = obj.workload_percentage
        if percentage == 0:
            return 'unassigned'
        elif percentage < 50:
            return 'underloaded'
        elif percentage <= 100:
            return 'optimal'
        elif percentage <= 120:
            return 'high'
        else:
            return 'overloaded'
    
    def validate_tsc_number(self, value):
        """Validate TSC number on update"""
        if self.instance and self.instance.tsc_number != value:
            raise serializers.ValidationError(
                _("TSC number cannot be changed after creation")
            )
        return validate_tsc_number(value)
    
    def validate(self, data):
        """Validate teacher profile on update"""
        errors = {}
        
        # Check role consistency
        is_principal = data.get('is_principal', False)
        is_deputy_principal = data.get('is_deputy_principal', False)
        is_head_of_department = data.get('is_head_of_department', False)
        
        # Ensure only one main role is set
        if sum([is_principal, is_deputy_principal, is_head_of_department]) > 1:
            errors['non_field_errors'] = _(
                "A teacher can only have one primary role (Principal, Deputy Principal, or Head of Department)"
            )
        
        # Validate workload
        weekly_periods = data.get('weekly_periods')
        if weekly_periods is not None and weekly_periods < 0:
            errors['weekly_periods'] = _("Weekly periods cannot be negative")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def update(self, instance, validated_data):
        """Update teacher profile with role handling"""
        # Handle many-to-many updates
        subjects = validated_data.pop('subjects', None)
        classes = validated_data.pop('classes', None)
        
        # Update the instance
        teacher_profile = super().update(instance, validated_data)
        
        # Update many-to-many relationships
        if subjects is not None:
            teacher_profile.subjects.set(subjects)
        
        if classes is not None:
            teacher_profile.classes.set(classes)
        
        # Update user role based on teacher profile
        user = teacher_profile.teacher
        
        if teacher_profile.is_principal:
            user.role = User.Role.HEAD_TEACHER
        elif teacher_profile.is_deputy_principal:
            user.role = User.Role.DEPUTY_HEAD_TEACHER
        elif teacher_profile.is_head_of_department:
            user.role = User.Role.CURRICULUM_COORDINATOR
        else:
            user.role = User.Role.TEACHER
        
        user.save()
        
        return teacher_profile


class TeacherProfileMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for TeacherProfile"""
    
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherProfile
        fields = ['id', 'full_name', 'tsc_number', 'email', 'phone_number', 
                 'designation', 'department', 'is_active']
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_email(self, obj):
        return obj.email
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.department:
            representation['department'] = {
                'id': instance.department.id,
                'name': instance.department.name,
                'code': instance.department.code
            }
        
        return representation


class TeacherProfileSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for TeacherProfile (for lists)"""
    
    full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    tsc_status_display = serializers.SerializerMethodField()
    employment_status_display = serializers.SerializerMethodField()
    workload_percentage = serializers.SerializerMethodField()
    workload_status = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'full_name', 'tsc_number', 'department_name',
            'designation', 'teaching_level', 'tsc_status', 'tsc_status_display',
            'employment_status', 'employment_status_display', 'cbc_trained',
            'weekly_periods', 'workload_percentage', 'workload_status',
            'years_of_service', 'is_active', 'created_at'
        ]
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_tsc_status_display(self, obj):
        return obj.get_tsc_status_display()
    
    def get_employment_status_display(self, obj):
        return obj.get_employment_status_display()
    
    def get_workload_percentage(self, obj):
        return obj.workload_percentage
    
    def get_workload_status(self, obj):
        return obj.workload_status
    
    def get_years_of_service(self, obj):
        return obj.years_of_service


class TeacherProfileStatsSerializer(serializers.Serializer):
    """Serializer for teacher statistics"""
    
    total_teachers = serializers.IntegerField()
    active_teachers = serializers.IntegerField()
    inactive_teachers = serializers.IntegerField()
    male_teachers = serializers.IntegerField()
    female_teachers = serializers.IntegerField()
    tsc_compliant = serializers.IntegerField()
    cbc_trained = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    by_department = serializers.DictField(child=serializers.IntegerField())
    by_teaching_level = serializers.DictField(child=serializers.IntegerField())
    by_employment_type = serializers.DictField(child=serializers.IntegerField())
    workload_distribution = serializers.DictField(child=serializers.IntegerField())


# ============================================================================
# TEACHER DOCUMENT SERIALIZERS
# ============================================================================

class TeacherDocumentSerializer(serializers.ModelSerializer):
    """Serializer for TeacherDocument model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    verified_by = UserNestedSerializer(read_only=True)
    verified_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='verified_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)
    expiry_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherDocument
        fields = [
            'id', 'teacher', 'teacher_id', 'document_type', 'title', 'description',
            'document_file', 'file_url', 'file_name', 'file_extension', 'file_size',
            'file_size_mb', 'upload_date', 'expiry_date', 'status', 'verified_by', 
            'verified_by_id', 'verification_date', 'verification_notes', 
            'is_required', 'is_archived', 'is_expired', 'days_to_expiry', 
            'expiry_status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'upload_date', 'verification_date', 'is_expired',
            'days_to_expiry', 'created_at', 'updated_at'
        ]
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and request:
            return request.build_absolute_uri(obj.document_file.url)
        return None
    
    def get_file_name(self, obj):
        if obj.document_file:
            return obj.document_file.name.split('/')[-1]
        return None
    
    def get_file_extension(self, obj):
        return obj.file_extension
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0
    
    def get_expiry_status(self, obj):
        if not obj.expiry_date:
            return 'no_expiry'
        
        today = timezone.now().date()
        days_to_expiry = (obj.expiry_date - today).days
        
        if days_to_expiry < 0:
            return 'expired'
        elif days_to_expiry <= 30:
            return 'expiring_soon'
        elif days_to_expiry <= 90:
            return 'expiring'
        else:
            return 'valid'
    
    def validate(self, data):
        """Validate document data"""
        errors = {}
        
        # Check file size (max 10MB)
        document_file = data.get('document_file')
        if document_file and document_file.size > 10 * 1024 * 1024:
            errors['document_file'] = _("File size cannot exceed 10MB")
        
        # Validate expiry date
        expiry_date = data.get('expiry_date')
        if expiry_date:
            if expiry_date < timezone.now().date():
                if data.get('status') != 'expired':
                    errors['expiry_date'] = _("Document has expired. Please update status to 'Expired'")
            else:
                # Auto-set status to active for future expiry dates
                if not data.get('status'):
                    data['status'] = 'active'
        
        # Validate required documents
        document_type = data.get('document_type')
        teacher = data.get('teacher')
        
        if document_type and teacher:
            # Check if required document already exists
            if document_type in ['id_copy', 'tsc_certificate', 'kcpe_certificate', 
                               'degree_certificate', 'cbc_certificate']:
                existing_doc = TeacherDocument.objects.filter(
                    teacher=teacher,
                    document_type=document_type,
                    is_active=True
                ).exists()
                
                if existing_doc and not self.instance:
                    errors['document_type'] = _(
                        f"A {document_type} already exists for this teacher."
                    )
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

class BulkTeacherCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating TeacherProfiles from a list"""
    
    teachers = TeacherProfileCreateSerializer(many=True)
    
    def create(self, validated_data):
        """Create multiple TeacherProfiles"""
        teachers_data = validated_data.get('teachers', [])
        created_teachers = []
        errors = []
        
        for index, teacher_data in enumerate(teachers_data):
            serializer = TeacherProfileCreateSerializer(data=teacher_data)
            if serializer.is_valid():
                try:
                    teacher_profile = serializer.save()
                    created_teachers.append(teacher_profile)
                except Exception as e:
                    errors.append({
                        'index': index,
                        'errors': str(e)
                    })
            else:
                errors.append({
                    'index': index,
                    'errors': serializer.errors
                })
        
        if errors:
            raise serializers.ValidationError({
                'non_field_errors': _("Some teacher profiles could not be created."),
                'details': errors
            })
        
        return created_teachers
# ============================================================================
# TEACHER QUALIFICATION SERIALIZERS
# ============================================================================

class TeacherQualificationSerializer(serializers.ModelSerializer):
    """Serializer for TeacherQualification model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    verified_by = UserNestedSerializer(read_only=True)
    verified_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='verified_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    document = TeacherDocumentSerializer(read_only=True)
    document_id = serializers.PrimaryKeyRelatedField(
        queryset=TeacherDocument.objects.filter(is_active=True),
        source='document',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    duration_years = serializers.FloatField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    qualification_level = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherQualification
        fields = [
            'id', 'teacher', 'teacher_id', 'qualification_type', 'title',
            'institution', 'institution_location', 'field_of_study',
            'grade_classification', 'start_date', 'end_date', 'completion_date',
            'is_completed', 'certificate_number', 'verification_status',
            'verified_by', 'verified_by_id', 'verification_date',
            'verification_notes', 'document', 'document_id', 'duration_years',
            'qualification_level', 'is_current', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration_years', 'qualification_level', 'is_current', 
            'created_at', 'updated_at'
        ]
    
    def get_qualification_level(self, obj):
        """Map qualification to education level"""
        qualification_map = {
            'phd': 'post_graduate',
            'masters': 'post_graduate',
            'postgraduate_diploma': 'post_graduate',
            'bachelors': 'university',
            'diploma': 'college',
            'certificate': 'college',
            'kcse': 'secondary',
            'kcpe': 'primary',
        }
        return qualification_map.get(obj.qualification_type, 'other')
    
    def validate(self, data):
        """Validate qualification dates"""
        errors = {}
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        completion_date = data.get('completion_date')
        
        if start_date and end_date:
            if start_date > end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            if completion_date:
                if completion_date < start_date:
                    errors['completion_date'] = _("Completion date cannot be before start date")
                if completion_date > end_date:
                    errors['completion_date'] = _("Completion date cannot be after end date")
        
        return data


# ============================================================================
# TEACHER TRAINING SERIALIZERS
# ============================================================================

class TeacherTrainingSerializer(serializers.ModelSerializer):
    """Serializer for TeacherTraining model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    document = TeacherDocumentSerializer(read_only=True)
    document_id = serializers.PrimaryKeyRelatedField(
        queryset=TeacherDocument.objects.filter(is_active=True),
        source='document',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    certificate_expiry_date = serializers.DateField(read_only=True)
    is_certificate_valid = serializers.BooleanField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TeacherTraining
        fields = [
            'id', 'teacher', 'teacher_id', 'training_type', 'title', 'description',
            'organizer', 'training_mode', 'start_date', 'end_date', 'duration_hours',
            'is_mandatory', 'is_certified', 'certificate_number',
            'certificate_issued_date', 'certificate_validity_years',
            'certificate_expiry_date', 'is_certificate_valid', 'days_to_expiry',
            'assessment_score', 'feedback', 'status', 'document', 'document_id', 
            'is_current', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'certificate_expiry_date', 'is_certificate_valid', 
            'days_to_expiry', 'is_current', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate training dates"""
        errors = {}
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if training is in the future
            if start_date > timezone.now().date() and data.get('status') == 'completed':
                errors['status'] = _("Cannot mark training as completed before it starts")
        
        return data


# ============================================================================
# TEACHER ASSIGNMENT SERIALIZERS
# ============================================================================

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TeacherAssignment model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    academic_year_details = serializers.SerializerMethodField(read_only=True)
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        write_only=True
    )
    
    term_details = serializers.SerializerMethodField(read_only=True)
    term = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    subject = SubjectMinimalSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.filter(is_active=True),
        source='subject',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class_assigned = ClassMinimalSerializer(read_only=True)
    class_assigned_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.filter(is_active=True),
        source='class_assigned',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    stream_details = serializers.SerializerMethodField(read_only=True)
    stream = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    approved_by = UserNestedSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Computed fields
    duration_weeks = serializers.IntegerField(read_only=True)
    workload_hours = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    adjusted_workload_hours = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_active_assignment = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'teacher', 'teacher_id', 'assignment_type', 'title', 'description',
            'academic_year', 'academic_year_details', 'term', 'term_details',
            'subject', 'subject_id', 'class_assigned', 'class_assigned_id', 
            'stream', 'stream_details', 'start_date', 'end_date', 'weekly_periods',
            'is_active_assignment', 'is_primary_assignment', 'workload_factor', 
            'duration_weeks', 'workload_hours', 'adjusted_workload_hours', 'notes', 
            'approved_by', 'approved_by_id', 'approval_date', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration_weeks', 'workload_hours', 'adjusted_workload_hours',
            'is_active_assignment', 'created_at', 'updated_at'
        ]
    
    def get_academic_year_details(self, obj):
        if obj.academic_year:
            return {
                'id': obj.academic_year.id,
                'name': str(obj.academic_year),
                'start_date': obj.academic_year.start_date,
                'end_date': obj.academic_year.end_date
            }
        return None
    
    def get_term_details(self, obj):
        if obj.term:
            return {
                'id': obj.term.id,
                'name': str(obj.term),
                'start_date': obj.term.start_date,
                'end_date': obj.term.end_date
            }
        return None
    
    def get_stream_details(self, obj):
        if obj.stream:
            return {
                'id': obj.stream.id,
                'name': obj.stream.name,
                'code': obj.stream.code
            }
        return None
    
    def validate(self, data):
        """Validate assignment details"""
        errors = {}
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        academic_year = data.get('academic_year')
        
        if start_date and end_date:
            if start_date > end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if assignment overlaps with academic year
            if academic_year:
                if start_date < academic_year.start_date:
                    errors['start_date'] = _("Assignment cannot start before academic year")
                if end_date > academic_year.end_date:
                    errors['end_date'] = _("Assignment cannot end after academic year")
        
        # Validate teaching assignment requirements
        if data.get('assignment_type') == 'teaching':
            if not data.get('subject'):
                errors['subject'] = _("Teaching assignment requires a subject")
            if not data.get('class_assigned'):
                errors['class_assigned'] = _("Teaching assignment requires a class")
        
        # Validate workload factor
        workload_factor = data.get('workload_factor', 1.0)
        if workload_factor < 0.5 or workload_factor > 2.0:
            errors['workload_factor'] = _("Workload factor must be between 0.5 and 2.0")
        
        return data


# ============================================================================
# TEACHER ATTENDANCE SERIALIZERS
# ============================================================================

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for TeacherAttendance model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    verified_by = UserNestedSerializer(read_only=True)
    verified_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='verified_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Computed fields
    is_full_day = serializers.BooleanField(read_only=True)
    is_absent = serializers.BooleanField(read_only=True)
    attendance_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherAttendance
        fields = [
            'id', 'teacher', 'teacher_id', 'date', 'check_in_time', 'check_out_time',
            'status', 'is_late', 'late_minutes', 'is_early_departure',
            'early_departure_minutes', 'working_hours', 'is_full_day', 'is_absent',
            'attendance_status', 'notes', 'verified_by', 'verified_by_id', 
            'verification_time', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_full_day', 'is_absent', 'attendance_status', 
            'created_at', 'updated_at'
        ]
    
    def get_attendance_status(self, obj):
        """Get detailed attendance status"""
        if obj.status == 'present':
            if obj.is_late:
                return 'late'
            elif obj.is_early_departure:
                return 'left_early'
            else:
                return 'present'
        elif obj.status == 'absent':
            return 'absent'
        elif obj.status == 'leave':
            return 'on_leave'
        else:
            return obj.status
    
    def validate(self, data):
        """Validate attendance data"""
        errors = {}
        
        date = data.get('date')
        check_in_time = data.get('check_in_time')
        check_out_time = data.get('check_out_time')
        
        # Check if date is in the future
        if date and date > timezone.now().date():
            errors['date'] = _("Attendance date cannot be in the future")
        
        # Check if check-out is before check-in
        if check_in_time and check_out_time:
            if check_out_time <= check_in_time:
                errors['check_out_time'] = _("Check-out time must be after check-in time")
        
        return data


class TeacherAttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary"""
    
    date = serializers.DateField()
    status = serializers.CharField()
    check_in = serializers.TimeField(allow_null=True)
    check_out = serializers.TimeField(allow_null=True)
    working_hours = serializers.FloatField()
    is_late = serializers.BooleanField()
    late_minutes = serializers.IntegerField()
    is_early_departure = serializers.BooleanField()
    early_departure_minutes = serializers.IntegerField()
    is_full_day = serializers.BooleanField()


# ============================================================================
# TEACHER LEAVE SERIALIZERS
# ============================================================================

class TeacherLeaveSerializer(serializers.ModelSerializer):
    """Serializer for TeacherLeave model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    approved_by = UserNestedSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    rejected_by = UserNestedSerializer(read_only=True)
    rejected_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='rejected_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    cover_teacher = TeacherProfileMinimalSerializer(read_only=True)
    cover_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='cover_teacher',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Computed fields
    is_current = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    leave_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherLeave
        fields = [
            'id', 'teacher', 'teacher_id', 'leave_type', 'start_date', 'end_date',
            'days_requested', 'reason', 'contact_address', 'contact_phone',
            'emergency_contact', 'status', 'applied_date', 'approved_by',
            'approved_by_id', 'approval_date', 'approval_notes', 'rejected_by',
            'rejected_by_id', 'rejection_date', 'rejection_reason', 'documents',
            'cover_teacher', 'cover_teacher_id', 'handover_notes', 'is_current',
            'days_remaining', 'leave_status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_current', 'days_remaining', 'leave_status', 
            'applied_date', 'created_at', 'updated_at'
        ]
    
    def get_leave_status(self, obj):
        """Get detailed leave status"""
        today = timezone.now().date()
        
        if obj.status == 'approved':
            if today < obj.start_date:
                return 'upcoming'
            elif today > obj.end_date:
                return 'completed'
            else:
                return 'in_progress'
        return obj.status
    
    def validate(self, data):
        """Validate leave application"""
        errors = {}
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        leave_type = data.get('leave_type')
        teacher = data.get('teacher')
        
        if start_date and end_date:
            if start_date > end_date:
                errors['start_date'] = _("Start date cannot be after end date")
                errors['end_date'] = _("End date cannot be before start date")
            
            # Check if leave is in the past (allow for backdated sick leave)
            if leave_type != 'sick' and start_date < timezone.now().date():
                if data.get('status') not in ['completed', 'in_progress']:
                    errors['start_date'] = _("Cannot apply for leave in the past")
            
            # Calculate days requested
            days = (end_date - start_date).days + 1
            data['days_requested'] = days
        
        # Validate leave type constraints
        if leave_type == 'maternity':
            if teacher and teacher.teacher.gender != 'female':
                errors['leave_type'] = _("Maternity leave is only for female teachers")
            if data.get('days_requested', 0) > 90:
                errors['days_requested'] = _("Maternity leave cannot exceed 90 days")
        
        elif leave_type == 'paternity':
            if teacher and teacher.teacher.gender != 'male':
                errors['leave_type'] = _("Paternity leave is only for male teachers")
            if data.get('days_requested', 0) > 14:
                errors['days_requested'] = _("Paternity leave cannot exceed 14 days")
        
        elif leave_type == 'sick':
            if data.get('days_requested', 0) > 30:
                errors['days_requested'] = _("Sick leave without medical certificate cannot exceed 30 days")
        
        elif leave_type == 'annual':
            if data.get('days_requested', 0) > 30:
                errors['days_requested'] = _("Annual leave cannot exceed 30 days at once")
        
        return data


class TeacherLeaveSummarySerializer(serializers.Serializer):
    """Serializer for leave summary"""
    
    teacher = serializers.CharField()
    leave_type = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    days_requested = serializers.IntegerField()
    status = serializers.CharField()
    is_current = serializers.BooleanField()
    days_remaining = serializers.IntegerField()
    approved_by = serializers.CharField(allow_null=True)
    approval_date = serializers.DateField(allow_null=True)


# ============================================================================
# PROFESSIONAL STANDING SERIALIZERS
# ============================================================================

class ProfessionalStandingSerializer(serializers.ModelSerializer):
    """Serializer for ProfessionalStanding model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    issued_by = UserNestedSerializer(read_only=True)
    issued_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='issued_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    document_url = serializers.SerializerMethodField()
    record_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfessionalStanding
        fields = [
            'id', 'teacher', 'teacher_id', 'record_type', 'record_type_display',
            'date', 'description', 'reference_number', 'issued_by', 'issued_by_id', 
            'status', 'status_display', 'resolution_date', 'resolution_notes', 
            'document', 'document_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document and request:
            return request.build_absolute_uri(obj.document.url)
        return None
    
    def get_record_type_display(self, obj):
        return obj.get_record_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()


# ============================================================================
# PERFORMANCE INDICATOR SERIALIZERS
# ============================================================================

class PerformanceIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceIndicator model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    academic_year_details = serializers.SerializerMethodField()
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        write_only=True
    )
    
    term_details = serializers.SerializerMethodField()
    term = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    evaluator = UserNestedSerializer(read_only=True)
    evaluator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='evaluator',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Computed score averages
    professional_conduct_score = serializers.SerializerMethodField()
    student_engagement_score = serializers.SerializerMethodField()
    professional_development_score = serializers.SerializerMethodField()
    overall_performance = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceIndicator
        fields = [
            'id', 'teacher', 'teacher_id', 'academic_year', 'academic_year_details',
            'term', 'term_details', 'student_performance_average', 
            'completion_rate', 'improvement_rate', 'punctuality_score', 
            'lesson_preparation_score', 'record_keeping_score',
            'professional_conduct_score', 'student_engagement_score',
            'parent_satisfaction_score', 'professional_development_score',
            'pd_completion_score', 'innovation_score', 'overall_score',
            'overall_performance', 'evaluator', 'evaluator_id', 
            'evaluation_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'professional_conduct_score', 'student_engagement_score',
            'professional_development_score', 'overall_performance',
            'created_at', 'updated_at'
        ]
    
    def get_academic_year_details(self, obj):
        if obj.academic_year:
            return {
                'id': obj.academic_year.id,
                'name': str(obj.academic_year),
                'start_date': obj.academic_year.start_date,
                'end_date': obj.academic_year.end_date
            }
        return None
    
    def get_term_details(self, obj):
        if obj.term:
            return {
                'id': obj.term.id,
                'name': str(obj.term),
                'start_date': obj.term.start_date,
                'end_date': obj.term.end_date
            }
        return None
    
    def get_professional_conduct_score(self, obj):
        scores = [obj.punctuality_score, obj.lesson_preparation_score, obj.record_keeping_score]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    def get_student_engagement_score(self, obj):
        scores = [obj.student_engagement_score, obj.parent_satisfaction_score]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    def get_professional_development_score(self, obj):
        scores = [obj.pd_completion_score, obj.innovation_score]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    def get_overall_performance(self, obj):
        """Get performance category based on overall score"""
        if obj.overall_score is None:
            return 'not_evaluated'
        elif obj.overall_score >= 4.5:
            return 'excellent'
        elif obj.overall_score >= 4.0:
            return 'very_good'
        elif obj.overall_score >= 3.0:
            return 'good'
        elif obj.overall_score >= 2.0:
            return 'satisfactory'
        else:
            return 'needs_improvement'
    
    def validate(self, data):
        """Validate performance scores"""
        errors = {}
        
        # Validate scores are between 0 and 5
        score_fields = [
            'student_performance_average', 'completion_rate', 'improvement_rate',
            'punctuality_score', 'lesson_preparation_score', 'record_keeping_score',
            'student_engagement_score', 'parent_satisfaction_score',
            'pd_completion_score', 'innovation_score', 'overall_score'
        ]
        
        for field in score_fields:
            score = data.get(field)
            if score is not None and (score < 0 or score > 5):
                errors[field] = _("Score must be between 0 and 5")
        
        # Validate completion rate and improvement rate
        completion_rate = data.get('completion_rate')
        if completion_rate is not None and (completion_rate < 0 or completion_rate > 100):
            errors['completion_rate'] = _("Completion rate must be between 0 and 100")
        
        improvement_rate = data.get('improvement_rate')
        if improvement_rate is not None and (improvement_rate < -100 or improvement_rate > 100):
            errors['improvement_rate'] = _("Improvement rate must be between -100 and 100")
        
        return data


# ============================================================================
# TEACHER TRANSFER SERIALIZERS
# ============================================================================

try:
    from administration.models import School
    SCHOOL_MODEL_EXISTS = True
except ImportError:
    SCHOOL_MODEL_EXISTS = False
    School = None


class SchoolMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for School"""
    
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'county', 'school_type'] if SCHOOL_MODEL_EXISTS else []


class TeacherTransferSerializer(serializers.ModelSerializer):
    """Serializer for TeacherTransfer model"""
    
    teacher = TeacherProfileMinimalSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=get_active_teacherprofiles(),
        source='teacher',
        write_only=True
    )
    
    from_school = SchoolMinimalSerializer(read_only=True) if SCHOOL_MODEL_EXISTS else serializers.DictField(read_only=True)
    from_school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all() if SCHOOL_MODEL_EXISTS else [],
        source='from_school',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    to_school = SchoolMinimalSerializer(read_only=True) if SCHOOL_MODEL_EXISTS else serializers.DictField(read_only=True)
    to_school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all() if SCHOOL_MODEL_EXISTS else [],
        source='to_school',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    approved_by_sending = UserNestedSerializer(read_only=True)
    approved_by_sending_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by_sending',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    approved_by_receiving = UserNestedSerializer(read_only=True)
    approved_by_receiving_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by_receiving',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    approved_by_tsc = UserNestedSerializer(read_only=True)
    approved_by_tsc_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='approved_by_tsc',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    transfer_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherTransfer
        fields = [
            'id', 'teacher', 'teacher_id', 'transfer_type', 'from_school',
            'from_school_id', 'to_school', 'to_school_id', 'effective_date',
            'reason', 'applied_date', 'approved_by_sending', 'approved_by_sending_id',
            'approved_by_receiving', 'approved_by_receiving_id', 'approved_by_tsc',
            'approved_by_tsc_id', 'handover_completed', 'handover_date',
            'handover_notes', 'status', 'transfer_status', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_date', 'transfer_status', 'created_at', 'updated_at']
    
    def get_transfer_status(self, obj):
        """Get detailed transfer status"""
        today = timezone.now().date()
        
        if obj.status == 'approved':
            if obj.effective_date and today < obj.effective_date:
                return 'pending_effective_date'
            elif obj.effective_date and today >= obj.effective_date:
                return 'effective'
            else:
                return 'approved_pending_date'
        return obj.status


# ============================================================================
# COMPOSITE SERIALIZERS (FOR COMPREHENSIVE VIEWS)
# ============================================================================

class TeacherProfileDetailSerializer(TeacherProfileSerializer):
    """Detailed serializer for TeacherProfile with all related data"""
    
    qualifications = TeacherQualificationSerializer(many=True, read_only=True)
    documents = TeacherDocumentSerializer(many=True, read_only=True)
    trainings = TeacherTrainingSerializer(many=True, read_only=True)
    assignments = TeacherAssignmentSerializer(many=True, read_only=True)
    attendance_records = TeacherAttendanceSerializer(many=True, read_only=True)
    leave_applications = TeacherLeaveSerializer(many=True, read_only=True)
    professional_standings = ProfessionalStandingSerializer(many=True, read_only=True)
    performance_indicators = PerformanceIndicatorSerializer(many=True, read_only=True)
    transfers = TeacherTransferSerializer(many=True, read_only=True)
    
    class Meta(TeacherProfileSerializer.Meta):
        fields = TeacherProfileSerializer.Meta.fields + [
            'qualifications', 'documents', 'trainings', 'assignments',
            'attendance_records', 'leave_applications', 'professional_standings',
            'performance_indicators', 'transfers'
        ]


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class TeacherBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk teacher creation"""
    
    teachers = TeacherProfileCreateSerializer(many=True)
    
    def create(self, validated_data):
        teachers_data = validated_data.pop('teachers')
        created_teachers = []
        
        for teacher_data in teachers_data:
            serializer = TeacherProfileCreateSerializer(data=teacher_data)
            if serializer.is_valid():
                teacher = serializer.save()
                created_teachers.append(teacher)
            else:
                raise serializers.ValidationError({
                    'errors': serializer.errors
                })
        
        return {'created': len(created_teachers), 'teachers': created_teachers}


class TeacherBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk teacher updates"""
    
    teacher_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    updates = serializers.DictField()
    
    def validate(self, data):
        teacher_ids = data['teacher_ids']
        updates = data['updates']
        
        # Check all teachers exist and are active
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids, is_active=True)
        if len(teachers) != len(teacher_ids):
            raise serializers.ValidationError({
                'teacher_ids': _("One or more teachers not found or inactive")
            })
        
        # Validate updates with a sample teacher
        sample_teacher = teachers.first()
        serializer = TeacherProfileSerializer(
            instance=sample_teacher,
            data=updates,
            partial=True,
            context=self.context
        )
        if not serializer.is_valid():
            raise serializers.ValidationError({
                'updates': serializer.errors
            })
        
        data['teachers'] = teachers
        return data


class TeacherBulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk teacher deletion"""
    
    teacher_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_teacher_ids(self, value):
        # Check all teachers exist and are active
        teachers = TeacherProfile.objects.filter(id__in=value, is_active=True)
        if len(teachers) != len(value):
            raise serializers.ValidationError(_("One or more teachers not found or inactive"))
        return value
class TeacherBulkActivateSerializer(serializers.Serializer):
    """Serializer for bulk teacher activation"""
    
    teacher_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_teacher_ids(self, value):
        # Check all teachers exist and are inactive
        teachers = TeacherProfile.objects.filter(id__in=value, is_active=False)
        if len(teachers) != len(value):
            raise serializers.ValidationError(_("One or more teachers not found or already active"))
        return value
class TeacherBulkDeactivateSerializer(serializers.Serializer):
    """Serializer for bulk teacher deactivation"""
    
    teacher_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_teacher_ids(self, value):
        # Check all teachers exist and are active
        teachers = TeacherProfile.objects.filter(id__in=value, is_active=True)
        if len(teachers) != len(value):
            raise serializers.ValidationError(_("One or more teachers not found or already inactive"))
        return value


class BulkAssignmentUpdateSerializer(serializers.Serializer):   
    """Serializer for bulk updating teacher assignments"""
    
    assignment_updates = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_assignment_updates(self, value):
        errors = []
        for index, record in enumerate(value):
            serializer = TeacherAssignmentSerializer(data=record)
            if not serializer.is_valid():
                errors.append({ 'index': index, 'errors': serializer.errors })
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return value
    

class BulkAttendanceUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating teacher attendance records"""
    
    attendance_updates = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_attendance_updates(self, value):
        errors = []
        for index, record in enumerate(value):
            serializer = TeacherAttendanceSerializer(data=record)
            if not serializer.is_valid():
                errors.append({ 'index': index, 'errors': serializer.errors })
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return value
class BulkLeaveApprovalSerializer(serializers.Serializer):
    """Serializer for bulk approving teacher leave applications"""
    
    leave_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    approval_notes = serializers.CharField(allow_blank=True, required=False)
    
    def validate_leave_ids(self, value):
        # Check all leave applications exist and are pending
        leaves = TeacherLeave.objects.filter(id__in=value, status='pending', is_active=True)
        if len(leaves) != len(value):
            raise serializers.ValidationError(_("One or more leave applications not found or not pending"))
        return value
class BulkLeaveRejectionSerializer(serializers.Serializer):
    """Serializer for bulk rejecting teacher leave applications"""
    
    leave_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    rejected_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    rejection_reason = serializers.CharField()
    
    def validate_leave_ids(self, value):
        # Check all leave applications exist and are pending
        leaves = TeacherLeave.objects.filter(id__in=value, status='pending', is_active=True)
        if len(leaves) != len(value):
            raise serializers.ValidationError(_("One or more leave applications not found or not pending"))
        return value
    