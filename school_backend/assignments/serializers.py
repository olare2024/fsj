# assignments/serializers.py
import uuid
import datetime
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import logging
from django.utils.dateparse import parse_datetime
from django.db import transaction
from .models import (
    Assignment, StudentAssignment, AssignmentCategory, AssignmentGradeScale,
    AssignmentGroup, GroupMembership, AssignmentComment, AssignmentAnalytics
)
from academics.models import AcademicYear, AcademicTerm, Subject, Class, Stream
from curriculum.models import Curriculum
from .serializers_student_assignment import StudentAssignmentMiniSerializer
from accounts.models import User


logger = logging.getLogger(__name__)

# FIXED IMPORTS - with proper error handling and fallbacks
try:
    from academics.serializers import (
        SubjectSerializer, 
        ClassSerializer as ClassRoomSerializer,
        AcademicYearSerializer,
        StudentProfileMinimalSerializer as StudentSerializer,
        TeacherProfileMinimalSerializer as TeacherSerializer,
        AcademicTermSerializer as TermSerializer
    )
except ImportError as e:
    # Create fallback serializers if imports fail
    class SubjectSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        code = serializers.CharField(read_only=True)
    
    class ClassRoomSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        display_name = serializers.CharField(read_only=True)
    
    class AcademicYearSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)
    
    class StudentSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        admission_number = serializers.CharField(read_only=True)
    
    class TeacherSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        full_name = serializers.CharField(read_only=True)
        teacher_id = serializers.CharField(read_only=True)
    
    class TermSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)

# StreamSerializer fallback (in case it doesn't exist)
class StreamSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)

# Import from accounts with fallback
try:
    from accounts.serializers import CustomUserSerializer, UserSerializer
except ImportError:
    class CustomUserSerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        email = serializers.EmailField(read_only=True)
        first_name = serializers.CharField(read_only=True)
        last_name = serializers.CharField(read_only=True)
        full_name = serializers.CharField(read_only=True)
    
    UserSerializer = CustomUserSerializer

class PrimaryKeyRelatedUUIDField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField with explicit UUID handling"""
    
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
    
    def to_representation(self, value):
        # Return the UUID string for representation
        if isinstance(value, str):
            return value
        return str(value.id)


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Basic assignment serializer for foreign key relationships and simple listings
    Used by other apps like teachers app - READ ONLY
    """
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.display_name', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    submission_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'assignment_type', 'description', 'subject', 'subject_name',
            'teacher', 'teacher_name', 'classroom', 'classroom_name', 'stream',
            'due_date', 'total_marks', 'passing_marks', 'status', 'difficulty_level',
            'days_until_due', 'is_overdue', 'submission_stats', 'created_at', 'published_at'
        ]
        read_only_fields = fields  # Make all fields read-only
    
    def get_days_until_due(self, obj):
        """Calculate days until due date"""
        if obj.due_date:
            current_time = timezone.now()
            if obj.due_date > current_time:
                delta = obj.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def get_is_overdue(self, obj):
        """Check if assignment is overdue"""
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False
    
    def get_submission_stats(self, obj):
        return obj.submission_stats

class AssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating assignments
    Handles foreign key relationships properly
    """
    # Explicit foreign key fields for create/update
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=True
    )
    term = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        required=True
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=True
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        required=True
    )
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        required=False,
        allow_null=True
    )
    stream = serializers.PrimaryKeyRelatedField(
        queryset=Stream.objects.all(),
        required=False,
        allow_null=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentCategory.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Read-only fields for display
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.display_name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    
    # Computed fields
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    can_be_published = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            # Basic info
            'id', 'title', 'description', 'assignment_type', 'category',
            
            # Academic context
            'subject', 'subject_name', 'teacher', 'teacher_name',
            'classroom', 'classroom_name', 'stream', 'stream_name',
            'academic_year', 'academic_year_name', 'term', 'term_name',
            'curriculum',
            
            # Assignment details
            'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
            'estimated_completion_time',
            
            # Content
            'instructions', 'learning_objectives', 'resources', 'rubric',
            
            # Competencies
            'competencies', 'core_competencies',
            
            # Attachments
            'attachment', 'additional_files',
            
            # Settings
            'allow_late_submission', 'late_submission_penalty',
            'allow_resubmission', 'max_resubmissions',
            'require_approval', 'is_group_assignment', 'max_group_size',
            
            # Status
            'status', 'published_at', 'closed_at',
            
            # Analytics (read-only)
            'views_count', 'average_score', 'completion_rate',
            
            # Approval
            'approved_by', 'approved_at',
            
            # Computed fields
            'days_until_due', 'is_overdue', 'can_be_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'published_at', 'closed_at',
            'approved_at', 'views_count', 'average_score', 'completion_rate',
            'academic_year_name', 'term_name', 'subject_name', 'teacher_name',
            'classroom_name', 'stream_name'
        ]
    
    def get_days_until_due(self, obj):
        """Calculate days until due date"""
        if obj.due_date:
            current_time = timezone.now()
            if obj.due_date > current_time:
                delta = obj.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def get_is_overdue(self, obj):
        """Check if assignment is overdue"""
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False
    
    def get_can_be_published(self, obj):
        """Check if assignment can be published"""
        return obj.can_be_published
    
    def validate(self, data):
        """Custom validation"""
        errors = {}
        
        # Ensure due_date is in the future
        if 'due_date' in data and data['due_date'] <= timezone.now():
            errors['due_date'] = _('Due date must be in the future.')
        
        # Ensure passing_marks <= total_marks
        if 'passing_marks' in data and 'total_marks' in data:
            if data['passing_marks'] > data['total_marks']:
                errors['passing_marks'] = _('Passing marks cannot exceed total marks.')
        
        # Validate group assignment settings
        if data.get('is_group_assignment', False):
            if data.get('max_group_size', 1) < 2:
                errors['max_group_size'] = _('Group assignments require at least 2 students per group.')
            if not data.get('classroom'):
                errors['classroom'] = _('Group assignments require a classroom to be specified.')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Override create to handle assignment creation"""
        try:
            # Set created_by if not provided
            if 'created_by' not in validated_data and self.context.get('request'):
                validated_data['created_by'] = self.context['request'].user
            
            # Create the assignment
            assignment = Assignment.objects.create(**validated_data)
            
            # If assignment is published, create student assignments
            if assignment.status == Assignment.StatusChoices.PUBLISHED and assignment.classroom:
                assignment.create_student_assignments()
            
            return assignment
            
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': [f'Failed to create assignment: {str(e)}']
            })
    
    def update(self, instance, validated_data):
        """Override update to handle status changes"""
        try:
            # Handle status transitions
            old_status = instance.status
            new_status = validated_data.get('status', old_status)
            
            # If publishing for the first time
            if (new_status == Assignment.StatusChoices.PUBLISHED and 
                old_status != Assignment.StatusChoices.PUBLISHED):
                validated_data['published_at'] = timezone.now()
                
                # Create student assignments if not already created
                if instance.classroom:
                    instance.create_student_assignments()
            
            # If closing
            if (new_status in [Assignment.StatusChoices.CLOSED, Assignment.StatusChoices.GRADED] and
                old_status not in [Assignment.StatusChoices.CLOSED, Assignment.StatusChoices.GRADED]):
                validated_data['closed_at'] = timezone.now()
            
            return super().update(instance, validated_data)
            
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': [f'Failed to update assignment: {str(e)}']
            })


class AssignmentCategorySerializer(serializers.ModelSerializer):
    assignment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_assignment_count(self, obj):
        return obj.assignment_set.count()


class AssignmentGradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentGradeScale
        fields = '__all__'


class AssignmentAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentAnalytics
        fields = '__all__'


