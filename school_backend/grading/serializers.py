# grading/serializers.py - FIXED VERSION
from rest_framework import serializers
from django.db import transaction
from .models import (
    GradingScale, GradingPeriod, AssessmentType, Assessment,
    StudentGrade, SubjectGrade, ReportCard, Gradebook
)
# Since Student is part of User model, import User
from accounts.models import User
from academics.models import Subject, Class
from datetime import datetime

# Helper to get students
def get_student_queryset():
    """Get all student users"""
    return User.objects.filter(role=User.Role.STUDENT, is_active=True)

class GradingScaleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = GradingScale
        fields = [
            'id', 'name', 'description', 'min_score', 'max_score',
            'grade', 'grade_points', 'remark', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class GradingPeriodSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = GradingPeriod
        fields = [
            'id', 'name', 'term', 'academic_year', 'start_date', 'end_date',
            'is_active', 'is_finalized', 'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_current(self, obj):
        today = datetime.now().date()
        return obj.start_date <= today <= obj.end_date

class AssessmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType
        fields = ['id', 'name', 'code', 'description', 'weight', 'max_score', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class AssessmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    grading_period_name = serializers.CharField(source='grading_period.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    student_count = serializers.SerializerMethodField()
    graded_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'name', 'assessment_type', 'subject', 'subject_name',
            'class_level', 'class_level_name', 'grading_period', 'grading_period_name',
            'total_marks', 'passing_marks', 'assessment_date', 'due_date',
            'created_by', 'created_by_name', 'is_published', 'published_at',
            'student_count', 'graded_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'published_at', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.class_level.students.count()
    
    def get_graded_count(self, obj):
        return obj.student_grades.exclude(marks_obtained__isnull=True).count()

class BulkStudentGradeSerializer(serializers.Serializer):
    """Serializer for bulk grade entry"""
    assessment_id = serializers.IntegerField()
    grades = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate(self, data):
        # Validate assessment exists
        try:
            assessment = Assessment.objects.get(id=data['assessment_id'])
            data['assessment'] = assessment
        except Assessment.DoesNotExist:
            raise serializers.ValidationError("Assessment not found")
        
        # Validate grades structure
        for grade_data in data['grades']:
            if 'student_id' not in grade_data:
                raise serializers.ValidationError("Each grade must have student_id")
            if 'marks_obtained' not in grade_data:
                raise serializers.ValidationError("Each grade must have marks_obtained")
        
        return data

class StudentGradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_adm_no = serializers.CharField(source='student.admission_number', read_only=True)
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    subject_name = serializers.CharField(source='assessment.subject.name', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentGrade
        fields = [
            'id', 'student', 'student_name', 'student_adm_no',
            'assessment', 'assessment_name', 'subject_name',
            'marks_obtained', 'percentage', 'grade', 'grade_points', 'remark',
            'is_absent', 'is_exempted', 'is_late_submission',
            'graded_by', 'graded_by_name', 'graded_at',
            'comments', 'needs_improvement', 'created_at', 'updated_at'
        ]
        read_only_fields = ['percentage', 'grade', 'grade_points', 'remark', 'graded_by', 'graded_at']




class SubjectGradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_adm_no = serializers.CharField(source='student.admission_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    grading_period_name = serializers.CharField(source='grading_period.name', read_only=True)
    finalized_by_name = serializers.CharField(source='finalized_by.get_full_name', read_only=True)
    
    class Meta:
        model = SubjectGrade
        fields = [
            'id', 'student', 'student_name', 'student_adm_no',
            'subject', 'subject_name', 'class_level', 'class_level_name',
            'grading_period', 'grading_period_name',
            'total_marks', 'marks_obtained', 'percentage', 'grade', 'grade_points', 'remark',
            'rank_in_class', 'rank_in_subject',
            'teacher_comments', 'principal_comments',
            'is_finalized', 'finalized_by', 'finalized_by_name', 'finalized_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_finalized', 'finalized_by', 'finalized_at']

class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_adm_no = serializers.CharField(source='student.admission_number', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    grading_period_name = serializers.CharField(source='grading_period.name', read_only=True)
    published_by_name = serializers.CharField(source='published_by.get_full_name', read_only=True)
    subject_grades = SubjectGradeSerializer(many=True, read_only=True, source='student.subject_grades.filter')
    
    class Meta:
        model = ReportCard
        fields = [
            'id', 'student', 'student_name', 'student_adm_no',
            'grading_period', 'grading_period_name',
            'class_level', 'class_level_name',
            'total_subjects', 'total_marks', 'marks_obtained',
            'overall_percentage', 'overall_grade', 'gpa',
            'attendance_days', 'days_present', 'attendance_percentage',
            'class_position', 'stream_position', 'overall_position',
            'teacher_comments', 'principal_comments', 'parent_comments',
            'status', 'published_by', 'published_by_name', 'published_at',
            'subject_grades', 'created_at', 'updated_at'
        ]
        read_only_fields = ['published_by', 'published_at']

class GradebookSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    grading_period_name = serializers.CharField(source='grading_period.name', read_only=True)
    student_count = serializers.SerializerMethodField()
    assessment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Gradebook
        fields = [
            'id', 'teacher', 'teacher_name',
            'subject', 'subject_name',
            'class_level', 'class_level_name',
            'grading_period', 'grading_period_name',
            'is_published', 'published_at', 'last_updated',
            'student_count', 'assessment_count'
        ]
    
    def get_student_count(self, obj):
        return obj.class_level.students.count()
    
    def get_assessment_count(self, obj):
        return Assessment.objects.filter(
            subject=obj.subject,
            class_level=obj.class_level,
            grading_period=obj.grading_period
        ).count()

class GradeStatisticsSerializer(serializers.Serializer):
    """Serializer for grade statistics"""
    total_students = serializers.IntegerField()
    total_assessments = serializers.IntegerField()
    average_percentage = serializers.FloatField()
    highest_percentage = serializers.FloatField()
    lowest_percentage = serializers.FloatField()
    grade_distribution = serializers.DictField()
    pass_rate = serializers.FloatField()

class PerformanceTrendSerializer(serializers.Serializer):
    """Serializer for performance trends"""
    grading_period = serializers.CharField()
    average_percentage = serializers.FloatField()
    student_count = serializers.IntegerField()
    top_performer = serializers.CharField()
    top_percentage = serializers.FloatField()