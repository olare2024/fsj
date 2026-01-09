"""
academics/serializers.py
Serializers for academic models with comprehensive CRUD operations.
"""

from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.exceptions import ValidationError
from django.db.models import Count, Avg, Q

from .models import (
    AcademicYear, AcademicTerm, Subject, Class, SubTopic, SubjectAssignment,
    StudentEnrollment, StudentClassAssignment, LessonPlan, Syllabus,
    AcademicEvent, Stream, CBCAssessment, CBCPortfolio, PathwaySelection,
    CompetencyTracking, CurriculumMapping
)
from accounts.models import User
from students.models import StudentProfile
from teachers.models import TeacherProfile


# ============================================================================
# HELPER FUNCTIONS AND BASE SERIALIZERS
# ============================================================================

class UUIDRelatedField(serializers.RelatedField):
    """Custom related field that handles UUID string conversion."""
    
    def to_internal_value(self, data):
        if isinstance(data, uuid.UUID):
            return data
        try:
            return uuid.UUID(str(data))
        except (ValueError, TypeError, AttributeError):
            raise serializers.ValidationError(
                _("Invalid UUID format. Expected a UUID string or object.")
            )
    
    def to_representation(self, value):
        return str(value)


class PrimaryKeyRelatedUUIDField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField with explicit UUID handling."""
    
    def __init__(self, **kwargs):
        kwargs['pk_field'] = serializers.UUIDField()
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        try:
            # Convert string to UUID if needed
            if isinstance(data, str):
                data = uuid.UUID(data)
            return super().to_internal_value(data)
        except (ValueError, TypeError):
            raise serializers.ValidationError(_("Invalid UUID format"))


class AuditFieldsMixin:
    """Mixin to include audit fields in serializers."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)


# ============================================================================
# USER SERIALIZERS
# ============================================================================

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for User model."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class TeacherMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for TeacherProfile model."""
    
    full_name = serializers.SerializerMethodField()
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = ['id', 'user_id', 'full_name', 'staff_id', 'qualification', 'department', 'is_active']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None


class StudentMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for StudentProfile model."""
    
    full_name = serializers.SerializerMethodField()
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user_id', 'full_name', 'admission_number', 'grade_level', 'date_of_birth', 'gender', 'is_active']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None


# ============================================================================
# MINIMAL SERIALIZERS FOR RELATED MODELS
# ============================================================================

class SubjectMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Subject."""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'category', 'curriculum', 'is_cbc_core']


class ClassMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Class."""
    
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'section', 'grade_level', 'display_name', 'room_number']


class AcademicYearMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for AcademicYear."""
    
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'code', 'start_date', 'end_date', 'is_current']


class AcademicTermMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for AcademicTerm."""
    
    class Meta:
        model = AcademicTerm
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current', 'term_order']


class SubTopicMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for SubTopic."""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = SubTopic
        fields = ['id', 'topic', 'name', 'full_name', 'order', 'estimated_hours']


# ============================================================================
# CORE MODEL SERIALIZERS
# ============================================================================

class AcademicYearSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Academic Year model."""
    
    # Computed fields
    duration_days = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    is_currently_active = serializers.ReadOnlyField()
    is_cbc = serializers.ReadOnlyField()
    is_international = serializers.ReadOnlyField()
    is_african = serializers.ReadOnlyField()
    curriculum_info = serializers.ReadOnlyField()
    
    # Nested fields
    current_term = serializers.SerializerMethodField()
    terms_count = serializers.SerializerMethodField()
    classes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = [
            # Basic fields
            'id', 'name', 'code', 'start_date', 'end_date', 'description',
            'is_current', 'is_active',
            
            # Curriculum configuration
            'curriculum_system', 'academic_structure', 'grading_system',
            'term_structure', 'total_terms', 'language_mode', 'additional_languages',
            'assessment_model', 'external_exams',
            
            # Configuration
            'fee_structure', 'currency', 'important_dates', 'holiday_calendar',
            'cbc_configuration', 'international_config', 'report_config', 'metadata',
            
            # Status flags
            'is_configured', 'is_locked', 'allow_admissions',
            'allow_assessments', 'allow_transcripts',
            
            # Computed fields
            'duration_days', 'progress_percentage', 'status', 'is_currently_active',
            'is_cbc', 'is_international', 'is_african', 'curriculum_info',
            
            # Nested counts
            'current_term', 'terms_count', 'classes_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_current_term(self, obj):
        """Get current term for the academic year."""
        current_term = obj.get_current_term()
        if current_term:
            return AcademicTermMinimalSerializer(current_term).data
        return None
    
    def get_terms_count(self, obj):
        """Get count of terms in this academic year."""
        return obj.terms.count()
    
    def get_classes_count(self, obj):
        """Get count of classes in this academic year."""
        return obj.classes.count()
    
    def validate(self, data):
        """Validate academic year data."""
        errors = {}
        
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        # Date validation
        if start_date and end_date and start_date >= end_date:
            errors['end_date'] = _('End date must be after start date')
        
        # Curriculum-specific validation
        curriculum_system = data.get('curriculum_system', getattr(self.instance, 'curriculum_system', None))
        if curriculum_system == 'cbc_kenya' and not data.get('cbc_configuration'):
            errors['cbc_configuration'] = _('CBC configuration is required for Kenya CBC system')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create academic year with auto-generated code."""
        if not validated_data.get('code'):
            year_part = ''.join(filter(str.isdigit, validated_data['name']))
            validated_data['code'] = f"AY{year_part}" if year_part else f"AY{validated_data['start_date'].year}"
        
        return super().create(validated_data)


class AcademicTermSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Academic Term model."""
    
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    
    # Computed fields
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    teaching_weeks = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    is_currently_active = serializers.ReadOnlyField()
    
    # Nested counts
    events_count = serializers.SerializerMethodField()
    lesson_plans_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicTerm
        fields = [
            'id', 'academic_year', 'academic_year_name', 'name', 'start_date', 'end_date',
            'is_current', 'term_order', 'assessment_periods', 'holidays', 'important_dates',
            'term_fees', 'is_active',
            
            # Computed fields
            'duration_days', 'teaching_weeks', 'progress_percentage', 'status',
            'is_currently_active',
            
            # Nested counts
            'events_count', 'lesson_plans_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_events_count(self, obj):
        """Get count of events in this term."""
        return obj.academic_events.count()
    
    def get_lesson_plans_count(self, obj):
        """Get count of lesson plans in this term."""
        return obj.lesson_plans.count()
    
    def validate(self, data):
        """Validate term data."""
        errors = {}
        
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        
        if start_date and end_date and academic_year:
            # Date order validation
            if start_date >= end_date:
                errors['end_date'] = _('End date must be after start date')
            
            # Validate within academic year
            if start_date < academic_year.start_date:
                errors['start_date'] = _('Term start date cannot be before academic year start date')
            
            if end_date > academic_year.end_date:
                errors['end_date'] = _('Term end date cannot be after academic year end date')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class SubjectSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Subject model."""
    
    # Related fields
    prerequisites = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        many=True,
        required=False
    )
    department = PrimaryKeyRelatedUUIDField(
        queryset='teachers.Department.objects.all()',
        required=False,
        allow_null=True
    )
    
    # Computed fields
    weekly_hours = serializers.ReadOnlyField()
    is_cbc_subject = serializers.ReadOnlyField()
    subject_info = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    # Nested counts
    teacher_assignments_count = serializers.SerializerMethodField()
    student_assignments_count = serializers.SerializerMethodField()
    syllabus_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            # Basic information
            'id', 'name', 'code', 'description', 'is_active',
            
            # Academic information
            'category', 'curriculum', 'cbc_competency_area', 'cbc_pathway',
            'is_cbc_core', 'is_compulsory', 'grade_levels',
            
            # Academic requirements
            'credits', 'periods_per_week', 'practical_weight', 'assessment_methods',
            'project_based',
            
            # Resources
            'resources_required', 'recommended_books', 'syllabus_link', 'notes',
            
            # Relationships
            'prerequisites', 'department', 'minimum_qualification',
            
            # Status flags
            'is_examined', 'is_elective',
            
            # Computed fields
            'weekly_hours', 'is_cbc_subject', 'subject_info', 'full_name',
            
            # Nested counts
            'teacher_assignments_count', 'student_assignments_count', 'syllabus_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_teacher_assignments_count(self, obj):
        """Get count of teacher assignments for this subject."""
        return obj.subject_assignments.count()
    
    def get_student_assignments_count(self, obj):
        """Get count of student assignments for this subject."""
        return obj.student_assignments.count()
    
    def get_syllabus_count(self, obj):
        """Get count of syllabus entries for this subject."""
        return obj.syllabi.count()
    
    def validate(self, data):
        """Validate subject data."""
        errors = {}
        
        # Practical weight validation
        practical_weight = data.get('practical_weight', getattr(self.instance, 'practical_weight', 0))
        if practical_weight < 0 or practical_weight > 100:
            errors['practical_weight'] = _('Practical weight must be between 0 and 100')
        
        # Periods per week validation
        periods_per_week = data.get('periods_per_week', getattr(self.instance, 'periods_per_week', 5))
        if periods_per_week < 1 or periods_per_week > 20:
            errors['periods_per_week'] = _('Periods per week must be between 1 and 20')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create subject with auto-generated code."""
        # Generate code from name if not provided
        if not validated_data.get('code') and validated_data.get('name'):
            name = validated_data['name']
            code = ''.join(c for c in name[:3] if c.isalpha()).upper()
            
            # Ensure uniqueness
            count = Subject.objects.filter(code__startswith=code).count()
            if count > 0:
                code = f"{code}{count + 1}"
            
            validated_data['code'] = code
        
        return super().create(validated_data)


class ClassSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Class model."""
    
    # Related fields
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    class_teacher = PrimaryKeyRelatedUUIDField(
        queryset=TeacherProfile.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    class_teacher_name = serializers.SerializerMethodField()
    display_name = serializers.ReadOnlyField()
    available_seats = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    occupancy_rate = serializers.ReadOnlyField()
    is_cbc_class = serializers.ReadOnlyField()
    cbc_info = serializers.ReadOnlyField()
    class_code = serializers.ReadOnlyField()
    academic_info = serializers.ReadOnlyField()
    
    # Nested counts
    student_count = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            # Basic Information
            'id', 'name', 'grade_level', 'section', 'stream', 'room_number',
            'is_active',
            
            # Academic Context
            'academic_year', 'academic_year_name', 'class_teacher', 'class_teacher_name',
            
            # CBC-Specific Fields
            'education_level', 'cbc_pathway', 'senior_track',
            
            # Curriculum Information
            'primary_curriculum', 'additional_curriculums',
            
            # Class Configuration
            'capacity', 'current_strength', 'schedule', 'portfolio_required',
            'project_work_required', 'community_service_hours', 'assessment_config',
            
            # Additional Information
            'description', 'class_rules', 'class_color', 'facilities',
            'average_performance', 'attendance_rate', 'parent_engagement_level',
            'technology_level', 'special_programs', 'metadata',
            
            # Computed fields
            'display_name', 'available_seats', 'is_full', 'occupancy_rate',
            'is_cbc_class', 'cbc_info', 'class_code', 'academic_info',
            
            # Nested counts
            'student_count', 'subject_count', 'teacher_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_strength', 'created_at', 'updated_at']
    
    def get_class_teacher_name(self, obj):
        """Get class teacher's full name."""
        if obj.class_teacher and obj.class_teacher.user:
            return obj.class_teacher.user.get_full_name()
        return None
    
    def get_student_count(self, obj):
        """Get count of students in this class."""
        return obj.enrollments.filter(status='active').count()
    
    def get_subject_count(self, obj):
        """Get count of subjects taught in this class."""
        return obj.get_subjects().count()
    
    def get_teacher_count(self, obj):
        """Get count of teachers assigned to this class."""
        return obj.get_teachers().count()
    
    def validate(self, data):
        """Validate class data."""
        errors = {}
        
        # Section validation
        section = data.get('section', getattr(self.instance, 'section', None))
        if section and not section.isalnum():
            errors['section'] = _('Section must be alphanumeric')
        
        # Capacity validation
        capacity = data.get('capacity', getattr(self.instance, 'capacity', 30))
        current_strength = getattr(self.instance, 'current_strength', 0) if self.instance else 0
        
        if capacity < current_strength:
            errors['capacity'] = _('Capacity cannot be less than current strength')
        
        # CBC-specific validation
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        if academic_year and academic_year.is_cbc:
            education_level = data.get('education_level', getattr(self.instance, 'education_level', None))
            cbc_pathway = data.get('cbc_pathway', getattr(self.instance, 'cbc_pathway', None))
            
            if education_level == 'senior_school' and not cbc_pathway:
                errors['cbc_pathway'] = _('CBC pathway is required for Senior School classes')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class SubTopicSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for SubTopic model."""
    
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    
    # Related fields
    prerequisite_topics = PrimaryKeyRelatedUUIDField(
        queryset='self',
        many=True,
        required=False
    )
    
    # Computed fields
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    full_name = serializers.ReadOnlyField()
    estimated_periods = serializers.ReadOnlyField()
    is_cbc_aligned = serializers.ReadOnlyField()
    difficulty_assessment = serializers.ReadOnlyField()
    
    # Nested counts
    lesson_plan_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubTopic
        fields = [
            # Basic Information
            'id', 'subject', 'subject_name', 'subject_code', 'topic', 'name', 'code',
            'description', 'order', 'is_active',
            
            # Academic Information
            'competency_alignment', 'learning_objectives', 'key_concepts',
            'skills_developed',
            
            # Time Allocation
            'estimated_hours', 'priority',
            
            # Resources
            'teaching_resources', 'assessment_methods',
            'differentiation_strategies', 'project_connections',
            
            # Prerequisites
            'prerequisite_topics',
            
            # Status and Tracking
            'is_completed', 'completion_date',
            
            # Computed fields
            'full_name', 'estimated_periods', 'is_cbc_aligned', 'difficulty_assessment',
            
            # Nested counts
            'lesson_plan_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_lesson_plan_count(self, obj):
        """Get count of lesson plans for this sub-topic."""
        return obj.lesson_plans.count()
    
    def create(self, validated_data):
        """Create sub-topic with auto-generated code."""
        if not validated_data.get('code'):
            subject = validated_data['subject']
            name = validated_data['name']
            subject_code = subject.code if subject else 'GEN'
            clean_name = ''.join(c for c in name if c.isalnum()).upper()
            validated_data['code'] = f"{subject_code}-{clean_name[:10]}" if clean_name else f"{subject_code}-ST"
        
        return super().create(validated_data)


# ============================================================================
# ASSIGNMENT SERIALIZERS
# ============================================================================

class SubjectAssignmentSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for SubjectAssignment model."""
    
    # Related fields
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    teacher = PrimaryKeyRelatedUUIDField(
        queryset=TeacherProfile.objects.all(),
        required=True
    )
    class_assigned = PrimaryKeyRelatedUUIDField(
        queryset=Class.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    
    # Computed fields
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='class_assigned.display_name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    teaching_load_hours = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    assignment_duration_days = serializers.ReadOnlyField()
    is_cbc_assignment = serializers.ReadOnlyField()
    competency_info = serializers.ReadOnlyField()
    workload_score = serializers.ReadOnlyField()
    
    # Nested
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubjectAssignment
        fields = [
            # Core Relationships
            'id', 'subject', 'subject_name', 'teacher', 'teacher_name',
            'class_assigned', 'class_name', 'academic_year', 'academic_year_name',
            'is_active',
            
            # Teaching Configuration
            'periods_per_week', 'is_class_teacher', 'role_type',
            
            # CBC-Specific Teaching Requirements
            'cbc_competency_focus', 'project_supervision_required',
            'portfolio_assessment_duty',
            
            # Schedule Information
            'teaching_schedule', 'assessment_responsibilities',
            'additional_responsibilities', 'responsibility_allowance',
            
            # Status and Dates
            'assigned_date', 'effective_from', 'effective_until',
            'performance_rating', 'last_performance_review',
            'assignment_status', 'notes',
            
            # Computed fields
            'teaching_load_hours', 'is_current', 'assignment_duration_days',
            'is_cbc_assignment', 'competency_info', 'workload_score',
            
            # Nested
            'student_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_date', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        """Get teacher's full name."""
        if obj.teacher and obj.teacher.user:
            return obj.teacher.user.get_full_name()
        return None
    
    def get_student_count(self, obj):
        """Get number of students in the assigned class."""
        return obj.class_assigned.current_strength
    
    def validate(self, data):
        """Validate assignment data."""
        errors = {}
        
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        periods_per_week = data.get('periods_per_week', getattr(self.instance, 'periods_per_week', 5))
        
        if teacher and academic_year and periods_per_week:
            # Check teacher overload
            current_assignments = SubjectAssignment.objects.filter(
                teacher=teacher,
                academic_year=academic_year,
                is_active=True,
                assignment_status='active'
            ).exclude(pk=getattr(self.instance, 'pk', None))
            
            total_periods = sum(assign.periods_per_week for assign in current_assignments) + periods_per_week
            max_periods = 40  # Default maximum
            
            # Adjust based on employment type
            if teacher.employment_type == 'full_time':
                max_periods = 40
            elif teacher.employment_type == 'part_time':
                max_periods = 20
            
            if total_periods > max_periods:
                errors['periods_per_week'] = _(
                    f'Teacher would be overloaded. Maximum {max_periods} periods allowed. '
                    f'Currently assigned {total_periods - periods_per_week} periods.'
                )
        
        # Date validation
        effective_from = data.get('effective_from', getattr(self.instance, 'effective_from', None))
        effective_until = data.get('effective_until', getattr(self.instance, 'effective_until', None))
        
        if effective_from and effective_until and effective_from > effective_until:
            errors['effective_until'] = _('Effective until date must be after effective from date')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class StudentEnrollmentSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for StudentEnrollment model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    class_enrolled = PrimaryKeyRelatedUUIDField(
        queryset=Class.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='class_enrolled.display_name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    is_current = serializers.ReadOnlyField()
    enrollment_duration = serializers.ReadOnlyField()
    is_cbc_enrollment = serializers.ReadOnlyField()
    cbc_info = serializers.ReadOnlyField()
    academic_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = StudentEnrollment
        fields = [
            # Core Relationships
            'id', 'student', 'student_name', 'class_enrolled', 'class_name',
            'academic_year', 'academic_year_name', 'is_active',
            
            # Enrollment Information
            'enrollment_date', 'enrollment_number', 'status', 'status_changed_date',
            'status_reason', 'roll_number',
            
            # CBC-Specific Information
            'cbc_pathway_selection', 'senior_track_selection', 'portfolio_status',
            'community_service_hours_completed',
            
            # House and Extracurricular
            'house', 'extracurricular_activities',
            
            # Previous School Information
            'previous_school', 'transfer_certificate', 'previous_performance',
            
            # Financial Information
            'fee_status', 'fee_arrears',
            
            # Parent/Guardian Information
            'parent_engagement_level',
            
            # Special Needs and Support
            'special_needs', 'support_services', 'academic_support_level',
            
            # Performance Tracking
            'average_performance', 'attendance_percentage',
            
            # Metadata
            'remarks', 'enrollment_metadata',
            
            # Computed fields
            'is_current', 'enrollment_duration', 'is_cbc_enrollment', 'cbc_info',
            'academic_progress',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollment_number', 'status_changed_date', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate enrollment data."""
        errors = {}
        
        student = data.get('student', getattr(self.instance, 'student', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        class_enrolled = data.get('class_enrolled', getattr(self.instance, 'class_enrolled', None))
        roll_number = data.get('roll_number', getattr(self.instance, 'roll_number', None))
        
        # Check duplicate enrollment
        if student and academic_year:
            duplicate_enrollment = StudentEnrollment.objects.filter(
                student=student,
                academic_year=academic_year
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if duplicate_enrollment:
                errors['academic_year'] = _('Student is already enrolled for this academic year')
        
        # Check roll number uniqueness
        if roll_number and class_enrolled and academic_year:
            duplicate_roll = StudentEnrollment.objects.filter(
                academic_year=academic_year,
                class_enrolled=class_enrolled,
                roll_number=roll_number
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if duplicate_roll:
                errors['roll_number'] = _('Roll number must be unique within the class for this academic year')
        
        # CBC validation
        if class_enrolled and class_enrolled.is_cbc_class:
            if class_enrolled.education_level == 'senior_school' and not data.get('cbc_pathway_selection'):
                errors['cbc_pathway_selection'] = _('CBC pathway selection is required for Senior School enrollment')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create enrollment with auto-generated roll number if not provided."""
        if 'roll_number' not in validated_data:
            class_enrolled = validated_data['class_enrolled']
            academic_year = validated_data['academic_year']
            
            last_roll = StudentEnrollment.objects.filter(
                class_enrolled=class_enrolled,
                academic_year=academic_year
            ).exclude(roll_number=None).order_by('-roll_number').first()
            
            validated_data['roll_number'] = (last_roll.roll_number + 1) if last_roll else 1
        
        return super().create(validated_data)


class StudentClassAssignmentSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for StudentClassAssignment model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    class_assigned = PrimaryKeyRelatedUUIDField(
        queryset=Class.objects.all(),
        required=True
    )
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    assigned_teacher = PrimaryKeyRelatedUUIDField(
        queryset=TeacherProfile.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='class_assigned.display_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True) if Subject else None
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    is_current = serializers.ReadOnlyField()
    assignment_duration = serializers.ReadOnlyField()
    is_cbc_assignment = serializers.ReadOnlyField()
    subject_info = serializers.ReadOnlyField()
    
    class Meta:
        model = StudentClassAssignment
        fields = [
            # Core Relationships
            'id', 'student', 'student_name', 'class_assigned', 'class_name',
            'subject', 'subject_name', 'academic_year', 'academic_year_name',
            'assigned_teacher', 'teacher_name', 'is_active',
            
            # Assignment Details
            'assignment_date', 'effective_from', 'effective_until', 'status',
            'status_changed_date',
            
            # Academic Information
            'seating_position', 'locker_number', 'desk_number',
            'is_core_subject', 'is_elective_subject', 'competency_tracking_enabled',
            'project_work_assigned',
            
            # Performance Tracking
            'performance_level', 'last_assessment_date',
            
            # Additional Information
            'learning_style', 'special_accommodations',
            
            # Metadata
            'remarks', 'assignment_metadata',
            
            # Computed fields
            'is_current', 'assignment_duration', 'is_cbc_assignment', 'subject_info',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status_changed_date', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def get_teacher_name(self, obj):
        """Get teacher's full name."""
        if obj.assigned_teacher and obj.assigned_teacher.user:
            return obj.assigned_teacher.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate assignment data."""
        errors = {}
        
        # Date validation
        effective_from = data.get('effective_from', getattr(self.instance, 'effective_from', None))
        effective_until = data.get('effective_until', getattr(self.instance, 'effective_until', None))
        
        if effective_from and effective_until and effective_from > effective_until:
            errors['effective_from'] = _('Effective from date must be before effective until date')
            errors['effective_until'] = _('Effective until date must be after effective from date')
        
        # Duplicate assignment validation
        student = data.get('student', getattr(self.instance, 'student', None))
        class_assigned = data.get('class_assigned', getattr(self.instance, 'class_assigned', None))
        subject = data.get('subject', getattr(self.instance, 'subject', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        
        if student and class_assigned and subject and academic_year:
            duplicate_assignment = StudentClassAssignment.objects.filter(
                student=student,
                class_assigned=class_assigned,
                subject=subject,
                academic_year=academic_year,
                status='active'
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if duplicate_assignment:
                errors['subject'] = _('Student already has an active assignment for this subject')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


# ============================================================================
# PLANNING AND CURRICULUM SERIALIZERS
# ============================================================================

class LessonPlanSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for LessonPlan model."""
    
    # Related fields
    teacher = PrimaryKeyRelatedUUIDField(
        queryset=TeacherProfile.objects.all(),
        required=True
    )
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    sub_topic = PrimaryKeyRelatedUUIDField(
        queryset=SubTopic.objects.all(),
        required=True
    )
    class_assigned = PrimaryKeyRelatedUUIDField(
        queryset=Class.objects.all(),
        required=True
    )
    
    # Computed fields
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    sub_topic_name = serializers.CharField(source='sub_topic.full_name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.display_name', read_only=True)
    
    lesson_duration_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = LessonPlan
        fields = [
            # Basic Information
            'id', 'title', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'sub_topic', 'sub_topic_name', 'class_assigned', 'class_name',
            'date', 'duration_minutes', 'is_active',
            
            # Lesson Components
            'learning_objectives', 'materials_needed', 'introduction',
            'development', 'conclusion',
            
            # Assessment
            'assessment_methods', 'differentiation_strategies',
            
            # Homework/Follow-up
            'homework_assignment', 'next_lesson_preview',
            
            # Status
            'is_completed', 'actual_duration_minutes',
            
            # Reflection
            'teacher_reflection',
            
            # Computed fields
            'lesson_duration_hours',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        """Get teacher's full name."""
        if obj.teacher and obj.teacher.user:
            return obj.teacher.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate lesson plan data."""
        errors = {}
        
        # Duration validation
        duration_minutes = data.get('duration_minutes', getattr(self.instance, 'duration_minutes', 40))
        if duration_minutes < 5 or duration_minutes > 120:
            errors['duration_minutes'] = _('Duration must be between 5 and 120 minutes')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class SyllabusSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Syllabus model."""
    
    # Related fields
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    approved_by = PrimaryKeyRelatedUUIDField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    total_topics = serializers.ReadOnlyField()
    total_weeks = serializers.ReadOnlyField()
    competency_coverage = serializers.ReadOnlyField()
    
    class Meta:
        model = Syllabus
        fields = [
            # Basic Information
            'id', 'subject', 'subject_name', 'academic_year', 'academic_year_name',
            'title', 'version', 'is_active',
            
            # Curriculum Standards
            'curriculum_standards', 'topics', 'objectives', 'methodology',
            
            # Learning Resources
            'recommended_books', 'teaching_resources',
            
            # Assessment Framework
            'assessment_framework',
            
            # Competency Mapping
            'competency_mapping', 'cbc_competencies', 'project_requirements',
            
            # Status
            'is_approved', 'approved_by', 'approved_by_name', 'approval_date',
            
            # Metadata
            'syllabus_file', 'notes',
            
            # Computed fields
            'total_topics', 'total_weeks', 'competency_coverage',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate syllabus data."""
        errors = {}
        
        # Validate topics structure
        topics = data.get('topics', getattr(self.instance, 'topics', []))
        if topics and not isinstance(topics, list):
            errors['topics'] = _('Topics must be a list')
        
        # Validate version uniqueness
        subject = data.get('subject', getattr(self.instance, 'subject', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        version = data.get('version', getattr(self.instance, 'version', None))
        
        if subject and academic_year and version:
            duplicate_syllabus = Syllabus.objects.filter(
                subject=subject,
                academic_year=academic_year,
                version=version
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if duplicate_syllabus:
                errors['version'] = _('A syllabus with this version already exists for this subject and academic year')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create syllabus with auto-generated version if not provided."""
        if not validated_data.get('version'):
            subject = validated_data['subject']
            academic_year = validated_data['academic_year']
            
            latest = Syllabus.objects.filter(
                subject=subject,
                academic_year=academic_year
            ).order_by('-version').first()
            
            if latest and latest.version:
                try:
                    version_num = float(latest.version)
                    validated_data['version'] = f"{version_num + 0.1:.1f}"
                except ValueError:
                    validated_data['version'] = '1.0'
            else:
                validated_data['version'] = '1.0'
        
        return super().create(validated_data)


class AcademicEventSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for AcademicEvent model."""
    
    # Related fields
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    term = PrimaryKeyRelatedUUIDField(
        queryset=AcademicTerm.objects.all(),
        required=False,
        allow_null=True
    )
    organizer = PrimaryKeyRelatedUUIDField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.get_name_display', read_only=True)
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    
    duration_hours = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = AcademicEvent
        fields = [
            # Basic Information
            'id', 'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'is_active',
            
            # Academic Context
            'academic_year', 'academic_year_name', 'term', 'term_name',
            
            # Participants
            'target_audience', 'organizer', 'organizer_name',
            
            # Status
            'is_published', 'is_cancelled', 'priority',
            
            # Resources
            'resources', 'requires_attendance', 'reminder_days_before',
            
            # Computed fields
            'duration_hours', 'is_upcoming', 'is_ongoing', 'is_past',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate event data."""
        errors = {}
        
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        if start_date and end_date and start_date >= end_date:
            errors['end_date'] = _('End date must be after start date')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class StreamSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for Stream model."""
    
    # Related fields
    core_subjects = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        many=True,
        required=False
    )
    elective_subjects = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        many=True,
        required=False
    )
    
    # Computed fields
    core_subjects_count = serializers.SerializerMethodField()
    elective_subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Stream
        fields = [
            # Basic Information
            'id', 'name', 'code', 'description', 'is_active',
            
            # Academic Information
            'education_level', 'curriculum', 'pathway',
            
            # Requirements
            'minimum_requirements', 'career_pathways',
            
            # Subjects
            'core_subjects', 'elective_subjects',
            
            # Computed counts
            'core_subjects_count', 'elective_subjects_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_core_subjects_count(self, obj):
        """Get count of core subjects."""
        return obj.core_subjects.count()
    
    def get_elective_subjects_count(self, obj):
        """Get count of elective subjects."""
        return obj.elective_subjects.count()
    
    def validate_code(self, value):
        """Validate stream code."""
        if not value.isalnum():
            raise serializers.ValidationError(_('Stream code must be alphanumeric'))
        return value


# ============================================================================
# CBC-SPECIFIC SERIALIZERS
# ============================================================================

class CBCAssessmentSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for CBCAssessment model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    class_assigned = PrimaryKeyRelatedUUIDField(
        queryset=Class.objects.all(),
        required=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.display_name', read_only=True)
    
    total_score = serializers.ReadOnlyField()
    is_national_exam = serializers.ReadOnlyField()
    
    class Meta:
        model = CBCAssessment
        fields = [
            # Relationships
            'id', 'student', 'student_name', 'subject', 'subject_name',
            'academic_year', 'academic_year_name', 'class_assigned', 'class_name',
            'is_active',
            
            # Assessment details
            'assessment_type', 'assessment_date',
            
            # Competency-based scores
            'competency_scores', 'practical_score', 'theory_score', 'project_score',
            
            # CBC descriptors
            'proficiency_level', 'teacher_comments', 'portfolio_evidence',
            
            # Computed fields
            'total_score', 'is_national_exam',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate CBC assessment data."""
        errors = {}
        
        # Validate scores
        practical_score = data.get('practical_score', getattr(self.instance, 'practical_score', None))
        theory_score = data.get('theory_score', getattr(self.instance, 'theory_score', None))
        project_score = data.get('project_score', getattr(self.instance, 'project_score', None))
        
        if practical_score and (practical_score < 0 or practical_score > 100):
            errors['practical_score'] = _('Practical score must be between 0 and 100')
        
        if theory_score and (theory_score < 0 or theory_score > 100):
            errors['theory_score'] = _('Theory score must be between 0 and 100')
        
        if project_score and (project_score < 0 or project_score > 100):
            errors['project_score'] = _('Project score must be between 0 and 100')
        
        # Validate competency scores structure
        competency_scores = data.get('competency_scores', getattr(self.instance, 'competency_scores', {}))
        if not isinstance(competency_scores, dict):
            errors['competency_scores'] = _('Competency scores must be a dictionary')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class CBCPortfolioSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for CBCPortfolio model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    artifacts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = CBCPortfolio
        fields = [
            # Relationships
            'id', 'student', 'student_name', 'academic_year', 'academic_year_name',
            'is_active',
            
            # Portfolio details
            'portfolio_title', 'portfolio_type', 'description', 'artifacts',
            'skills_demonstrated', 'reflection', 'teacher_feedback',
            
            # Status
            'submission_date', 'is_complete',
            
            # Computed fields
            'artifacts_count',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submission_date', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def validate_artifacts(self, value):
        """Validate artifacts structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError(_('Artifacts must be a list'))
        
        for artifact in value:
            if not isinstance(artifact, dict):
                raise serializers.ValidationError(_('Each artifact must be an object'))
            
            if 'name' not in artifact or 'type' not in artifact:
                raise serializers.ValidationError(_('Each artifact must have a name and type'))
        
        return value


class PathwaySelectionSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for PathwaySelection model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    approved_by = PrimaryKeyRelatedUUIDField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = PathwaySelection
        fields = [
            # Relationships
            'id', 'student', 'student_name', 'academic_year', 'academic_year_name',
            'is_active',
            
            # Pathways
            'preferred_pathway', 'alternative_pathway', 'senior_track',
            
            # Selection details
            'selection_date', 'is_approved', 'approved_by', 'approval_date',
            
            # Rationale
            'student_statement', 'parent_consent', 'teacher_recommendation',
            
            # Career aspirations
            'career_interests',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'selection_date', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate pathway selection data."""
        errors = {}
        
        # Validate that alternative pathway is different from preferred pathway
        preferred_pathway = data.get('preferred_pathway', getattr(self.instance, 'preferred_pathway', None))
        alternative_pathway = data.get('alternative_pathway', getattr(self.instance, 'alternative_pathway', None))
        
        if preferred_pathway and alternative_pathway and preferred_pathway == alternative_pathway:
            errors['alternative_pathway'] = _('Alternative pathway must be different from preferred pathway')
        
        # Validate senior track for senior school
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        if academic_year and academic_year.is_cbc:
            if preferred_pathway and not data.get('senior_track'):
                errors['senior_track'] = _('Senior track is required when a pathway is selected')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class CompetencyTrackingSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for CompetencyTracking model."""
    
    # Related fields
    student = PrimaryKeyRelatedUUIDField(
        queryset=StudentProfile.objects.all(),
        required=True
    )
    academic_year = PrimaryKeyRelatedUUIDField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    
    # Computed fields
    student_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    has_improved = serializers.ReadOnlyField()
    
    class Meta:
        model = CompetencyTracking
        fields = [
            # Relationships
            'id', 'student', 'student_name', 'academic_year', 'academic_year_name',
            'is_active',
            
            # Competency details
            'competency_area', 'baseline_level', 'current_level', 'target_level',
            
            # Evidence and tracking
            'evidence', 'teacher_comments', 'last_assessed', 'next_review',
            
            # Computed fields
            'has_improved',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Get student's full name."""
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return None
    
    def validate(self, data):
        """Validate competency tracking data."""
        errors = {}
        
        # Validate level progression
        baseline_level = data.get('baseline_level', getattr(self.instance, 'baseline_level', None))
        current_level = data.get('current_level', getattr(self.instance, 'current_level', None))
        target_level = data.get('target_level', getattr(self.instance, 'target_level', None))
        
        levels = ['beginning', 'developing', 'proficient', 'advanced']
        
        if baseline_level and current_level:
            try:
                baseline_index = levels.index(baseline_level)
                current_index = levels.index(current_level)
                
                if current_index < baseline_index:
                    errors['current_level'] = _('Current level cannot be lower than baseline level')
            except ValueError:
                pass
        
        if current_level and target_level:
            try:
                current_index = levels.index(current_level)
                target_index = levels.index(target_level)
                
                if target_index < current_index:
                    errors['target_level'] = _('Target level cannot be lower than current level')
            except ValueError:
                pass
        
        # Validate evidence structure
        evidence = data.get('evidence', getattr(self.instance, 'evidence', []))
        if not isinstance(evidence, list):
            errors['evidence'] = _('Evidence must be a list')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class CurriculumMappingSerializer(AuditFieldsMixin, serializers.ModelSerializer):
    """Serializer for CurriculumMapping model."""
    
    # Related fields
    subject = PrimaryKeyRelatedUUIDField(
        queryset=Subject.objects.all(),
        required=True
    )
    
    # Computed fields
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    curriculum_system_display = serializers.CharField(source='get_curriculum_system_display', read_only=True)
    grade_level_display = serializers.CharField(source='get_grade_level_display', read_only=True)
    
    class Meta:
        model = CurriculumMapping
        fields = [
            # Basic Information
            'id', 'curriculum_system', 'curriculum_system_display', 'grade_level',
            'grade_level_display', 'subject', 'subject_name', 'is_active',
            
            # Standards mapping
            'standard_code', 'standard_description',
            
            # Competency alignment
            'aligned_competencies', 'learning_outcomes', 'assessment_criteria',
            
            # Resources and links
            'resources', 'international_equivalents',
            
            # Audit fields
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate curriculum mapping data."""
        errors = {}
        
        # Validate uniqueness
        curriculum_system = data.get('curriculum_system', getattr(self.instance, 'curriculum_system', None))
        grade_level = data.get('grade_level', getattr(self.instance, 'grade_level', None))
        subject = data.get('subject', getattr(self.instance, 'subject', None))
        standard_code = data.get('standard_code', getattr(self.instance, 'standard_code', None))
        
        if curriculum_system and grade_level and subject and standard_code:
            duplicate_mapping = CurriculumMapping.objects.filter(
                curriculum_system=curriculum_system,
                grade_level=grade_level,
                subject=subject,
                standard_code=standard_code
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if duplicate_mapping:
                errors['standard_code'] = _('A mapping with this standard code already exists for this combination')
        
        # Validate JSON fields
        aligned_competencies = data.get('aligned_competencies', getattr(self.instance, 'aligned_competencies', []))
        if not isinstance(aligned_competencies, list):
            errors['aligned_competencies'] = _('Aligned competencies must be a list')
        
        learning_outcomes = data.get('learning_outcomes', getattr(self.instance, 'learning_outcomes', []))
        if not isinstance(learning_outcomes, list):
            errors['learning_outcomes'] = _('Learning outcomes must be a list')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


# ============================================================================
# DETAILED SERIALIZERS WITH NESTED RELATIONSHIPS
# ============================================================================

class AcademicYearDetailSerializer(AcademicYearSerializer):
    """Detailed serializer for Academic Year with nested terms and classes."""
    
    terms = AcademicTermSerializer(many=True, read_only=True)
    classes = ClassMinimalSerializer(many=True, read_only=True)
    events = AcademicEventSerializer(many=True, read_only=True)
    statistics = serializers.SerializerMethodField()
    
    class Meta(AcademicYearSerializer.Meta):
        fields = AcademicYearSerializer.Meta.fields + ['terms', 'classes', 'events', 'statistics']
    
    def get_statistics(self, obj):
        """Get academic year statistics."""
        return obj.get_statistics()


class AcademicTermDetailSerializer(AcademicTermSerializer):
    """Detailed serializer for Academic Term with nested events."""
    
    events = AcademicEventSerializer(many=True, read_only=True)
    lesson_plans = LessonPlanSerializer(many=True, read_only=True)
    
    class Meta(AcademicTermSerializer.Meta):
        fields = AcademicTermSerializer.Meta.fields + ['events', 'lesson_plans']


class SubjectDetailSerializer(SubjectSerializer):
    """Detailed serializer for Subject with nested syllabus and assignments."""
    
    syllabi = SyllabusSerializer(many=True, read_only=True)
    subject_assignments = SubjectAssignmentSerializer(many=True, read_only=True)
    sub_topics = SubTopicMinimalSerializer(many=True, read_only=True)
    prerequisite_details = SubjectMinimalSerializer(source='prerequisites', many=True, read_only=True)
    
    class Meta(SubjectSerializer.Meta):
        fields = SubjectSerializer.Meta.fields + [
            'syllabi', 'subject_assignments', 'sub_topics', 'prerequisite_details'
        ]


class ClassDetailSerializer(ClassSerializer):
    """Detailed serializer for Class with nested enrollments and assignments."""
    
    enrollments = StudentEnrollmentSerializer(many=True, read_only=True)
    subject_assignments = SubjectAssignmentSerializer(many=True, read_only=True)
    lesson_plans = LessonPlanSerializer(many=True, read_only=True)
    class_teacher_details = TeacherMinimalSerializer(source='class_teacher', read_only=True)
    class_statistics = serializers.SerializerMethodField()
    
    class Meta(ClassSerializer.Meta):
        fields = ClassSerializer.Meta.fields + [
            'enrollments', 'subject_assignments', 'lesson_plans',
            'class_teacher_details', 'class_statistics'
        ]
    
    def get_class_statistics(self, obj):
        """Get class statistics."""
        return obj.get_class_statistics()


class SubTopicDetailSerializer(SubTopicSerializer):
    """Detailed serializer for SubTopic with nested lesson plans."""
    
    lesson_plans = LessonPlanSerializer(many=True, read_only=True)
    subject_details = SubjectMinimalSerializer(source='subject', read_only=True)
    
    class Meta(SubTopicSerializer.Meta):
        fields = SubTopicSerializer.Meta.fields + ['lesson_plans', 'subject_details']


class StudentEnrollmentDetailSerializer(StudentEnrollmentSerializer):
    """Detailed serializer for StudentEnrollment with nested assignments."""
    
    student_assignments = StudentClassAssignmentSerializer(many=True, read_only=True)
    student_details = StudentMinimalSerializer(source='student', read_only=True)
    class_details = ClassMinimalSerializer(source='class_enrolled', read_only=True)
    attendance_summary = serializers.SerializerMethodField()
    
    class Meta(StudentEnrollmentSerializer.Meta):
        fields = StudentEnrollmentSerializer.Meta.fields + [
            'student_assignments', 'student_details', 'class_details', 'attendance_summary'
        ]
    
    def get_attendance_summary(self, obj):
        """Get attendance summary."""
        return obj.get_attendance_summary()


# ============================================================================
# STATISTICS AND REPORT SERIALIZERS
# ============================================================================

class AcademicStatisticsSerializer(serializers.Serializer):
    """Serializer for academic statistics."""
    
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_subjects = serializers.IntegerField()
    active_academic_year = serializers.CharField(required=False, allow_null=True)
    current_term = serializers.CharField(required=False, allow_null=True)
    upcoming_events = serializers.IntegerField()
    enrollment_rate = serializers.FloatField()
    class_occupancy_rate = serializers.FloatField()
    cbc_students_count = serializers.IntegerField(required=False)
    portfolio_completion_rate = serializers.FloatField(required=False)


class ClassStatisticsSerializer(serializers.Serializer):
    """Serializer for class statistics."""
    
    class_id = serializers.UUIDField()
    class_name = serializers.CharField()
    display_name = serializers.CharField()
    total_students = serializers.IntegerField()
    capacity = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    subject_count = serializers.IntegerField()
    teacher_count = serializers.IntegerField()
    average_performance = serializers.FloatField(required=False, allow_null=True)
    attendance_rate = serializers.FloatField(required=False, allow_null=True)
    is_cbc_class = serializers.BooleanField()


class TeacherWorkloadSerializer(serializers.Serializer):
    """Serializer for teacher workload statistics."""
    
    teacher_id = serializers.UUIDField()
    teacher_name = serializers.CharField()
    total_periods = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_subjects = serializers.IntegerField()
    workload_percentage = serializers.FloatField()
    is_class_teacher = serializers.BooleanField()
    current_assignments = serializers.IntegerField()


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class BulkStudentEnrollmentSerializer(serializers.Serializer):
    """Serializer for bulk student enrollment."""
    
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of student profile IDs to enroll"
    )
    class_id = serializers.UUIDField()
    academic_year_id = serializers.UUIDField()
    enrollment_date = serializers.DateField(default=serializers.CreateOnlyDefault(timezone.now))
    assign_roll_numbers = serializers.BooleanField(default=True)


class BulkSubjectAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk subject assignment."""
    
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of teacher profile IDs to assign"
    )
    subject_id = serializers.UUIDField()
    class_id = serializers.UUIDField()
    academic_year_id = serializers.UUIDField()
    periods_per_week = serializers.IntegerField(default=5, min_value=1, max_value=20)


class BulkLessonPlanSerializer(serializers.Serializer):
    """Serializer for bulk lesson plan creation."""
    
    teacher_id = serializers.UUIDField()
    subject_id = serializers.UUIDField()
    class_id = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    duration_minutes = serializers.IntegerField(default=40, min_value=5, max_value=120)
    days_of_week = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        help_text="Days of week (0=Sunday, 6=Saturday)"
    )


# ============================================================================
# SEARCH AND FILTER SERIALIZERS
# ============================================================================

class AcademicSearchSerializer(serializers.Serializer):
    """Serializer for academic search parameters."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    academic_year = serializers.UUIDField(required=False)
    term = serializers.UUIDField(required=False)
    grade_level = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    curriculum = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class EnrollmentReportSerializer(serializers.Serializer):
    """Serializer for enrollment reports."""
    
    academic_year = serializers.UUIDField()
    grade_level = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    cbc_pathway = serializers.CharField(required=False)
    report_type = serializers.ChoiceField(
        choices=['summary', 'detailed', 'analytics', 'export'],
        default='summary'
    )
    format = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf'],
        default='json'
    )


# ============================================================================
# EXPORT AND IMPORT SERIALIZERS
# ============================================================================

class AcademicDataExportSerializer(serializers.Serializer):
    """Serializer for academic data export."""
    
    include_academic_years = serializers.BooleanField(default=True)
    include_terms = serializers.BooleanField(default=True)
    include_subjects = serializers.BooleanField(default=True)
    include_classes = serializers.BooleanField(default=True)
    include_enrollments = serializers.BooleanField(default=True)
    include_assignments = serializers.BooleanField(default=True)
    include_syllabi = serializers.BooleanField(default=True)
    include_cbc_data = serializers.BooleanField(default=True)
    
    format = serializers.ChoiceField(choices=['json', 'csv', 'excel'], default='json')
    academic_year = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    compress = serializers.BooleanField(default=False)


class AcademicDataImportSerializer(serializers.Serializer):
    """Serializer for academic data import."""
    
    file = serializers.FileField()
    format = serializers.ChoiceField(choices=['json', 'csv', 'excel'], default='json')
    academic_year = serializers.UUIDField(required=False)
    overwrite = serializers.BooleanField(default=False)
    validate_only = serializers.BooleanField(default=False)


# ============================================================================
# SETUP AND CONFIGURATION SERIALIZERS
# ============================================================================

class AcademicSetupRequirementsSerializer(serializers.Serializer):
    """Serializer for academic setup requirements check."""
    
    has_academic_years = serializers.BooleanField()
    has_terms = serializers.BooleanField()
    has_subjects = serializers.BooleanField()
    has_classes = serializers.BooleanField()
    has_enrollments = serializers.BooleanField()
    has_teachers = serializers.BooleanField()
    has_students = serializers.BooleanField()
    
    missing_items = serializers.ListField(child=serializers.CharField())
    setup_complete = serializers.BooleanField()
    
    current_academic_year = serializers.CharField(required=False, allow_null=True)
    current_term = serializers.CharField(required=False, allow_null=True)
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()


class QuickSetupSerializer(serializers.Serializer):
    """Serializer for quick academic setup."""
    
    academic_year_name = serializers.CharField(max_length=100)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    curriculum_system = serializers.ChoiceField(
        choices=AcademicYear.CURRICULUM_SYSTEMS,
        default='cbc_kenya'
    )
    
    create_terms = serializers.BooleanField(default=True)
    terms = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    create_sample_subjects = serializers.BooleanField(default=True)
    subject_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['core', 'elective', 'cbc_core']
    )
    
    create_sample_classes = serializers.BooleanField(default=True)
    grade_levels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['grade_1', 'grade_2', 'grade_3']
    )
    
    auto_configure = serializers.BooleanField(default=True)


class CBCConfigurationSerializer(serializers.Serializer):
    """Serializer for CBC configuration."""
    
    pathways = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('stem', 'STEM'),
            ('social_sciences', 'Social Sciences'),
            ('arts_sports', 'Arts & Sports')
        ]),
        default=['stem', 'social_sciences', 'arts_sports']
    )
    
    assessment_windows = serializers.DictField(default={
        'kpsea': {'grade': 6, 'month': 'November'},
        'kjsea': {'grade': 9, 'month': 'October'},
        'kcse': {'grade': 12, 'month': 'November'},
    })
    
    competency_areas = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('communication', 'Communication'),
            ('critical_thinking', 'Critical Thinking'),
            ('creativity', 'Creativity'),
            ('citizenship', 'Citizenship'),
            ('digital_literacy', 'Digital Literacy'),
            ('learning_to_learn', 'Learning to Learn'),
            ('self_efficacy', 'Self-efficacy'),
        ]),
        default=[
            'communication', 'critical_thinking', 'creativity',
            'citizenship', 'digital_literacy'
        ]
    )
    
    portfolio_required = serializers.BooleanField(default=True)
    community_service_hours = serializers.IntegerField(default=40, min_value=0, max_value=200)
    parental_engagement_required = serializers.BooleanField(default=True)
    
    senior_tracks = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


# ============================================================================
# VALIDATION AND UTILITY SERIALIZERS
# ============================================================================

class ValidationResultSerializer(serializers.Serializer):
    """Serializer for validation results."""
    
    is_valid = serializers.BooleanField()
    errors = serializers.DictField(required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)


class ImportResultSerializer(serializers.Serializer):
    """Serializer for import results."""
    
    success = serializers.BooleanField()
    imported_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.DictField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)


class SyncStatusSerializer(serializers.Serializer):
    """Serializer for sync status."""
    
    last_sync = serializers.DateTimeField()
    sync_type = serializers.CharField()
    status = serializers.ChoiceField(choices=['pending', 'in_progress', 'completed', 'failed'])
    processed_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField(), required=False)


# ============================================================================
# COMPREHENSIVE LIST SERIALIZERS
# ============================================================================

class AcademicListSerializer(serializers.Serializer):
    """Serializer for listing academic entities with counts."""
    
    academic_years = AcademicYearMinimalSerializer(many=True, read_only=True)
    terms = AcademicTermMinimalSerializer(many=True, read_only=True)
    subjects = SubjectMinimalSerializer(many=True, read_only=True)
    classes = ClassMinimalSerializer(many=True, read_only=True)
    streams = StreamSerializer(many=True, read_only=True)
    
    counts = serializers.DictField(read_only=True)
    current_academic_year = AcademicYearMinimalSerializer(read_only=True)
    current_term = AcademicTermMinimalSerializer(read_only=True)


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for academic dashboard summary."""
    
    academic_summary = AcademicStatisticsSerializer(read_only=True)
    recent_enrollments = StudentEnrollmentSerializer(many=True, read_only=True)
    upcoming_events = AcademicEventSerializer(many=True, read_only=True)
    class_occupancy = ClassStatisticsSerializer(many=True, read_only=True)
    teacher_workload = TeacherWorkloadSerializer(many=True, read_only=True)
    
    cbc_stats = serializers.DictField(read_only=True, required=False)
    attendance_summary = serializers.DictField(read_only=True)
    performance_trend = serializers.ListField(read_only=True)


# ============================================================================
# REQUEST/RESPONSE WRAPPER SERIALIZERS
# ============================================================================

class ApiResponseSerializer(serializers.Serializer):
    """Standard API response serializer."""
    
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)


class PaginatedResponseSerializer(serializers.Serializer):
    """Paginated API response serializer."""
    
    count = serializers.IntegerField()
    next = serializers.URLField(required=False, allow_null=True)
    previous = serializers.URLField(required=False, allow_null=True)
    results = serializers.ListField(child=serializers.DictField())
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()