class AssignmentListSerializer(serializers.ModelSerializer):
    """Serializer for assignment listing (optimized for performance)"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.display_name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    
    # Statistics
    submission_stats = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'assignment_type', 'subject', 'subject_name',
            'teacher', 'teacher_name', 'classroom', 'classroom_name',
            'term', 'term_name', 'due_date', 'total_marks', 'status',
            'difficulty_level', 'submission_stats', 'days_until_due', 'is_overdue',
            'created_at', 'published_at'
        ]
    
    def get_submission_stats(self, obj):
        return obj.get_submission_stats()
    
    def get_days_until_due(self, obj):
        """Calculate days until due date - FIXED VERSION"""
        if obj.due_date:
            current_time = timezone.now()
            
            if obj.due_date > current_time:
                delta = obj.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def get_is_overdue(self, obj):
        """Check if assignment is overdue - FIXED VERSION"""
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single assignment"""
    subject_details = SubjectSerializer(read_only=True, source='subject')
    teacher_details = TeacherSerializer(read_only=True, source='teacher')
    classroom_details = ClassRoomSerializer(read_only=True, source='classroom')
    stream_details = StreamSerializer(read_only=True, source='stream')
    term_details = TermSerializer(read_only=True, source='term')
    academic_year_details = AcademicYearSerializer(read_only=True, source='academic_year')
    category_details = AssignmentCategorySerializer(read_only=True, source='category')
    created_by_details = CustomUserSerializer(read_only=True, source='created_by')
    analytics_details = AssignmentAnalyticsSerializer(read_only=True, source='analytics')
    
    # Statistics
    submission_stats = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    # Student-specific data (for student users)
    student_submission = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'assignment_type', 'category', 'category_details',
            'subject', 'subject_details', 'teacher', 'teacher_details',
            'classroom', 'classroom_details', 'stream', 'stream_details',
            'academic_year', 'academic_year_details', 'term', 'term_details',
            'curriculum', 'due_date', 'total_marks', 'passing_marks',
            'difficulty_level', 'estimated_completion_time', 'instructions',
            'learning_objectives', 'resources', 'rubric', 'attachment',
            'additional_files', 'allow_late_submission', 'late_submission_penalty',
            'allow_resubmission', 'max_resubmissions', 'require_approval',
            'is_group_assignment', 'max_group_size', 'status', 'published_at',
            'closed_at', 'created_at', 'updated_at', 'created_by', 'created_by_details',
            'views_count', 'average_score', 'completion_rate', 'submission_stats',
            'days_until_due', 'is_overdue', 'total_students', 'student_submission',
            'analytics_details'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'published_at', 'closed_at',
            'views_count', 'average_score', 'completion_rate'
        ]
    
    def get_submission_stats(self, obj):
        return obj.get_submission_stats()
    
    def get_average_score(self, obj):
        return obj.get_average_score()
    
    def get_completion_rate(self, obj):
        return obj.get_completion_rate()
    
    def get_days_until_due(self, obj):
        """Calculate days until due date - FIXED VERSION"""
        if obj.due_date:
            current_time = timezone.now()
            
            if obj.due_date > current_time:
                delta = obj.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def get_is_overdue(self, obj):
        """Check if assignment is overdue - FIXED VERSION"""
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False
    
    def get_total_students(self, obj):
        return obj.get_total_students()
    
    def get_student_submission(self, obj):
        """Get current student's submission if exists"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if user has student profile
            if hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                try:
                    submission = obj.student_assignments.filter(student=student).first()
                    if submission:
                        return StudentAssignmentMiniSerializer(submission, context=self.context).data
                except Exception:
                    return None
        return None


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assignments with comprehensive validation and UUID support"""
    
    # ===== EXPLICITLY DEFINE UUID FOREIGN KEYS =====
    # Use standard PrimaryKeyRelatedField - Django REST Framework handles UUIDs automatically
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(is_active=True),
        required=True
    )
    term = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.filter(is_active=True),
        required=True
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.filter(is_active=True),
        required=True
    )
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.filter(is_active=True),
        required=True
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        required=True
    )

    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'assignment_type', 'category', 'subject',
            'teacher', 'classroom', 'stream', 'academic_year', 'term', 'curriculum',
            'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
            'estimated_completion_time', 'instructions', 'learning_objectives',
            'resources', 'rubric', 'attachment', 'allow_late_submission',
            'late_submission_penalty', 'allow_resubmission', 'max_resubmissions',
            'require_approval', 'is_group_assignment', 'max_group_size', 'status'
        ]
        extra_kwargs = {
            'status': {'default': 'draft'},
            'allow_late_submission': {'default': True},
            'allow_resubmission': {'default': False},
            'max_resubmissions': {'default': 1},
            'require_approval': {'default': False},
            'is_group_assignment': {'default': False},
            'max_group_size': {'default': 4},
            'late_submission_penalty': {'default': 0},
        }
    
    def to_internal_value(self, data):
        """Convert incoming data - handle UUID string conversion for PrimaryKeyRelatedField"""
        # Debug incoming data
        logger.debug(f"to_internal_value received data: {data}")
        
        # Create a mutable copy
        data_copy = data.copy()
        
        # Handle UUID fields - ensure they're in the correct format
        uuid_fields = ['academic_year', 'term', 'subject', 'classroom', 'teacher', 'stream', 'category']
        
        for field in uuid_fields:
            if field in data_copy and data_copy[field]:
                try:
                    # If it's already a string, try to parse it as UUID
                    if isinstance(data_copy[field], str):
                        # Check if it's already a valid UUID string
                        uuid_value = uuid.UUID(data_copy[field])
                        # Keep it as string (PrimaryKeyRelatedField expects string)
                        data_copy[field] = str(uuid_value)
                        logger.debug(f"Converted {field} to UUID string: {data_copy[field]}")
                    elif isinstance(data_copy[field], uuid.UUID):
                        # Convert UUID object to string
                        data_copy[field] = str(data_copy[field])
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Invalid UUID format for {field}: {data_copy[field]} - {e}")
                    # Let the serializer validation handle the error
        
        # Call parent method
        result = super().to_internal_value(data_copy)
        logger.debug(f"to_internal_value returning: {result}")
        return result
    
    def validate(self, data):
        """Comprehensive validation for assignment creation"""
        request = self.context.get('request')
        errors = {}
        
        # Debug validated data
        logger.debug(f"validate received data: {data}")
        
        # ===== TEACHER PERMISSION VALIDATION =====
        if request and hasattr(request, 'user'):
            user = request.user
            
            # Check if user has teacher permissions
            if not self._user_is_teacher(user):
                raise serializers.ValidationError({
                    'permission': "Only teachers can create assignments"
                })
        
        # ===== REQUIRED FIELD VALIDATION =====
        required_fields = ['title', 'subject', 'academic_year', 'term', 'due_date', 'teacher']
        for field in required_fields:
            if field not in data:
                errors[field] = f'{field.replace("_", " ").title()} is required.'
        
        # ===== DATE VALIDATION =====
        if 'due_date' in data:
            due_date = data['due_date']
            current_time = timezone.now()
            
            # Handle if due_date is a string (from frontend)
            if isinstance(due_date, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    due_date = parse_datetime(due_date)
                    if not due_date:
                        errors['due_date'] = 'Invalid date format.'
                except (ValueError, TypeError):
                    errors['due_date'] = 'Invalid date format.'
            
            if not errors.get('due_date'):
                # Check if due_date is a date (no time component)
                if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime.datetime):
                    # Convert date to datetime for comparison
                    due_datetime = datetime.datetime.combine(due_date, datetime.time(23, 59, 59))
                    due_datetime = timezone.make_aware(due_datetime)
                    due_date = due_datetime
                
                # Check if due date is in the past
                if due_date < current_time:
                    errors['due_date'] = 'Due date cannot be in the past.'
                
                # Check if due date is too far in the future (optional)
                max_future_days = 365  # 1 year maximum
                if (due_date - current_time).days > max_future_days:
                    errors['due_date'] = f'Due date cannot be more than {max_future_days} days in the future.'
                
                # Update the data with properly formatted datetime
                data['due_date'] = due_date
        
        # ===== MARKS VALIDATION =====
        if 'total_marks' in data:
            total_marks = data['total_marks']
            
            # Check total marks range
            if total_marks <= 0:
                errors['total_marks'] = 'Total marks must be greater than 0.'
            elif total_marks > 1000:  # Reasonable maximum
                errors['total_marks'] = 'Total marks cannot exceed 1000.'
        
        if 'passing_marks' in data and 'total_marks' in data:
            passing_marks = data['passing_marks']
            total_marks = data['total_marks']
            
            if passing_marks < 0:
                errors['passing_marks'] = 'Passing marks cannot be negative.'
            elif passing_marks > total_marks:
                errors['passing_marks'] = 'Passing marks cannot exceed total marks.'
            elif passing_marks == 0 and total_marks > 0:
                # Warning but not error (allow zero passing marks if intentional)
                data['passing_marks'] = 0
        
        # ===== DIFFICULTY LEVEL VALIDATION =====
        if 'difficulty_level' in data:
            difficulty = data['difficulty_level']
            valid_difficulties = ['easy', 'medium', 'hard', 'advanced']
            if difficulty not in valid_difficulties:
                errors['difficulty_level'] = f'Invalid difficulty level. Must be one of: {", ".join(valid_difficulties)}'
        
        # ===== COMPLETION TIME VALIDATION =====
        if 'estimated_completion_time' in data:
            completion_time = data['estimated_completion_time']
            if completion_time <= 0:
                errors['estimated_completion_time'] = 'Estimated completion time must be greater than 0 minutes.'
            elif completion_time > 10080:  # 1 week in minutes
                errors['estimated_completion_time'] = 'Estimated completion time cannot exceed 1 week (10080 minutes).'
        
        # ===== GROUP ASSIGNMENT VALIDATION =====
        if 'is_group_assignment' in data and data['is_group_assignment']:
            if 'max_group_size' not in data:
                errors['max_group_size'] = 'Maximum group size is required for group assignments.'
            elif data['max_group_size'] < 2:
                errors['max_group_size'] = 'Group size must be at least 2 for group assignments.'
            elif data['max_group_size'] > 10:
                errors['max_group_size'] = 'Group size cannot exceed 10 members.'
        
        # ===== RESUBMISSION VALIDATION =====
        if 'allow_resubmission' in data and data['allow_resubmission']:
            if 'max_resubmissions' not in data:
                errors['max_resubmissions'] = 'Maximum resubmissions is required when allowing resubmissions.'
            elif data['max_resubmissions'] < 1:
                errors['max_resubmissions'] = 'Maximum resubmissions must be at least 1.'
            elif data['max_resubmissions'] > 10:
                errors['max_resubmissions'] = 'Maximum resubmissions cannot exceed 10.'
        
        # ===== LATE SUBMISSION PENALTY VALIDATION =====
        if 'late_submission_penalty' in data:
            penalty = data['late_submission_penalty']
            if penalty < 0:
                errors['late_submission_penalty'] = 'Penalty cannot be negative.'
            elif penalty > 100:
                errors['late_submission_penalty'] = 'Penalty cannot exceed 100%.'
        
        # ===== ATTACHMENT VALIDATION =====
        if 'attachment' in data and data['attachment']:
            attachment = data['attachment']
            max_size = 50 * 1024 * 1024  # 50MB
            allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', 
                                  '.jpg', '.jpeg', '.png', '.zip', '.rar']
            
            if attachment.size > max_size:
                errors['attachment'] = f'File size cannot exceed {max_size // (1024*1024)}MB.'
            
            import os
            ext = os.path.splitext(attachment.name)[1].lower()
            if ext not in allowed_extensions:
                errors['attachment'] = f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
        
        # ===== STATUS VALIDATION =====
        if 'status' in data:
            status_value = data['status']
            valid_statuses = ['draft', 'published', 'closed']
            if status_value not in valid_statuses:
                errors['status'] = f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        
        # ===== CURRICULUM VALIDATION =====
        if 'curriculum' in data:
            curriculum = data['curriculum']
            valid_curricula = ['cbc', 'icse', 'american', 'british', 'montessori', 
                               'combined', 'igcse', 'ib']
            if curriculum not in valid_curricula:
                errors['curriculum'] = f'Invalid curriculum. Must be one of: {", ".join(valid_curricula)}'
        
        # ===== THROW ERRORS IF ANY =====
        if errors:
            logger.error(f"Validation errors: {errors}")
            raise serializers.ValidationError(errors)
        
        logger.debug(f"Validation passed for data: {data}")
        return data
    
    def _user_is_teacher(self, user):
        """
        Safe method to check if user is a teacher.
        Handles both User model with is_teacher property and without.
        """
        # Method 1: Check if user has is_teacher property
        if hasattr(user, 'is_teacher'):
            return user.is_teacher
        
        # Method 2: Check role directly
        if hasattr(user, 'role'):
            # Convert to string and lowercase for safe comparison
            user_role = str(user.role).lower()
            teacher_roles = [
                'teacher',
                'head_teacher', 
                'curriculum_coordinator',
                'admin'
            ]
            return user_role in teacher_roles
        
        # Method 3: Check if user is staff (admin/teacher)
        if hasattr(user, 'is_staff'):
            return user.is_staff
        
        return False
    
    def create(self, validated_data):
        """Create assignment with automatic field population"""
        request = self.context.get('request')
        
        logger.info(f"Creating assignment with data: {validated_data}")
        
        # ===== SET CREATED BY =====
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            logger.info(f"Set created_by to: {request.user.id}")
        
        # ===== SET PUBLISHED DATE IF STATUS IS PUBLISHED =====
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
            logger.info("Set published_at to current time")
        
        # ===== LOG FOREIGN KEY VALUES =====
        for field in ['academic_year', 'term', 'subject', 'classroom', 'teacher']:
            if field in validated_data:
                value = validated_data[field]
                logger.info(f"{field}: {value} (type: {type(value).__name__})")
                if hasattr(value, 'id'):
                    logger.info(f"{field} ID: {value.id}")
        
        # ===== CREATE THE ASSIGNMENT =====
        try:
            with transaction.atomic():
                logger.info("Starting assignment creation transaction")
                
                # Create the assignment
                assignment = super().create(validated_data)
                logger.info(f"Assignment created with ID: {assignment.id}")
                
                # ===== CREATE STUDENT ASSIGNMENTS (if published) =====
                if assignment.status == 'published':
                    logger.info("Assignment is published, creating student assignments")
                    self._create_student_assignments(assignment)
                
                # ===== CREATE ANALYTICS RECORD =====
                AssignmentAnalytics.objects.create(assignment=assignment)
                logger.info("Created analytics record")
                
                # ===== LOG THE CREATION =====
                logger.info(f"Assignment '{assignment.title}' (ID: {assignment.id}) created successfully by {request.user.email if request and request.user else 'unknown'}")
                
                return assignment
                
        except Exception as e:
            logger.error(f"Failed to create assignment: {str(e)}", exc_info=True)
            raise serializers.ValidationError({
                'non_field_errors': f'Failed to create assignment: {str(e)}'
            })
    
    def _create_student_assignments(self, assignment):
        """Create student assignments for all students in the classroom"""
        from academics.models import StudentEnrollment
        
        if not assignment.classroom:
            logger.warning(f"No classroom specified for assignment {assignment.id}, skipping student assignment creation")
            return
        
        try:
            # Get all active enrollments in this class
            enrollments = StudentEnrollment.objects.filter(
                class_enrolled=assignment.classroom,
                status='active',
                is_active=True
            )
            
            if not enrollments.exists():
                logger.warning(f"No active students found in classroom {assignment.classroom.display_name}")
                return
            
            student_assignments = []
            for enrollment in enrollments:
                student_assignments.append(StudentAssignment(
                    assignment=assignment,
                    student=enrollment.student,
                    status='pending'
                ))
            
            # Bulk create for performance
            StudentAssignment.objects.bulk_create(student_assignments)
            logger.info(f"Created {len(student_assignments)} student assignments for assignment {assignment.id}")
            
        except Exception as e:
            logger.error(f"Failed to create student assignments: {str(e)}")
            # Don't raise error, assignment creation should still succeed
    
    def to_representation(self, instance):
        """Custom representation for created assignments"""
        representation = super().to_representation(instance)
        
        # Add additional computed fields
        representation['days_until_due'] = self._get_days_until_due(instance)
        representation['is_overdue'] = self._get_is_overdue(instance)
        representation['student_count'] = self._get_student_count(instance)
        
        return representation
    
    def _get_days_until_due(self, instance):
        """Calculate days until due date - FIXED VERSION"""
        if instance.due_date:
            current_time = timezone.now()
            
            if instance.due_date > current_time:
                delta = instance.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def _get_is_overdue(self, instance):
        """Check if assignment is overdue - FIXED VERSION"""
        if instance.due_date:
            return timezone.now() > instance.due_date
        return False
    
    def _get_student_count(self, instance):
        """Get number of students assigned"""
        try:
            return instance.student_assignments.count()
        except Exception:
            return 0
            
class AssignmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating assignments"""
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'assignment_type', 'category',
            'due_date', 'total_marks', 'passing_marks', 'difficulty_level',
            'estimated_completion_time', 'instructions', 'learning_objectives',
            'resources', 'rubric', 'attachment', 'allow_late_submission',
            'late_submission_penalty', 'allow_resubmission', 'max_resubmissions',
            'require_approval', 'is_group_assignment', 'max_group_size', 'status'
        ]
    
    def validate(self, data):
        """Validate update data"""
        if 'due_date' in data:
            due_date = data['due_date']
            current_time = timezone.now()
            
            # Handle if due_date is a string
            if isinstance(due_date, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    due_date = parse_datetime(due_date)
                    if not due_date:
                        raise serializers.ValidationError({
                            'due_date': 'Invalid date format.'
                        })
                except (ValueError, TypeError):
                    raise serializers.ValidationError({
                        'due_date': 'Invalid date format.'
                    })
            
            # Check if due_date is a date (no time component)
            if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime.datetime):
                # Convert date to datetime for comparison
                due_datetime = datetime.datetime.combine(due_date, datetime.time(23, 59, 59))
                due_datetime = timezone.make_aware(due_datetime)
                due_date = due_datetime
            
            # Check if due date is in the past
            if due_date < current_time:
                raise serializers.ValidationError({
                    'due_date': 'Due date cannot be in the past.'
                })
            
            # Update the data with properly formatted datetime
            data['due_date'] = due_date
        
        instance = self.instance
        if 'passing_marks' in data and 'total_marks' in data:
            if data['passing_marks'] > data['total_marks']:
                raise serializers.ValidationError({
                    'passing_marks': 'Passing marks cannot exceed total marks.'
                })
        elif 'passing_marks' in data and instance:
            if data['passing_marks'] > instance.total_marks:
                raise serializers.ValidationError({
                    'passing_marks': 'Passing marks cannot exceed total marks.'
                })
        elif 'total_marks' in data and instance:
            if instance.passing_marks > data['total_marks']:
                raise serializers.ValidationError({
                    'total_marks': 'Total marks cannot be less than current passing marks.'
                })
        
        return data


class StudentAssignmentMiniSerializer(serializers.ModelSerializer):
    """Mini serializer for student assignment (for listings)"""
    student_name = serializers.SerializerMethodField()
    student_admission_no = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    days_late = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAssignment
        fields = [
            'id', 'student', 'student_name', 'student_admission_no', 'status',
            'submission_date', 'marks_obtained', 'final_marks', 'grade',
            'percentage', 'is_late', 'days_late', 'version', 'graded_at'
        ]
    
    def get_student_name(self, obj):
        try:
            return obj.student.user.get_full_name()
        except Exception:
            return "Unknown Student"
    
    def get_student_admission_no(self, obj):
        try:
            return obj.student.admission_number
        except Exception:
            return "N/A"
    
    def get_percentage(self, obj):
        if obj.marks_obtained and obj.assignment.total_marks:
            return (obj.marks_obtained / obj.assignment.total_marks) * 100
        return None
    
    def get_is_late(self, obj):
        if obj.submission_date and obj.assignment.due_date:
            return obj.submission_date > obj.assignment.due_date
        return False
    
    def get_days_late(self, obj):
        if obj.submission_date and obj.assignment.due_date and obj.submission_date > obj.assignment.due_date:
            return (obj.submission_date - obj.assignment.due_date).days
        return 0


class StudentAssignmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for student assignment"""
    assignment_details = AssignmentListSerializer(read_only=True, source='assignment')
    student_details = StudentSerializer(read_only=True, source='student')
    graded_by_details = TeacherSerializer(read_only=True, source='graded_by')
    group_details = serializers.SerializerMethodField()
    
    # Computed fields
    percentage = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    days_late = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    can_resubmit = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAssignment
        fields = [
            'id', 'assignment', 'assignment_details', 'student', 'student_details',
            'group', 'group_details', 'is_group_submission', 'submission_date',
            'submission_text', 'submission_file', 'submission_files', 'word_count',
            'character_count', 'version', 'previous_version', 'marks_obtained',
            'penalty_points', 'final_marks', 'grade', 'grade_points',
            'teacher_feedback', 'rubric_scores', 'audio_feedback', 'status',
            'graded_at', 'graded_by', 'graded_by_details', 'time_spent',
            'last_accessed', 'draft_saved', 'created_at', 'updated_at',
            'percentage', 'is_late', 'days_late', 'days_remaining', 'can_resubmit'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'graded_at', 'percentage',
            'is_late', 'days_late', 'can_resubmit'
        ]
    
    def get_group_details(self, obj):
        if obj.group:
            return {
                'id': obj.group.id,
                'name': obj.group.name,
                'leader': obj.group.leader.user.get_full_name() if obj.group.leader else "No Leader"
            }
        return None
    
    def get_percentage(self, obj):
        if obj.marks_obtained and obj.assignment.total_marks:
            return (obj.marks_obtained / obj.assignment.total_marks) * 100
        return None
    
    def get_is_late(self, obj):
        if obj.submission_date and obj.assignment.due_date:
            return obj.submission_date > obj.assignment.due_date
        return False
    
    def get_days_late(self, obj):
        if obj.submission_date and obj.assignment.due_date and obj.submission_date > obj.assignment.due_date:
            return (obj.submission_date - obj.assignment.due_date).days
        return 0
    
    def get_days_remaining(self, obj):
        """Calculate days remaining until due date - FIXED VERSION"""
        if obj.assignment.due_date:
            current_time = timezone.now()
            
            if obj.assignment.due_date > current_time:
                delta = obj.assignment.due_date - current_time
                return delta.days
            else:
                return 0
        return None
    
    def get_can_resubmit(self, obj):
        if obj.assignment.allow_resubmission:
            if obj.version < obj.assignment.max_resubmissions:
                return True
        return False


