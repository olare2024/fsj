"""
Serializers for Student Assignment models.
This file contains the StudentAssignmentMiniSerializer import that's used in the main serializers.py
"""

from rest_framework import serializers
from .models import StudentAssignment


class StudentAssignmentMiniSerializer(serializers.ModelSerializer):
    """
    Mini serializer for StudentAssignment model with essential fields only.
    This is the version that will be imported by serializers.py
    """
    
    # Student information
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_admission_no = serializers.SerializerMethodField(read_only=True)
    
    # Assignment information
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    # Calculated fields
    percentage = serializers.SerializerMethodField(read_only=True)
    is_late = serializers.BooleanField(source='is_late', read_only=True)
    days_late = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = [
            'id',
            'student',
            'student_name',
            'student_admission_no',
            'assignment',
            'assignment_title',
            'status',
            'submission_date',
            'marks_obtained',
            'final_marks',
            'grade',
            'percentage',
            'is_late',
            'days_late',
            'version',
            'graded_at',
            'created_at',
        ]
        read_only_fields = [
            'id', 'student', 'assignment', 'submission_date', 
            'created_at'
        ]
    
    def get_student_admission_no(self, obj):
        """Get student admission number"""
        try:
            # Try to get from student profile
            if hasattr(obj.student, 'student_profile'):
                return obj.student.student_profile.admission_no
            # Try to get from user profile
            if hasattr(obj.student, 'admission_number'):
                return obj.student.admission_number
        except Exception:
            pass
        return "N/A"
    
    def get_percentage(self, obj):
        """Calculate percentage from final marks"""
        if obj.final_marks and obj.assignment.total_marks:
            return (obj.final_marks / obj.assignment.total_marks) * 100
        return None
    
    def get_days_late(self, obj):
        """Calculate days late if applicable"""
        if obj.submission_date and obj.assignment.due_date:
            if obj.submission_date > obj.assignment.due_date:
                return (obj.submission_date - obj.assignment.due_date).days
        return 0


# Export the serializer
__all__ = ['StudentAssignmentMiniSerializer']