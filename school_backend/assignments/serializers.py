# assignments/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging
from .models import (
    Assignment, StudentAssignment, AssignmentCategory,
    AssignmentGroup, GroupMembership, AssignmentComment,
    AssignmentAnalytics, AssignmentReminder
)
from academics.models import Subject, Class, AcademicYear, AcademicTerm
from accounts.models import User

logger = logging.getLogger(__name__)

User = get_user_model()


# ==================== BASE SERIALIZERS ====================

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for display purposes"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'full_name', 'profile_picture']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class SubjectMinimalSerializer(serializers.ModelSerializer):
    """Minimal subject serializer"""
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'classification']
        read_only_fields = fields


class ClassroomMinimalSerializer(serializers.ModelSerializer):
    """Minimal classroom serializer"""
    class Meta:
        model = Class
        fields = ['id', 'name', 'room_number', 'capacity']
        read_only_fields = fields


class StreamMinimalSerializer(serializers.ModelSerializer):
    """Minimal stream serializer"""
    class Meta:
        model = Class
        fields = ['id', 'name', 'code']
        read_only_fields = fields


class AcademicYearMinimalSerializer(serializers.ModelSerializer):
    """Minimal academic year serializer"""
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'code', 'start_date', 'end_date', 'is_current']
        read_only_fields = fields


class AcademicTermMinimalSerializer(serializers.ModelSerializer):
    """Minimal academic term serializer"""
    class Meta:
        model = AcademicTerm
        fields = ['id', 'name', 'term_number', 'start_date', 'end_date', 'is_current']
        read_only_fields = fields


# ==================== ASSIGNMENT CATEGORY SERIALIZERS ====================

class AssignmentCategorySerializer(serializers.ModelSerializer):
    """Full Assignment Category serializer"""
    assignment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentCategory
        fields = [
            'id', 'name', 'description', 'color', 'icon',
            'curriculum', 'education_level', 'assignment_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assignment_count']
    
    def get_assignment_count(self, obj):
        return obj.assignment_set.count()


class AssignmentCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assignment categories"""
    class Meta:
        model = AssignmentCategory
        fields = [
            'name', 'description', 'color', 'icon',
            'curriculum', 'education_level', 'is_active'
        ]
    
    def validate_color(self, value):
        """Validate hex color code"""
        if not value.startswith('#'):
            raise serializers.ValidationError("Color must be a hex code starting with #")
        return value
    
    def validate_name(self, value):
        """Ensure category name is unique"""
        if AssignmentCategory.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists")
        return value


# ==================== ASSIGNMENT SERIALIZERS ====================

class AssignmentListSerializer(serializers.ModelSerializer):
    """List view serializer for assignments"""
    subject = SubjectMinimalSerializer(read_only=True)
    teacher = UserMinimalSerializer(read_only=True)
    classroom = ClassroomMinimalSerializer(read_only=True)
    stream = StreamMinimalSerializer(read_only=True)
    academic_year = AcademicYearMinimalSerializer(read_only=True)
    term = AcademicTermMinimalSerializer(read_only=True)
    category = AssignmentCategorySerializer(read_only=True)
    
    # Dynamic fields
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    is_due_soon = serializers.SerializerMethodField()
    submission_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'assignment_type', 'category',
            'subject', 'teacher', 'classroom', 'stream',
            'academic_year', 'term', 'curriculum',
            'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
            'estimated_completion_time', 'status', 'is_group_assignment',
            'views_count', 'average_score', 'completion_rate',
            'days_until_due', 'is_overdue', 'is_due_soon',
            'submission_stats', 'created_at', 'published_at'
        ]
        read_only_fields = fields
    
    def get_days_until_due(self, obj):
        return obj.days_until_due
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_is_due_soon(self, obj):
        return obj.is_due_soon
    
    def get_submission_stats(self, obj):
        return obj.submission_stats


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Detailed view serializer for assignments"""
    subject = SubjectMinimalSerializer(read_only=True)
    teacher = UserMinimalSerializer(read_only=True)
    classroom = ClassroomMinimalSerializer(read_only=True)
    stream = StreamMinimalSerializer(read_only=True)
    academic_year = AcademicYearMinimalSerializer(read_only=True)
    term = AcademicTermMinimalSerializer(read_only=True)
    category = AssignmentCategorySerializer(read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
    approved_by = UserMinimalSerializer(read_only=True)
    
    # Dynamic fields
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    is_due_soon = serializers.SerializerMethodField()
    submission_stats = serializers.SerializerMethodField()
    grade_summary = serializers.SerializerMethodField()
    can_be_published = serializers.SerializerMethodField()
    requires_approval = serializers.SerializerMethodField()
    teacher_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'assignment_type', 'category',
            'subject', 'teacher', 'classroom', 'stream',
            'academic_year', 'term', 'curriculum',
            'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
            'estimated_completion_time', 'instructions', 'learning_objectives',
            'resources', 'rubric', 'competencies', 'core_competencies',
            'created_by', 'attachment', 'additional_files',
            'allow_late_submission', 'late_submission_penalty',
            'allow_resubmission', 'max_resubmissions', 'require_approval',
            'is_group_assignment', 'max_group_size',
            'status', 'published_at', 'closed_at',
            'views_count', 'average_score', 'completion_rate',
            'approved_by', 'approved_at',
            'days_until_due', 'is_overdue', 'is_due_soon',
            'submission_stats', 'grade_summary', 'can_be_published',
            'requires_approval', 'teacher_stats',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_days_until_due(self, obj):
        return obj.days_until_due
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_is_due_soon(self, obj):
        return obj.is_due_soon
    
    def get_submission_stats(self, obj):
        return obj.submission_stats
    
    def get_grade_summary(self, obj):
        return obj.grade_summary
    
    def get_can_be_published(self, obj):
        return obj.can_be_published
    
    def get_requires_approval(self, obj):
        return obj.requires_approval
    
    def get_teacher_stats(self, obj):
        return obj.get_teacher_stats()


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assignments"""
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'assignment_type', 'category',
            'subject', 'classroom', 'stream', 'academic_year', 'term',
            'curriculum', 'due_date', 'total_marks', 'passing_marks',
            'difficulty_level', 'estimated_completion_time',
            'instructions', 'learning_objectives', 'resources', 'rubric',
            'competencies', 'core_competencies',
            'allow_late_submission', 'late_submission_penalty',
            'allow_resubmission', 'max_resubmissions', 'require_approval',
            'is_group_assignment', 'max_group_size', 'status'
        ]
    
    def validate(self, data):
        """Validate assignment data"""
        # Ensure due date is in the future
        if data.get('due_date') and data['due_date'] < timezone.now():
            raise serializers.ValidationError({
                'due_date': 'Due date must be in the future'
            })
        
        # Ensure passing marks are less than total marks
        if data.get('passing_marks') and data.get('total_marks'):
            if data['passing_marks'] > data['total_marks']:
                raise serializers.ValidationError({
                    'passing_marks': 'Passing marks cannot exceed total marks'
                })
        
        # Validate group assignment settings
        if data.get('is_group_assignment'):
            if not data.get('classroom'):
                raise serializers.ValidationError({
                    'classroom': 'Group assignments require a classroom'
                })
            if data.get('max_group_size', 1) < 2:
                raise serializers.ValidationError({
                    'max_group_size': 'Group assignments require at least 2 students per group'
                })
        
        return data
    
    def create(self, validated_data):
        """Create assignment with teacher and created_by"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['teacher'] = request.user
            validated_data['created_by'] = request.user
        
        # Set default status to draft if not provided
        if 'status' not in validated_data:
            validated_data['status'] = 'draft'
        
        assignment = Assignment.objects.create(**validated_data)
        
        # Log creation
        logger.info(f"Assignment created: {assignment.title} by {request.user if request else 'Unknown'}")
        
        return assignment


class AssignmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating assignments"""
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'assignment_type', 'category',
            'subject', 'classroom', 'stream', 'academic_year', 'term',
            'curriculum', 'due_date', 'total_marks', 'passing_marks',
            'difficulty_level', 'estimated_completion_time',
            'instructions', 'learning_objectives', 'resources', 'rubric',
            'competencies', 'core_competencies',
            'allow_late_submission', 'late_submission_penalty',
            'allow_resubmission', 'max_resubmissions', 'require_approval',
            'is_group_assignment', 'max_group_size', 'status'
        ]
    
    def validate(self, data):
        """Validate update data"""
        # Get the instance being updated
        instance = self.instance
        
        # Check if assignment can be modified (not closed or archived)
        if instance.status in ['closed', 'graded', 'archived']:
            raise serializers.ValidationError({
                'status': f'Cannot modify assignment with status: {instance.get_status_display()}'
            })
        
        # Validate due date
        if data.get('due_date') and data['due_date'] < timezone.now():
            raise serializers.ValidationError({
                'due_date': 'Due date must be in the future'
            })
        
        return data


# ==================== STUDENT ASSIGNMENT SERIALIZERS ====================

class StudentAssignmentMiniSerializer(serializers.ModelSerializer):
    """Minimal student assignment serializer for lists"""
    student = UserMinimalSerializer(read_only=True)
    assignment = serializers.SerializerMethodField()
    
    # Dynamic fields
    percentage = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    days_late = serializers.SerializerMethodField()
    can_resubmit = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAssignment
        fields = [
            'id', 'assignment', 'student', 'status',
            'submission_date', 'marks_obtained', 'final_marks', 'grade',
            'percentage', 'is_late', 'days_late', 'can_resubmit',
            'graded_at', 'created_at'
        ]
        read_only_fields = fields
    
    def get_assignment(self, obj):
        return {
            'id': str(obj.assignment.id),
            'title': obj.assignment.title,
            'subject': obj.assignment.subject.name if obj.assignment.subject else None,
            'total_marks': obj.assignment.total_marks
        }
    
    def get_percentage(self, obj):
        return obj.percentage
    
    def get_is_late(self, obj):
        return obj.is_late
    
    def get_days_late(self, obj):
        return obj.days_late
    
    def get_can_resubmit(self, obj):
        return obj.can_resubmit


class StudentAssignmentDetailSerializer(serializers.ModelSerializer):
    """Detailed student assignment serializer"""
    student = UserMinimalSerializer(read_only=True)
    assignment = AssignmentListSerializer(read_only=True)
    group = serializers.SerializerMethodField()
    graded_by = UserMinimalSerializer(read_only=True)
    
    # Dynamic fields
    percentage = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    days_late = serializers.SerializerMethodField()
    can_resubmit = serializers.SerializerMethodField()
    submission_files_list = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAssignment
        fields = [
            'id', 'assignment', 'student', 'group', 'is_group_submission',
            'status', 'submission_date', 'submission_text',
            'submission_file', 'submission_files', 'submission_files_list',
            'word_count', 'character_count', 'version', 'previous_version',
            'marks_obtained', 'penalty_points', 'final_marks', 'grade',
            'grade_points', 'teacher_feedback', 'rubric_scores', 'audio_feedback',
            'graded_by', 'graded_at', 'time_spent', 'last_accessed', 'draft_saved',
            'percentage', 'is_late', 'days_late', 'can_resubmit',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_group(self, obj):
        if obj.group:
            return {
                'id': str(obj.group.id),
                'name': obj.group.name,
                'leader': obj.group.leader.get_full_name() if obj.group.leader else None
            }
        return None
    
    def get_percentage(self, obj):
        return obj.percentage
    
    def get_is_late(self, obj):
        return obj.is_late
    
    def get_days_late(self, obj):
        return obj.days_late
    
    def get_can_resubmit(self, obj):
        return obj.can_resubmit
    
    def get_submission_files_list(self, obj):
        """Return a more structured list of submission files"""
        if obj.submission_files and isinstance(obj.submission_files, list):
            return obj.submission_files
        return []


class StudentAssignmentSubmitSerializer(serializers.ModelSerializer):
    """Serializer for submitting assignments"""
    class Meta:
        model = StudentAssignment
        fields = [
            'submission_text', 'submission_file',
            'submission_files', 'time_spent'
        ]
    
    def validate(self, data):
        """Validate submission data"""
        instance = self.instance
        
        # Check if assignment is open for submission
        if instance.assignment.status not in ['published', 'in_progress']:
            raise serializers.ValidationError({
                'assignment': 'Assignment is not open for submission'
            })
        
        # Check if student has already submitted
        if instance.status in ['submitted', 'late', 'graded', 'resubmitted']:
            raise serializers.ValidationError({
                'status': 'Assignment has already been submitted'
            })
        
        # Check if submission is allowed (not returned for revision)
        if instance.status == 'returned' and not instance.can_resubmit:
            raise serializers.ValidationError({
                'status': 'Resubmission limit reached'
            })
        
        # Validate that at least one submission method is provided
        if not any([data.get('submission_text'), data.get('submission_file'), data.get('submission_files')]):
            raise serializers.ValidationError({
                'submission': 'At least one submission method is required (text, file, or files)'
            })
        
        return data
    
    def update(self, instance, validated_data):
        """Update student assignment with submission"""
        # Set submission date
        validated_data['submission_date'] = timezone.now()
        
        # Determine if submission is late
        if validated_data['submission_date'] > instance.assignment.due_date:
            validated_data['status'] = 'late'
        else:
            validated_data['status'] = 'submitted'
        
        # Update version if this is a resubmission
        if instance.status == 'returned':
            validated_data['version'] = instance.version + 1
        
        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Log submission
        logger.info(f"Assignment submitted by student: {instance.student.get_full_name()}")
        
        return instance


class StudentAssignmentGradeSerializer(serializers.ModelSerializer):
    """Serializer for grading student assignments"""
    class Meta:
        model = StudentAssignment
        fields = [
            'marks_obtained', 'penalty_points', 'teacher_feedback',
            'rubric_scores', 'audio_feedback', 'grade'
        ]
    
    def validate(self, data):
        """Validate grading data"""
        instance = self.instance
        
        # Check if assignment can be graded
        if instance.status not in ['submitted', 'late', 'returned', 'resubmitted']:
            raise serializers.ValidationError({
                'status': 'Only submitted assignments can be graded'
            })
        
        # Validate marks
        if data.get('marks_obtained'):
            if data['marks_obtained'] > instance.assignment.total_marks:
                raise serializers.ValidationError({
                    'marks_obtained': f'Marks obtained cannot exceed total marks ({instance.assignment.total_marks})'
                })
        
        # Validate penalty points
        if data.get('penalty_points'):
            if data['penalty_points'] < 0:
                raise serializers.ValidationError({
                    'penalty_points': 'Penalty points cannot be negative'
                })
        
        return data
    
    def update(self, instance, validated_data):
        """Update student assignment with grade"""
        request = self.context.get('request')
        
        # Set grading metadata
        validated_data['status'] = 'graded'
        validated_data['graded_at'] = timezone.now()
        
        if request and request.user:
            validated_data['graded_by'] = request.user
        
        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update assignment analytics
        instance.assignment.update_analytics()
        
        # Log grading
        logger.info(f"Assignment graded by teacher: {request.user.get_full_name() if request else 'Unknown'}")
        
        return instance


# ==================== ASSIGNMENT GROUP SERIALIZERS ====================

class AssignmentGroupSerializer(serializers.ModelSerializer):
    """Serializer for assignment groups"""
    assignment = AssignmentListSerializer(read_only=True)
    leader = UserMinimalSerializer(read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
    members = UserMinimalSerializer(many=True, read_only=True)
    
    # Dynamic fields
    member_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentGroup
        fields = [
            'id', 'name', 'assignment', 'leader', 'members',
            'description', 'created_by', 'member_count', 'is_full',
            'available_seats', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_full(self, obj):
        return obj.is_full
    
    def get_available_seats(self, obj):
        return obj.available_seats


class AssignmentGroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assignment groups"""
    class Meta:
        model = AssignmentGroup
        fields = ['name', 'assignment', 'description']
    
    def validate(self, data):
        """Validate group creation"""
        assignment = data.get('assignment')
        request = self.context.get('request')
        
        if not assignment:
            raise serializers.ValidationError({
                'assignment': 'Assignment is required'
            })
        
        # Check if assignment allows groups
        if not assignment.is_group_assignment:
            raise serializers.ValidationError({
                'assignment': 'This assignment does not allow group work'
            })
        
        # Check if user is a student
        if request and not (hasattr(request.user, 'student_profile') or request.user.role == 'student'):
            raise serializers.ValidationError({
                'user': 'Only students can create groups'
            })
        
        # Check if group name is unique for this assignment
        if AssignmentGroup.objects.filter(
            assignment=assignment,
            name=data['name']
        ).exists():
            raise serializers.ValidationError({
                'name': 'A group with this name already exists for this assignment'
            })
        
        return data
    
    def create(self, validated_data):
        """Create assignment group"""
        request = self.context.get('request')
        
        # Set leader and created_by
        if request and request.user:
            validated_data['leader'] = request.user
            validated_data['created_by'] = request.user
        
        # Create group
        group = AssignmentGroup.objects.create(**validated_data)
        
        # Add creator as first member
        if request and request.user:
            GroupMembership.objects.create(
                group=group,
                student=request.user,
                role='leader'
            )
        
        logger.info(f"Assignment group created: {group.name}")
        
        return group


# ==================== GROUP MEMBERSHIP SERIALIZERS ====================

class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group memberships"""
    group = AssignmentGroupSerializer(read_only=True)
    student = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'group', 'student', 'role', 'is_active',
            'joined_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class GroupMembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating group memberships"""
    class Meta:
        model = GroupMembership
        fields = ['group', 'student', 'role']
    
    def validate(self, data):
        """Validate membership creation"""
        group = data.get('group')
        student = data.get('student')
        
        # Check if group is full
        if group.is_full:
            raise serializers.ValidationError({
                'group': 'Group is full'
            })
        
        # Check if student is already a member
        if GroupMembership.objects.filter(group=group, student=student).exists():
            raise serializers.ValidationError({
                'student': 'Student is already a member of this group'
            })
        
        # Check if student is eligible to join (same class as assignment)
        if hasattr(student, 'student_profile'):
            if student.student_profile.classroom != group.assignment.classroom:
                raise serializers.ValidationError({
                    'student': 'Student is not in the same class as this assignment'
                })
        
        return data
    
    def create(self, validated_data):
        """Create group membership"""
        membership = GroupMembership.objects.create(**validated_data)
        logger.info(f"Group membership created: {membership.student.get_full_name()} joined {membership.group.name}")
        return membership


# ==================== ASSIGNMENT COMMENT SERIALIZERS ====================

class AssignmentCommentSerializer(serializers.ModelSerializer):
    """Serializer for assignment comments"""
    author = UserMinimalSerializer(read_only=True)
    assignment = AssignmentListSerializer(read_only=True)
    student_assignment = StudentAssignmentMiniSerializer(read_only=True)
    parent_comment = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentComment.objects.all(),
        required=False,
        allow_null=True
    )
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentComment
        fields = [
            'id', 'assignment', 'student_assignment', 'author',
            'parent_comment', 'content', 'is_private',
            'file_attachment', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'replies']
    
    def get_replies(self, obj):
        """Get nested replies"""
        replies = obj.replies.all()
        return AssignmentCommentSerializer(replies, many=True).data
    
    def validate(self, data):
        """Validate comment data"""
        request = self.context.get('request')
        
        # Check if user has permission to create private comments
        if data.get('is_private') and request:
            if not (request.user.is_teacher or request.user.is_staff or request.user.is_superuser):
                raise serializers.ValidationError({
                    'is_private': 'Only teachers can create private comments'
                })
        
        return data
    
    def create(self, validated_data):
        """Create assignment comment"""
        request = self.context.get('request')
        
        if request and request.user:
            validated_data['author'] = request.user
        
        comment = AssignmentComment.objects.create(**validated_data)
        logger.info(f"Comment created by {comment.author.get_full_name()}")
        
        return comment