class StudentAssignmentSubmitSerializer(serializers.ModelSerializer):
    """Serializer for submitting assignments"""
    class Meta:
        model = StudentAssignment
        fields = ['submission_text', 'submission_file', 'submission_files', 'time_spent']
    
    def validate(self, data):
        """Validate submission"""
        instance = self.instance
        
        if instance.status in ['graded', 'closed']:
            raise serializers.ValidationError(
                "Cannot submit. Assignment is already graded or closed."
            )
        
        if not instance.assignment.allow_late_submission and instance.assignment.is_overdue:
            raise serializers.ValidationError(
                "Late submissions are not allowed for this assignment."
            )
        
        return data
    
    def update(self, instance, validated_data):
        """Handle submission with IP and user agent tracking"""
        request = self.context.get('request')
        
        instance.submission_text = validated_data.get('submission_text', instance.submission_text)
        instance.submission_file = validated_data.get('submission_file', instance.submission_file)
        instance.submission_files = validated_data.get('submission_files', instance.submission_files)
        instance.time_spent = validated_data.get('time_spent', instance.time_spent)
        instance.submission_date = timezone.now()
        instance.last_accessed = timezone.now()
        
        if request:
            instance.ip_address = request.META.get('REMOTE_ADDR')
            instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Set status based on submission time
        if instance.submission_date > instance.assignment.due_date:
            instance.status = 'late'
        else:
            instance.status = 'submitted'
        
        instance.version += 1
        instance.save()
        return instance


