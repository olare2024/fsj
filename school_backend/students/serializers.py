"""
Serializers for students models.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.apps import apps

from accounts.serializers import UserSerializer, UserMinimalSerializer
from accounts.models import User
from .models import (
    StudentProfile, StudentEnrollment,
    STUDENT_STATUS, ENROLLMENT_STATUS, TRANSPORT_CHOICES, GENDER_CHOICES, BLOOD_GROUP_CHOICES
)


# ============================================================================
# STUDENT PROFILE SERIALIZERS
# ============================================================================

class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student profiles."""
    
    # User fields that can be set during creation
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices= GENDER_CHOICES, required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    blood_group = serializers.ChoiceField(choices= BLOOD_GROUP_CHOICES, required=False, allow_null=True)
    
    # Parent information
    parent_name = serializers.CharField(required=False, allow_blank=True)
    parent_email = serializers.EmailField(required=False, allow_blank=True)
    parent_phone = serializers.CharField(required=False, allow_blank=True)
    parent_occupation = serializers.CharField(required=False, allow_blank=True)
    
    # Emergency contact
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_relationship = serializers.CharField(required=False, allow_blank=True)
    
    # Medical information
    medical_info = serializers.CharField(required=False, allow_blank=True)
    current_medications = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True)
    doctor_phone = serializers.CharField(required=False, allow_blank=True)
    
    admission_number = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This admission number is already in use.")
            )
        ]
    )
    upi_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This UPI number is already in use.")
            )
        ]
    )
    nemis_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This NEMIS number is already in use.")
            )
        ]
    )

    class Meta:
        model = StudentProfile
        fields = [
            # User fields
            'email', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'address', 'blood_group',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'medical_info', 'current_medications', 'doctor_name', 'doctor_phone',
            
            # Student profile fields
            'admission_number', 'upi_number', 'nemis_number',
            'current_class', 'current_academic_year',
            'cbc_pathway', 'portfolio_status', 'community_service_hours_completed',
            'overall_grade', 'gpa', 'attendance_percentage', 'rank_in_class',
            'learning_style', 'strengths', 'weaknesses',
            'conduct_rating', 'behavioral_notes',
            'extracurricular_activities', 'talents', 'club_memberships',
            'health_conditions', 'allergies', 'dietary_restrictions', 'medication_schedule',
            'transport_mode', 'bus_route', 'bus_stop',
            'fee_status', 'fee_arrears', 'scholarship_details',
            'career_interests', 'future_plans',
            'previous_school', 'previous_class',
            'student_status', 'is_active', 'remarks',
            'previous_grades', 'test_scores', 'disciplinary_actions',
            'transfer_certificate', 'birth_certificate', 'recommendation_letter',
        ]
        extra_kwargs = {
            'current_class': {'required': False, 'allow_null': True},
            'current_academic_year': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        """Validate student profile data."""
        # Validate date of birth for reasonable age
        date_of_birth = data.get('date_of_birth')
        if date_of_birth:
            age = (timezone.now().date() - date_of_birth).days // 365
            if age < 3:
                raise serializers.ValidationError({
                    'date_of_birth': _("Student must be at least 3 years old.")
                })
            if age > 25:
                raise serializers.ValidationError({
                    'date_of_birth': _("Student age seems unrealistic for school.")
                })
        
        # Validate GPA range
        gpa = data.get('gpa', 0.00)
        if gpa < 0.00 or gpa > 4.00:
            raise serializers.ValidationError({
                'gpa': _("GPA must be between 0.00 and 4.00.")
            })
        
        # Validate attendance percentage
        attendance = data.get('attendance_percentage', 0.00)
        if attendance < 0.00 or attendance > 100.00:
            raise serializers.ValidationError({
                'attendance_percentage': _("Attendance percentage must be between 0.00 and 100.00.")
            })
        
        return data

    def create(self, validated_data):
        """Create student profile and associated user."""
        # Extract user data
        user_data = {
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'role': User.Role.STUDENT,
        }
        
        # Optional user fields
        optional_user_fields = [
            'phone_number', 'address', 'blood_group',
            'parent_name', 'parent_email', 'parent_phone', 'parent_occupation',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'medical_info', 'current_medications', 'doctor_name', 'doctor_phone'
        ]
        
        for field in optional_user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        # Create or get user
        try:
            user = User.objects.get(email=user_data['email'])
            # Update user if exists
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                **{k: v for k, v in user_data.items() if k not in ['email', 'first_name', 'last_name']}
            )
        
        # Create student profile
        student_profile = StudentProfile.objects.create(
            user=user,
            **validated_data
        )
        
        return student_profile


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student profiles."""
    
    # Embedded user serializer for updating user fields
    user = UserSerializer(required=False)
    
    admission_number = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This admission number is already in use.")
            )
        ]
    )
    upi_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This UPI number is already in use.")
            )
        ]
    )
    nemis_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=StudentProfile.objects.all(),
                message=_("This NEMIS number is already in use.")
            )
        ]
    )

    class Meta:
        model = StudentProfile
        fields = [
            'user',
            'admission_number', 'upi_number', 'nemis_number',
            'current_class', 'current_academic_year',
            'cbc_pathway', 'portfolio_status', 'community_service_hours_completed',
            'overall_grade', 'gpa', 'attendance_percentage', 'rank_in_class',
            'learning_style', 'strengths', 'weaknesses',
            'conduct_rating', 'behavioral_notes',
            'extracurricular_activities', 'talents', 'club_memberships',
            'health_conditions', 'allergies', 'dietary_restrictions', 'medication_schedule',
            'transport_mode', 'bus_route', 'bus_stop',
            'fee_status', 'fee_arrears', 'scholarship_details',
            'career_interests', 'future_plans',
            'previous_school', 'previous_class',
            'student_status', 'is_active', 'remarks',
            'previous_grades', 'test_scores', 'disciplinary_actions',
            'transfer_certificate', 'birth_certificate', 'recommendation_letter',
            'friends',
        ]
        read_only_fields = ['user']

    def validate(self, data):
        """Validate student profile update data."""
        # Validate GPA range
        if 'gpa' in data and (data['gpa'] < 0.00 or data['gpa'] > 4.00):
            raise serializers.ValidationError({
                'gpa': _("GPA must be between 0.00 and 4.00.")
            })
        
        # Validate attendance percentage
        if 'attendance_percentage' in data and (data['attendance_percentage'] < 0.00 or data['attendance_percentage'] > 100.00):
            raise serializers.ValidationError({
                'attendance_percentage': _("Attendance percentage must be between 0.00 and 100.00.")
            })
        
        return data

    def update(self, instance, validated_data):
        """Update student profile and associated user."""
        # Update user data if provided
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(
                instance.user,
                data=user_data,
                partial=True
            )
            if user_serializer.is_valid():
                user_serializer.save()
        
        # Update student profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class StudentProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing student profiles (minimal data)."""
    
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    current_class_name = serializers.CharField(source='current_class.display_name', read_only=True)
    gender_display = serializers.CharField(source='user.get_gender_display', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'admission_number',
            'full_name',
            'email',
            'phone_number',
            'current_class',
            'current_class_name',
            'current_academic_year',
            'gender_display',
            'student_status',
            'is_active',
            'gpa',
            'attendance_percentage',
            'created_at',
        ]


class StudentProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed student profile view."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.IntegerField(source='user.age', read_only=True)
    current_class_name = serializers.CharField(source='current_class.display_name', read_only=True)
    academic_year_name = serializers.CharField(source='current_academic_year.name', read_only=True)
    
    # Display choices as readable text
    student_status_display = serializers.CharField(source='get_student_status_display', read_only=True)
    conduct_rating_display = serializers.CharField(source='get_conduct_rating_display', read_only=True)
    cbc_pathway_display = serializers.CharField(source='get_cbc_pathway_display', read_only=True)
    portfolio_status_display = serializers.CharField(source='get_portfolio_status_display', read_only=True)
    transport_mode_display = serializers.CharField(source='get_transport_mode_display', read_only=True)
    fee_status_display = serializers.CharField(source='get_fee_status_display', read_only=True)
    learning_style_display = serializers.CharField(source='get_learning_style_display', read_only=True)
    
    # File URLs
    transfer_certificate_url = serializers.FileField(source='transfer_certificate', read_only=True)
    birth_certificate_url = serializers.FileField(source='birth_certificate', read_only=True)
    recommendation_letter_url = serializers.FileField(source='recommendation_letter', read_only=True)
    
    # Related data
    enrollments = serializers.SerializerMethodField()
    friends_list = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'full_name',
            'age',
            'admission_number',
            'upi_number',
            'nemis_number',
            'current_class',
            'current_class_name',
            'current_academic_year',
            'academic_year_name',
            
            # CBC Information
            'cbc_pathway',
            'cbc_pathway_display',
            'portfolio_status',
            'portfolio_status_display',
            'community_service_hours_completed',
            
            # Academic Performance
            'overall_grade',
            'gpa',
            'attendance_percentage',
            'rank_in_class',
            'previous_grades',
            'test_scores',
            
            # Learning Preferences
            'learning_style',
            'learning_style_display',
            'strengths',
            'weaknesses',
            
            # Behavioral Information
            'conduct_rating',
            'conduct_rating_display',
            'behavioral_notes',
            'disciplinary_actions',
            
            # Extracurricular
            'extracurricular_activities',
            'talents',
            'club_memberships',
            
            # Health Information
            'health_conditions',
            'allergies',
            'dietary_restrictions',
            'medication_schedule',
            
            # Transport Information
            'transport_mode',
            'transport_mode_display',
            'bus_route',
            'bus_stop',
            
            # Financial Information
            'fee_status',
            'fee_status_display',
            'fee_arrears',
            'scholarship_details',
            
            # Career Information
            'career_interests',
            'future_plans',
            
            # Social Information
            'friends',
            'friends_list',
            
            # Previous Education
            'previous_school',
            'previous_class',
            'transfer_certificate',
            'transfer_certificate_url',
            'birth_certificate',
            'birth_certificate_url',
            'recommendation_letter',
            'recommendation_letter_url',
            
            # Status and Metadata
            'student_status',
            'student_status_display',
            'is_active',
            'remarks',
            'metadata',
            
            # Related Data
            'enrollments',
            
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_enrollments(self, obj):
        """Get student's enrollments."""
        enrollments = obj.enrollments.all().order_by('-academic_year__start_date')
        return StudentEnrollmentListSerializer(enrollments, many=True).data

    def get_friends_list(self, obj):
        """Get list of friends."""
        friends = obj.friends.all()
        return StudentProfileSimpleSerializer(friends, many=True).data


class StudentProfileSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for student profile references."""
    
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'admission_number',
            'full_name',
            'email',
            'current_class',
        ]


# ============================================================================
# STUDENT ENROLLMENT SERIALIZERS
# ============================================================================

class StudentEnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student enrollments."""
    
    enrollment_number = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=StudentEnrollment.objects.all(),
                message=_("This enrollment number is already in use.")
            )
        ]
    )
    
    roll_number = serializers.IntegerField(
        required=False,
        min_value=1
    )
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'student_profile',
            'class_enrolled',
            'academic_year',
            'enrollment_date',
            'enrollment_number',
            'status',
            'roll_number',
            'cbc_pathway_selection',
            'senior_track_selection',
            'house',
            'fee_status',
            'fee_arrears',
            'remarks',
            'enrollment_metadata',
            'is_active',
        ]
        extra_kwargs = {
            'status': {'default': 'active'},
            'fee_status': {'default': 'unpaid'},
        }

    def validate(self, data):
        """Validate enrollment data."""
        errors = {}
        
        # Check if student is already enrolled for this academic year
        student_profile = data.get('student_profile')
        academic_year = data.get('academic_year')
        
        if student_profile and academic_year:
            duplicate = StudentEnrollment.objects.filter(
                student_profile=student_profile,
                academic_year=academic_year
            ).exists()
            
            if duplicate and not self.instance:
                errors['academic_year'] = _('Student is already enrolled for this academic year.')
        
        # Validate roll number uniqueness
        class_enrolled = data.get('class_enrolled')
        roll_number = data.get('roll_number')
        
        if class_enrolled and roll_number and academic_year:
            duplicate_roll = StudentEnrollment.objects.filter(
                class_enrolled=class_enrolled,
                academic_year=academic_year,
                roll_number=roll_number
            ).exists()
            
            if duplicate_roll and not self.instance:
                errors['roll_number'] = _('This roll number is already assigned to another student in this class.')
        
        # Validate senior track selection for senior school
        senior_track = data.get('senior_track_selection')
        if senior_track and data.get('class_enrolled'):
            # Check if class is senior school
            try:
                if hasattr(data['class_enrolled'], 'education_level'):
                    if data['class_enrolled'].education_level != 'senior_school' and senior_track:
                        errors['senior_track_selection'] = _('Senior track selection is only applicable for senior school.')
            except:
                pass
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        """Create enrollment with auto-generated fields."""
        enrollment = StudentEnrollment.objects.create(**validated_data)
        return enrollment


class StudentEnrollmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student enrollments."""
    
    roll_number = serializers.IntegerField(
        required=False,
        min_value=1
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'class_enrolled',
            'academic_year',
            'enrollment_date',
            'status',
            'status_reason',
            'roll_number',
            'cbc_pathway_selection',
            'senior_track_selection',
            'house',
            'fee_status',
            'fee_arrears',
            'remarks',
            'enrollment_metadata',
            'is_active',
        ]

    def validate(self, data):
        """Validate enrollment update data."""
        errors = {}
        
        instance = self.instance
        roll_number = data.get('roll_number')
        class_enrolled = data.get('class_enrolled', instance.class_enrolled if instance else None)
        academic_year = data.get('academic_year', instance.academic_year if instance else None)
        
        # Validate roll number uniqueness
        if roll_number and class_enrolled and academic_year:
            duplicate_roll = StudentEnrollment.objects.filter(
                class_enrolled=class_enrolled,
                academic_year=academic_year,
                roll_number=roll_number
            ).exclude(pk=instance.pk if instance else None).exists()
            
            if duplicate_roll:
                errors['roll_number'] = _('This roll number is already assigned to another student in this class.')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class StudentEnrollmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing student enrollments."""
    
    student_name = serializers.CharField(source='student_profile.full_name', read_only=True)
    student_admission_number = serializers.CharField(source='student_profile.admission_number', read_only=True)
    class_name = serializers.CharField(source='class_enrolled.display_name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    # Display choices
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    house_display = serializers.CharField(source='get_house_display', read_only=True)
    fee_status_display = serializers.CharField(source='get_fee_status_display', read_only=True)
    cbc_pathway_display = serializers.CharField(source='get_cbc_pathway_selection_display', read_only=True)
    senior_track_display = serializers.CharField(source='get_senior_track_selection_display', read_only=True)
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'enrollment_number',
            'student_profile',
            'student_name',
            'student_admission_number',
            'class_enrolled',
            'class_name',
            'academic_year',
            'academic_year_name',
            'enrollment_date',
            'status',
            'status_display',
            'roll_number',
            'cbc_pathway_selection',
            'cbc_pathway_display',
            'senior_track_selection',
            'senior_track_display',
            'house',
            'house_display',
            'fee_status',
            'fee_status_display',
            'fee_arrears',
            'is_active',
            'created_at',
        ]


class StudentEnrollmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed student enrollment view."""
    
    student_profile = StudentProfileSimpleSerializer(read_only=True)
    class_enrolled_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    
    # Display choices
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    house_display = serializers.CharField(source='get_house_display', read_only=True)
    fee_status_display = serializers.CharField(source='get_fee_status_display', read_only=True)
    cbc_pathway_display = serializers.CharField(source='get_cbc_pathway_selection_display', read_only=True)
    senior_track_display = serializers.CharField(source='get_senior_track_selection_display', read_only=True)
    
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'enrollment_number',
            'student_profile',
            'class_enrolled',
            'class_enrolled_detail',
            'academic_year',
            'academic_year_detail',
            'enrollment_date',
            'status',
            'status_display',
            'status_changed_date',
            'status_reason',
            'roll_number',
            'cbc_pathway_selection',
            'cbc_pathway_display',
            'senior_track_selection',
            'senior_track_display',
            'house',
            'house_display',
            'fee_status',
            'fee_status_display',
            'fee_arrears',
            'remarks',
            'enrollment_metadata',
            'is_current',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'enrollment_number']

    def get_class_enrolled_detail(self, obj):
        """Get detailed class information."""
        if obj.class_enrolled:
            from academics.serializers import ClassSimpleSerializer
            return ClassSimpleSerializer(obj.class_enrolled).data
        return None

    def get_academic_year_detail(self, obj):
        """Get detailed academic year information."""
        if obj.academic_year:
            from academics.serializers import AcademicYearSimpleSerializer
            return AcademicYearSimpleSerializer(obj.academic_year).data
        return None


class StudentEnrollmentBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk enrollment creation."""
    
    student_profiles = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all()),
        required=True
    )
    class_enrolled = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'Class').objects.all(),
        required=True
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'AcademicYear').objects.all(),
        required=True
    )
    enrollment_date = serializers.DateField(default=timezone.now)
    status = serializers.ChoiceField(choices=ENROLLMENT_STATUS, default='active')
    fee_status = serializers.ChoiceField(
        choices=[
            ('paid', 'Fully Paid'),
            ('partial', 'Partially Paid'),
            ('unpaid', 'Unpaid'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
        ],
        default='unpaid'
    )

    def validate(self, data):
        """Validate bulk enrollment data."""
        student_profiles = data['student_profiles']
        academic_year = data['academic_year']
        
        # Check for duplicate enrollments
        existing_enrollments = StudentEnrollment.objects.filter(
            student_profile__in=student_profiles,
            academic_year=academic_year
        ).values_list('student_profile_id', flat=True)
        
        if existing_enrollments:
            duplicate_students = StudentProfile.objects.filter(
                id__in=existing_enrollments
            ).values_list('admission_number', flat=True)
            
            raise serializers.ValidationError({
                'student_profiles': _(
                    f"The following students are already enrolled for this academic year: "
                    f"{', '.join(duplicate_students)}"
                )
            })
        
        return data

    def create(self, validated_data):
        """Create bulk enrollments."""
        student_profiles = validated_data.pop('student_profiles')
        enrollments = []
        
        for student_profile in student_profiles:
            enrollment = StudentEnrollment(
                student_profile=student_profile,
                **validated_data
            )
            enrollments.append(enrollment)
        
        StudentEnrollment.objects.bulk_create(enrollments)
        return enrollments


# ============================================================================
# STATISTICS AND REPORT SERIALIZERS
# ============================================================================

class StudentStatisticsSerializer(serializers.Serializer):
    """Serializer for student statistics."""
    
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    male_students = serializers.IntegerField()
    female_students = serializers.IntegerField()
    other_gender_students = serializers.IntegerField()
    average_gpa = serializers.FloatField()
    average_attendance = serializers.FloatField()
    cbc_students = serializers.IntegerField()
    scholarship_students = serializers.IntegerField()
    
    # Status distribution
    status_distribution = serializers.DictField()
    
    # Class distribution
    class_distribution = serializers.DictField()
    
    # CBC pathway distribution
    cbc_pathway_distribution = serializers.DictField()


class StudentReportSerializer(serializers.Serializer):
    """Serializer for student report generation."""
    
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    class_filter = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'Class').objects.all(),
        required=False
    )
    status_filter = serializers.ChoiceField(choices=STUDENT_STATUS, required=False)
    include_medical = serializers.BooleanField(default=False)
    include_financial = serializers.BooleanField(default=False)
    include_academic = serializers.BooleanField(default=True)


# ============================================================================
# SPECIALIZED SERIALIZERS
# ============================================================================

class StudentAcademicUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating academic information only."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'overall_grade',
            'gpa',
            'attendance_percentage',
            'rank_in_class',
            'previous_grades',
            'test_scores',
            'learning_style',
            'strengths',
            'weaknesses',
        ]


class StudentBehavioralUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating behavioral information only."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'conduct_rating',
            'behavioral_notes',
            'disciplinary_actions',
        ]


class StudentHealthUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating health information only."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'health_conditions',
            'allergies',
            'dietary_restrictions',
            'medication_schedule',
        ]


class StudentExtracurricularUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating extracurricular information only."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'extracurricular_activities',
            'talents',
            'club_memberships',
        ]


class StudentFeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating fee information only."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'fee_status',
            'fee_arrears',
            'scholarship_details',
        ]