# ==================== ASSIGNMENT ANALYTICS SERIALIZERS ====================

class AssignmentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for assignment analytics"""
    assignment = AssignmentListSerializer(read_only=True)
    
    # Dynamic fields
    last_updated = serializers.SerializerMethodField()
    analytics_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentAnalytics
        fields = [
            'id', 'assignment', 'total_views', 'unique_viewers',
            'average_time_spent', 'common_issues', 'plagiarism_cases',
            'average_completion_time', 'question_analysis',
            'average_score', 'submission_rate', 'last_updated',
            'analytics_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_last_updated(self, obj):
        return obj.last_updated.strftime('%Y-%m-%d %H:%M:%S') if obj.last_updated else None
    
    def get_analytics_summary(self, obj):
        return {
            'total_views': obj.total_views,
            'unique_viewers': obj.unique_viewers,
            'average_time_spent': obj.average_time_spent,
            'plagiarism_cases': obj.plagiarism_cases,
            'average_score': float(obj.average_score) if obj.average_score else 0,
            'submission_rate': float(obj.submission_rate) if obj.submission_rate else 0
        }


# ==================== ASSIGNMENT REMINDER SERIALIZERS ====================

class AssignmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for assignment reminders"""
    assignment = AssignmentListSerializer(read_only=True)
    target_users = UserMinimalSerializer(many=True, read_only=True)
    
    # Dynamic fields
    is_overdue = serializers.SerializerMethodField()
    days_until_reminder = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentReminder
        fields = [
            'id', 'assignment', 'reminder_type', 'reminder_date',
            'message', 'sent', 'sent_at', 'target_users',
            'send_to_all_students', 'is_overdue', 'days_until_reminder',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_days_until_reminder(self, obj):
        if obj.reminder_date and not obj.sent:
            delta = obj.reminder_date - timezone.now()
            return delta.days
        return None


class AssignmentReminderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assignment reminders"""
    class Meta:
        model = AssignmentReminder
        fields = [
            'assignment', 'reminder_type', 'reminder_date',
            'message', 'target_users', 'send_to_all_students'
        ]
    
    def validate(self, data):
        """Validate reminder data"""
        # Check if reminder date is in the future
        if data.get('reminder_date') and data['reminder_date'] <= timezone.now():
            raise serializers.ValidationError({
                'reminder_date': 'Reminder date must be in the future'
            })
        
        # Check if target_users or send_to_all_students is specified
        if not data.get('send_to_all_students') and not data.get('target_users'):
            raise serializers.ValidationError({
                'target_users': 'Either specify target users or send to all students'
            })
        
        return data


# ==================== DASHBOARD & STATISTICS SERIALIZERS ====================

class AssignmentDashboardSerializer(serializers.Serializer):
    """Serializer for assignment dashboard data"""
    total_assignments = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()
    submitted_assignments = serializers.IntegerField()
    graded_assignments = serializers.IntegerField()
    overdue_assignments = serializers.IntegerField()
    average_score = serializers.FloatField()
    recent_assignments = AssignmentListSerializer(many=True)
    upcoming_deadlines = AssignmentListSerializer(many=True)
    
    class Meta:
        fields = [
            'total_assignments', 'pending_assignments',
            'submitted_assignments', 'graded_assignments',
            'overdue_assignments', 'average_score',
            'recent_assignments', 'upcoming_deadlines'
        ]


class TeacherAssignmentStatsSerializer(serializers.Serializer):
    """Serializer for teacher assignment statistics"""
    teacher = serializers.DictField()
    statistics = serializers.DictField()
    subject_breakdown = serializers.ListField()
    recent_assignments = AssignmentListSerializer(many=True)
    
    class Meta:
        fields = ['teacher', 'statistics', 'subject_breakdown', 'recent_assignments']


class StudentProgressReportSerializer(serializers.Serializer):
    """Serializer for student progress report"""
    student = serializers.DictField()
    overall_stats = serializers.DictField()
    subject_performance = serializers.ListField()
    recent_submissions = StudentAssignmentMiniSerializer(many=True)
    
    class Meta:
        fields = ['student', 'overall_stats', 'subject_performance', 'recent_submissions']


# ==================== EXPORT SERIALIZERS ====================

class AssignmentExportSerializer(serializers.ModelSerializer):
    """Serializer for exporting assignments to CSV/Excel"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assignment_type_display = serializers.CharField(source='get_assignment_type_display', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'subject_name', 'teacher_name', 'classroom_name',
            'due_date', 'total_marks', 'passing_marks', 'status_display',
            'assignment_type_display', 'created_at', 'published_at',
            'average_score', 'completion_rate'
        ]
    
    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else ''