class StudentAssignmentGradeSerializer(serializers.ModelSerializer):
    """Serializer for grading assignments"""
    class Meta:
        model = StudentAssignment
        fields = ['marks_obtained', 'penalty_points', 'grade', 'teacher_feedback', 'rubric_scores']
    
    def validate(self, data):
        """Validate grading data"""
        marks_obtained = data.get('marks_obtained')
        if marks_obtained is not None:
            if marks_obtained > self.instance.assignment.total_marks:
                raise serializers.ValidationError({
                    'marks_obtained': f'Marks obtained cannot exceed total marks ({self.instance.assignment.total_marks}).'
                })
        
        return data
    
    def update(self, instance, validated_data):
        """Handle grading"""
        request = self.context.get('request')
        
        instance.marks_obtained = validated_data.get('marks_obtained', instance.marks_obtained)
        instance.penalty_points = validated_data.get('penalty_points', instance.penalty_points)
        instance.grade = validated_data.get('grade', instance.grade)
        instance.teacher_feedback = validated_data.get('teacher_feedback', instance.teacher_feedback)
        instance.rubric_scores = validated_data.get('rubric_scores', instance.rubric_scores)
        instance.status = 'graded'
        instance.graded_at = timezone.now()
        
        if request and hasattr(request.user, 'teacher_profile'):
            instance.graded_by = request.user.teacher_profile
        
        instance.save()
        return instance


