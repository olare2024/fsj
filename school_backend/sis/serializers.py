from rest_framework import serializers
from academic.models import (
    Student, 
    Parent, 
    StudentMedicalHistory,  # FIXED: Changed from StudentsMedicalHistory to StudentMedicalHistory
    StudentClassEnrollment,
    DormitoryAllocation,
    StudentParentRelationship
)
from users.serializers import CustomUserSerializer


class StudentMedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for student medical history"""
    class Meta:
        model = StudentMedicalHistory  # FIXED: Use the correct model name
        fields = [
            'id', 'blood_group', 'known_allergies', 'chronic_conditions',
            'current_medications', 'immunization_history', 'emergency_contact',
            'hospital_preference', 'insurance_provider', 'insurance_policy_number',
            'height', 'weight', 'bmi', 'vision', 'dental_health', 'medical_events',
            'last_medical_checkup', 'next_medical_checkup', 'special_needs',
            'accommodations_required', 'dietary_restrictions', 
            'physical_activity_restrictions', 'notes'
        ]
        read_only_fields = ['id']


class ParentSerializer(serializers.ModelSerializer):
    """Serializer for parent model"""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Parent
        fields = [
            'id', 'user', 'first_name', 'middle_name', 'last_name', 'gender',
            'date_of_birth', 'relationship', 'personal_phone', 'alternative_phone',
            'email', 'address', 'county', 'town', 'occupation', 'employer',
            'work_phone', 'work_email', 'national_id', 'kra_pin', 'monthly_income',
            'income_source', 'preferred_contact_method', 'receive_sms_alerts',
            'receive_email_alerts', 'is_primary_contact', 'can_pickup_student',
            'emergency_contact', 'notes', 'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentParentRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for student-parent relationships"""
    parent_details = ParentSerializer(source='parent', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = StudentParentRelationship
        fields = [
            'id', 'student', 'student_name', 'parent', 'parent_details', 'relationship',
            'is_primary', 'can_pickup', 'can_view_grades', 'can_receive_notifications',
            'emergency_contact', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StudentClassEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for student class enrollment"""
    class Meta:
        model = StudentClassEnrollment
        fields = [
            'id', 'student', 'classroom', 'academic_year', 'term', 'enrollment_date',
            'enrollment_type', 'is_active', 'seat_number', 'house', 'club_memberships',
            'attendance_rate', 'average_score', 'class_position', 'enrollment_notes',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DormitoryAllocationSerializer(serializers.ModelSerializer):
    """Serializer for dormitory allocations"""
    class Meta:
        model = DormitoryAllocation
        fields = [
            'id', 'student', 'dormitory', 'academic_year', 'term', 'date_from',
            'date_till', 'room_number', 'bed_number', 'is_active', 'allocation_type',
            'notes', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    """Main student serializer with related data"""
    # Basic information
    full_name = serializers.SerializerMethodField()
    current_age = serializers.ReadOnlyField()
    
    # Related data
    medical_history = StudentMedicalHistorySerializer(read_only=True)
    parents = StudentParentRelationshipSerializer(
        source='parent_relationships', 
        many=True, 
        read_only=True
    )
    current_enrollment = serializers.SerializerMethodField()
    dormitory_allocation = serializers.SerializerMethodField()
    
    # Computed fields
    fee_balance = serializers.ReadOnlyField()
    attendance_rate = serializers.ReadOnlyField()
    academic_performance = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = [
            # Personal information
            'id', 'admission_number', 'first_name', 'middle_name', 'last_name', 
            'full_name', 'gender', 'date_of_birth', 'current_age', 'place_of_birth',
            'nationality', 'personal_phone', 'email',
            
            # Address information
            'home_address', 'county', 'town', 'estate',
            
            # Academic information
            'admission_date', 'current_class', 'curriculum', 'grade_level',
            'student_status', 'boarding_status',
            
            # Medical information
            'blood_group', 'known_allergies', 'medical_conditions', 'special_needs',
            'medication', 'religion',
            
            # Background information
            'previous_school', 'previous_school_address', 'reason_for_transfer',
            'enrollment_history', 'academic_notes', 'talents_interests',
            'career_aspiration',
            
            # Documents
            'birth_certificate_number', 'image', 'documents',
            
            # Related data
            'medical_history', 'parents', 'current_enrollment', 'dormitory_allocation',
            
            # Computed fields
            'fee_balance', 'attendance_rate', 'academic_performance',
            'years_in_school',
            
            # System fields
            'created_by', 'last_medical_check', 'last_academic_review',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'admission_number', 'created_at', 'updated_at', 
            'current_age', 'fee_balance', 'attendance_rate', 'academic_performance',
            'years_in_school'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name

    def get_current_enrollment(self, obj):
        """Get current class enrollment"""
        current_enrollment = obj.class_enrollments.filter(is_active=True).first()
        if current_enrollment:
            return StudentClassEnrollmentSerializer(current_enrollment).data
        return None

    def get_dormitory_allocation(self, obj):
        """Get current dormitory allocation"""
        current_allocation = obj.dormitory_allocations.filter(is_active=True).first()
        if current_allocation:
            return DormitoryAllocationSerializer(current_allocation).data
        return None

    def validate_grade_level(self, value):
        """Validate grade level against available choices"""
        from academic.models import GRADE_LEVEL_CHOICES
        valid_choices = [choice[0] for choice in GRADE_LEVEL_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid grade level. Must be one of: {valid_choices}"
            )
        return value

    def create(self, validated_data):
        """Create student with automatic admission number generation"""
        # Remove read-only fields if present
        validated_data.pop('admission_number', None)
        
        student = Student.objects.create(**validated_data)
        return student


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new students"""
    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth',
            'place_of_birth', 'nationality', 'personal_phone', 'email',
            'home_address', 'county', 'town', 'estate', 'curriculum', 'grade_level',
            'blood_group', 'known_allergies', 'medical_conditions', 'special_needs',
            'medication', 'religion', 'previous_school', 'previous_school_address',
            'reason_for_transfer', 'birth_certificate_number', 'image'
        ]

    def validate_date_of_birth(self, value):
        """Validate student age"""
        from datetime import date
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        
        if age < 3:
            raise serializers.ValidationError("Student must be at least 3 years old.")
        if age > 25:
            raise serializers.ValidationError("Student age cannot exceed 25 years.")
            
        return value


class StudentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student information"""
    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name', 'gender', 'personal_phone', 'email',
            'home_address', 'county', 'town', 'estate', 'current_class', 'grade_level',
            'blood_group', 'known_allergies', 'medical_conditions', 'special_needs',
            'medication', 'religion', 'talents_interests', 'career_aspiration',
            'student_status', 'boarding_status', 'image'
        ]

    def validate_grade_level(self, value):
        """Validate grade level against available choices"""
        from academic.models import GRADE_LEVEL_CHOICES
        valid_choices = [choice[0] for choice in GRADE_LEVEL_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid grade level. Must be one of: {valid_choices}"
            )
        return value


class StudentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for student lists"""
    full_name = serializers.SerializerMethodField()
    current_age = serializers.ReadOnlyField()
    current_class_name = serializers.CharField(source='current_class.full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'full_name', 'gender', 'current_age',
            'current_class_name', 'grade_level', 'student_status', 'boarding_status',
            'created_at'
        ]
        read_only_fields = ['id', 'admission_number', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name


class StudentExportSerializer(serializers.ModelSerializer):
    """Serializer for student data export"""
    full_name = serializers.SerializerMethodField()
    current_age = serializers.ReadOnlyField()
    parents_info = serializers.SerializerMethodField()
    current_class_name = serializers.CharField(source='current_class.full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'admission_number', 'full_name', 'gender', 'current_age', 'date_of_birth',
            'nationality', 'personal_phone', 'email', 'home_address', 'county', 'town',
            'current_class_name', 'grade_level', 'curriculum', 'student_status',
            'boarding_status', 'religion', 'blood_group', 'known_allergies',
            'medical_conditions', 'parents_info', 'admission_date', 'previous_school'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name

    def get_parents_info(self, obj):
        """Get formatted parents information"""
        parents = obj.parent_relationships.all()
        parent_info = []
        for parent_rel in parents:
            parent_info.append({
                'name': parent_rel.parent.get_full_name,
                'relationship': parent_rel.relationship,
                'phone': parent_rel.parent.personal_phone,
                'email': parent_rel.parent.email,
                'is_primary': parent_rel.is_primary
            })
        return parent_info