class GradeExportSerializer(serializers.ModelSerializer):
    """Serializer for exporting grades to CSV/Excel"""
    student_name = serializers.SerializerMethodField()
    admission_number = serializers.SerializerMethodField()
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    subject_name = serializers.CharField(source='assignment.subject.name', read_only=True)
    total_marks = serializers.DecimalField(source='assignment.total_marks', read_only=True, max_digits=6, decimal_places=2)
    percentage = serializers.SerializerMethodField()
    graded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAssignment
        fields = [
            'student_name', 'admission_number', 'assignment_title',
            'subject_name', 'total_marks', 'marks_obtained', 'percentage',
            'grade', 'status', 'submission_date', 'graded_at',
            'graded_by_name', 'teacher_feedback'
        ]
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() if obj.student else ''
    
    def get_admission_number(self, obj):
        return obj.student.admission_number if hasattr(obj.student, 'admission_number') else ''
    
    def get_percentage(self, obj):
        return obj.percentage
    
    def get_graded_by_name(self, obj):
        return obj.graded_by.get_full_name() if obj.graded_by else ''


# ==================== BULK OPERATION SERIALIZERS ====================

class BulkAssignmentCreateSerializer(serializers.Serializer):
    """Serializer for bulk assignment creation"""
    assignments = AssignmentCreateSerializer(many=True)
    
    class Meta:
        fields = ['assignments']