class AssignmentGroupSerializer(serializers.ModelSerializer):
    """Serializer for assignment groups"""
    leader_details = StudentSerializer(read_only=True, source='leader')
    assignment_details = AssignmentListSerializer(read_only=True, source='assignment')
    members_count = serializers.SerializerMethodField()
    has_valid_size = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentGroup
        fields = [
            'id', 'name', 'assignment', 'assignment_details', 'leader', 'leader_details',
            'members_count', 'has_valid_size', 'members', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_has_valid_size(self, obj):
        return obj.members.count() <= obj.assignment.max_group_size
    
    def get_members(self, obj):
        members = obj.members.all()
        return StudentSerializer(members, many=True).data


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group membership"""
    student_details = StudentSerializer(read_only=True, source='student')
    group_details = AssignmentGroupSerializer(read_only=True, source='group')
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'group', 'group_details', 'student', 'student_details', 'joined_at', 'is_active']


class AssignmentCommentSerializer(serializers.ModelSerializer):
    """Serializer for assignment comments"""
    author_details = CustomUserSerializer(read_only=True, source='author')
    assignment_details = AssignmentListSerializer(read_only=True, source='assignment')
    student_assignment_details = StudentAssignmentMiniSerializer(read_only=True, source='student_assignment')
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentComment
        fields = [
            'id', 'assignment', 'assignment_details', 'student_assignment', 'student_assignment_details',
            'author', 'author_details', 'parent_comment', 'content', 'is_private',
            'file_attachment', 'replies', 'reply_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Get nested replies"""
        replies = obj.replies.all()
        return AssignmentCommentSerializer(replies, many=True).data
    
    def get_reply_count(self, obj):
        return obj.replies.count()
    
    def create(self, validated_data):
        """Set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AssignmentDashboardSerializer(serializers.Serializer):
    """Serializer for assignment dashboard data"""
    total_assignments = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()
    submitted_assignments = serializers.IntegerField()
    graded_assignments = serializers.IntegerField()
    overdue_assignments = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    recent_assignments = AssignmentListSerializer(many=True)
    upcoming_deadlines = AssignmentListSerializer(many=True)


class TeacherAssignmentStatsSerializer(serializers.Serializer):
    """Serializer for teacher assignment statistics"""
    total_created = serializers.IntegerField()
    published_count = serializers.IntegerField()
    graded_count = serializers.IntegerField()
    average_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    pending_grading = serializers.IntegerField()
    subject_breakdown = serializers.JSONField()