class StudentPromotionSerializer(serializers.Serializer):
    """Serializer for student promotion."""
    
    next_academic_year = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'AcademicYear').objects.all(),
        required=True,
        help_text=_("Academic year to promote students to")
    )
    
    promote_all = serializers.BooleanField(
        default=False,
        help_text=_("Promote all active students")
    )
    
    student_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all()),
        required=False,
        help_text=_("List of student IDs to promote (required if promote_all is False)")
    )
    
    next_class = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'Class').objects.all(),
        required=False,
        allow_null=True,
        help_text=_("Specific class to promote students to (optional)")
    )
    
    # Optional parameters
    promotion_date = serializers.DateField(
        default=timezone.now().date,
        required=False,
        help_text=_("Date of promotion (defaults to today)")
    )
    
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text=_("Promotion remarks or notes")
    )
    
    def validate(self, data):
        """Validate promotion data."""
        promote_all = data.get('promote_all', False)
        student_ids = data.get('student_ids', [])
        
        if not promote_all and not student_ids:
            raise serializers.ValidationError({
                'student_ids': _(
                    "Either set promote_all to True or provide student_ids to promote."
                )
            })
        
        # If promoting all, we don't need student_ids
        if promote_all:
            data.pop('student_ids', None)
        
        # Validate that the academic year is not in the past
        next_academic_year = data.get('next_academic_year')
        if next_academic_year and next_academic_year.end_date:
            if next_academic_year.end_date < timezone.now().date():
                raise serializers.ValidationError({
                    'next_academic_year': _(
                        f"Cannot promote to academic year {next_academic_year} "
                        f"which ended on {next_academic_year.end_date}"
                    )
                })
        
        # If next_class is provided, validate it belongs to the next academic year
        next_class = data.get('next_class')
        if next_class and next_academic_year:
            if next_class.academic_year != next_academic_year:
                raise serializers.ValidationError({
                    'next_class': _(
                        f"Class {next_class} does not belong to academic year {next_academic_year}"
                    )
                })
        
        return data


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class StudentBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk student updates."""
    
    student_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all()),
        required=True
    )
    update_fields = serializers.DictField(required=True)
    
    def validate_update_fields(self, value):
        """Validate update fields."""
        allowed_fields = [
            'student_status',
            'is_active',
            'current_class',
            'current_academic_year',
            'conduct_rating',
            'fee_status',
            'house',
        ]
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    _("Field '{}' is not allowed for bulk update.".format(field))
                )
        
        return value


class StudentImportSerializer(serializers.Serializer):
    """Serializer for importing students from CSV/Excel."""
    
    file = serializers.FileField(required=True)
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'AcademicYear').objects.all(),
        required=False
    )
    default_class = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'Class').objects.all(),
        required=False
    )
    skip_duplicates = serializers.BooleanField(default=True)
    send_welcome_email = serializers.BooleanField(default=False)


# ============================================================================
# SEARCH AND FILTER SERIALIZERS
# ============================================================================

class StudentSearchSerializer(serializers.Serializer):
    """Serializer for student search."""
    
    query = serializers.CharField(required=False)
    admission_number = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'Class').objects.all(),
        required=False
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('academics', 'AcademicYear').objects.all(),
        required=False
    )
    status = serializers.ChoiceField(choices=STUDENT_STATUS, required=False)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    cbc_pathway = serializers.ChoiceField(
        choices=[
            ('stem', 'STEM Pathway'),
            ('social_sciences', 'Social Sciences Pathway'),
            ('arts_sports', 'Arts & Sports Pathway'),
            ('general', 'General Pathway'),
        ],
        required=False
    )
    fee_status = serializers.ChoiceField(
        choices=[
            ('paid', 'Fully Paid'),
            ('partial', 'Partially Paid'),
            ('unpaid', 'Unpaid'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
        ],
        required=False
    )
    
    # Pagination
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)
    
    # Ordering
    order_by = serializers.ChoiceField(
        choices=[
            'admission_number',
            'full_name',
            'gpa',
            'attendance_percentage',
            'created_at',
        ],
        default='admission_number'
    )
    order_direction = serializers.ChoiceField(
        choices=['asc', 'desc'],
        default='asc'
    )