class BulkGradingSerializer(serializers.Serializer):
    """Serializer for bulk grading"""
    grading = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    class Meta:
        fields = ['grading']


class ImportGradesSerializer(serializers.Serializer):
    """Serializer for importing grades"""
    file = serializers.FileField()
    
    class Meta:
        fields = ['file']


# ==================== NOTIFICATION SERIALIZERS ====================

class AssignmentNotificationSerializer(serializers.Serializer):
    """Serializer for assignment notifications"""
    type = serializers.CharField()
    assignment_id = serializers.UUIDField()
    assignment_title = serializers.CharField()
    due_date = serializers.DateTimeField()
    days_left = serializers.IntegerField(required=False)
    days_overdue = serializers.IntegerField(required=False)
    message = serializers.CharField()
    priority = serializers.CharField()
    
    class Meta:
        fields = [
            'type', 'assignment_id', 'assignment_title',
            'due_date', 'days_left', 'days_overdue',
            'message', 'priority'
        ]


class CalendarEventSerializer(serializers.Serializer):
    """Serializer for calendar events"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    allDay = serializers.BooleanField(default=True)
    color = serializers.CharField()
    textColor = serializers.CharField(default='#ffffff')
    extendedProps = serializers.DictField()
    
    class Meta:
        fields = [
            'id', 'title', 'start', 'end', 'allDay',
            'color', 'textColor', 'extendedProps'
        ]


# ==================== VALIDATION SERIALIZERS ====================

class AssignmentValidationSerializer(serializers.Serializer):
    """Serializer for assignment validation"""
    field = serializers.CharField()
    value = serializers.CharField()
    is_valid = serializers.BooleanField()
    message = serializers.CharField(required=False)
    
    class Meta:
        fields = ['field', 'value', 'is_valid', 'message']


class SubmissionValidationSerializer(serializers.Serializer):
    """Serializer for submission validation"""
    can_submit = serializers.BooleanField()
    message = serializers.CharField(required=False)
    deadline = serializers.DateTimeField(required=False)
    is_late_allowed = serializers.BooleanField(default=False)
    late_penalty = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    class Meta:
        fields = [
            'can_submit', 'message', 'deadline',
            'is_late_allowed', 'late_penalty'
        ]




# Add these to your serializers.py file

class StudentProgressReportSerializer(serializers.Serializer):
    """Serializer for student progress report."""
    student = serializers.DictField()
    overall_statistics = serializers.DictField()
    subject_performance = serializers.ListField()
    recent_assignments = serializers.ListField()
    recommendations = serializers.ListField()


class BatchUpdateStatusSerializer(serializers.Serializer):
    """Serializer for batch updating assignment statuses."""
    assignment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of assignment IDs to update"
    )
    status = serializers.ChoiceField(
        choices=['draft', 'published', 'in_progress', 'closed', 'graded'],
        help_text="New status for the assignments"
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for the status change"
    )


class AssignmentAnalyticsSerializer(serializers.Serializer):
    """Serializer for assignment analytics."""
    assignment = serializers.DictField()
    statistics = serializers.DictField()
    score_distribution = serializers.DictField()
    submission_analysis = serializers.DictField()
    performance_by_gender = serializers.ListField()
    generated_at = serializers.DateTimeField()