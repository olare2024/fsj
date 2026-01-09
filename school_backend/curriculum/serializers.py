from rest_framework import serializers
from .models import (
    Curriculum, CBCStrand, CBCSubStrand, ICSESubject,
    AmericanStandard, AmericanCourse, CurriculumMapping,
    CurriculumImplementation, LearningObjective, ResourceLibrary,
    ProfessionalDevelopment
)
from teachers.serializers import TeacherProfileSerializer
from academics.serializers import ClassSerializer, AcademicYearSerializer, SubjectSerializer

class CurriculumSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    
    class Meta:
        model = Curriculum
        fields = [
            'id', 'name', 'full_name', 'description', 'country_origin',
            'implementing_body', 'website', 'grade_levels', 'assessment_methods',
            'key_features', 'is_active', 'implementation_date', 'coordinator',
            'coordinator_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CBCStrandSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    
    class Meta:
        model = CBCStrand
        fields = [
            'id', 'curriculum', 'curriculum_name', 'learning_area', 'name', 'code',
            'description', 'grade_levels', 'core_competencies', 'learning_outcomes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CBCSubStrandSerializer(serializers.ModelSerializer):
    strand_name = serializers.CharField(source='strand.name', read_only=True)
    strand_code = serializers.CharField(source='strand.code', read_only=True)
    learning_area = serializers.CharField(source='strand.learning_area', read_only=True)
    
    class Meta:
        model = CBCSubStrand
        fields = [
            'id', 'strand', 'strand_name', 'strand_code', 'learning_area', 'name', 'code',
            'description', 'specific_learning_outcomes', 'key_inquiry_questions',
            'learning_resources', 'suggested_activities', 'assessment_methods',
            'assessment_rubrics', 'suggested_weeks', 'priority_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ICSESubjectSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    
    class Meta:
        model = ICSESubject
        fields = [
            'id', 'curriculum', 'curriculum_name', 'name', 'code', 'subject_group',
            'description', 'is_compulsory', 'has_practical', 'theory_marks',
            'practical_marks', 'total_marks', 'syllabus_content', 'prescribed_books',
            'reference_books', 'available_grades', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AmericanStandardSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    
    class Meta:
        model = AmericanStandard
        fields = [
            'id', 'curriculum', 'curriculum_name', 'domain', 'grade_level',
            'standard_code', 'description', 'cluster', 'category', 'complexity_level',
            'learning_objectives', 'essential_questions', 'vocabulary',
            'performance_indicators', 'assessment_ideas', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AmericanCourseSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    prerequisites_names = serializers.SerializerMethodField()
    
    class Meta:
        model = AmericanCourse
        fields = [
            'id', 'curriculum', 'curriculum_name', 'name', 'course_code',
            'course_type', 'credit_type', 'description', 'credits', 'grade_levels',
            'prerequisites', 'prerequisites_names', 'course_objectives',
            'units_of_study', 'learning_outcomes', 'assessment_methods',
            'required_materials', 'recommended_texts', 'online_resources',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_prerequisites_names(self, obj):
        return [f"{course.course_code} - {course.name}" for course in obj.prerequisites.all()]

class CurriculumMappingSerializer(serializers.ModelSerializer):
    source_curriculum_name = serializers.CharField(source='source_curriculum.get_name_display', read_only=True)
    target_curriculum_name = serializers.CharField(source='target_curriculum.get_name_display', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = CurriculumMapping
        fields = [
            'id', 'source_curriculum', 'source_curriculum_name', 'target_curriculum',
            'target_curriculum_name', 'source_component', 'source_identifier',
            'target_component', 'target_identifier', 'mapping_strength', 'notes',
            'confidence_level', 'is_verified', 'verified_by', 'verified_by_name',
            'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CurriculumImplementationSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    class_name = serializers.CharField(source='class_enrolled.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    lead_teacher_name = serializers.CharField(source='lead_teacher.user.get_full_name', read_only=True)
    supporting_teachers_names = serializers.SerializerMethodField()
    grading_system_name = serializers.CharField(source='grading_system_used.name', read_only=True)
    
    class Meta:
        model = CurriculumImplementation
        fields = [
            'id', 'curriculum', 'curriculum_name', 'class_enrolled', 'class_name',
            'academic_year', 'academic_year_name', 'implementation_date',
            'is_primary', 'implementation_status', 'textbooks_used',
            'digital_resources', 'teaching_aids', 'assessment_strategy',
            'grading_system_used', 'grading_system_name', 'lead_teacher',
            'lead_teacher_name', 'supporting_teachers', 'supporting_teachers_names',
            'progress_notes', 'challenges_faced', 'success_stories', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_supporting_teachers_names(self, obj):
        return [teacher.user.get_full_name() for teacher in obj.supporting_teachers.all()]

class LearningObjectiveSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = LearningObjective
        fields = [
            'id', 'curriculum', 'curriculum_name', 'subject', 'subject_name', 'code',
            'description', 'bloom_level', 'grade_levels', 'success_criteria',
            'assessment_methods', 'differentiation_strategies', 'cross_curricular_links',
            'real_world_connections', 'teaching_resources', 'learning_activities',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ResourceLibrarySerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = ResourceLibrary
        fields = [
            'id', 'curriculum', 'curriculum_name', 'resource_type', 'title',
            'description', 'author', 'publisher', 'publication_year', 'isbn',
            'resource_file', 'resource_url', 'access_notes', 'grade_levels',
            'subjects', 'topics', 'learning_objectives', 'is_approved',
            'approved_by', 'approved_by_name', 'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']

class ProfessionalDevelopmentSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    target_teachers_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfessionalDevelopment
        fields = [
            'id', 'curriculum', 'curriculum_name', 'title', 'development_type',
            'description', 'start_date', 'end_date', 'location', 'facilitator',
            'target_teachers', 'target_teachers_names', 'target_grades',
            'target_subjects', 'materials', 'resource_files', 'learning_objectives',
            'expected_outcomes', 'is_completed', 'attendance_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_target_teachers_names(self, obj):
        return [teacher.user.get_full_name() for teacher in obj.target_teachers.all()]

class CurriculumOverviewSerializer(serializers.Serializer):
    total_curricula = serializers.IntegerField()
    active_implementations = serializers.IntegerField()
    cbc_strands_count = serializers.IntegerField()
    icse_subjects_count = serializers.IntegerField()
    american_standards_count = serializers.IntegerField()
    resource_count = serializers.IntegerField()
    recent_implementations = CurriculumImplementationSerializer(many=True)

class CrossCurriculumAnalysisSerializer(serializers.Serializer):
    source_curriculum = CurriculumSerializer()
    target_curriculum = CurriculumSerializer()
    mapping_count = serializers.IntegerField()
    coverage_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    strong_mappings = serializers.IntegerField()
    weak_mappings = serializers.IntegerField()